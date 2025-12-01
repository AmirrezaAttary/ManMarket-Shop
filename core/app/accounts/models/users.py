from django.db import models
# Create your models here.
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from ...wallets.models import Wallet
from ...accounts.validators import validate_iranian_cellphone_number



class UserType(models.IntegerChoices):
    customer = 1, _("customer")
    admin = 2, _("admin")
    superuser = 3, _("superuser")


class UserManager(BaseUserManager):

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("type", UserType.superuser.value)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(_("email address"), unique=False, null=True, blank=True)
    phone_number = models.CharField(
        max_length=12,
        unique=True,
        validators=[validate_iranian_cellphone_number]
    )
    
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    code_melli = models.CharField(max_length=10,unique=True,null=True,blank=True)
    type = models.IntegerField(
        choices=UserType.choices, default=UserType.customer.value)

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        if self.email:
            return str(self.email)
        elif self.phone_number:
            return str(self.phone_number)
        return f"User #{self.pk}"

    class Meta:
        ordering = ['-phone_number']

class Profile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE,related_name="user_profile")
    first_name = models.CharField(max_length=255,null=True,blank=True)
    last_name = models.CharField(max_length=255,null=True,blank=True)

    image = models.ImageField(upload_to='profile/',default='default/default-profile.webp')
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    birth_date = models.CharField(max_length=10, null=True, blank=True, help_text="تاریخ تولد را وارد کنید (مثلاً 1375-05-10)")

    # def age(self):
    #     """محاسبه‌ی سن کاربر بر اساس birth_date"""
    #     if self.birth_date:
    #         today = date.today()
    #         return today.year - self.birth_date.year - (
    #             (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
    #         )
    #     return None

    def get_fullname(self):
        name = " ".join(filter(None, [self.first_name, self.last_name]))
        return name if name else "کاربر جدید"
    
    
    
    
@receiver(post_save,sender=User)
def create_profile(sender,instance,created,**kwargs):
    if created and instance.type == UserType.customer.value:
        Profile.objects.create(user=instance, pk=instance.pk)
        

@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)