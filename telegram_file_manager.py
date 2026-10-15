import logging
import os
import tempfile
from typing import Union

from telegram import Audio, Voice
from telegram.ext import CallbackContext

logger = logging.getLogger(__name__)

MAX_DOWNLOAD_SIZE = 20 * 1024 * 1024


class FileTooBigError(Exception):
    pass


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
        self.input_audio_path = os.path.join(
            file_download_path, f"{file.file_unique_id}"
        )

    async def download_file(self) -> None:
        if self.file.file_size and self.file.file_size > MAX_DOWNLOAD_SIZE:
            raise FileTooBigError(
                f"File {self.file.file_id} is {self.file.file_size} bytes, "
                f"which exceeds the {MAX_DOWNLOAD_SIZE} bytes download limit"
            )
        logger.info(f"Downloading file {self.file.file_id}")
        new_file = await self.context.bot.get_file(self.file.file_id)
        await new_file.download_to_drive(custom_path=self.input_audio_path)
        logger.info(f"File {self.file.file_id} has been downloaded successfully")

    def clean_up_file(self) -> None:
        if not os.path.exists(self.input_audio_path):
            return
        logger.info(f"Removing temporary file {self.input_audio_path}")
        os.remove(self.input_audio_path)
