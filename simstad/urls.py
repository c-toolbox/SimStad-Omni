from django.urls import path
from . import views

urlpatterns = [
	path("", views.index),

	path("get_city/<str:city_key>/", views.get_city),
	path("get_collection/<str:collection_key>/", views.get_collection),
	path("get_scenarios/", views.get_scenarios),
	path("get_scenario/<str:scenario_key>/", views.get_scenario),
	path("get_rasters/", views.get_rasters),
	path("get_raster/<str:raster_key>/", views.get_raster),
	path("get_legend/<str:legend_key>/", views.get_legend),
	path("get_tags/", views.get_tags),
	path("legend/<str:scenario_key>/", views.legend_page),
]
