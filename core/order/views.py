from django.http import HttpResponse
from django.views.generic import (
    TemplateView,
    FormView,
    View
)

from django.contrib.auth.mixins import LoginRequiredMixin
from order.permissions import HasCustomerAccessPermission
from order.models import UserAddressModel
from order.forms import CheckOutForm
from cart.models import CartModel
from order.models import OrderModel, OrderItemModel
from django.urls import reverse_lazy
from cart.cart import CartSession
from decimal import Decimal
from order.models import CouponModel,OrderStatusType,TrackingType
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import redirect
# Create your views here.
from payment.zarinpal_client import ZarinPalSandbox
from payment.models import PaymentModel,PayemntStatusType,PayemntType
from wallets.models import Wallet,WalletTransaction
from django.contrib import messages
from shop.models import ProductColorInventory
from accounts.models import UserType


class OrderCheckOutView(LoginRequiredMixin, HasCustomerAccessPermission, FormView):
    template_name = "order/checkout.html"
    form_class = CheckOutForm
    success_url = reverse_lazy('order:completed')

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        # بررسی تایید ایمیل و شماره تلفن
        if not user.is_phone_verified:
            messages.error(request, "برای ادامه خرید، ابتدا باید شماره تلفن خود را تأیید کنید.")
            return redirect("dashboard:home")  # آدرس صفحه تایید را اینجا بگذار

        # بررسی پروفایل کامل
        profile = getattr(user, "user_profile", None)
        if not profile or not profile.first_name or not profile.last_name:
            messages.error(request, "لطفاً نام و نام خانوادگی خود را در پروفایل تکمیل کنید.")
            return redirect("dashboard:home")
        
        # بررسی شماره موبایل
        if not user.phone_number:
            messages.error(request, "لطفاً شماره موبایل خود را وارد کنید.")
            return redirect("dashboard:home")
        
        # بررسی آدرس
        if not UserAddressModel.objects.filter(user=user).exists():
            messages.error(request, "لطفاً ابتدا یک آدرس ثبت کنید.")
            return redirect("dashboard:home")

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(OrderCheckOutView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        payment_method = self.request.POST.get("payment_method")
        user = self.request.user
        cleaned_data = form.cleaned_data
        address = cleaned_data['address_id']
        coupon = cleaned_data['coupon']
        tracking_type = cleaned_data['tracking_type']  # 👈 دریافت روش ارسال

        cart = CartModel.objects.get(user=user)
        order = self.create_order(address, tracking_type)  # 👈 ارسال روش ارسال

        self.create_order_items(order, cart)

        total_price = order.calculate_total_price()
        self.apply_coupon(coupon, order, user, total_price)
        order.save()
        return redirect(self.create_payment_url(order, cart))


    def create_payment_url(self, order, cart):
        payment_method = self.request.POST.get("payment_method")

        if payment_method == "wallet":
            wallet = Wallet.objects.get(user=self.request.user)
            total_tax = round((order.total_price))

            # ✅ افزودن هزینه‌ی ثابت
            order.total_price += 50000

            if wallet.balance >= order.total_price:
                # پرداخت موفق   
                wallet.balance -= order.total_price
                wallet.save()

                payment_obj = PaymentModel.objects.create(
                    authority_id="WALLET-" + timezone.now().strftime("%Y%m%d%H%M%S"),
                    amount=order.total_price,
                    status=PayemntStatusType.success,
                    wallet=wallet,
                    order=order,
                    response_json={"data":{"code":100}},
                    response_code = 100,
                    payemnt_type = PayemntType.wallet.value
                )

                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=order.total_price,
                    description=f"پرداخت سفارش #{order.id}",
                    transaction_type='payment'
                )

                # ✅ به‌روزرسانی وضعیت سفارش
                order.payment = payment_obj
                order.status = OrderStatusType.awaiting.value
                order.save()

                # ✅ کاهش موجودی محصولات
                for item in order.order_items.all():
                    try:
                        inventory = ProductColorInventory.objects.get(
                            product=item.product,
                            color=item.color
                        )
                        inventory.stock = max(0, inventory.stock - item.quantity)
                        inventory.save()
                    except ProductColorInventory.DoesNotExist:
                        continue

                self.clear_cart(cart)
                return reverse_lazy("order:completed")

            else:
                zarinpal = ZarinPalSandbox()
                wallet = Wallet.objects.get(user=self.request.user)
                wallet_value = wallet.balance
                total_tax = round((order.total_price)) + 50000

                final_price = int(total_tax - wallet_value)
                
                callback_url = self.request.build_absolute_uri(reverse_lazy("payment:verify"))
                response = zarinpal.payment_request(callback_url,final_price)
                print(response)
                payment_obj = PaymentModel.objects.create(
                    authority_id = response['data']['authority'],
                    amount = final_price,
                    order=order,
                    wallet=wallet,
                    payemnt_type = PayemntType.wallet_cart.value
                )
                order.payment = payment_obj
                order.save()
                return zarinpal.generate_payment_url(response['data']['authority'])
                
                # messages.error(self.request, "موجودی کیف پول شما کافی نیست.")
                # return reverse_lazy("order:checkout")



        if payment_method == "zarinpal":
            zarinpal = ZarinPalSandbox()
            total_tax = round((order.total_price)) + 50000
            order.total_price = total_tax 
            

            callback_url = self.request.build_absolute_uri(reverse_lazy("payment:verify"))
            response = zarinpal.payment_request(callback_url,order.total_price)
            payment_obj = PaymentModel.objects.create(
                authority_id = response['data']['authority'],
                amount = order.total_price,
                order=order,
                payemnt_type = PayemntType.cart.value
            )
            order.payment = payment_obj
            order.save()
            return zarinpal.generate_payment_url(response['data']['authority'])
        
        if payment_method == "card_mahax":
            zarinpal = ZarinPalSandbox()
            total_price = round((order.total_price)) + 50000
            total_tax = round((order.total_price) /10) + 50000  
            remainder = total_price - total_tax
            order.total_price = total_tax 
            
            callback_url = self.request.build_absolute_uri(reverse_lazy("payment:verify"))
            response = zarinpal.payment_request(callback_url,order.total_price)
            payment_obj = PaymentModel.objects.create(
                authority_id = response['data']['authority'],
                amount = order.total_price,
                order=order,
                payemnt_type = PayemntType.cart_home.value,
                remainder = remainder,
            )
            order.payment = payment_obj
            order.save()
            return zarinpal.generate_payment_url(response['data']['authority'])
            
            
        if payment_method == "person":
            user = self.request.user
            if user.type not in [UserType.admin, UserType.superuser]:
                messages.error(self.request, "شما اجازه ثبت سفارش حضوری را ندارید.")
                return reverse_lazy("order:checkout")

            order.total_price += 50000  # ✅ افزودن هزینه ثابت برای حضوری

            # 🟩 مقداردهی آدرس به صورت حضوری
            order.address = "تحویل حضوری در فروشگاه"
            order.state = "خراسان رضوی"
            order.city = "سبزوار"
            order.zip_code = "0000000000"
            order.tracking_type = TrackingType.person.value

            # ایجاد شی پرداخت حضوری
            payment_obj = PaymentModel.objects.create(
                authority_id="PERSON-" + timezone.now().strftime("%Y%m%d%H%M%S"),
                amount=order.total_price,
                status=PayemntStatusType.success,
                order=order,
                payemnt_type=PayemntType.person.value,
                response_json={"data": {"code": 100}},
                response_code=100,
                remainder=order.total_price
            )

            order.payment = payment_obj
            order.status = OrderStatusType.awaiting.value
            order.save()

            # کاهش موجودی محصولات
            for item in order.order_items.all():
                try:
                    inventory = ProductColorInventory.objects.get(
                        product=item.product,
                        color=item.color
                    )
                    inventory.stock = max(0, inventory.stock - item.quantity)
                    inventory.save()
                except ProductColorInventory.DoesNotExist:
                    continue

            self.clear_cart(cart)
            return reverse_lazy("order:completed")


        
        
        # برای روش‌های دیگر پرداخت (مثلاً زرین‌پال) باید else اضافه کنی
        messages.error(self.request, "روش پرداخت نامعتبر است.")
        return reverse_lazy("order:checkout")

    def create_order(self, address, tracking_type):
        return OrderModel.objects.create(
            user=self.request.user,
            address=address.address,
            state=address.state,
            city=address.city,
            zip_code=address.zip_code,
            tracking_type=tracking_type,  # 👈 ذخیره نوع ارسال
        )


    def create_order_items(self, order, cart):
        for item in cart.cart_items.all():
            print(item.color)
            OrderItemModel.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.color_inventory.get_price(),
                color = item.color,
            )

    def clear_cart(self, cart):
        cart.cart_items.all().delete()
        CartSession(self.request.session).clear()

    def apply_coupon(self, coupon, order, user, total_price):
        if coupon:
            discount_amount = round(
                (total_price * Decimal(coupon.discount_percent / 100)))
            total_price -= discount_amount

            order.coupon = coupon
            coupon.used_by.add(user)
            coupon.save()

        order.total_price = total_price

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartModel.objects.get(user=self.request.user)
        context["addresses"] = UserAddressModel.objects.filter(
            user=self.request.user)
        total_price = cart.calculate_total_price()
        
        wallet = Wallet.objects.get(user=self.request.user)
        context['wallet'] = wallet
        context["total_price"] = total_price

        context['total_price_with_tax'] = total_price  + 50000
        cart = CartSession(self.request.session)
        total_payment_price = cart.get_total_payment_amount()
        tot_payment_price = cart.get_tot_payment_amount()
        sod = tot_payment_price - total_payment_price
        context["sod"] = sod
        cart_items = cart.get_cart_items()
        context["cart_items"] = cart_items
        return context



class OrderCompletedView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = "order/completed.html"
    


class OrderFailedView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = "order/failed.html"


class ValidateCouponView(LoginRequiredMixin, HasCustomerAccessPermission, View):

    def post(self, request, *args, **kwargs):
        code = request.POST.get("code")
        user = self.request.user

        status_code = 200
        message = "کد تخفیف با موفقیت ثبت شد"
        total_price = 0
        total_tax = 0

        try:
            coupon = CouponModel.objects.get(code=code)
        except CouponModel.DoesNotExist:
            return JsonResponse({"message": "کد تخفیف یافت نشد"}, status=404)
        else:
            if coupon.used_by.count() >= coupon.max_limit_usage:
                status_code, message = 403, "محدودیت در تعداد استفاده"

            elif coupon.expiration_date and coupon.expiration_date < timezone.now():
                status_code, message = 403, "کد تخفیف منقضی شده است"

            elif user in coupon.used_by.all():
                status_code, message = 403, "این کد تخفیف قبلا توسط شما استفاده شده است"

            else:
                cart = CartModel.objects.get(user=self.request.user)

                total_price = cart.calculate_total_price()
                total_price = round(
                    total_price - (total_price * (coupon.discount_percent/100)))
                total_tax = round((total_price * 10)/100)
        return JsonResponse({"message": message, "total_tax": total_tax, "total_price": total_price}, status=status_code)