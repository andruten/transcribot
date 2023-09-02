import logging
import os

from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler

from filter_allowed_chats import FilterAllowedChats
from message_transcriber import AudioMessageTranscriber

LOG_LEVEL = logging.DEBUG if os.environ.get('LOG_LEVEL', 'INFO') == 'DEBUG' else logging.INFO

allowed_chat_ids = os.environ.get('ALLOWED_CHAT_IDS', default='').split(',')

logging.basicConfig(level=LOG_LEVEL,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


async def transcribe(audio, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info('Transcribing Audio message')
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    markdown_text = await AudioMessageTranscriber.transcribe(context, audio)
    await update.message.reply_text(markdown_text, parse_mode=ParseMode.MARKDOWN)


async def transcribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.reply_to_message.voice:
        audio = update.message.reply_to_message.voice
    elif update.message.reply_to_message.audio:
        audio = update.message.reply_to_message.audio
    else:
        logger.debug('Message is not a video, not an audio, not a voice and not a document.')
        return
    await transcribe(audio, update, context)


async def transcribe_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.voice:
        audio = update.message.voice
    elif update.message.audio:
        audio = update.message.audio
    else:
        logger.debug('Message is not a video, not an audio, not a voice and not a document.')
        return
    await transcribe(audio, update, context)


def main():
    bot_token = os.environ.get('BOT_TOKEN')
    app = ApplicationBuilder().token(bot_token).build()
    # Filters
    filter_allowed_chats = FilterAllowedChats(allowed_chat_ids)
    # Handlers
    app.add_handler(CommandHandler('transcribe', transcribe_command, filter_allowed_chats))
    app.add_handler(MessageHandler(filter_allowed_chats, transcribe_message))
    app.run_polling()


if __name__ == '__main__':
    main()
