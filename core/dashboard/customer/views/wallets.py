from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from dashboard.permissions import HasCustomerAccessPermission
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from wallets.models import Wallet

@method_decorator(cache_page(60 * 15), name='dispatch')
class WalletDetailView(LoginRequiredMixin, HasCustomerAccessPermission, TemplateView):
    template_name = 'dashboard/customer/wallets/wallet_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wallet = Wallet.objects.get(user=self.request.user)
        context['wallet'] = wallet
        context['transactions'] = wallet.transactions.order_by('-created_at')[:5]  # مثلاً ۵ تراکنش آخر
        return context
