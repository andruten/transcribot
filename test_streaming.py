from streaming import next_reveal


def test_reveals_one_word_from_empty_text():
    assert next_reveal('', 'Hola mundo') == 'Hola'


def test_reveals_half_of_pending_words():
    full_text = 'uno dos tres cuatro cinco seis'
    first = next_reveal('', full_text)
    assert first == 'uno dos tres'
    second = next_reveal(first, full_text)
    assert second == 'uno dos tres cuatro'


def test_returns_current_text_when_fully_revealed():
    assert next_reveal('Hola mundo', 'Hola mundo') == 'Hola mundo'


def test_returns_current_text_when_only_whitespace_remains():
    assert next_reveal('Hola mundo', 'Hola mundo ') == 'Hola mundo'


def test_handles_whitespace_between_words():
    full_text = 'Hola\nmundo  que tal'
    assert next_reveal('', full_text) == 'Hola\nmundo'
    assert next_reveal('Hola\nmundo', full_text) == 'Hola\nmundo  que'


def test_returns_full_text_when_current_is_not_a_prefix():
    assert next_reveal('otra cosa', 'Hola mundo') == 'Hola mundo'


def test_returns_empty_text_when_there_is_nothing_to_reveal():
    assert next_reveal('', '') == ''
