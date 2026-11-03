from django.urls import include, path

app_name = "website"

urlpatterns = [
    path("v1/", include("app.website.api.v1.urls")),
]
