from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from ...permissions import HasAdminAccessPermission



class AdminDashboardHomeView(LoginRequiredMixin, HasAdminAccessPermission, TemplateView):
    template_name = "dashboard/admin/home.html"

    def get_context_data(self, **kwargs):
        from ....bwdk.models import BWDKOrder
        from ....shop.models import ProductQuestion
        ctx = super().get_context_data(**kwargs)
        ctx["bwdk_needs_review"] = BWDKOrder.objects.filter(needs_review=True).count()
        ctx["questions_pending"] = ProductQuestion.objects.filter(status=1).count()
        return ctx
