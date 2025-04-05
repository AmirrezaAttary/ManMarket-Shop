from django.shortcuts import render
from django.views.generic import ListView, DetailView
from shop.models import ProductModel, ProductStatusType
# Create your views here.

class ShopListProductView(ListView):
    template_name = 'shop/product_list.html'
    queryset = ProductModel.objects.filter(
            status=ProductStatusType.publish.value)
    
    
class ShopDetailProductView(DetailView):
    template_name = 'shop/product_detail.html'
    queryset = ProductModel.objects.filter(
            status=ProductStatusType.publish.value)