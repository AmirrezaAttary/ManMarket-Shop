from django.shortcuts import render
from django.views.generic import ListView, DetailView
from shop.models import (ProductModel, ProductStatusType,
                         ProductColorInventory)
# Create your views here.

class ShopListProductView(ListView):
    template_name = 'shop/product_list.html'
    queryset = ProductModel.objects.filter(
            status=ProductStatusType.publish.value)
    
    
class ShopDetailProductView(DetailView):
    template_name = 'shop/product_detail.html'
    queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value)
    context_object_name = 'product'



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = context['product']  # محصول خاص در context

        # افزودن رنگ‌ها و قیمت‌ها به context
        context['colors'] = ProductColorInventory.objects.filter(product=product)  # دسترسی به رنگ‌ها و قیمت‌های محصول
        return context