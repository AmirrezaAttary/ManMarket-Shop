"""
تنظیمات بخش‌های CRUD داشبورد (مگا منو، بنر، منو، سوالات متداول، صفحات ثابت، خبرنامه، پرسش‌های محصول).

هر بخش فقط با یک CrudConfig تعریف می‌شود؛ view ها، URL ها و تمپلیت‌ها عمومی‌اند
(dashboard/admin/views/crud.py و templates/dashboard/admin/crud/).
"""
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Sequence

from ...shop.models import MegaMenu, ProductQuestion
from ...website.models import Banner, FAQ


@dataclass
class Column:
    label: str
    attr: str
    kind: str = "text"  # text | bool | image | choice | date | fk | trunc


@dataclass
class CrudConfig:
    key: str  # نام URL و مسیر؛ مثلاً "banner" → banner-list / banner-add / banner-edit / banner-delete
    model: type
    title: str  # مفرد
    plural: str  # جمع
    fields: Sequence[str]
    columns: List[Column]
    search_fields: Sequence[str] = ()
    filters: Sequence[str] = ()
    icon: str = "i-grid"
    description: str = ""
    form_class: Optional[type] = None
    can_add: bool = True
    ordering: Sequence[str] = ()
    select_related: Sequence[str] = ()
    date_hint: str = ""


# ----- مگا منو: فرم اختصاصی در views/megamenu.py
MEGAMENU = CrudConfig(
    key="mega-menu",
    model=MegaMenu,
    title="مگا منو",
    plural="مگا منو",
    fields=("category", "brand"),
    columns=[Column("دسته‌بندی", "category", "fk"), Column("برند", "brand", "fk"), Column("تاریخ ایجاد", "created_date", "date")],
    search_fields=("category__title", "brand__title"),
    filters=("category", "brand"),
    icon="i-grid",
    description="برندهایی که زیر هر دسته‌بندی در مگا منوی بالای سایت نمایش داده می‌شوند.",
    select_related=("category", "brand"),
)

BANNER = CrudConfig(
    key="banner",
    model=Banner,
    title="بنر",
    plural="بنرها",
    fields=("title", "position", "image", "mobile_image", "link", "alt_text", "sort_order", "is_active", "start_date", "end_date"),
    columns=[
        Column("تصویر", "image", "image"), Column("عنوان", "title"), Column("جایگاه", "position", "choice"),
        Column("ترتیب", "sort_order"), Column("فعال", "is_active", "bool"),
    ],
    search_fields=("title", "link"),
    filters=("position", "is_active"),
    icon="i-photo",
    description="اسلایدر و بنرهای تبلیغاتی صفحه‌ی اول و دسته‌بندی‌ها. خالی گذاشتن تاریخ یعنی بدون محدودیت زمانی.",
)


FAQ_CONFIG = CrudConfig(
    key="faq",
    model=FAQ,
    title="سوال متداول",
    plural="سوالات متداول",
    fields=("question", "answer", "category", "sort_order", "is_active"),
    columns=[
        Column("پرسش", "question", "trunc"), Column("دسته‌بندی", "category", "choice"),
        Column("ترتیب", "sort_order"), Column("فعال", "is_active", "bool"),
    ],
    search_fields=("question", "answer"),
    filters=("category", "is_active"),
    icon="i-clipboard",
)


QUESTION = CrudConfig(
    key="product-question",
    model=ProductQuestion,
    title="پرسش محصول",
    plural="پرسش و پاسخ محصولات",
    fields=("question", "answer", "status"),
    columns=[
        Column("محصول", "product", "fk"), Column("پرسش", "question", "trunc"),
        Column("وضعیت", "status", "choice"), Column("تاریخ ثبت", "created_date", "date"),
    ],
    search_fields=("question", "answer", "product__title"),
    filters=("status",),
    icon="i-chat",
    description="پرسش‌های کاربران درباره‌ی محصولات. فقط پرسش‌های «تایید شده» در سایت نمایش داده می‌شوند.",
    can_add=False,
    select_related=("product", "user"),
)

ALL_CRUDS = [MEGAMENU, BANNER, FAQ_CONFIG, QUESTION]
