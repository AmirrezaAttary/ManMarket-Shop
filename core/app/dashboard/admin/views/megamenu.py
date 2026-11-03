from django import forms
from django.contrib import messages
from django.http import HttpResponseRedirect

from ....shop.models import Brand, MegaMenu, ProductCategoryModel
from ....website.models import SiteSetting
from ..crud import MEGAMENU, Column, CrudConfig
from .crud import (
    CrudCreateView,
    CrudDeleteView,
    CrudListView,
    CrudUpdateView,
    DashboardModelForm,
    SingletonUpdateView,
)

DUPLICATE_MSG = "این برند قبلاً برای این دسته‌بندی در مگا منو ثبت شده است."


class MegaMenuEditForm(DashboardModelForm):
    """ویرایش یک ردیف مگا منو (یک دسته‌بندی + یک برند)."""

    class Meta:
        model = MegaMenu
        fields = ("category", "brand")

    def clean(self):
        cleaned = super().clean()
        category, brand = cleaned.get("category"), cleaned.get("brand")
        if category and brand:
            dup = MegaMenu.objects.filter(category=category, brand=brand).exclude(pk=self.instance.pk)
            if dup.exists():
                raise forms.ValidationError(DUPLICATE_MSG)
        return cleaned


class MegaMenuBulkForm(forms.Form):
    """افزودن چند برند به یک دسته‌بندی با یک بار ثبت."""

    category = forms.ModelChoiceField(queryset=ProductCategoryModel.objects.all(), label="دسته‌بندی")
    brands = forms.ModelMultipleChoiceField(
        queryset=Brand.objects.order_by("title"),
        widget=forms.CheckboxSelectMultiple,
        label="برندها (می‌توانید چند برند انتخاب کنید)",
    )


class AdminMegaMenuListView(CrudListView):
    config = MEGAMENU


class AdminMegaMenuCreateView(CrudCreateView):
    config = MEGAMENU

    def get_form_class(self):
        return MegaMenuBulkForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop("instance", None)  # فرم ساده است، نه ModelForm
        return kwargs

    def form_valid(self, form):
        category = form.cleaned_data["category"]
        created = 0
        for brand in form.cleaned_data["brands"]:
            _, was_created = MegaMenu.objects.get_or_create(category=category, brand=brand)
            created += int(was_created)
        skipped = len(form.cleaned_data["brands"]) - created
        if created:
            messages.success(self.request, f"{created} برند به مگا منوی «{category.title}» اضافه شد.")
        if skipped:
            messages.warning(self.request, f"{skipped} برند از قبل در این دسته‌بندی وجود داشت و تکراری اضافه نشد.")
        return HttpResponseRedirect(self.get_success_url())


class AdminMegaMenuUpdateView(CrudUpdateView):
    config = MEGAMENU

    def get_form_class(self):
        return MegaMenuEditForm


class AdminMegaMenuDeleteView(CrudDeleteView):
    config = MEGAMENU


# ------------------------------------------------------------------ تنظیمات سایت (تک‌رکوردی)
SITE_SETTING = CrudConfig(
    key="site-setting",
    model=SiteSetting,
    title="تنظیمات سایت",
    plural="تنظیمات سایت",
    fields=(
        "site_name", "logo", "favicon", "phone", "support_phone", "email", "address", "working_hours",
        "instagram", "telegram", "whatsapp", "eitaa",
        "announcement_active", "announcement_text", "announcement_link",
        "free_shipping_threshold", "footer_text", "enamad_code", "meta_title", "meta_description",
    ),
    columns=[],
    icon="i-cog",
    description="اطلاعات تماس، شبکه‌های اجتماعی، نوار اعلان و سئوی کلی سایت. این اطلاعات از طریق API به فرانت داده می‌شود.",
)


class AdminSiteSettingView(SingletonUpdateView):
    config = SITE_SETTING
