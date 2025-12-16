from django.http import JsonResponse, Http404
from django.shortcuts import render
from django.utils.translation import activate
from functools import wraps
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import (
    CitySerializer,
    CollectionSerializer,
    ScenarioSerializer,
    RasterSerializer,
    LegendSerializer,
    LegendSymbolSerializer,
    TagSerializer,
)
from .models import (
    City,
    Collection,
    Scenario,
    Raster,
    Legend,
    LegendSymbol,
    Tag,
    LocalizedString,
)


# --- Html pages --- #


def index(request):
    return render(
        request,
        "simstad/index.html",
        {"is_authenticated": request.user.is_authenticated},
    )


def legend_page(request, scenario_key):
    activate(request.GET.get("language", "sv"))

    if Scenario.objects.filter(key=scenario_key).exists():
        scenario = Scenario.objects.get(key=scenario_key)
        context = {"scenario": scenario}
    else:
        context = {
            "scenario": {
                "name": scenario_key,
                "description": f'Scenario "{scenario_key}" could not be found.',
            }
        }

    return render(request, "simstad/legend.html", context)


# --- Decorators --- #


def with_language(default="sv"):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            lang = request.GET.get("language", default)
            activate(lang)
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


# --- City --- #


@with_language()
@api_view(["GET"])
def get_cities(request):
    instances = City.objects.all()
    serializer = CitySerializer(instances, many=True)
    return Response(serializer.data)


@with_language()
@api_view(["GET"])
def get_city(request, city_key):
    try:
        instance = City.objects.get(key=city_key)
    except City.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CitySerializer(instance)
    return Response(serializer.data)


# --- Collection --- #


@with_language()
@api_view(["GET"])
def get_collections(request):
    instances = Collection.objects.all()
    serializer = CollectionSerializer(instances, many=True)
    return Response(serializer.data)


@with_language()
@api_view(["GET"])
def get_collection(request, collection_key):
    try:
        instance = Collection.objects.get(key=collection_key)
    except Collection.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CollectionSerializer(instance)
    return Response(serializer.data)


# --- Scenario --- #


@with_language()
@api_view(["GET"])
def get_scenarios(request):
    instances = Scenario.objects.all()
    serializer = ScenarioSerializer(instances, many=True)
    return Response(serializer.data)


@with_language()
@api_view(["GET"])
def get_scenario(request, scenario_key):
    try:
        instance = Scenario.objects.get(key=scenario_key)
    except Scenario.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ScenarioSerializer(instance)
    return Response(serializer.data)


# --- Raster --- #


@with_language()
@api_view(["GET"])
def get_rasters(request):
    instances = Raster.objects.all()
    serializer = RasterSerializer(instances, many=True)
    return Response(serializer.data)


@with_language()
@api_view(["GET"])
def get_raster(request, raster_key):
    try:
        instance = Raster.objects.get(key=raster_key)
    except Raster.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = RasterSerializer(instance)
    return Response(serializer.data)


# --- Legend --- #


@with_language()
@api_view(["GET"])
def get_legends(request):
    instances = Legend.objects.all()
    serializer = LegendSerializer(instances, many=True)
    return Response(serializer.data)


@with_language()
@api_view(["GET"])
def get_legend(request, legend_key):
    try:
        instance = Legend.objects.get(key=legend_key)
    except Legend.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = LegendSerializer(instance)
    return Response(serializer.data)


# --- Legend Symbol --- #


@with_language()
@api_view(["GET"])
def get_symbols(request):
    instances = LegendSymbol.objects.all()
    serializer = LegendSymbolSerializer(instances, many=True)
    return Response(serializer.data)


@with_language()
@api_view(["GET"])
def get_symbol(request, symbol_key):
    try:
        instance = LegendSymbol.objects.get(key=symbol_key)
    except LegendSymbol.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = LegendSymbolSerializer(instance)
    return Response(serializer.data)


# --- Tag --- #


@with_language()
@api_view(["GET"])
def get_tags(request):
    instances = Tag.objects.all()
    serializer = TagSerializer(instances, many=True)
    return Response(serializer.data)


@with_language()
@api_view(["GET"])
def get_tag(request, tag_key):
    try:
        instance = Tag.objects.get(key=tag_key)
    except Tag.DoesNotExist:
        return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = TagSerializer(instance)
    return Response(serializer.data)


# --- Localization --- #


@with_language()
@api_view(["GET"])
def get_localization(request):
    localization_dict = {}

    # Add LocalizedString entries
    for localizedString in LocalizedString.objects.all():
        localization_dict[localizedString.key] = localizedString.text

    # Add City translations
    for city in City.objects.all():
        localization_dict[f"city_{city.key}_name"] = city.name

    # Add Collection translations
    for collection in Collection.objects.all():
        localization_dict[f"collection_{collection.key}_name"] = collection.name

    # Add Scenario translations
    for scenario in Scenario.objects.all():
        localization_dict[f"scenario_{scenario.key}_name"] = scenario.name
        localization_dict[f"scenario_{scenario.key}_short_name"] = scenario.short_name
        localization_dict[f"scenario_{scenario.key}_description"] = scenario.description
        if scenario.legend_image_source:
            localization_dict[f"scenario_{scenario.key}_legend_image_source"] = (
                scenario.legend_image_source
            )

    # Add Legend translations
    for legend in Legend.objects.all():
        localization_dict[f"legend_{legend.key}_title"] = legend.title

        # Add LegendEntry translations
        for idx, entry in enumerate(legend.entries.all()):
            localization_dict[f"legend_{legend.key}_{idx+1}_text"] = entry.text

    # Add Tag translations
    for tag in Tag.objects.all():
        localization_dict[f"tag_{tag.key}"] = tag.name

    return Response(localization_dict)
