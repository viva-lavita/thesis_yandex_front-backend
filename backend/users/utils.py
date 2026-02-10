import os


def user_avatar_upload_path(instance, filename):
    return os.path.join("avatars", filename)
