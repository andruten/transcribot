import re

from telegram.constants import MessageLimit

STREAM_EDIT_INTERVAL = 1.0
TYPING_ACTION_INTERVAL = 4.0
MAX_MESSAGE_LENGTH = MessageLimit.MAX_TEXT_LENGTH

WORD_PATTERN = re.compile(r'\S+')

BREAK_CHARACTERS = ('\n', ' ')


def split_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list[str]:
    if len(text) <= max_length:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        if len(text) - start <= max_length:
            chunks.append(text[start:])
            break
        window = text[start:start + max_length]
        cut = 0
        for break_character in BREAK_CHARACTERS:
            cut = max(cut, window.rfind(break_character))
        if cut == 0:
            cut = max_length
        chunks.append(text[start:start + cut])
        start += cut
        while start < len(text) and text[start] in BREAK_CHARACTERS:
            start += 1
    return [chunk for chunk in chunks if chunk]


def next_reveal(current_text: str, full_text: str) -> str:
    if not full_text or not full_text.startswith(current_text):
        return full_text
    total_words = len(WORD_PATTERN.findall(full_text))
    revealed_words = len(WORD_PATTERN.findall(current_text))
    pending_words = total_words - revealed_words
    if pending_words <= 0:
        return current_text
    words_to_reveal = max(1, pending_words // 2)
    target_word = revealed_words + words_to_reveal
    for count, match in enumerate(WORD_PATTERN.finditer(full_text), start=1):
        if count == target_word:
            return full_text[:match.end()]
    return full_text
