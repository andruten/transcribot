import asyncio
import logging
import os
from collections.abc import AsyncGenerator

from faster_whisper import WhisperModel
from faster_whisper.transcribe import TranscriptionInfo

logger = logging.getLogger(__name__)

whisper_model_name = os.environ.get("WHISPER_MODEL", default="tiny")
device = os.environ.get("WHISPER_DEVICE", default="cpu")
compute_type = os.environ.get("WHISPER_COMPUTE_TYPE", default="int8")
beam_size = int(os.environ.get("WHISPER_BEAM_SIZE", default="5"))

model_kwargs = {
    "device": device,
    "compute_type": compute_type,
}

if cpu_threads := os.environ.get("WHISPER_CPU_THREADS"):
    model_kwargs["cpu_threads"] = int(cpu_threads)

if num_workers := os.environ.get("WHISPER_NUM_WORKERS"):
    model_kwargs["num_workers"] = int(num_workers)

logger.info(
    "Loading faster-whisper model %s with device=%s compute_type=%s",
    whisper_model_name,
    device,
    compute_type,
)
whisper_model = WhisperModel(whisper_model_name, **model_kwargs)


class AudioTranscriber:
    @property
    def model(self) -> WhisperModel:
        return whisper_model

    async def transcribe_audio_stream(
        self, mp3_audio_path: str
    ) -> AsyncGenerator[tuple[str, TranscriptionInfo], None]:
        logger.info(f"Transcribing audio file {mp3_audio_path}")
        segments, info = await asyncio.to_thread(
            self.model.transcribe,
            mp3_audio_path,
            beam_size=beam_size,
            temperature=0,
            suppress_tokens=None,
        )
        text = ""
        yield text, info
        while (segment := await asyncio.to_thread(next, segments, None)) is not None:
            text += segment.text
            yield text, info
        logger.info(f"Audio file {mp3_audio_path} has been transcribed successfully")


audio_transcriber = AudioTranscriber()
