import os


def skill_image_upload_path(instance, filename):
    return os.path.join("skills", str(instance.skill.user.id), str(instance.skill.id), filename)
