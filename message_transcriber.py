import logging
from collections.abc import AsyncGenerator
from html import escape
from time import perf_counter
from typing import Any

from telegram.ext import CallbackContext

from streaming import MAX_MESSAGE_LENGTH, split_message
from telegram_file_manager import TelegramFileDownloader
from transcriber import audio_transcriber

logger = logging.getLogger(__name__)

TRANSCRIPTION_LABEL = "Transcription:\n"
CODE_TAG_OVERHEAD = len("<pre>\n") + len("\n</pre>")


class AudioMessageTranscriber:
    @staticmethod
    async def transcribe_stream(
        context: CallbackContext, audio
    ) -> AsyncGenerator[tuple[str, Any], None]:
        telegram_file_downloader = TelegramFileDownloader(context, audio)
        download_start = perf_counter()
        await telegram_file_downloader.download_file()
        logger.info(
            f"File {audio.file_id} downloaded in {perf_counter() - download_start:.1f}s"
        )
        try:
            async for partial in audio_transcriber.transcribe_audio_stream(
                telegram_file_downloader.input_audio_path
            ):
                yield partial
        finally:
            telegram_file_downloader.clean_up_file()

    @staticmethod
    def to_markdown(
        text: dict, processing_time: float, max_length: int = MAX_MESSAGE_LENGTH
    ) -> list[str]:
        transcription = text["text"].removeprefix(" ")
        language_ = text["language"]
        header = f"Detected language: {language_}\nProcessing time: {int(processing_time)}s\n"
        first_chunk_capacity = (
            max_length - len(header) - len(TRANSCRIPTION_LABEL) - CODE_TAG_OVERHEAD
        )
        chunks = split_message(transcription, first_chunk_capacity)
        first_part = f"{header}{TRANSCRIPTION_LABEL}<pre>\n{escape(chunks[0])}\n</pre>"
        return [first_part] + [
            f"<pre>\n{escape(chunk)}\n</pre>" for chunk in chunks[1:]
        ]
