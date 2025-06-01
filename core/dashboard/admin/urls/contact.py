from django.urls import path, include
from ..views import ContactListView, ContactDetailView, ContactDeleteView

urlpatterns = [
    path('contacts/', ContactListView.as_view(), name='contact-list'),
    path('contacts/<int:pk>/', ContactDetailView.as_view(), name='contact-detail'),
    path('contacts/<int:pk>/delete/', ContactDeleteView.as_view(), name='contact-delete'),
]