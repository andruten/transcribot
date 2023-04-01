import logging
import os
import time
from typing import Dict

import whisper

logger = logging.getLogger(__name__)

whisper_model = os.environ.get('WHISPER_MODEL', default='tiny')
device = os.environ.get('WHISPER_DEVICE', default='cpu')

whisper_model = whisper.load_model(whisper_model, device=device)


class AudioTranscriber:

    @property
    def model(self) -> whisper.Whisper:
        return whisper_model

    def transcribe_audio(self, mp3_audio_path: str) -> [Dict, float]:
        start_time = time.time()
        audio = whisper.load_audio(mp3_audio_path)
        result = self.model.transcribe(audio, fp16=False)
        final_time = time.time()
        processing_time = final_time - start_time
        logger.info(f'Audio processed in {processing_time}')
        return result, processing_time

    async def escape_markdown_chars(self, text: str) -> str:
        escaping_chars = ['_', '*', '[', ']', '(', ')', '~', '>', '+', '-', '=', '|', '{', '}', '.', '!']
        temporal = text
        for char in escaping_chars:
            temporal = temporal.replace(char, f"\\{char}")
        return temporal.replace('\. ', '.\n\n').replace('\.', '.')

    def get_as_markdown(self, text: Dict, processing_time) -> str:
        transcription = text["text"].removeprefix(" ")
        language_ = text["language"]
        markdown_message = f'''\
Detected language: {language_}
Processing time: {int(processing_time)}s
Transcription:
```
{transcription}
```
        '''
        return await self.escape_markdown_chars(markdown_message)


audio_transcriber = AudioTranscriber()
