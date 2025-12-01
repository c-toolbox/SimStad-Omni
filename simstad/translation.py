from modeltranslation.translator import register, TranslationOptions
from .models import City, Collection, Scenario, Raster, Tag, Legend, LegendEntry, LocalizedString


@register(City)
class CityTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Collection)
class CollectionTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Scenario)
class ScenarioTranslationOptions(TranslationOptions):
    fields = ("name", "short_name", "description", "legend_image_source")


@register(Raster)
class RasterTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ("name",)


@register(Legend)
class LegendTranslationOptions(TranslationOptions):
    fields = ("title",)


@register(LegendEntry)
class LegendEntryTranslationOptions(TranslationOptions):
    fields = ("text",)


@register(LocalizedString)
class LocalizedStringTranslationOptions(TranslationOptions):
    fields = ("text",)
