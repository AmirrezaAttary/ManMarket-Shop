# accounts/views.py
from django import forms
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, View
from django.http import JsonResponse

from accounts.models import OTP_LOGIN, User
from accounts.utils import send_email_otp, send_sms_otp  # همان‌هایی که ساختی
from accounts.scripts import send_bulk_sms

class OTPForm(forms.Form):
    code = forms.CharField(label="کد تأیید", max_length=5)


class VerifyOTPView(FormView):
    template_name = 'accounts/verify_otp.html'
    form_class = OTPForm

    def dispatch(self, request, *args, **kwargs):
        # user_id را از GET/POST/session بردار و در session نگه دار
        uid = (request.GET.get('user_id')
               or request.POST.get('user_id')
               or request.session.get('otp_user_id'))
        if not uid:
            messages.error(request, "شناسه کاربر یافت نشد.")
            return redirect('accounts:register')
        request.session['otp_user_id'] = uid
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['user_id'] = self.request.session.get('otp_user_id')
        return ctx

    def form_valid(self, form):
        user_id = self.request.session.get('otp_user_id')
        code = form.cleaned_data['code'].strip()

        # آخرین OTP استفاده‌نشده‌ی کاربر را پیدا کن
        try:
            otp = (OTP_LOGIN.objects
                   .filter(user_id=user_id, is_used=False)
                   .latest('created_at'))
        except OTP_LOGIN.DoesNotExist:
            form.add_error('code', 'کدی برای این کاربر پیدا نشد. لطفاً دوباره کد بگیرید.')
            return self.form_invalid(form)

        # هم کد را چک کن، هم اعتبار زمانی را
        if otp.code != code or not otp.is_valid():
            form.add_error('code', 'کد وارد شده معتبر نیست یا منقضی شده است.')
            return self.form_invalid(form)

        # موفق: مصرف کد + فعال‌سازی کاربر + لاگین
        otp.is_used = True
        otp.save()

        user = otp.user
        if user.phone_number:
            user.is_phone_verified = True
        elif user.email:
            user.is_verified = True
        user.save()
        if user.phone_number:
            # اگر شماره همراه دارد، پیامک خوش‌آمدگویی ارسال کن
            send_bulk_sms("تبریک!\nشما به خانواده من مارکت پیوستید.\nاینجا جاییه که همیشه برات بهترین ها رو داریم ♥️\nمـــن مـــارکـــت  - ارزش شما برای ما بـیـنـهـایـت است .",user.phone_number)


        login(self.request, user, backend='accounts.backends.EmailOrPhoneBackend')
        messages.success(self.request, "حساب شما با موفقیت تأیید شد.")
        return redirect('dashboard:home')


class ResendOTPView(View):
    def post(self, request):
        uid = (request.POST.get('user_id')
               or request.session.get('otp_user_id'))

        if not uid:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "message": "شناسه کاربر نامعتبر است."}, status=400)
            messages.error(request, "شناسه کاربر نامعتبر است.")
            return redirect('accounts:register')

        try:
            user = User.objects.get(pk=uid)
        except User.DoesNotExist:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "message": "کاربر یافت نشد."}, status=404)
            messages.error(request, "کاربر یافت نشد.")
            return redirect('accounts:register')

        OTP_LOGIN.objects.filter(user=user, is_used=False).update(is_used=True)

        if user.email:
            send_email_otp(user)
        elif user.phone_number:
            send_sms_otp(user)
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "message": "اطلاعات تماس کاربر ناقص است."}, status=400)
            messages.error(request, "اطلاعات تماس کاربر ناقص است.")
            return redirect('accounts:register')

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "ok", "message": "کد جدید ارسال شد."})

        messages.info(request, "کد جدید ارسال شد.")
        return redirect(reverse_lazy('accounts:verify_otp'))

