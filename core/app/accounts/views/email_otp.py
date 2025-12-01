from ..forms import ResendActivationEmailForm
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_encode
from ..utils import send_email_otp,send_otp
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib import messages  
from django.views import View
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from ..models import User,OTP
from django.core.mail import send_mail
from django.views.generic import FormView
from django.utils.encoding import force_str
import smtplib
from smtplib import SMTPException



class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save()
            messages.success(request, 'حساب شما با موفقیت فعال شد.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'لینک فعال‌سازی نامعتبر یا منقضی شده است.')
            return redirect('accounts:login')

   
class ResendActivationEmailView(FormView):
    template_name = "accounts/resend_activation.html"
    form_class = ResendActivationEmailForm
    success_url = reverse_lazy("dashboard:home")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
            if not user.is_verified:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                activation_link = self.request.build_absolute_uri(
                    reverse_lazy('accounts:activate_account', kwargs={'uidb64': uid, 'token': token})
                )

                try:
                    send_mail(
                        subject="فعال‌سازی حساب کاربری",
                        message=f"برای فعال‌سازی حساب خود روی لینک زیر کلیک کنید:\n{activation_link}",
                        from_email="info@manmarket.ir",
                        recipient_list=[user.email],
                        fail_silently=False,
                    )
                    messages.success(self.request, "لینک فعال‌سازی به ایمیل شما ارسال شد.")
                except SMTPException as e:
                    # خطای SMTP (مثلاً محدودیت روزانه یا قطعی سرور)
                    messages.error(self.request, "مشکلی در ارسال ایمیل به وجود آمد. لطفاً بعداً دوباره تلاش کنید.")
                    # لاگ گرفتن برای بررسی دقیق‌تر
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"خطا در ارسال ایمیل فعال‌سازی برای {user.email}: {e}")

            else:
                messages.info(self.request, "حساب شما قبلاً فعال شده است.")
        except User.DoesNotExist:
            messages.error(self.request, "کاربری با این ایمیل یافت نشد.")

        return super().form_valid(form)

class OTPOrEmailRequestView(FormView):
    pass





class EmailOTPVerifyView(FormView):
    pass




class ResendEmailOTPView(View):
    def post(self, request, *args, **kwargs):
        email = request.session.get('otp_email')
        if not email:
            return JsonResponse({'status': 'error', 'message': 'ایمیل یافت نشد.'}, status=400)

        try:
            user = User.objects.get(email=email)
            send_email_otp(user)
            return JsonResponse({'status': 'ok', 'message': 'کد جدید ارسال شد.'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'کاربر یافت نشد.'}, status=404)

