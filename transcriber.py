import asyncio
import logging
import os
import time
from collections.abc import AsyncGenerator

from faster_whisper import WhisperModel
from faster_whisper.transcribe import TranscriptionInfo

logger = logging.getLogger(__name__)

whisper_model_name = os.environ.get("WHISPER_MODEL", default="tiny")
device = os.environ.get("WHISPER_DEVICE", default="cpu")
compute_type = os.environ.get("WHISPER_COMPUTE_TYPE", default="int8")
beam_size = int(os.environ.get("WHISPER_BEAM_SIZE", default="1"))
language = os.environ.get("WHISPER_LANGUAGE") or None

model_kwargs = {
    "device": device,
    "compute_type": compute_type,
}

if cpu_threads := os.environ.get("WHISPER_CPU_THREADS"):
    model_kwargs["cpu_threads"] = int(cpu_threads)

if num_workers := os.environ.get("WHISPER_NUM_WORKERS"):
    model_kwargs["num_workers"] = int(num_workers)

transcribe_options = {
    "beam_size": beam_size,
    "vad_filter": True,
    "vad_parameters": {"min_silence_duration_ms": 500},
    "condition_on_previous_text": False,
    "temperature": 0,
}

if language:
    transcribe_options["language"] = language

logger.info(
    "Loading faster-whisper model %s with device=%s compute_type=%s",
    whisper_model_name,
    device,
    compute_type,
)
whisper_model = WhisperModel(whisper_model_name, **model_kwargs)


class AudioTranscriber:
    # CTranslate2 inference is CPU-bound and the WhisperModel instance is a
    # singleton: serialize it so concurrent audio messages don't fight for CPU
    # threads. The eager audio preparation (decode, VAD, features) runs outside
    # the lock and overlaps with another message's inference; its language
    # detection makes one model call at most, which CTranslate2 serializes
    # safely anyway. Downloads and Telegram renders still overlap in parallel
    # (see concurrent_updates in main.py).
    transcribe_lock = asyncio.Semaphore(1)

    @property
    def model(self) -> WhisperModel:
        return whisper_model

    async def transcribe_audio_stream(
        self, audio_path: str
    ) -> AsyncGenerator[tuple[str, TranscriptionInfo], None]:
        logger.info(f"Transcribing audio file {audio_path}")
        start_time = time.perf_counter()
        segments, info = await asyncio.to_thread(
            self.model.transcribe,
            audio_path,
            suppress_tokens=None,
            **transcribe_options,
        )
        preparation_time = time.perf_counter() - start_time
        logger.info(
            f"Audio is prepared in {preparation_time:.1f}s (decode, VAD, features)"
        )
        async with self.transcribe_lock:
            text = ""
            yield text, info
            while (
                segment := await asyncio.to_thread(next, segments, None)
            ) is not None:
                text += segment.text
                yield text, info
            processing_time = time.perf_counter() - start_time
            logger.info(
                f"Audio file {audio_path} has been transcribed in "
                f"{processing_time:.1f}s ({preparation_time:.1f}s of preparation)"
            )


audio_transcriber = AudioTranscriber()
