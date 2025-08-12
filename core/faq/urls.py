from faq import views

from django.urls import path

app_name = 'faq'

urlpatterns = [
    path('', views.FaqView.as_view(), name='faq'),
    path('rules/', views.RulesView.as_view(), name='rules'),
    path('call-we/', views.CallWeView.as_view(), name='call-we'),
    path('target/', views.TargetView.as_view(), name='target'),
    path('man-one-seen/', views.ManOneSeenView.as_view(), name='man-one-seen'),
    path('tasis/', views.TasisView.as_view(), name='tasis'),
    path('asas/', views.AsasView.as_view(), name='asas'),
    path('afzayesh/', views.AfzayeshView.as_view(), name='afzayesh'),
]