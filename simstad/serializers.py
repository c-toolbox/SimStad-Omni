from rest_framework import serializers
from .models import (
    City,
    Collection,
    Scenario,
    Raster,
    Tag,
    Legend,
    LegendEntry,
    LegendSymbol,
)


class LegendSymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegendSymbol
        fields = ["name", "image"]


class LegendEntrySerializer(serializers.ModelSerializer):
    symbol = LegendSymbolSerializer(read_only=True)

    class Meta:
        model = LegendEntry
        fields = ["text", "color", "symbol", "order"]


class LegendSerializer(serializers.ModelSerializer):
    entries = LegendEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Legend
        fields = ["key", "title", "entries"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name"]


class RasterSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")

    class Meta:
        model = Raster
        fields = [
            "key",
            "name_en",
            "name_sv",
            "image",
            "minimap",
            "thumbnail",
            "tags",
        ]


class ScenarioSerializer(serializers.ModelSerializer):
    legend = LegendSerializer(many=False, read_only=True)
    rasters = RasterSerializer(many=True, read_only=True)

    class Meta:
        model = Scenario
        fields = ["key", "name", "description", "legend_image", "legend", "rasters"]


class CollectionSerializer(serializers.ModelSerializer):
    scenarios = ScenarioSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = ["key", "name", "blocks_video", "image", "scenarios"]


class CitySerializer(serializers.ModelSerializer):
    collections = CollectionSerializer(many=True, read_only=True)

    class Meta:
        model = City
        fields = ["id", "key", "name", "collections"]
