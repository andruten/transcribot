import logging
import os
import tempfile
from typing import Union

from pydub import AudioSegment
from telegram import Audio, Voice
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)


class TelegramFileDownloader:
    def __init__(
            self,
            context: CallbackContext,
            file: Union[Voice, Audio],
            file_download_path: str = None,
    ):
        if file_download_path is None:
            file_download_path = tempfile.gettempdir()
        self.context = context
        self.file = file
        self.input_audio_path = os.path.join(file_download_path, f'{file.file_unique_id}')

    async def download_file(self) -> None:
        logger.info(f'Downloading file {self.file.file_id}')
        new_file = await self.context.bot.get_file(self.file.file_id)
        await new_file.download_to_drive(custom_path=self.input_audio_path)
        logger.info(f'File {self.file.file_id} has been downloaded successfully')

    def clean_up_file(self) -> None:
        logger.info(f'Removing temporary file {self.input_audio_path}')
        os.remove(self.input_audio_path)


class AudioConverter:
    def __init__(
            self,
            input_audio_path: str = None,
    ):
        self.input_audio_path = input_audio_path
        self.mp3_audio_path = f'{input_audio_path}.mp3'

    def convert_ogg_to_mp3(self) -> None:
        logger.info(f'Converting file {self.input_audio_path} to mp3')
        audio = AudioSegment.from_file(self.input_audio_path)
        audio.export(self.mp3_audio_path, format='mp3')
        logger.info(f'File {self.input_audio_path} has been converted to mp3 successfully')

    def clean_up_file(self) -> None:
        logger.info(f'Removing temporary file {self.mp3_audio_path}')
        os.remove(self.mp3_audio_path)
