from django.urls import path

from . import views

app_name = "blog"

urlpatterns = [
    path("", views.list, name="list"),
    path("<int:pk>/", views.detail, name="detail"),
]
