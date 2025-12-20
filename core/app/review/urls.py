from django.urls import path,include
from . import views
from .api.v1 import urls as api_urls

app_name = "review"

urlpatterns = [
    path("v1",include(api_urls)),
    path("submit-review/",views.SubmitReviewView.as_view(),name="submit-review")
]