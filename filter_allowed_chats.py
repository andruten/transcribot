import logging
from typing import List

from telegram import Message
from telegram.ext.filters import MessageFilter

logger = logging.getLogger(__name__)


class FilterAllowedChats(MessageFilter):

    def __init__(self, allowed_chat_ids: List[str]):
        super().__init__()
        self.allowed_chat_ids = allowed_chat_ids

    def _effective_message(self, message: Message):
        return message if message.reply_to_message is None else message.reply_to_message

    def _is_voice(self, message: Message) -> bool:
        effective_message = self._effective_message(message)
        return bool(
            effective_message.voice
            or effective_message.audio
            or effective_message.video
            or effective_message.video_note
            or effective_message.document
        )

    def filter(self, message: Message) -> bool:
        chat_id = str(message.chat.id)
        is_allowed_user = chat_id in self.allowed_chat_ids
        if not is_allowed_user:
            logger.info(f'chat_id="{chat_id}" is not allowed')

        is_voice = self._is_voice(message)
        if not is_voice:
            logger.debug(f'chat_id={chat_id}: ignoring a message because it is not a voice or audio or video or '
                         f'document message')

        return is_voice and is_allowed_user
