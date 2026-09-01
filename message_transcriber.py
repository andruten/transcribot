from collections.abc import AsyncGenerator
from typing import Any

from telegram.ext import CallbackContext

from telegram_file_manager import AudioConverter, TelegramFileDownloader
from transcriber import audio_transcriber


class AudioMessageTranscriber:
    @staticmethod
    async def transcribe_stream(context: CallbackContext, audio) -> AsyncGenerator[tuple[str, Any], None]:
        telegram_file_downloader = TelegramFileDownloader(context, audio)
        await telegram_file_downloader.download_file()
        audio_converter = AudioConverter(telegram_file_downloader.input_audio_path)
        try:
            audio_converter.convert_ogg_to_mp3()
            async for partial in audio_transcriber.transcribe_audio_stream(audio_converter.mp3_audio_path):
                yield partial
        finally:
            telegram_file_downloader.clean_up_file()
            audio_converter.clean_up_file()

    @staticmethod
    def to_markdown(text: dict, processing_time: float) -> str:
        transcription = text['text'].removeprefix(' ')
        language_ = text['language']
        markdown_message = f'''\
Detected language: {language_}
Processing time: {int(processing_time)}s
Transcription:
```
{transcription}
```
        '''
        return markdown_message
