from django.http import HttpResponse
from django.views.generic import (
    TemplateView,
    FormView,
    View
)

from django.contrib.auth.mixins import LoginRequiredMixin
from .permissions import HasCustomerAccessPermission
from .models import UserAddressModel
from .forms import CheckOutForm
from ..cart.models import CartModel
from .models import OrderModel, OrderItemModel
from django.urls import reverse_lazy
from ..cart.cart import CartSession
from decimal import Decimal
from .models import CouponModel,OrderStatusType,TrackingType
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
# Create your views here.
from ..payment.zarinpal_client import ZarinPalSandbox
from ..payment.gsmpay_client import GSMPay
from ..payment.refah_client import RefahClient
from ..payment.models import PaymentModel,PayemntStatusType,PayemntType
from ..wallets.models import Wallet,WalletTransaction
from django.contrib import messages
from ..shop.models import ProductColorInventory
from ..accounts.models import UserType
from ..accounts.scripts import send_bulk_sms
from django.db import transaction
from .tasks import check_order_pending_status


class CheckoutAddressView(LoginRequiredMixin, TemplateView):
    template_name = "order/checkout_address.html"

    def post(self, request, *args, **kwargs):
        address_id = request.POST.get("address_id")

        if not UserAddressModel.objects.filter(id=address_id, user=request.user).exists():
            messages.error(request, "آدرس نامعتبر است")
            return redirect("order:checkout-address")

        request.session['checkout'] = {
            'address_id': address_id
        }
        print(request.session['checkout']['address_id'])
        return redirect("order:checkout-shipping")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["addresses"] = UserAddressModel.objects.filter(user=self.request.user)
        cart_session = CartSession(self.request.session)
        context["cart_items"] = cart_session.get_cart_items()
        cart = CartModel.objects.get(user=self.request.user)
        context["total_price"] = cart.calculate_total_price()
        context['total_price_with_tax'] = cart.calculate_total_price() + 50000
        context["sod"] = cart_session.get_tot_payment_amount() - cart_session.get_total_payment_amount()

        return context

class CheckoutShippingView(LoginRequiredMixin, TemplateView):
    template_name = "order/checkout_shipping.html"

    def post(self, request, *args, **kwargs):
        tracking_type = request.POST.get("tracking_type")
        
        checkout = request.session.get("checkout", {})
        
        checkout["tracking_type"] = tracking_type
        request.session["checkout"] = checkout

        return redirect("order:checkout-payment")

    def get_context_data(self, **kwargs):
        address_id = self.request.session.get("checkout").get('address_id')
        context = super().get_context_data(**kwargs)
        cart_session = CartSession(self.request.session)
        context["cart_items"] = cart_session.get_cart_items()
        cart = CartModel.objects.get(user=self.request.user)
        context["total_price"] = cart.calculate_total_price()
        context['total_price_with_tax'] = cart.calculate_total_price() + 50000
        context["sod"] = cart_session.get_tot_payment_amount() - cart_session.get_total_payment_amount()
        wallet = Wallet.objects.get(user=self.request.user)
        context["addresses"] = UserAddressModel.objects.filter(id=address_id)
        context["wallet"] = wallet
        return context
    

class CheckoutPaymentView(LoginRequiredMixin, View): 
    def post(self, request, *args, **kwargs):
        payment_method = request.POST.get("payment_method")
        tracking_type = request.POST.get("tracking_type")
        checkout = request.session.get("checkout")
        if not checkout: 
            messages.error(request, "فرآیند خرید نامعتبر است") 
            return redirect("order:checkout-address") 

        address = get_object_or_404(UserAddressModel, id=checkout["address_id"], user=request.user) 
        cart = CartModel.objects.get(user=request.user) 

        with transaction.atomic(): 
            # ایجاد سفارش
            order = OrderModel.objects.create(
                user=request.user,
                address=address.address,
                name=address.name, 
                phone_number=address.phone_number, 
                state=address.state, 
                city=address.city, 
                zip_code=address.zip_code, 
                tracking_type=tracking_type,
            ) 

            # ایجاد آیتم‌های سفارش
            for item in cart.cart_items.all(): 
                OrderItemModel.objects.create(
                    order=order, 
                    product=item.product, 
                    quantity=item.quantity, 
                    price=item.color_inventory.get_price(), 
                    color=item.color,
                )

            # محاسبه کل مبلغ بعد از ایجاد همه آیتم‌ها
            order.total_price = order.calculate_total_price() 
            order.save()

        # فراخوانی متد پرداخت
        return OrderCheckOutView().create_payment_url(request=request, order=order, cart=cart)





class OrderCheckOutView(LoginRequiredMixin, FormView):
    template_name = "order/checkout.html"
    form_class = CheckOutForm
    success_url = reverse_lazy('order:completed')

    def dispatch(self, request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            messages.error(request, "برای ادامه خرید باید وارد شوید.")
            return self.handle_no_permission()

        # بررسی سبد خرید
        cart = CartModel.objects.filter(user=user).first()
        if not cart or cart.cart_items.count() == 0:
            messages.error(request, "سبد خرید شما خالی است.")
            return redirect("shop:product-list")

        # بررسی احراز هویت شماره موبایل
        if not getattr(user, "is_verified", False):
            messages.error(request, "برای ادامه خرید، ابتدا باید شماره همراه خود را تأیید کنید.")
            return redirect("dashboard:home")

        # بررسی اطلاعات پروفایل
        profile = getattr(user, "user_profile", None)
        if not profile or not profile.first_name or not profile.last_name:
            messages.error(request, "لطفاً نام و نام خانوادگی خود را در پروفایل تکمیل کنید.")
            return redirect("dashboard:home")

        if not getattr(user, "phone_number", None):
            messages.error(request, "لطفاً شماره موبایل خود را وارد کنید.")
            return redirect("dashboard:home")

        if not getattr(user, "code_melli", None):
            messages.error(request, "لطفاً شماره کد ملی خود را وارد کنید.")
            return redirect("dashboard:home")

        if not UserAddressModel.objects.filter(user=user).exists():
            messages.error(request, "لطفاً ابتدا یک آدرس ثبت کنید.")
            return redirect("dashboard:customer:address-create")

        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        cleaned_data = form.cleaned_data
        address = cleaned_data['address_id']
        coupon = cleaned_data['coupon']
        tracking_type = cleaned_data['tracking_type']

        cart = CartModel.objects.get(user=user)
        order = self.create_order(address, tracking_type)
        self.create_order_items(order, cart)

        total_price = order.calculate_total_price()
        self.apply_coupon(coupon, order, user, total_price)
        order.save()

        check_order_pending_status.apply_async(args=[order.id], countdown=180)
        self.clear_cart(cart)

        payment_result = self.create_payment_url(order, cart)

        from django.http import HttpResponseRedirect
        if isinstance(payment_result, HttpResponseRedirect):
            return payment_result  

        return redirect(payment_result)

    def create_payment_url(self, request, order, cart):
        user = request.user
        payment_method = request.POST.get("payment_method")

        # ================= کیف پول =================
        if payment_method == "wallet":
            wallet = Wallet.objects.get(user=user)
            order.total_price += 50000  # هزینه ثابت

            if wallet.balance >= order.total_price:
                wallet.balance -= order.total_price
                wallet.save()

                payment_obj = PaymentModel.objects.create(
                    authority_id=f"WALLET-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                    amount=order.total_price,
                    status=PayemntStatusType.success,
                    wallet=wallet,
                    order=order,
                    payemnt_type=PayemntType.wallet.value,
                    response_json={"data": {"code": 100}},
                    response_code=100
                )

                WalletTransaction.objects.create(
                    wallet=wallet,
                    amount=order.total_price,
                    description=f"پرداخت سفارش #{order.id}",
                    transaction_type='payment'
                )

                order.payment = payment_obj
                order.status = OrderStatusType.awaiting.value
                order.save()
                self.update_inventory(order)
                self.send_notifications(order)
                return redirect("order:completed")

            else:
                # ترکیبی کیف پول + درگاه
                zarinpal = ZarinPalSandbox()
                wallet_value = wallet.balance
                total_price = order.total_price
                final_price = int(total_price - wallet_value)
                if final_price <= 0:
                    messages.error(request, "خطا در محاسبه مبلغ قابل پرداخت.")
                    return redirect("order:checkout-shipping")

                callback_url = request.build_absolute_uri(reverse_lazy("payment:verify"))
                response = zarinpal.payment_request(callback_url, final_price)
                authority = response.get('data', {}).get('authority')
                if not authority:
                    print("Zarinpal wallet+cart error:", response)
                    messages.error(request, "خطا در ایجاد پرداخت. لطفاً دوباره تلاش کنید.")
                    return redirect("order:checkout-shipping")

                payment_obj = PaymentModel.objects.create(
                    authority_id=authority,
                    amount=final_price,
                    order=order,
                    wallet=wallet,
                    payemnt_type=PayemntType.wallet_cart.value
                )
                order.payment = payment_obj
                order.save()
                return redirect(zarinpal.generate_payment_url(authority))

        # ================= زرین پال =================
        if payment_method == "zarinpal":
            zarinpal = ZarinPalSandbox()
            order.total_price += 50000
            callback_url = request.build_absolute_uri(reverse_lazy("payment:verify"))
            response = zarinpal.payment_request(callback_url, order.total_price)
            authority = response.get('data', {}).get('authority')
            if not authority:
                print("Zarinpal error:", response)
                messages.error(request, "خطا در ایجاد پرداخت. لطفاً دوباره تلاش کنید.")
                return redirect("order:checkout-shipping")

            payment_obj = PaymentModel.objects.create(
                authority_id=authority,
                amount=order.total_price,
                order=order,
                payemnt_type=PayemntType.cart.value
            )
            order.payment = payment_obj
            order.save()
            return redirect(zarinpal.generate_payment_url(authority))

        # ================= حضوری =================
        if payment_method == "person":
            if user.type not in [UserType.admin, UserType.superuser]:
                messages.error(request, "شما اجازه ثبت سفارش حضوری را ندارید.")
                return reverse_lazy("order:checkout-shipping")

            order.total_price += 50000
            order.address = "تحویل حضوری در فروشگاه"
            order.state = "خراسان رضوی"
            order.city = "سبزوار"
            order.zip_code = "0000000000"
            order.tracking_type = TrackingType.person.value

            payment_obj = PaymentModel.objects.create(
                authority_id=f"PERSON-{timezone.now().strftime('%Y%m%d%H%M%S')}",
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
            self.update_inventory(order)
            self.send_notifications(order)
            return redirect("order:completed")

        # ================= کارت به کارت مهاب =================
        if payment_method == "card_mahax":
            zarinpal = ZarinPalSandbox()
            total_price = round(order.total_price) + 50000
            total_tax = round(order.total_price / 10) + 50000
            remainder = total_price - total_tax
            order.total_price = total_tax

            callback_url = request.build_absolute_uri(reverse_lazy("payment:verify"))
            response = zarinpal.payment_request(callback_url, order.total_price)
            authority = response.get('data', {}).get('authority')
            if not authority:
                print("Card Mahax error:", response)
                messages.error(request, "خطا در ایجاد پرداخت کارت به کارت. لطفاً دوباره تلاش کنید.")
                return redirect("order:checkout-shipping")

            payment_obj = PaymentModel.objects.create(
                authority_id=authority,
                amount=order.total_price,
                order=order,
                payemnt_type=PayemntType.cart_home.value,
                remainder=remainder,
            )
            order.payment = payment_obj
            order.save()
            return redirect(zarinpal.generate_payment_url(authority))

        # ================= GSMPay =================
        if payment_method == "gsmpay":
            gsmpay = GSMPay()
            order.total_price += 50000
            callback_url = request.build_absolute_uri(reverse_lazy("payment:verify"))
            invoice_reference = f"ORDER-{order.id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
            response, status_code = gsmpay.create_payment(
                callback_url=callback_url,
                invoice_reference=invoice_reference,
                invoice_amount=int(order.total_price),
                invoice_date=timezone.now().isoformat(),
                payer_mobile=user.phone_number,
                payer_first_name=user.user_profile.first_name,
                payer_last_name=user.user_profile.last_name,
                payer_national_code=user.code_melli,
                description=f"پرداخت سفارش #{order.id}",
                items=[{
                    "reference": str(item.id),
                    "name": item.product.title,
                    "is_product": True,
                    "quantity": item.quantity,
                    "unit_price": str(item.price),
                    "unit_discount": "0",
                    "unit_tax_amount": "0"
                } for item in order.order_items.all()]
            )

            if status_code == 201:
                token = response.get('data', {}).get('token')
                redirect_url = response.get('data', {}).get('redirect_url')
                if not token or not redirect_url:
                    messages.error(request, "خطا در ایجاد پرداخت GSMPay.")
                    return redirect("order:checkout")

                payment_obj = PaymentModel.objects.create(
                    authority_id=token,
                    amount=order.total_price,
                    order=order,
                    payemnt_type=PayemntType.gsm_cart.value,
                    response_json=response,
                )
                order.payment = payment_obj
                order.save()
                return redirect(redirect_url)
            else:
                messages.error(request, f"خطا در ایجاد پرداخت: {response}")
                return redirect("order:checkout-shipping")

        # ================= Refah =================
        if payment_method == "refah":
            refah = RefahClient()
            callback_url = request.build_absolute_uri(reverse_lazy('payment:refah_callback'))
            response = refah.purchase_request(
                amount=order.total_price,
                callback_url=callback_url,
                order_id=order.id
            )

            refahToken = response.get('data', {}).get('token')
            print(refahToken)
            if not refahToken:
                print("Refah payment error:", response)
                messages.error(request, "خطا در ارتباط با درگاه رفاه. لطفاً دوباره تلاش کنید.")
                return redirect("order:checkout-shipping")

            payment_obj = PaymentModel.objects.create(
                authority_id=refahToken,
                amount=order.total_price,
                order=order,
                payemnt_type=PayemntType.refah.value
            )
            order.payment = payment_obj
            order.save()
            return refah.generate_payment_url(refahToken)

    # ================= متدهای کمکی =================
    def create_order(self, address, tracking_type):
        return OrderModel.objects.create(
            user=self.request.user,
            address=address.address,
            name=address.name,
            phone_number=address.phone_number,
            state=address.state,
            city=address.city,
            zip_code=address.zip_code,
            tracking_type=tracking_type,
        )

    def create_order_items(self, order, cart):
        for item in cart.cart_items.all():
            OrderItemModel.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.color_inventory.get_price(),
                color=item.color,
            )

    def clear_cart(self, cart):
        cart.cart_items.all().delete()
        CartSession(self.request.session).clear()

    def apply_coupon(self, coupon, order, user, total_price):
        if coupon:
            discount_amount = round(total_price * Decimal(coupon.discount_percent / 100))
            total_price -= discount_amount
            order.coupon = coupon
            coupon.used_by.add(user)
            coupon.save()
        order.total_price = total_price

    def update_inventory(self, order):
        for item in order.order_items.all():
            try:
                inventory = ProductColorInventory.objects.get(product=item.product, color=item.color)
                inventory.stock = max(0, inventory.stock - item.quantity)
                inventory.save()
            except ProductColorInventory.DoesNotExist:
                continue

    def send_notifications(self, order):
        send_bulk_sms(
            message_text=f"مشتری گرامی،\nسفارش شما {order.order_number} تأیید شد\nدر حال آماده‌سازی است.\nمـــن مـــارکـــت",
            mobiles=[order.user.phone_number]
        )
        send_bulk_sms(
            message_text="یک سفارش جدید در من مارکت ثبت شد !",
            mobiles=["09120983411"]
        )

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = CartModel.objects.get(user=self.request.user)
        wallet = Wallet.objects.get(user=self.request.user)

        context["addresses"] = UserAddressModel.objects.filter(user=self.request.user)
        context["total_price"] = cart.calculate_total_price()
        context["wallet"] = wallet
        context['total_price_with_tax'] = cart.calculate_total_price() + 50000

        cart_session = CartSession(self.request.session)
        context["cart_items"] = cart_session.get_cart_items()
        context["sod"] = cart_session.get_tot_payment_amount() - cart_session.get_total_payment_amount()

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
    
    
    
class OrderRetryPaymentView(LoginRequiredMixin, View):
    def get(self, request, order_id, *args, **kwargs):
        # فقط سفارش‌هایی که پرداخت نشده‌اند
        order = get_object_or_404(
            OrderModel,
            id=order_id,
            user=request.user,
            status=OrderStatusType.pending.value
        )

        try:
            with transaction.atomic():
                for item in order.order_items.all():
                    try:
                        color_inventory = ProductColorInventory.objects.select_for_update().get(
                            product=item.product,
                            color=item.color
                        )
                    except ProductColorInventory.DoesNotExist:
                        messages.error(
                            request,
                            f"محصول '{item.product.title}' با رنگ {item.color.title} در انبار یافت نشد."
                        )
                        return redirect("dashboard:customer:order-list")

                    if color_inventory.stock < item.quantity:
                        messages.error(
                            request,
                            f"موجودی محصول '{item.product.title}' با رنگ {item.color.title} کافی نیست."
                        )
                        return redirect("dashboard:customer:order-list")

                # اگر موجودی کافی بود برو سراغ درگاه
                zarinpal = ZarinPalSandbox()
                callback_url = request.build_absolute_uri(reverse_lazy("payment:verify"))
                response = zarinpal.payment_request(callback_url, int(order.total_price))

                if response.get("data"):
                    payment_obj = PaymentModel.objects.create(
                        authority_id=response["data"]["authority"],
                        amount=order.total_price,
                        order=order,
                        payemnt_type=PayemntType.cart.value
                    )
                    order.payment = payment_obj
                    order.save()
                    return redirect(zarinpal.generate_payment_url(response["data"]["authority"]))

        except Exception as e:
            messages.error(request, f"خطایی رخ داد: {str(e)}")
            return redirect("dashboard:customer:order-list")

        messages.error(request, "خطا در اتصال به درگاه پرداخت.")
        return redirect("dashboard:customer:order-list")

