from cart.cart import CartSession

def cart_processor(request):
    cart = CartSession(request.session)
    return {"cart": cart}
