import logging
import os
import time

from telegram import Audio, Document, Message, Update, Video, VideoNote, Voice
from telegram.constants import ChatAction, ParseMode
from telegram.error import BadRequest
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler

from filter_allowed_chats import FilterAllowedChats
from message_transcriber import AudioMessageTranscriber
from telegram_file_manager import MAX_DOWNLOAD_SIZE, FileTooBigError

LOG_LEVEL = logging.DEBUG if os.environ.get('LOG_LEVEL', 'INFO') == 'DEBUG' else logging.INFO

allowed_chat_ids = os.environ.get('ALLOWED_CHAT_IDS', default='').split(',')

logging.basicConfig(level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('httpx').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

STREAM_EDIT_INTERVAL = 1.5


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
    partial_text, info = '', None
    start_time = time.time()
    last_edit_time = 0.0
    last_edited_text = ''
    async for partial_text, info in AudioMessageTranscriber.transcribe_stream(context, audio):
        if not partial_text or partial_text == last_edited_text:
            continue
        if time.time() - last_edit_time >= STREAM_EDIT_INTERVAL:
            await placeholder.edit_text(partial_text)
            last_edited_text = partial_text
            last_edit_time = time.time()
    processing_time = time.time() - start_time
    markdown_text = AudioMessageTranscriber.to_markdown(
        {'text': partial_text, 'language': info.language}, processing_time,
    )
    await placeholder.edit_text(markdown_text, parse_mode=ParseMode.MARKDOWN)


def _get_audio_from_message(message: Message) -> Voice | Audio | Video | VideoNote | Document | None:
    try:
        return (
            message.voice
            or message.audio
            or message.video
            or message.video_note
            or None
        )
    except AttributeError:
        return None


async def prepare_to_transcribe(update, context, message):
    audio = _get_audio_from_message(message)
    if audio is None:
        logger.info('Message is not a video, not an audio or not a voice.')
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
