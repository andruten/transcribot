from streaming import next_reveal, split_message


def test_reveals_one_word_from_empty_text():
    assert next_reveal("", "Hola mundo") == "Hola"


def test_reveals_half_of_pending_words():
    full_text = "uno dos tres cuatro cinco seis"
    first = next_reveal("", full_text)
    assert first == "uno dos tres"
    second = next_reveal(first, full_text)
    assert second == "uno dos tres cuatro"


def test_returns_current_text_when_fully_revealed():
    assert next_reveal("Hola mundo", "Hola mundo") == "Hola mundo"


def test_returns_current_text_when_only_whitespace_remains():
    assert next_reveal("Hola mundo", "Hola mundo ") == "Hola mundo"


def test_handles_whitespace_between_words():
    full_text = "Hola\nmundo  que tal"
    assert next_reveal("", full_text) == "Hola\nmundo"
    assert next_reveal("Hola\nmundo", full_text) == "Hola\nmundo  que"


def test_returns_full_text_when_current_is_not_a_prefix():
    assert next_reveal("otra cosa", "Hola mundo") == "Hola mundo"


def test_returns_empty_text_when_there_is_nothing_to_reveal():
    assert next_reveal("", "") == ""


def test_split_message_returns_single_chunk_for_short_text():
    assert split_message("Hola mundo") == ["Hola mundo"]


def test_split_message_breaks_at_newlines():
    text = "a" * 30 + "\n" + "b" * 30
    chunks = split_message(text, 40)
    assert chunks == ["a" * 30, "b" * 30]


def test_split_message_breaks_at_spaces():
    text = "a" * 30 + " " + "b" * 30
    chunks = split_message(text, 40)
    assert chunks == ["a" * 30, "b" * 30]


def test_split_message_hard_breaks_long_words():
    text = "a" * 100
    chunks = split_message(text, 40)
    assert chunks == ["a" * 40, "a" * 40, "a" * 20]


def test_split_message_reassembles_original_text():
    text = ("palabra " * 200).strip()
    chunks = split_message(text, 50)
    assert all(len(chunk) <= 50 for chunk in chunks)
    assert " ".join(chunks) == text


def test_split_message_handles_multiple_break_characters():
    text = "a" * 20 + "\n" + "b" * 20 + " " + "c" * 20
    chunks = split_message(text, 50)
    assert chunks == ["a" * 20 + "\n" + "b" * 20, "c" * 20]
    assert all(len(chunk) <= 50 for chunk in chunks)


def test_split_message_with_empty_text():
    assert split_message("") == [""]
