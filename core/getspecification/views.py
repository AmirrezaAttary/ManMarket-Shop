from django.views import View
from django.http import HttpResponseRedirect
from shop.models import ProductSpecification
from .scripts import getspecificationDigikala
from .models import PriceSpecification
from django.urls import reverse

class GetSpecification(View):

    def post(self, request, *args, **kwargs):
        return self.handle_request(request)

    def get(self, request, *args, **kwargs):
        return self.handle_request(request)

    def handle_request(self, request):
        product_id = self.kwargs.get("pk")
        products = PriceSpecification.objects.filter(product__id=product_id)

        if not products.exists():
            return HttpResponseRedirect(self.get_success_url())

        product = products.first().product
        extra = getspecificationDigikala(products.first().url)

        if extra:
            for key, value in extra.items():
                ProductSpecification.objects.update_or_create(
                    product=product,
                    name=str(key),
                    defaults={"value": str(value)}
                )

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("dashboard:admin:product-edit", kwargs={"pk": self.kwargs.get("pk")})