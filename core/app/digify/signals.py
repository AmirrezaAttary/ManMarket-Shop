"""Keep `updated_at` of the feed honest.

The feed's updated_at = newest of the product row and its inventory rows. Things that change what the
feed shows but would NOT touch those rows are handled here.
"""
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from app.shop.models import Brand, Color, ProductCategoryModel, ProductColorInventory, ProductImageModel, ProductModel


def _touch_product(product_id):
    if product_id:
        # queryset.update() on purpose: no save() side effects / signals on the product
        ProductModel.objects.filter(pk=product_id).update(updated_date=timezone.now())


@receiver(post_delete, sender=ProductColorInventory)
def inventory_deleted(sender, instance, **kwargs):
    _touch_product(instance.product_id)


@receiver([post_save, post_delete], sender=ProductImageModel)
def image_changed(sender, instance, **kwargs):
    _touch_product(instance.product_id)


@receiver(post_save, sender=Brand)
def brand_changed(sender, instance, created, **kwargs):
    if not created:
        ProductModel.objects.filter(brand_id=instance.pk).update(updated_date=timezone.now())


@receiver(post_save, sender=ProductCategoryModel)
def category_changed(sender, instance, created, **kwargs):
    if not created:
        ProductModel.objects.filter(category_id=instance.pk).update(updated_date=timezone.now())


@receiver(post_save, sender=Color)
def color_changed(sender, instance, created, **kwargs):
    if not created:
        ProductColorInventory.objects.filter(color_id=instance.pk).update(updated_date=timezone.now())
