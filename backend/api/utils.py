import os
from logging import getLogger

from django.utils.deconstruct import deconstructible

logger = getLogger(__name__)


def is_russian(s):
    if not s:
        return False
    russian_alphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"
    allowed_chars = russian_alphabet + "-' "
    return all(c.lower() in allowed_chars or c.isspace() for c in s)


@deconstructible
class UserContentUploadPath:
    """По дефолту путь content/, но можно создать экземпляр с другим путем."""

    def __init__(self, sub_path="content"):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        user_id = instance.user.id
        # путь: content/<user_id>/<filename>
        return os.path.join(self.sub_path, str(user_id), filename)
