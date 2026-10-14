import uuid
from unittest import mock

from django.test import RequestFactory, TestCase, override_settings

from app.accounts.models import User
from app.order.models import OrderStatusType
from app.shop.models import Color, ProductColorInventory, ProductModel

from .client import BWDKError
from .models import BWDKOrder
from .services import BWDKService


@override_settings(BWDK_API_KEY="test", BWDK_CALLBACK_BASE="https://manmarket.ir", ALLOWED_HOSTS=["*"])
class BWDKFlowTests(TestCase):
    def setUp(self):
        color = Color.objects.create(title="قرمز", hex_color="#FF0000")
        product = ProductModel.objects.create(title="گوشی تست", slug="test-phone", description="d")
        self.inv = ProductColorInventory.objects.create(
            product=product, color=color, price=100000, stock=5, hex_color="#FF0000"
        )
        self.svc = BWDKService()
        self.request = RequestFactory().get("/", HTTP_HOST="api.manmarket.ir")

    def _create(self, qty=2):
        def fake(payload):
            self.sent = payload
            return {"order_uuid": str(uuid.uuid4()), "order_start_url": "https://bwdk/start"}

        with mock.patch.object(self.svc.client, "create_order", side_effect=fake):
            return self.svc.create_checkout(
                user=None, items=[{"color_inventory": self.inv.pk, "quantity": qty}], request=self.request
            )

    def _remote(self, bw, status, **extra):
        data = {
            "status": status, "status_display": "x", "merchant_order_id": bw.merchant_order_id,
            "main_amount": int(bw.main_amount), "discount_amount": 0, "tax_amount": 0,
            "is_paid": status in (7, 9), "total_paid_amount": 215000, "shipping_amount": 10000,
            "packing_amount": 5000, "reference_code": "BD-1",
            "items": [{"count": 2, "amount": 100000, "name": "x"}],
            "payment": {"gateway_name": "Digipay", "gateway_type_display": "BNPL",
                        "paid_at": "2026-10-13T10:00:00+03:30"},
            "user": {"first_name": "علی", "last_name": "رضایی", "phone_number": "+989121234567"},
            "destination_address": {"receiver_name": "علی رضایی", "receiver_phone": "989121234567",
                                    "state_name": "تهران", "city_name": "تهران", "address": "خیابان ۱",
                                    "building_number": "3", "unit": "4", "postal_code": "1111111111"},
            "selected_shipping_method": {"name": "ارسال"},
        }
        data.update(extra)
        return data

    def test_create_reserves_stock_and_builds_valid_payload(self):
        bw = self._create()
        self.inv.refresh_from_db()
        self.assertEqual(self.inv.stock, 3)
        self.assertTrue(bw.guest_checkout)
        self.assertEqual(self.sent["main_amount"], 200000)
        self.assertEqual(self.sent["final_amount"], 200000)
        self.assertEqual(self.sent["items"][0]["discount_amount"], 0)
        self.assertEqual(self.sent["items"][0]["options"][0]["value"], "#FF0000")
        self.assertNotIn("?", self.sent["callback_url"])
        self.assertTrue(self.sent["callback_url"].endswith(f"/bwdk/callback/{bw.merchant_unique_id}/"))

    def test_create_failure_rolls_back_stock(self):
        with mock.patch.object(self.svc.client, "create_order", side_effect=BWDKError("x", 500, {})):
            with self.assertRaises(ValueError):
                self.svc.create_checkout(
                    user=None, items=[{"color_inventory": self.inv.pk, "quantity": 1}], request=self.request
                )
        self.inv.refresh_from_db()
        self.assertEqual(self.inv.stock, 5)
        self.assertEqual(BWDKOrder.objects.count(), 0)

    def test_out_of_stock_is_rejected(self):
        with self.assertRaises(ValueError):
            self._create(qty=99)

    def test_paid_order_is_verified_once_and_attached_to_real_user(self):
        bw = self._create()
        with mock.patch.object(self.svc.client, "get_order", return_value=self._remote(bw, 7)), \
                mock.patch.object(self.svc.client, "verify_order", return_value={}) as verify:
            self.assertEqual(self.svc.complete(bw.merchant_unique_id)["state"], "paid")
            self.assertEqual(self.svc.complete(bw.merchant_unique_id)["state"], "paid")
        self.assertEqual(verify.call_count, 1)
        self.assertEqual(verify.call_args.args[1], bw.merchant_unique_id)
        bw.refresh_from_db()
        self.assertEqual(bw.order.status, OrderStatusType.success.value)
        self.assertEqual(bw.order.user.phone_number, "09121234567")
        self.assertIn("پلاک 3", bw.order.address)
        self.inv.refresh_from_db()
        self.assertEqual(self.inv.stock, 3)  # reserved at create, not decremented twice

    def test_failed_verify_is_retried_later(self):
        bw = self._create()
        with mock.patch.object(self.svc.client, "get_order", return_value=self._remote(bw, 7)), \
                mock.patch.object(self.svc.client, "verify_order", side_effect=BWDKError("x", 500, {})):
            self.assertEqual(self.svc.complete(bw.merchant_unique_id)["state"], "pending")
        bw.refresh_from_db()
        self.assertEqual(bw.verify_attempts, 1)
        with mock.patch.object(self.svc.client, "get_order", return_value=self._remote(bw, 7)), \
                mock.patch.object(self.svc.client, "verify_order", return_value={}):
            self.assertEqual(self.svc.reconcile(bw.pk).finalized_at is not None, True)

    def test_mismatching_amounts_block_verify(self):
        bw = self._create()
        bad = self._remote(bw, 7, main_amount=1)
        with mock.patch.object(self.svc.client, "get_order", return_value=bad), \
                mock.patch.object(self.svc.client, "verify_order") as verify:
            self.assertEqual(self.svc.complete(bw.merchant_unique_id)["state"], "review")
        self.assertFalse(verify.called)

    def test_failed_payment_cancels_and_restocks(self):
        bw = self._create()
        with mock.patch.object(self.svc.client, "get_order", return_value=self._remote(bw, 8)):
            self.assertEqual(self.svc.complete(bw.merchant_unique_id)["state"], "failed")
        self.inv.refresh_from_db()
        self.assertEqual(self.inv.stock, 5)

    def test_edit_basket_cancels_and_restocks(self):
        bw = self._create()
        with mock.patch.object(self.svc.client, "get_order", return_value=self._remote(bw, 3)):
            self.assertEqual(self.svc.complete(bw.merchant_unique_id, edit_basket=True)["state"], "edit_basket")
        self.inv.refresh_from_db()
        self.assertEqual(self.inv.stock, 5)

    def test_guest_owner_cannot_log_in(self):
        owner = BWDKService.guest_owner()
        self.assertFalse(owner.is_active)
        self.assertFalse(owner.has_usable_password())
        self.assertEqual(User.objects.filter(phone_number=owner.phone_number).count(), 1)


@override_settings(BWDK_API_KEY="test", ALLOWED_HOSTS=["*"])
class BWDKApiTests(TestCase):
    def setUp(self):
        from rest_framework.test import APIClient

        color = Color.objects.create(title="آبی", hex_color="#0000FF")
        product = ProductModel.objects.create(title="هدفون", slug="headphone", description="d")
        self.inv = ProductColorInventory.objects.create(
            product=product, color=color, price=50000, stock=3, hex_color="#0000FF"
        )
        self.client = APIClient()

    def _fake_create(self, payload):
        return {"order_uuid": str(uuid.uuid4()), "order_start_url": "https://bwdk/start"}

    def test_guest_can_create_without_login(self):
        with mock.patch("app.bwdk.client.BWDKClient.create_order", side_effect=self._fake_create):
            res = self.client.post(
                "/bwdk/v1/create/",
                {"items": [{"color_inventory": self.inv.pk, "quantity": 1}]},
                format="json",
            )
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(res.json()["order_start_url"], "https://bwdk/start")

    def test_guest_with_empty_cart_gets_400(self):
        res = self.client.post("/bwdk/v1/create/", {}, format="json")
        self.assertEqual(res.status_code, 400)

    def test_logged_in_user_uses_saved_cart(self):
        from app.cart.models import CartItemModel, CartModel

        user = User.objects.create_user(phone_number="09123334444", password="x")
        cart, _ = CartModel.objects.get_or_create(user=user)
        CartItemModel.objects.create(
            cart=cart, product=self.inv.product, color=self.inv.color, color_inventory=self.inv, quantity=2
        )
        self.client.force_authenticate(user)
        with mock.patch("app.bwdk.client.BWDKClient.create_order", side_effect=self._fake_create):
            res = self.client.post("/bwdk/v1/create/", {}, format="json")
        self.assertEqual(res.status_code, 201, res.content)
        bw = BWDKOrder.objects.get()
        self.assertFalse(bw.guest_checkout)
        self.assertEqual(bw.order.user_id, user.id)
        self.assertEqual(int(bw.main_amount), 100000)

    def test_complete_unknown_id_is_404(self):
        res = self.client.post("/bwdk/v1/complete/", {"merchant_unique_id": "nope"}, format="json")
        self.assertEqual(res.status_code, 404)

    def test_refund_requires_admin(self):
        user = User.objects.create_user(phone_number="09125556666", password="x")
        self.client.force_authenticate(user)
        res = self.client.post(f"/bwdk/v1/orders/{uuid.uuid4()}/refund/", {}, format="json")
        self.assertIn(res.status_code, (401, 403))


@override_settings(BWDK_API_KEY="test", ALLOWED_HOSTS=["*"])
class BWDKDashboardTests(BWDKFlowTests):
    """Dashboard tests (inherits the fixtures of BWDKFlowTests)."""

    def test_admin_order_detail_renders_bwdk_card_and_buttons(self):
        from app.accounts.models import UserType

        bw = self._create()
        with mock.patch.object(self.svc.client, "get_order", return_value=self._remote(bw, 7)), \
                mock.patch.object(self.svc.client, "verify_order", return_value={}):
            self.svc.complete(bw.merchant_unique_id)

        admin = User.objects.create_user(phone_number="09120001111", password="x", type=UserType.admin.value)
        self.client.force_login(admin)
        url = f"/dashboard/admin/order/{bw.order_id}/detail/"
        res = self.client.get(url)
        if res.status_code == 404:  # path differs in this project: find it by name
            from django.urls import reverse

            res = self.client.get(reverse("dashboard:admin:order-detail", kwargs={"pk": bw.order_id}))
        self.assertEqual(res.status_code, 200)
        html = res.content.decode()
        self.assertIn("خرید با دیجی‌کالا (BWDK)", html)
        self.assertIn("BD-1", html)
        self.assertIn("بازگشت وجه (Refund)", html)  # Digipay + finalized

    def test_admin_refund_view_calls_api_and_restocks(self):
        from django.urls import reverse
        from app.accounts.models import UserType

        bw = self._create()
        with mock.patch.object(self.svc.client, "get_order", return_value=self._remote(bw, 7)), \
                mock.patch.object(self.svc.client, "verify_order", return_value={}):
            self.svc.complete(bw.merchant_unique_id)

        admin = User.objects.create_user(phone_number="09120001112", password="x", type=UserType.admin.value)
        self.client.force_login(admin)
        with mock.patch("app.bwdk.client.BWDKClient.get_order", return_value=self._remote(bw, 9)), \
                mock.patch("app.bwdk.client.BWDKClient.refund_order", return_value={"status": 17}) as refund:
            res = self.client.post(
                reverse("dashboard:admin:order-bwdk-refund", kwargs={"pk": bw.order_id}), {"reason": "test"}
            )
        self.assertEqual(res.status_code, 302)
        self.assertEqual(refund.call_args.args[2], 215000)  # full total_paid_amount
        bw.refresh_from_db()
        self.assertEqual(bw.status, 17)
        self.inv.refresh_from_db()
        self.assertEqual(self.inv.stock, 5)
