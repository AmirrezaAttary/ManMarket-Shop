from django.shortcuts import render
from django.views.generic import ListView, DetailView
from shop.models import (ProductModel, ProductStatusType,
                         ProductColorInventory,ProductCategoryModel,
                         ProductSpecification)
# Create your views here.

class ShopListProductView(ListView):
    template_name = 'shop/product_list.html'
    paginate_by = 9
    

    def get_queryset(self):
        queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value)
        search_q=self.request.GET.get('q')
        if search_q:
            queryset = queryset.filter(title__icontains=search_q)
            
        category_id=self.request.GET.get('category_id')
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        if min_price:= self.request.GET.get('min_price'):
            queryset = queryset.filter(price__gte=min_price)

        if max_price:= self.request.GET.get('max_price'):
            queryset = queryset.filter(price__lte=max_price)

        return queryset
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_items'] = self.get_queryset().count()
        context["categories"] = ProductCategoryModel.objects.all()
        return context
    
    
class ShopDetailProductView(DetailView):
    template_name = 'shop/product_detail.html'
    queryset = ProductModel.objects.filter(status=ProductStatusType.publish.value)
    context_object_name = 'product'



    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = context['product']  # محصول خاص در context

        # افزودن رنگ‌ها و قیمت‌ها به context
        context['colors'] = ProductColorInventory.objects.filter(product=product)  # دسترسی به رنگ‌ها و قیمت‌های محصول
        context['specifications'] = ProductSpecification.objects.filter(product=product)  # دسترسی به مشخصات محصول
        return context