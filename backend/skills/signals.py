from django.db.models.signals import post_save
from django.dispatch import receiver

from skills.models import SkillExchangeNotification, SkillExchangeRequest


@receiver(post_save, sender=SkillExchangeRequest)
def create_notification_on_request(sender, instance, created, **kwargs):
    """Создаёт уведомление при создании/изменении заявки."""
    if created:
        SkillExchangeNotification.objects.create(
            request=instance, recipient=instance.recipient, event_type="new_request"
        )
    else:
        if instance.status == "accepted":
            SkillExchangeNotification.objects.create(
                request=instance, recipient=instance.requester, event_type="accepted"
            )
        elif instance.status == "rejected":
            SkillExchangeNotification.objects.create(
                request=instance, recipient=instance.requester, event_type="rejected"
            )
        elif instance.status == "cancelled":
            SkillExchangeNotification.objects.create(
                request=instance, recipient=instance.recipient, event_type="cancelled"
            )
