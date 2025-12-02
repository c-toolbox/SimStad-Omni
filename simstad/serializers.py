from rest_framework import serializers
from .models import (
    City,
    Collection,
    Scenario,
    Raster,
    Legend,
    LegendEntry,
    LegendSymbol,
    Tag,
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            "created_at",
            "changed_at",
            "key",
            "name",
        ]


class LegendSymbolSerializer(serializers.ModelSerializer):
    class Meta:
        model = LegendSymbol
        fields = [
            "created_at",
            "changed_at",
            "key",
            "image",
        ]


class LegendEntrySerializer(serializers.ModelSerializer):
    symbol = serializers.SlugRelatedField(read_only=True, slug_field="key")

    class Meta:
        model = LegendEntry
        fields = [
            "legend",
            "text",
            "symbol",
            "order",
        ]


class LegendSerializer(serializers.ModelSerializer):
    entries = LegendEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Legend
        fields = [
            "created_at",
            "changed_at",
            "key",
            "title",
            "entries",
        ]


class RasterSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field="key")

    class Meta:
        model = Raster
        fields = [
            "created_at",
            "changed_at",
            "key",
            "name",
            "notes",
            "city",
            "tags",
            "image",
            "minimap",
            "thumbnail",
        ]


class ScenarioSerializer(serializers.ModelSerializer):
    rasters = serializers.SlugRelatedField(many=True, read_only=True, slug_field="key")
    legend = serializers.SlugRelatedField(many=False, read_only=True, slug_field="key")

    class Meta:
        model = Scenario
        fields = [
            "created_at",
            "changed_at",
            "key",
            "name",
            "short_name",
            "description",
            "city",
            "rasters",
            "legend",
            "legend_image",
            "legend_image_source",
        ]


class CollectionSerializer(serializers.ModelSerializer):
    scenarios = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="key"
    )

    class Meta:
        model = Collection
        fields = [
            "created_at",
            "changed_at",
            "key",
            "name",
            "city",
            "blocks_video",
            "image",
            "scenarios",
        ]


class CitySerializer(serializers.ModelSerializer):
    collections = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="key"
    )

    class Meta:
        model = City
        fields = [
            "created_at",
            "changed_at",
            "key",
            "name",
            "min_x",
            "min_y",
            "max_x",
            "max_y",
            "default_blocks_video",
            "collections",
        ]
