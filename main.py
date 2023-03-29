import logging
import os

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler

from filter_allowed_chats import FilterAllowedChats
from message_transcriber import AudioMessageTranscriber

LOG_LEVEL = logging.DEBUG if os.environ.get('LOG_LEVEL', 'INFO') == 'DEBUG' else logging.INFO

allowed_chat_ids = os.environ.get("ALLOWED_CHAT_IDS", default="").split(",")

logging.basicConfig(level=LOG_LEVEL,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


async def transcribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.voice:
        audio = update.message.voice
    elif update.message.audio:
        audio = update.message.audio
    elif update.message.video:
        audio = update.message.video
    elif update.message.document:
        audio = update.message.document
    else:
        logger.warning('Message is not a video, not an audio, not a voice and not a document.')
        return
    logger.info('Transcribing Audio message')
    markdown_text = await AudioMessageTranscriber.transcribe(context, audio)
    await update.message.reply_text(markdown_text, parse_mode=ParseMode.MARKDOWN)


if __name__ == '__main__':
    app = ApplicationBuilder().token(os.environ.get('BOT_TOKEN')).build()

    app.add_handler(CommandHandler('transcribe', transcribe))

    filter_allowed_chats = FilterAllowedChats(allowed_chat_ids)
    audio_message_handler = MessageHandler(filter_allowed_chats, transcribe)
    app.add_handler(audio_message_handler)

    app.run_polling()
