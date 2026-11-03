import operator

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.forms import modelform_factory
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.admin_mixins import to_jalali

from ...permissions import HasAdminAccessPermission

DT_LOCAL = "%Y-%m-%dT%H:%M"


class PersianFileInput(forms.ClearableFileInput):
    initial_text = "فایل فعلی"
    input_text = "تغییر"
    clear_checkbox_label = "حذف فایل"


class DashboardModelForm(forms.ModelForm):
    """فرم پایه‌ی پنل: فیلدهای تاریخ‌وساعت با ورودی datetime-local مرورگر."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.DateTimeField):
                field.widget = forms.DateTimeInput(attrs={"type": "datetime-local"}, format=DT_LOCAL)
                field.input_formats = [DT_LOCAL, "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]
            elif isinstance(field, forms.FileField):
                field.widget = PersianFileInput()
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 6)


class CrudBase(LoginRequiredMixin, HasAdminAccessPermission):
    config = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["config"] = self.config
        return ctx


def _cell_value(obj, column):
    try:
        value = operator.attrgetter(column.attr)(obj)
    except AttributeError:
        value = None
    kind = column.kind
    if kind == "bool":
        return bool(value)
    if kind == "image":
        return value.url if value else ""
    if kind == "choice":
        getter = getattr(obj, f"get_{column.attr}_display", None)
        return getter() if getter else value
    if kind == "date":
        return to_jalali(value)
    if kind == "fk":
        return str(value) if value else "—"
    if kind == "trunc":
        text = str(value or "")
        return text if len(text) <= 70 else text[:70] + "…"
    return "—" if value in (None, "") else value


class CrudListView(CrudBase, ListView):
    template_name = "dashboard/admin/crud/list.html"
    paginate_by = 10

    def get_paginate_by(self, queryset):
        value = self.request.GET.get("page_size", self.paginate_by)
        try:
            return min(max(int(value), 5), 100)
        except (TypeError, ValueError):
            return self.paginate_by

    def _model_field(self, name):
        try:
            return self.config.model._meta.get_field(name)
        except FieldDoesNotExist:
            return None

    def get_queryset(self):
        cfg = self.config
        qs = cfg.model.objects.all()
        if cfg.select_related:
            qs = qs.select_related(*cfg.select_related)

        if q := self.request.GET.get("q", "").strip():
            cond = models.Q()
            for name in cfg.search_fields:
                cond |= models.Q(**{f"{name}__icontains": q})
            qs = qs.filter(cond)

        for name in cfg.filters:
            value = self.request.GET.get(name, "")
            if value == "":
                continue
            fld = self._model_field(name)
            if isinstance(fld, models.BooleanField):
                value = value == "true"
            try:
                qs = qs.filter(**{name: value})
            except (ValueError, TypeError):
                continue

        order_by = self.request.GET.get("order_by", "")
        if order_by.lstrip("-") in {f.name for f in cfg.model._meta.concrete_fields}:
            qs = qs.order_by(order_by)
        return qs

    def _filter_context(self):
        result = []
        for name in self.config.filters:
            fld = self._model_field(name)
            if fld is None:
                continue
            if isinstance(fld, models.BooleanField):
                options = [("true", "بله"), ("false", "خیر")]
            elif fld.choices:
                options = [(str(k), v) for k, v in fld.choices]
            elif isinstance(fld, models.ForeignKey):
                options = [(str(o.pk), str(o)) for o in fld.related_model.objects.all()[:300]]
            else:
                continue
            result.append({
                "name": name,
                "label": str(fld.verbose_name),
                "options": options,
                "current": self.request.GET.get(name, ""),
            })
        return result

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cfg = self.config
        ctx["total_items"] = self.get_queryset().count()
        ctx["filter_fields"] = self._filter_context()
        ctx["headers"] = [c.label for c in cfg.columns]
        ctx["rows"] = [
            {
                "obj": obj,
                "cells": [{"label": c.label, "kind": c.kind, "value": _cell_value(obj, c)} for c in cfg.columns],
            }
            for obj in ctx["object_list"]
        ]
        ctx["current_q"] = self.request.GET.get("q", "")
        ctx["current_order"] = self.request.GET.get("order_by", "")
        ctx["current_page_size"] = self.request.GET.get("page_size", "")
        return ctx


class CrudFormMixin(CrudBase):
    template_name = "dashboard/admin/crud/form.html"

    def get_form_class(self):
        if self.config.form_class:
            return self.config.form_class
        return modelform_factory(self.config.model, form=DashboardModelForm, fields=list(self.config.fields))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form = ctx["form"]
        ctx["wide_fields"] = [
            name for name, f in form.fields.items()
            if isinstance(f.widget, (forms.Textarea, forms.CheckboxSelectMultiple))
        ]
        ctx["multi_fields"] = [
            name for name, f in form.fields.items() if isinstance(f.widget, forms.CheckboxSelectMultiple)
        ]
        ctx["bool_fields"] = [name for name, f in form.fields.items() if isinstance(f, forms.BooleanField)]
        return ctx

    def get_list_url(self):
        return reverse_lazy(f"dashboard:admin:{self.config.key}-list")


class CrudCreateView(CrudFormMixin, SuccessMessageMixin, CreateView):
    def get_success_message(self, cleaned_data):
        return f"{self.config.title} با موفقیت ثبت شد."

    def get_success_url(self):
        return self.get_list_url()


class CrudUpdateView(CrudFormMixin, SuccessMessageMixin, UpdateView):
    def get_queryset(self):
        return self.config.model.objects.all()

    def get_success_message(self, cleaned_data):
        return f"{self.config.title} با موفقیت ویرایش شد."

    def get_success_url(self):
        return reverse_lazy(f"dashboard:admin:{self.config.key}-edit", kwargs={"pk": self.object.pk})


class CrudDeleteView(CrudBase, SuccessMessageMixin, DeleteView):
    template_name = "dashboard/admin/crud/delete.html"

    def get_queryset(self):
        return self.config.model.objects.all()

    def get_success_message(self, cleaned_data):
        return f"{self.config.title} حذف شد."

    def get_success_url(self):
        return reverse_lazy(f"dashboard:admin:{self.config.key}-list")


class SingletonUpdateView(CrudFormMixin, SuccessMessageMixin, UpdateView):
    """برای مدل‌های تک‌رکوردی مثل تنظیمات سایت."""

    def get_object(self, queryset=None):
        return self.config.model.load()

    def get_success_message(self, cleaned_data):
        return f"{self.config.title} ذخیره شد."

    def get_success_url(self):
        return reverse_lazy(f"dashboard:admin:{self.config.key}")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["singleton"] = True
        return ctx


def build_crud_views(config):
    """چهار view استاندارد (لیست / افزودن / ویرایش / حذف) را برای یک CrudConfig می‌سازد."""
    name = config.key.title().replace("-", "")
    return {
        "list": type(f"Admin{name}ListView", (CrudListView,), {"config": config}),
        "add": type(f"Admin{name}CreateView", (CrudCreateView,), {"config": config}),
        "edit": type(f"Admin{name}UpdateView", (CrudUpdateView,), {"config": config}),
        "delete": type(f"Admin{name}DeleteView", (CrudDeleteView,), {"config": config}),
    }
