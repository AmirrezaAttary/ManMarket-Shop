from django.db import models


class QuestionStatusType(models.IntegerChoices):
    pending = 1, "در انتظار بررسی"
    approved = 2, "تایید شده"
    rejected = 3, "رد شده"


class ProductQuestion(models.Model):
    """پرسش و پاسخ کاربران درباره‌ی هر محصول."""

    product = models.ForeignKey(
        "shop.ProductModel", verbose_name="محصول",
        on_delete=models.CASCADE, related_name="questions",
    )
    user = models.ForeignKey(
        "accounts.User", verbose_name="کاربر", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="product_questions",
    )
    question = models.TextField("پرسش")
    answer = models.TextField("پاسخ فروشگاه", blank=True)
    status = models.IntegerField(
        "وضعیت", choices=QuestionStatusType.choices, default=QuestionStatusType.pending.value
    )
    created_date = models.DateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_date = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        ordering = ["-created_date"]
        verbose_name = "پرسش محصول"
        verbose_name_plural = "پرسش و پاسخ محصولات"

    def __str__(self):
        return f"{self.product_id} - {self.question[:40]}"
