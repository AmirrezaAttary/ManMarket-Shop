from django.shortcuts import render
from django.views.generic import View, TemplateView
from django.http import JsonResponse
from cart.cart import CartSession
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Create your views here.

class SessionAddProduct(View):

    def post(self,request,*args,**kwargs):
        cart = CartSession(request.session)
        product_id = request.POST.get("product_id")
        color_id = request.POST.get("color_id")
        color_inventory_id = request.POST.get("color_inventory_id")
        if product_id:
            messages.success(request,message='محصول با موفقیت به سبد خرید اضافه شد.')
            cart.add_product(product_id,color_id,color_inventory_id)
        if request.user.is_authenticated:
            cart.merge_session_cart_in_db(request.user)
        return JsonResponse({'cart':cart.get_cart_dict()})
    
@method_decorator(cache_page(60 * 15), name='dispatch') 
class SessionCartSummry(TemplateView):
    template_name = 'cart/cart-summery.html'
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        cart = CartSession(self.request.session)
        cart_items = cart.get_cart_items()
        context["cart_items"] = cart_items
        context["total_quantity"] = cart.get_total_quantity()
        total_payment_price = cart.get_total_payment_amount()
        tot_payment_price = cart.get_tot_payment_amount()
        sod = tot_payment_price - total_payment_price
        context["sod"] = sod
        context["total_payment_price"] = total_payment_price
        context["tot_payment_price"] = tot_payment_price
        return context
    


class SessionRemoveProductView(View):
    
    def post(self,request,*args,**kwargs):
        cart = CartSession(request.session)
        product_id = request.POST.get("product_id")
        color_id = request.POST.get("color_id")
        if product_id:
            cart.remove_product(product_id,color_id)
            
        if request.user.is_authenticated:
            cart.merge_session_cart_in_db(request.user)
        return JsonResponse({"cart":cart.get_cart_dict(),"total_quantity":cart.get_total_quantity()})
    
class SessionUpdateProductQuantityView(View):
    
    def post(self,request,*args,**kwargs):
        cart = CartSession(request.session)
        product_id = request.POST.get("product_id")
        color_id = request.POST.get("color_id")
        quantity = request.POST.get("quantity")
        if product_id and quantity:
            cart.update_product_quantity(product_id,color_id,quantity)
        return JsonResponse({"cart":cart.get_cart_dict(),"total_quantity":cart.get_total_quantity()})
    
@method_decorator(cache_page(60 * 15), name='dispatch')
class SessionCartSummryView(TemplateView):
    template_name = "cart/cart-summary.html"
    
    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        cart = CartSession(self.request.session)
        cart_items = cart.get_cart_items()
        context["cart_items"] = cart_items
        context["total_quantity"] = cart.get_total_quantity()
        context["total_payment_price"] = cart.get_total_payment_amount()
        return context
    
    
    
class SessionCartProductRemoveOneQuantityView(View):

    def post(self,request,*args,**kwargs):
        cart = CartSession(request.session)
        product_id = request.POST.get("product_id")
        color_id = request.POST.get("color_id")
        cart.decrease_product_quantity(product_id,color_id)
        if request.user.is_authenticated:
            cart.merge_session_cart_in_db(request.user)

        return JsonResponse({"cart":cart.get_cart_dict()})


class SessionCartProductAddOneQuantityView(View):

    def post(self,request,*args,**kwargs):
        cart = CartSession(request.session)
        product_id = request.POST.get("product_id")
        color_id = request.POST.get("color_id")
        cart.increase_product_quantity(product_id,color_id)
        if request.user.is_authenticated:
            cart.merge_session_cart_in_db(request.user)

        return JsonResponse({"cart":cart.get_cart_dict()})