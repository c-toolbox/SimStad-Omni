from django.http import JsonResponse, Http404
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import CitySerializer, CollectionSerializer, ScenarioSerializer
from .models import City, Collection, Scenario


def index(request):
    return render(
        request,
        "simstad/index.html",
        {"is_authenticated": request.user.is_authenticated},
    )


# --- Cities --- #

@api_view(["GET"])
# Takes a service token and returns a json response with this structure:
def get_city(request, city_id):
    try:
        instance = City.objects.get(key=city_id)
    except City.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CitySerializer(instance)
    return Response(serializer.data)


@api_view(["GET"])
def get_city2(request, city_id):
    try:
        city = City.objects.get(key=city_id)
    except City.DoesNotExist:
        raise Http404("City not found")

    collections = Collection.objects.filter(city=city)
    return JsonResponse(
        {
            "id": "visualcity",
            "title": "VisualCity",
            "defaultBlocksVideo": "VisualCity-Wall_360",
            "collections": [
                {
                    "id": city_id,
                    "blocksVideo": c.blocks_video,
                    "image": (
                        request.build_absolute_uri(c.image.url) if c.image else None
                    ),
                }
                for c in collections
            ],
        }
    )


# Takes a collection id and returns a json response with a list of its scenarios as previews.
@api_view(["GET"])
def get_collection(request, collection_id):
    try:
        instance = Collection.objects.get(key=collection_id)
    except Collection.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CollectionSerializer(instance)
    return Response(serializer.data)


# --- Collections --- #

@api_view(["GET"])
def get_collection2(request):
    collection_id = request.GET.get("id")
    if not collection_id:
        return JsonResponse({"error": "Missing id"}, status=400)

    try:
        collection = Collection.objects.get(id=collection_id)
    except Collection.DoesNotExist:
        raise Http404("Collection not found")

    scenarios = collection.scenarios.all()
    return JsonResponse(
        {
            "id": collection.id,
            "title": collection.title,
            "scenarios": [
                {"id": s.id, "title": s.title, "default": s.is_default}
                for s in scenarios
            ],
        }
    )


# --- Scenarios --- #

# Takes a scenario id and returns a json response with all the information about it.
@api_view(["GET"])
def get_scenario(request, scenario_id):
    try:
        instance = Scenario.objects.get(key=scenario_id)
    except Scenario.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ScenarioSerializer(instance)
    return Response(serializer.data)


@api_view(["GET"])
def get_scenario2(request):
    scenario_id = request.GET.get("scenario_id")
    if not scenario_id:
        return JsonResponse({"error": "Missing id"}, status=400)

    try:
        scenario = Scenario.objects.get(id=scenario_id)
    except Scenario.DoesNotExist:
        raise Http404("Scenario not found")

    layers = scenario.layers.select_related("raster").all()

    return JsonResponse(
        {
            "id": scenario.id,
            "title": scenario.title,
            "description": scenario.description,
            "layers": [
                {
                    "type": "image",
                    "name": sr.raster.filename,
                    "image": request.build_absolute_uri(sr.raster.image.url),
                    "minimap": (
                        request.build_absolute_uri(sr.raster.minimap.url)
                        if sr.raster.minimap
                        else None
                    ),
                    "thumbnail": (
                        request.build_absolute_uri(sr.raster.thumbnail.url)
                        if sr.raster.thumbnail
                        else None
                    ),
                    "opacity": sr.opacity,
                    "lit": sr.lit,
                    "crop": {
                        "min_u": sr.min_u,
                        "max_u": sr.max_u,
                        "min_v": sr.min_v,
                        "max_v": sr.max_v,
                    },
                }
                for sr in layers
            ],
            "legend": {
                "title": scenario.legend.title if hasattr(scenario, "legend") else "",
                "entries": (
                    [
                        {"color": entry.color, "text": entry.text, "type": entry.type}
                        for entry in scenario.legend.entries.all()
                    ]
                    if hasattr(scenario, "legend")
                    else []
                ),
            },
        }
    )
