from rest_framework import serializers
from .models import City, Collection, Scenario, Raster, Tag, Legend, LegendEntry


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["name"]


class LegendEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LegendEntry
        fields = ["text", "color", "type", "order"]


class LegendSerializer(serializers.ModelSerializer):
    entries = LegendEntrySerializer(many=True, read_only=True)

    class Meta:
        model = Legend
        fields = ["title", "entries"]


class RasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Raster
        fields = [
            "key",
            "name",
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
        fields = ["id", "key", "name", "service", "collections"]
