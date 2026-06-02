BASE62_ALPHABET = (
    '0123456789'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    'abcdefghijklmnopqrstuvwxyz'
)


def encode_id(number):
    """Кодирование числа в Base62."""
    if number == 0:
        return BASE62_ALPHABET[0]
    result = []

    while number:
        number, remainder = divmod(number, 62)
        result.append(BASE62_ALPHABET[remainder])
    return ''.join(reversed(result))


def decode_id(short_code):
    """Декодирование Base62 в число."""
    result = 0
    for char in short_code:
        result = result * 62 + BASE62_ALPHABET.index(char)
    return result
