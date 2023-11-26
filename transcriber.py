import logging
import os
import time

import whisper

logger = logging.getLogger(__name__)

whisper_model = os.environ.get('WHISPER_MODEL', default='tiny')
device = os.environ.get('WHISPER_DEVICE', default='cpu')

whisper_model = whisper.load_model(whisper_model, device=device)


class AudioTranscriber:

    @property
    def model(self) -> whisper.Whisper:
        return whisper_model

    def transcribe_audio(self, mp3_audio_path: str) -> tuple[dict, float]:
        start_time = time.time()
        audio = whisper.load_audio(mp3_audio_path)
        result = self.model.transcribe(audio, fp16=False)
        final_time = time.time()
        processing_time = final_time - start_time
        logger.info(f'Audio processed in {processing_time}')
        return result, processing_time


audio_transcriber = AudioTranscriber()
