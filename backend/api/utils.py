def is_russian(s):
    if not s:
        return False
    russian_alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    allowed_chars = russian_alphabet + "-' "
    return all(c.lower() in allowed_chars or c.isspace() for c in s)
