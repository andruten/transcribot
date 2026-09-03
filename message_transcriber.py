from collections.abc import AsyncGenerator
from typing import Any

from telegram.ext import CallbackContext

from streaming import MAX_MESSAGE_LENGTH, split_message
from telegram_file_manager import AudioConverter, TelegramFileDownloader
from transcriber import audio_transcriber

TRANSCRIPTION_LABEL = 'Transcription:\n'
CODE_FENCE_OVERHEAD = len('```\n') + len('\n```')


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
    def to_markdown(text: dict, processing_time: float, max_length: int = MAX_MESSAGE_LENGTH) -> list[str]:
        transcription = text['text'].removeprefix(' ')
        language_ = text['language']
        header = f'Detected language: {language_}\nProcessing time: {int(processing_time)}s\n'
        first_chunk_capacity = max_length - len(header) - len(TRANSCRIPTION_LABEL) - CODE_FENCE_OVERHEAD
        chunks = split_message(transcription, first_chunk_capacity)
        first_part = f'{header}{TRANSCRIPTION_LABEL}```\n{chunks[0]}\n```'
        return [first_part] + [f'```\n{chunk}\n```' for chunk in chunks[1:]]
