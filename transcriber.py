import logging
import os
from typing import Dict, Iterator

import faster_whisper

logger = logging.getLogger(__name__)

whisper_model = os.environ.get('WHISPER_MODEL', default='tiny')
device = os.environ.get('WHISPER_DEVICE', default='cpu')

whisper_model = model = faster_whisper.WhisperModel(
    whisper_model,
    device=device,
    compute_type='float32',
)


class AudioTranscriber:

    @property
    def model(self) -> faster_whisper.WhisperModel:
        return whisper_model

    def transcribe_audio(self, mp3_audio_path: str) -> [Dict, float]:
        segments, transcription_info = self.model.transcribe(mp3_audio_path)
        logger.info('Audio processed')
        return segments, transcription_info

    def escape_markdown_chars(self, text: str) -> str:
        escaping_chars = ['_', '*', '[', ']', '(', ')', '~', '>', '+', '-', '=', '|', '{', '}', '.', '!']
        temporal = text
        for char in escaping_chars:
            temporal = temporal.replace(char, f'\\{char}')
        return temporal.replace(r'\. ', '.\n\n').replace(r'\.', '.')

    def get_as_markdown(self, segments: Iterator, transcription_info) -> str:
        transcription = ''
        for segment in segments:
            transcription += f'{segment.text}'
        markdown_message = f'''\
Detected language: {transcription_info.language}
Transcription:
```
{transcription}
```
        '''
        return self.escape_markdown_chars(markdown_message)


audio_transcriber = AudioTranscriber()
