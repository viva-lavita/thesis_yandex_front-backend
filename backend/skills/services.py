from django.db import transaction

from skills.models import Skill, SkillImage


def create_skill_with_images(validated_data, image_files):
    with transaction.atomic():
        skill = Skill.objects.create(**validated_data)
        if image_files:
            images = [SkillImage(skill=skill, image=file) for file in image_files]
            SkillImage.objects.bulk_create(images)
        return skill
