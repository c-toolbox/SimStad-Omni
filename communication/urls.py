from django.urls import path, re_path
from . import views

urlpatterns = [
    path("", views.index),
    # re_path("^get_example/?$", views.get_example),
    # re_path("^post_example/?$", views.post_example),
]
