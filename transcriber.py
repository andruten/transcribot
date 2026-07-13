import logging
import os
import time

from faster_whisper import WhisperModel

logger = logging.getLogger(__name__)

whisper_model_name = os.environ.get('WHISPER_MODEL', default='tiny')
device = os.environ.get('WHISPER_DEVICE', default='cpu')
compute_type = os.environ.get('WHISPER_COMPUTE_TYPE', default='int8')
beam_size = int(os.environ.get('WHISPER_BEAM_SIZE', default='5'))

model_kwargs = {
    'device': device,
    'compute_type': compute_type,
}

if cpu_threads := os.environ.get('WHISPER_CPU_THREADS'):
    model_kwargs['cpu_threads'] = int(cpu_threads)

if num_workers := os.environ.get('WHISPER_NUM_WORKERS'):
    model_kwargs['num_workers'] = int(num_workers)

logger.info(
    'Loading faster-whisper model %s with device=%s compute_type=%s',
    whisper_model_name,
    device,
    compute_type,
)
whisper_model = WhisperModel(whisper_model_name, **model_kwargs)


class AudioTranscriber:

    @property
    def model(self) -> WhisperModel:
        return whisper_model

    def transcribe_audio(self, mp3_audio_path: str) -> tuple[dict, float]:
        start_time = time.time()
        segments, info = self.model.transcribe(mp3_audio_path, beam_size=beam_size)
        transcription = ''.join(segment.text for segment in segments)
        result = {
            'text': transcription,
            'language': info.language,
        }
        final_time = time.time()
        processing_time = final_time - start_time
        logger.info(f'Audio processed in {processing_time}')
        return result, processing_time


audio_transcriber = AudioTranscriber()
