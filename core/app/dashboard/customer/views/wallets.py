from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from ...permissions import HasCustomerAccessPermission

from ....wallets.models import Wallet


class WalletDetailView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = 'dashboard/customer/wallets/wallet_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wallet = Wallet.objects.get(user=self.request.user)
        context['wallet'] = wallet
        context['transactions'] = wallet.transactions.order_by('-created_at')[:5]  # مثلاً ۵ تراکنش آخر
        return context
