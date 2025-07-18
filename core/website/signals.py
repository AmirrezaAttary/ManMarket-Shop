# signals.py

import os
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Story

@receiver(post_delete, sender=Story)
def delete_story_files(sender, instance, **kwargs):
    # حذف ویدیو
    if instance.video and os.path.isfile(instance.video.path):
        os.remove(instance.video.path)

    # حذف آیکون
    if instance.icon and os.path.isfile(instance.icon.path):
        os.remove(instance.icon.path)
