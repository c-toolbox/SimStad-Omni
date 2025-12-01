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
        fields = ["key", "image"]


class LegendEntrySerializer(serializers.ModelSerializer):
    symbol = serializers.SlugRelatedField(read_only=True, slug_field="key")

    class Meta:
        model = LegendEntry
        fields = ["text", "color", "symbol", "order"]


class LegendSerializer(serializers.ModelSerializer):
    entries = LegendEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Legend
        fields = ["key", "title", "entries"]


class RasterSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="key")

    class Meta:
        model = Raster
        fields = [
            "key",
            "name",
            "notes",
            "image",
            "minimap",
            "thumbnail",
            "tags",
        ]


class ScenarioSerializer(serializers.ModelSerializer):
    legend = serializers.SlugRelatedField(many=False, read_only=True, slug_field="key")
    rasters = serializers.SlugRelatedField(many=True, read_only=True, slug_field="key")

    class Meta:
        model = Scenario
        fields = [
            "key",
            "name",
            "description",
            "legend_image",
            "legend",
            "rasters",
        ]


class CollectionSerializer(serializers.ModelSerializer):
    scenarios = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="key"
    )

    class Meta:
        model = Collection
        fields = ["key", "name", "blocks_video", "image", "scenarios"]


class CitySerializer(serializers.ModelSerializer):
    collections = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="key"
    )

    class Meta:
        model = City
        fields = ["id", "key", "name", "collections"]
