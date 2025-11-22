# urls.py
from django.urls import path
from .. import views

urlpatterns = [
    path('download-db/', views.DownloadDatabaseView.as_view(), name='download_database'),
    path('media-db/', views.DownloadMediaView.as_view(), name='download_media'),
]
