import json
from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.utils import timezone
from .models import (
    City,
    Collection,
    CollectionScenario,
    Scenario,
    ScenarioRaster,
    Raster,
    Tag,
    Legend,
    LegendEntry,
)
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline
from .forms import BulkUploadForm, LegendJsonImportForm


# --- City --- #


@admin.register(City)
class CityAdmin(TranslationAdmin):
    list_display = [
        "key",
        "name",
        "service",
        "collection_count",
        "scenario_count",
        "raster_count",
        "created_at",
        "changed_at",
    ]
    fields = [
        "key",
        "name",
        "service",
        "min_x",
        "min_y",
        "max_x",
        "max_y",
    ]

    @admin.display(description="Collections")
    def collection_count(self, obj: City):
        return obj.collections.count()

    @admin.display(description="Scenarios")
    def scenario_count(self, obj: City):
        return obj.scenarios.count()

    @admin.display(description="Rasters")
    def raster_count(self, obj: City):
        return obj.rasters.count()


# --- Collection --- #


class CollectionScenarioInline(admin.TabularInline):
    verbose_name = "Scenario"
    verbose_name_plural = "Scenarios"
    model = CollectionScenario
    extra = 0
    fields = ["scenario"]
    sortable_field_name = "order"


@admin.register(Collection)
class CollectionAdmin(TranslationAdmin):
    inlines = [CollectionScenarioInline]
    list_filter = ["city"]
    list_display = [
        "key",
        "name",
        "city",
        "blocks_video",
        "scenario_count",
        "image_preview",
        "created_at",
        "changed_at",
    ]
    fields = [
        "key",
        "name",
        "city",
        "blocks_video",
        "image",
    ]

    def image_preview(self, obj: Collection):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return ""

    @admin.display(description="Scenarios")
    def scenario_count(self, obj: Collection):
        return obj.scenarios.count()


# --- Scenario --- #


class ScenarioRasterInline(admin.TabularInline):
    verbose_name = "Raster"
    verbose_name_plural = "Rasters"
    model = ScenarioRaster
    extra = 0
    fields = ["raster"]
    sortable_field_name = "order"


@admin.register(Scenario)
class ScenarioAdmin(TranslationAdmin):
    inlines = [ScenarioRasterInline]
    list_filter = ["city", "collections"]
    list_display = [
        "key",
        "name",
        "city",
        "collection",
        "raster_count",
        "legend_type",
        "created_at",
        "changed_at",
    ]
    fields = [
        "key",
        "name",
        "description",
        "city",
        "legend",
        "legend_image",
    ]

    @admin.display(description="Collection")
    def collection(self, obj: Scenario):
        return obj.collections.first()

    @admin.display(description="Rasters")
    def raster_count(self, obj: Scenario):
        return obj.rasters.count()

    @admin.display(description="Legend")
    def legend_type(self, obj: Scenario):
        if obj.legend:
            return obj.legend
        elif obj.legend_image:
            return obj.legend_image
        else:
            return None


# --- Raster --- #


@admin.register(Raster)
class RasterAdmin(TranslationAdmin):
    change_list_template = "admin/raster_change_list.html"
    list_filter = ["city", "scenarios", "tags"]
    list_display = [
        "key",
        "name",
        "city",
        "scenario",
        "tag_list",
        "image_preview",
        "created_at",
        "changed_at",
    ]
    fields = [
        "key",
        "name",
        "city",
        "tags",
        "image",
        "minimap",
        "thumbnail",
        "image_preview",
    ]
    readonly_fields = [
        "minimap",
        "thumbnail",
        "image_preview",
    ]

    @admin.display(description="Scenario")
    def scenario(self, obj: Raster):
        return ", ".join([scenario.name for scenario in obj.scenarios.all()])

    @admin.display(description="Tags")
    def tag_list(self, obj: Raster):
        return ", ".join([tag.name for tag in obj.tags.all()])

    @admin.display(description="Image")
    def image_preview(self, obj: Raster):
        if obj.image and obj.thumbnail:
            return format_html(
                '<img src="{}" height="64" />',
                obj.thumbnail.url,
            )
        return ""

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "bulk_upload",
                self.admin_site.admin_view(self.bulk_upload_view),
                name="raster_bulk_upload",
            ),
        ]
        return custom_urls + urls

    def bulk_upload_view(self, request):
        if request.method == "POST":
            form = BulkUploadForm(request.POST, request.FILES)
            if form.is_valid():
                city = form.cleaned_data["city"]
                tags = form.cleaned_data["tags"]
                images = request.FILES.getlist("images")

                for image in images:
                    # Find a unique key for the raster
                    base_name = image.name.rsplit(".", 1)[0]  # Use the image filename as base
                    key = base_name[:64]
                    counter = 1
                    while Raster.objects.filter(key=key).exists():
                        key = f"{base_name}_{counter}"
                        counter += 1

                    raster = Raster(
                        key=key,
                        name_en=base_name.replace("_", " ").title(),
                        name_sv=base_name.replace("_", " ").title(),
                        city=city,
                        image=image,
                        created_at=timezone.now(),
                        changed_at=timezone.now(),
                    )
                    raster.save()
                    raster.tags.set(tags)

                self.message_user(
                    request, f"Successfully uploaded {len(images)} images."
                )
                return redirect(reverse("admin:simstad_raster_changelist"))

        else:
            form = BulkUploadForm()

        context = dict(
            self.admin_site.each_context(request),
            title="Bulk upload rasters",
            form=form,
        )
        return render(request, "admin/bulk_upload.html", context)


# --- Tag --- #


@admin.register(Tag)
class TagAdmin(TranslationAdmin):
    list_display = [
        "name",
        "raster_count",
        "created_at",
        "changed_at",
    ]
    fields = ["name"]

    @admin.display(description="Rasters")
    def raster_count(self, obj: Tag):
        return Raster.objects.filter(tags=obj).count()


# --- Legend --- #


class LegendEntryInline(TranslationTabularInline):
    model = LegendEntry
    extra = 0
    fields = ["text", "color", "type"]


@admin.register(Legend)
class LegendAdmin(TranslationAdmin):
    change_list_template = "admin/legend_change_list.html"
    inlines = [LegendEntryInline]
    list_display = [
        "title",
        "scenarios",
        "colors",
        "created_at",
        "changed_at",
    ]
    fields = [
        "title",
    ]

    @admin.display(description="Scenarios")
    def scenarios(self, obj: Legend):
        return ", ".join([scenario.name for scenario in obj.scenario_set.all()])

    @admin.display(description="Colors")
    def colors(self, obj: Legend):
        html = ""
        for entry in obj.entries.all():
            html += f'<div style="display:inline-block;width:16px;height:16px;margin:1px;background-color:{entry.color};"></div>'
        return format_html(html)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import_json",
                self.admin_site.admin_view(self.import_json_view),
                name="legend_json_import",
            ),
        ]
        return custom_urls + urls

    def import_json_view(self, request):
        if request.method == "POST":
            form = LegendJsonImportForm(request.POST)
            if form.is_valid():
                title = form.cleaned_data["title"]
                json_data = form.cleaned_data["json_data"]
                try:
                    entries = json.loads(json_data)
                    legend = Legend.objects.create(title_en=title, title_sv=title)
                    for idx, entry in enumerate(entries):
                        LegendEntry.objects.create(
                            legend=legend,
                            text_en=entry.get("text", ""),
                            text_sv=entry.get("text", ""),
                            color=entry.get("color", "#FFFFFF"),
                            type=entry.get("type", "rect"),
                            order=idx,
                        )
                    self.message_user(
                        request,
                        f"Legend '{title}' imported with {len(entries)} entries.",
                    )
                    return redirect(
                        reverse("admin:simstad_legend_change", args=[legend.id])
                    )
                except Exception as e:
                    form.add_error(
                        "json_data", f"Invalid JSON or error creating entries: {e}"
                    )
        else:
            form = LegendJsonImportForm()

        context = dict(
            self.admin_site.each_context(request),
            title="Import Legend from JSON",
            form=form,
        )
        return render(request, "admin/legend_json_import.html", context)
