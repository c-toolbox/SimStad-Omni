from django.urls import path
from . import views

urlpatterns = [
	path("", views.index),

	path("get_city/<str:city_key>/", views.get_city),
	path("get_collection/<str:collection_key>/", views.get_collection),
	path("get_scenario/<str:scenario_key>/", views.get_scenario),
	path("get_raster/<str:raster_key>/", views.get_raster),
]
