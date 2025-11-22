import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import ProductModel, ProductImageModel

# حذف تصویر اصلی محصول هنگام حذف محصول (همان سیگنال قبلی)
@receiver(post_delete, sender=ProductModel)
def delete_product_image(sender, instance, **kwargs):
    if instance.image and instance.image.name != 'default/product-image.png':
        image_path = instance.image.path
        if os.path.isfile(image_path):
            os.remove(image_path)

# حذف فایل عکس اضافه محصول وقتی رکورد حذف شد
@receiver(post_delete, sender=ProductImageModel)
def delete_product_extra_image(sender, instance, **kwargs):
    if instance.file:
        file_path = instance.file.path
        if os.path.isfile(file_path):
            os.remove(file_path)

# حذف عکس قبلی اگر در مدل ProductImageModel فایل تغییر کند
@receiver(pre_save, sender=ProductImageModel)
def delete_old_product_extra_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = ProductImageModel.objects.get(pk=instance.pk)
    except ProductImageModel.DoesNotExist:
        return

    old_file = old_instance.file
    new_file = instance.file

    if old_file and old_file != new_file:
        old_file_path = old_file.path
        if os.path.isfile(old_file_path):
            os.remove(old_file_path)
