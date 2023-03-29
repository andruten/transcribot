import logging
import os
import tempfile
from typing import Union

from pydub import AudioSegment
from telegram import Voice, Audio
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)


class TelegramAudioManager:

    def __init__(
            self,
            context: CallbackContext,
            file: Union[Voice, Audio],
            file_download_path: str = None,
    ) -> None:
        if not isinstance(file, Audio) and not isinstance(file, Voice):
            raise RuntimeError('file must be an Audio or Voice instance')
        if file_download_path is None:
            file_download_path = tempfile.gettempdir()
        self.context = context
        self.file = file
        self.ogg_audio_path = os.path.join(file_download_path, f'{file.file_unique_id}.ogg')
        self.mp3_audio_path = os.path.join(file_download_path, f'{file.file_unique_id}.mp3')

    async def __aenter__(self) -> str:
        await self._download_voice_message()
        self._convert_ogg_to_mp3()
        return self.mp3_audio_path

    async def __aexit__(self, *args, **kwargs) -> bool:
        self._clean_up_files()
        return True

    def _clean_up_files(self) -> None:
        logger.debug(f'Removing temporary files {self.mp3_audio_path} and {self.ogg_audio_path}')
        os.remove(self.mp3_audio_path)
        os.remove(self.ogg_audio_path)

    async def _download_voice_message(self) -> None:
        logger.debug(f'Downloading file')
        new_file = await self.context.bot.get_file(self.file.file_id)
        await new_file.download_to_drive(custom_path=self.ogg_audio_path)

    def _convert_ogg_to_mp3(self) -> None:
        audio = AudioSegment.from_file(self.ogg_audio_path, format='ogg')
        audio.export(self.mp3_audio_path, format='mp3')
