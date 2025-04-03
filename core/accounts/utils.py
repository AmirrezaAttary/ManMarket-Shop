import threading
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_email_async(subject, message, recipient_list):
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

def send_password_reset_email(request, email, reset_link):
    subject = "درخواست بازیابی رمز عبور"
    message = render_to_string('email/password_reset_email.tpl', {'reset_link': reset_link})

    # ارسال ایمیل به صورت غیر همزمان
    threading.Thread(target=send_email_async, args=(subject, message, [email])).start()
