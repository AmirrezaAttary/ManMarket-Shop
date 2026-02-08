from django.views import View
from django.http import HttpResponseRedirect
from django.urls import reverse
from concurrent.futures import ThreadPoolExecutor


# from .tasks import fetch_and_save_specifications, all_specifications_updated
from .models import PriceSpecification
# from celery import chord
from .utils import process_comments

# class GetSpecification(View):

#     def post(self, request, *args, **kwargs):
#         return self.handle_request(request)

#     def get(self, request, *args, **kwargs):
#         return self.handle_request(request)

#     def handle_request(self, request):
#         product_id = self.kwargs.get("pk")

#         # بررسی وجود محصول قبل از اجرای تسک
#         products = PriceSpecification.objects.filter(product__id=product_id)
#         if not products.exists():
#             return HttpResponseRedirect(self.get_success_url(None))

#         # اجرای تسک به صورت async
#         fetch_and_save_specifications.delay(product_id)

#         return HttpResponseRedirect(self.get_success_url(products.first().id))

#     def get_success_url(self, product_spec_id):
#         if product_spec_id:
#             return reverse("dashboard:admin:specification-edit", kwargs={"pk": product_spec_id})
#         return reverse("dashboard:admin:product-list")  # یا هر آدرس دیگری



# class GetAllSpecifications(View):
#     def get(self, request, *args, **kwargs):
#         all_products = PriceSpecification.objects.select_related("product").all()

#         if not all_products.exists():
#             # می‌تونی یک پیغام فیدبک به یوزر بدی مثلاً با messages
#             return HttpResponseRedirect(reverse("dashboard:admin:product-list"))

#         # ساخت header (همه تسک‌ها)
#         header = [
#             fetch_and_save_specifications.s(price.product.id)
#             for price in all_products
#         ]

#         # اجرای همزمان همه تسک‌ها و سپس اجرای callback نهایی
#         chord(header)(all_specifications_updated.s())

#         return HttpResponseRedirect(reverse("dashboard:admin:product-list"))
    


class GetComment(View):

    # تعداد همزمان threadها را محدود می‌کنیم
    executor = ThreadPoolExecutor(max_workers=3)  # حداکثر ۳ پردازش همزمان

    def post(self, request, *args, **kwargs):
        return self.handle_request(request)

    def get(self, request, *args, **kwargs):
        return self.handle_request(request)

    def handle_request(self, request):
        product_id = self.kwargs.get("pk")
        product_comment = PriceSpecification.objects.filter(product_id=product_id).first()

        if product_comment:
            # پردازش در پس‌زمینه بدون مسدود کردن کاربر
            self.executor.submit(
                process_comments,
                product_id,
                product_comment.number_comments,
                product_comment.url
            )

        # پاسخ فوری به کاربر
        return HttpResponseRedirect(reverse("dashboard:admin:review-list"))

    def get_success_url(self, product_spec_id):
        if product_spec_id:
            return reverse("dashboard:admin:specification-edit", kwargs={"pk": product_spec_id})
        return reverse("dashboard:admin:review-list")