from django.urls import path
from . import views

urlpatterns = [
	path("", views.index),

	path("get_city/<str:city_id>/", views.get_city),
	path("get_collection/<str:collection_id>/", views.get_collection),
	path("get_scenario/<str:scenario_id>/", views.get_scenario),

    # re_path("^get_example/?$", views.get_example),
    # re_path("^post_example/?$", views.post_example),
]
