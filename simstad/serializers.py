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
            "text",
            "color",
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
            "tags",
            "image",
            "minimap",
            "thumbnail",
        ]


class ScenarioSerializer(serializers.ModelSerializer):
    rasters = serializers.SerializerMethodField()
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
            "rasters",
            "legend",
            "legend_image",
            "legend_image_source",
        ]

    def get_rasters(self, obj):
        return list(
            obj.scenarioraster_set.order_by("order").values_list(
                "raster__key", flat=True
            )
        )


class CollectionSerializer(serializers.ModelSerializer):
    scenarios = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            "created_at",
            "changed_at",
            "key",
            "name",
            "blocks_video",
            "image",
            "scenarios",
        ]

    def get_scenarios(self, obj):
        return list(
            obj.collectionscenario_set.order_by("order").values_list(
                "scenario__key", flat=True
            )
        )


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
