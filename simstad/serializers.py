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
    layers = serializers.SerializerMethodField()
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
            "layers",
            "legend",
            "legend_image",
            "legend_image_source",
        ]

    def serialize_layer(self, layer):
        data = {
            "type": layer.type,
        }

        # Raster (shared by image / flow / movie)
        if layer.type in {"image", "flow", "movie"} and layer.raster:
            data["raster"] = layer.raster.key

        # Flow
        if layer.type == "flow":
            data["flow"] = {
                "texture": layer.flow_texture.key if layer.flow_texture else None,
                "scale": layer.flow_scale,
                "speed": layer.flow_speed,
            }

        # Movie
        if layer.type == "movie":
            data["movie"] = {
                "speed": layer.movie_speed,
            }

        # Color
        if layer.type == "color":
            data["color"] = layer.color

        # NDI
        if layer.type == "ndi":
            data["ndi"] = {
                "stream": layer.ndi_stream,
            }
            if layer.ndi_machine:
                data["ndi"]["machine"] = layer.ndi_machine

        # Optional modifiers (only if non-default)
        if layer.opacity is not None and layer.opacity != 1.0:
            data["opacity"] = layer.opacity

        if layer.emission is not None and layer.emission != 0.0:
            data["emission"] = layer.emission

        crop = layer.get_crop_data()
        if crop:
            data["crop"] = crop

        return data

    def get_layers(self, obj):
        layers = obj.layers.select_related("raster").order_by("order")
        return [self.serialize_layer(layer) for layer in layers]


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
