import asyncio
import contextlib
import logging
import os
import time

from telegram import Audio, Message, Update, VideoNote, Voice
from telegram.constants import ChatAction, ParseMode
from telegram.error import BadRequest, RetryAfter, TelegramError
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler

from filter_allowed_chats import FilterAllowedChats
from message_transcriber import AudioMessageTranscriber
from streaming import MAX_MESSAGE_LENGTH, STREAM_EDIT_INTERVAL, TYPING_ACTION_INTERVAL, next_reveal, split_message
from telegram_file_manager import MAX_DOWNLOAD_SIZE, FileTooBigError

LOG_LEVEL = logging.DEBUG if os.environ.get('LOG_LEVEL', 'INFO') == 'DEBUG' else logging.INFO

allowed_chat_ids = os.environ.get('ALLOWED_CHAT_IDS', default='').split(',')

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


async def transcribe(audio, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if audio.file_size and audio.file_size > MAX_DOWNLOAD_SIZE:
        logger.info(f'Audio file too big to transcribe: {audio.file_size} bytes')
        await update.effective_message.reply_text(
            f'Este fichero es demasiado grande para transcribir '
            f'({audio.file_size / (1024 * 1024):.1f} MB). '
            f'El máximo que permite descargar la API de Telegram es '
            f'{MAX_DOWNLOAD_SIZE // (1024 * 1024)} MB.',
        )
        return
    logger.info('Transcribing Audio message')
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    placeholder = await update.message.reply_text('Transcribing…')
    parts = [placeholder]
    start_time = time.time()
    stream = {'text': '', 'info': None, 'done': False}

    async def produce() -> None:
        try:
            async for partial_text, info in AudioMessageTranscriber.transcribe_stream(context, audio):
                if partial_text:
                    stream['text'] = partial_text
                stream['info'] = info
        finally:
            stream['done'] = True

    async def keep_typing() -> None:
        while True:
            await asyncio.sleep(TYPING_ACTION_INTERVAL)
            try:
                await context.bot.send_chat_action(
                    chat_id=update.effective_chat.id, action=ChatAction.TYPING,
                )
            except TelegramError:
                logger.debug('Failed to refresh the typing chat action')

    async def render_parts(new_parts: list[str], parse_mode: str | None = None) -> None:
        while len(parts) > len(new_parts):
            extra = parts.pop()
            with contextlib.suppress(TelegramError):
                await extra.delete()
        for index, part in enumerate(new_parts):
            try:
                if index < len(parts):
                    message = parts[index]
                    if message.text == part:
                        continue
                    await message.edit_text(part, parse_mode=parse_mode)
                else:
                    parts.append(await update.message.reply_text(part, parse_mode=parse_mode))
            except RetryAfter as error:
                logger.debug(f'Telegram flood limit hit, retrying in {error.retry_after}s')
                await asyncio.sleep(error.retry_after)
                if index < len(parts):
                    await parts[index].edit_text(part, parse_mode=parse_mode)
                else:
                    parts.append(await update.message.reply_text(part, parse_mode=parse_mode))

    async def render() -> None:
        shown_text = ''
        while True:
            await asyncio.sleep(STREAM_EDIT_INTERVAL)
            target_text = next_reveal(shown_text, stream['text'])
            if target_text == shown_text:
                if stream['done']:
                    return
                continue
            await render_parts(split_message(target_text, MAX_MESSAGE_LENGTH))
            shown_text = target_text

    producer_task = asyncio.create_task(produce())
    typing_task = asyncio.create_task(keep_typing())
    try:
        await render()
        await producer_task
    finally:
        typing_task.cancel()
        if not producer_task.done():
            producer_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await typing_task
            if not producer_task.done():
                await producer_task
    processing_time = time.time() - start_time
    markdown_parts = AudioMessageTranscriber.to_markdown(
        {'text': stream['text'], 'language': stream['info'].language}, processing_time,
    )
    await render_parts(markdown_parts, parse_mode=ParseMode.MARKDOWN)


def _get_audio_from_message(message: Message) -> Voice | Audio | VideoNote | None:
    try:
        return (
            message.voice
            or message.audio
            or message.video_note
            or None
        )
    except AttributeError:
        return None


async def prepare_to_transcribe(update, context, message):
    audio = _get_audio_from_message(message)
    if audio is None:
        logger.info('Message is not a voice, not an audio or not a video note.')
        return
    await transcribe(audio, update, context)


async def transcribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await prepare_to_transcribe(update, context, update.message.reply_to_message)


async def transcribe_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await prepare_to_transcribe(update, context, update.message)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error('Exception while handling an update:', exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        if isinstance(context.error, (BadRequest, FileTooBigError)) and 'too big' in str(context.error).lower():
            reply_text = 'El fichero es demasiado grande para ser descargado (máximo 20 MB).'
        else:
            reply_text = (
                'No he podido transcribir este mensaje. '
                'Comprueba que contiene audio e inténtalo de nuevo.'
            )
        try:
            await update.effective_message.reply_text(reply_text)
        except Exception:
            logger.exception('Failed to notify the user about the error')


def main():
    bot_token = os.environ.get('BOT_TOKEN')
    app = ApplicationBuilder().token(bot_token).build()
    # Filters
    filter_allowed_chats = FilterAllowedChats(allowed_chat_ids)
    # Handlers
    app.add_handler(CommandHandler('transcribe', transcribe_command, filter_allowed_chats))
    app.add_handler(MessageHandler(filter_allowed_chats, transcribe_message))
    app.add_error_handler(error_handler)
    app.run_polling()


if __name__ == '__main__':
    main()
