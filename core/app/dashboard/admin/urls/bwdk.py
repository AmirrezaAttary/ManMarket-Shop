from django.urls import path

from .. import views

urlpatterns = [
    path("bwdk/list/", views.AdminBWDKListView.as_view(), name="bwdk-list"),
    path("bwdk/sync/", views.AdminBWDKSyncAllView.as_view(), name="bwdk-sync"),
    path("bwdk/<int:pk>/detail/", views.AdminBWDKDetailView.as_view(), name="bwdk-detail"),
    path("bwdk/<int:pk>/verify/", views.AdminBWDKVerifyView.as_view(), name="bwdk-verify"),
    path("bwdk/<int:pk>/refund/", views.AdminBWDKRefundView.as_view(), name="bwdk-refund"),
    path("bwdk/<int:pk>/review-done/", views.AdminBWDKReviewDoneView.as_view(), name="bwdk-review-done"),
]
