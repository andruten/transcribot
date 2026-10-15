import re

from telegram.constants import MessageLimit

STREAM_EDIT_INTERVAL = 1.0
TYPING_ACTION_INTERVAL = 4.0
MAX_MESSAGE_LENGTH = MessageLimit.MAX_TEXT_LENGTH
# Skip Telegram edits while the revealed text has grown by less than this;
# each edit re-uploads the full message text, so small increments waste API
# calls and risk flood limits on long transcriptions.
MIN_REVEAL_GROWTH = 40

WORD_PATTERN = re.compile(r"\S+")

BREAK_CHARACTERS = ("\n", " ")


def split_message(text: str, max_length: int = MAX_MESSAGE_LENGTH) -> list[str]:
    if len(text) <= max_length:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        if len(text) - start <= max_length:
            chunks.append(text[start:])
            break
        window = text[start : start + max_length]
        cut = 0
        for break_character in BREAK_CHARACTERS:
            cut = max(cut, window.rfind(break_character))
        if cut == 0:
            cut = max_length
        chunks.append(text[start : start + cut])
        start += cut
        while start < len(text) and text[start] in BREAK_CHARACTERS:
            start += 1
    return [chunk for chunk in chunks if chunk]


def next_reveal(current_text: str, full_text: str) -> str:
    # current_text is always a prefix of full_text cut at a word boundary, so
    # work only on the pending suffix instead of scanning the full text.
    if not full_text or not full_text.startswith(current_text):
        return full_text
    pending = full_text[len(current_text) :]
    if not pending.strip():
        return current_text
    pending_words = WORD_PATTERN.findall(pending)
    words_to_reveal = max(1, len(pending_words) // 2)
    for count, match in enumerate(WORD_PATTERN.finditer(pending), start=1):
        if count == words_to_reveal:
            return full_text[: len(current_text) + match.end()]
    return full_text
