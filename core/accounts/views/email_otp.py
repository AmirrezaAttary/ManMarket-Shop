from accounts.forms import ResendActivationEmailForm,OTPOrEmailRequestForm, EmailOTPVerifyForm
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_encode
from accounts.utils import send_email_otp,send_otp
from django.contrib.auth import login
from django.shortcuts import redirect
from django.contrib import messages  
from django.views import View
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from accounts.models import User, EmailOTP,OTP
from django.core.mail import send_mail
from django.views.generic import FormView
from django.utils.encoding import force_str
import smtplib


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

                # ارسال ایمیل
                send_mail(
                    subject="فعال‌سازی حساب کاربری",
                    message=f"برای فعال‌سازی حساب خود روی لینک زیر کلیک کنید:\n{activation_link}",
                    from_email="info@manmarket.ir",
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                messages.success(self.request, "لینک فعال‌سازی به ایمیل شما ارسال شد.")
            else:
                messages.info(self.request, "حساب شما قبلاً فعال شده است.")
        except User.DoesNotExist:
            messages.error(self.request, "کاربری با این ایمیل یافت نشد.")

        return super().form_valid(form)
    


class OTPOrEmailRequestView(FormView):
    template_name = 'accounts/otp_or_email_request.html'
    form_class = OTPOrEmailRequestForm

    def form_valid(self, form):
        identifier = form.cleaned_data['identifier']
        method_type = form.cleaned_data['type']

        try:
            if method_type == 'email':
                user = User.objects.get(email=identifier)
                send_email_otp(user)
                self.request.session['otp_email'] = identifier
                return redirect('accounts:email_otp_verify')

            elif method_type == 'phone':
                user = User.objects.get(phone_number=identifier)
                send_otp(user)
                self.request.session['otp_phone'] = identifier
                return redirect('accounts:otp_verify')

        except smtplib.SMTPDataError as e:
            if b"You have reached the daily limit" in e.smtp_error:
                messages.error(self.request, "فعلاً امکان ارسال ایمیل وجود ندارد. لطفاً بعداً تلاش کنید.")
            else:
                messages.error(self.request, "خطایی در ارسال ایمیل رخ داد. لطفاً دوباره تلاش کنید.")
            return redirect('accounts:otp_or_email_request')

        except Exception as e:
            messages.error(self.request, "خطایی در ارسال کد رخ داد. لطفاً دوباره تلاش کنید.")
            return redirect('accounts:otp_or_email_request')

        messages.error(self.request, "ورودی نامعتبر است.")
        return redirect('accounts:otp_or_email_request')





class EmailOTPVerifyView(FormView):
    template_name = 'accounts/email_otp_verify.html'
    form_class = EmailOTPVerifyForm

    def get_initial(self):
        email = self.request.session.get('otp_email')
        if not email:
            return {}
        return {'email': email}

    def form_valid(self, form):
        # ایمیل رو از سشن بگیریم نه از POST
        email = self.request.session.get('otp_email')
        if not email:
            messages.error(self.request, "اطلاعات شما منقضی شده است. دوباره تلاش کنید.")
            return redirect('accounts:otp_or_email_request')

        user = form.cleaned_data['user']
        user.backend = 'accounts.backends.EmailOrPhoneBackend'
        login(self.request, user)
        EmailOTP.objects.filter(user=user, code=form.cleaned_data['code']).update(is_used=True)

        # پاک کردن از سشن
        del self.request.session['otp_email']

        messages.success(self.request, "ورود شما با موفقیت انجام شد.")
        return redirect('dashboard:home')




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

