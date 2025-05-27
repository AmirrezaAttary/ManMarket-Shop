from .models import ProductCategoryModel, Brand, ProductModel

def category_brand_menu(request):
    category_brand_map = {}
    categories = ProductCategoryModel.objects.all()

    for category in categories:
        brands = Brand.objects.filter(
            id__in=ProductModel.objects.filter(category=category)
                                      .values_list('brand', flat=True)
                                      .distinct()
        )
        category_brand_map[category] = brands

    return {'category_brand_map': category_brand_map}
