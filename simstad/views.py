from django.http import JsonResponse, Http404
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import (
    CitySerializer,
    CollectionSerializer,
    ScenarioSerializer,
    RasterSerializer,
    TagSerializer,
)
from .models import City, Collection, Scenario, Raster, Tag


def index(request):
    return render(
        request,
        "simstad/index.html",
        {"is_authenticated": request.user.is_authenticated},
    )


# --- City --- #

@api_view(["GET"])
def get_city(request, city_key):
    try:
        instance = City.objects.get(key=city_key)
    except City.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CitySerializer(instance)
    return Response(serializer.data)


# --- Collection --- #

@api_view(["GET"])
def get_collection(request, collection_key):
    try:
        instance = Collection.objects.get(key=collection_key)
    except Collection.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CollectionSerializer(instance)
    return Response(serializer.data)


# --- Scenario --- #

@api_view(["GET"])
def get_scenarios(request):
    instances = Scenario.objects.all()
    serializer = ScenarioSerializer(instances, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_scenario(request, scenario_key):
    try:
        instance = Scenario.objects.get(key=scenario_key)
    except Scenario.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ScenarioSerializer(instance)
    return Response(serializer.data)


# --- Raster --- #

@api_view(["GET"])
def get_rasters(request):
    instances = Raster.objects.all()
    serializer = RasterSerializer(instances, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_raster(request, raster_key):
    try:
        instance = Raster.objects.get(key=raster_key)
    except Raster.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = RasterSerializer(instance)
    return Response(serializer.data)


# --- Tag --- #

@api_view(["GET"])
def get_tags(request):
    instances = Tag.objects.all()
    serializer = TagSerializer(instances, many=True)
    return Response(serializer.data)
