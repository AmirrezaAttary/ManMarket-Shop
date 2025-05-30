from .models import WishlistProductModel

def wishlist_total_items(request):
    if request.user.is_authenticated:
        total_items = WishlistProductModel.objects.filter(user=request.user).count()
    else:
        total_items = 0
    return {
        'wishlist_total_items': total_items
    }