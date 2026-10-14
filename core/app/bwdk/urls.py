from django.urls import include, path

app_name = "bwdk"

urlpatterns = [
    path("v1/", include("app.bwdk.api.v1.urls")),
]
