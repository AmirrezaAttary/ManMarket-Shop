import threading
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse

def send_email_async(subject, message, recipient_list):
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

def send_password_reset_email(request, email, reset_link):
    subject = "درخواست بازیابی رمز عبور"
    message = render_to_string('email/password_reset_email.tpl', {'reset_link': reset_link})

    # ارسال ایمیل به صورت غیر همزمان
    threading.Thread(target=send_email_async, args=(subject, message, [email])).start()




def send_activation_link(request, user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_link = request.build_absolute_uri(
        reverse('accounts:activate_account', kwargs={'uidb64': uidb64, 'token': token})
    )

    # حالا این لینک رو می‌تونی توی ایمیل ارسال کنی یا به کاربر نشون بدی
    print("Activation link:", activation_link)
