import re

STREAM_EDIT_INTERVAL = 1.0
TYPING_ACTION_INTERVAL = 4.0

WORD_PATTERN = re.compile(r'\S+')


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
