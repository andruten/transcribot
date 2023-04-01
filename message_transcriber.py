from telegram.ext import CallbackContext

from telegram_file_manager import TelegramAudioManager
from transcriber import audio_transcriber


class AudioMessageTranscriber:

    @staticmethod
    async def transcribe(context: CallbackContext, audio) -> str:
        async with TelegramAudioManager(context, audio) as mp3_audio_path:
            try:
                result, processing_time = audio_transcriber.transcribe_audio(mp3_audio_path)
                text = audio_transcriber.get_as_markdown(result, processing_time)
            except Exception as e:
                text = f'Error converting video to audio. Exception={e}'
        return text
