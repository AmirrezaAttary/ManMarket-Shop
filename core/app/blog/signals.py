import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Post

@receiver(post_delete, sender=Post)
def delete_post_image(sender, instance, **kwargs):
    if instance.image and instance.image.name != 'blog/images/default.jpg':
        image_path = instance.image.path
        if os.path.isfile(image_path):
            os.remove(image_path)

@receiver(pre_save, sender=Post)
def delete_old_post_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        # پست جدید است، قبلی وجود ندارد
        return

    try:
        old_instance = Post.objects.get(pk=instance.pk)
    except Post.DoesNotExist:
        return

    old_image = old_instance.image
    new_image = instance.image

    if old_image and old_image != new_image and old_image.name != 'blog/images/default.jpg':
        old_image_path = old_image.path
        if os.path.isfile(old_image_path):
            os.remove(old_image_path)
