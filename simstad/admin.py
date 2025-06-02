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
from .forms import BulkUploadForm

# Return the installed apps in the order the user has registred them
def get_app_list(self, request, app_label=None):
    app_dict = self._build_app_dict(request, app_label)
    app_list = app_dict.values()
    return app_list

admin.AdminSite.get_app_list = get_app_list

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "key",
        "service",
        "collection_count",
        "scenario_count",
        "raster_count",
        "created_at",
        "changed_at",
    ]
    fields = [
        "name",
        "key",
        "service",
    ]

    @admin.display(description="Collections")
    def collection_count(self, obj: City):
        return obj.collection_set.count()

    @admin.display(description="Scenarios")
    def scenario_count(self, obj: City):
        return obj.scenario_set.count()

    @admin.display(description="Rasters")
    def raster_count(self, obj: City):
        return obj.raster_set.count()

class CollectionScenarioInline(admin.TabularInline):
    verbose_name = "Scenario"
    verbose_name_plural = "Scenarios"
    model = CollectionScenario
    extra = 0
    fields = ["scenario"]
    sortable_field_name = "order"

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    inlines = [CollectionScenarioInline]
    list_filter = ["city"]
    list_display = [
        "name",
        "key",
        "city",
        "blocks_video",
        "scenario_count",
        "image_preview",
        "created_at",
        "changed_at",
    ]
    fields = [
        "name",
        "key",
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

class ScenarioRasterInline(admin.TabularInline):
    verbose_name = "Raster"
    verbose_name_plural = "Rasters"
    model = ScenarioRaster
    extra = 0
    fields = ["raster"]
    sortable_field_name = "order"

@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    inlines = [ScenarioRasterInline]
    list_filter = ["city", "collections"]
    list_display = [
        "name",
        "key",
        "city",
        "collection",
        "legend_type",
        "created_at",
        "changed_at",
    ]
    fields = [
        "name",
        "key",
        "description",
        "city",
        "legend",
        "legend_image",
    ]

    @admin.display(description="Collection")
    def collection(self, obj: Scenario):
        return obj.collections.first()

    @admin.display(description="Legend")
    def legend_type(self, obj: Scenario):
        if obj.legend:
            return obj.legend
        elif obj.legend_image:
            return obj.legend_image
        else:
            return "uh oh"

@admin.register(Raster)
class RasterAdmin(admin.ModelAdmin):
    change_list_template = "admin/raster_change_list.html"
    list_filter = ["city", "scenarios", "tags"]
    list_display = [
        "name",
        "key",
        "city",
        "scenario",
        "tag_list",
        "image_preview",
        "created_at",
        "changed_at",
    ]
    fields = [
        "name",
        "key",
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
                    name = image.name.rsplit(".", 1)[0]  # Use the filename as the name
                    raster = Raster(
                        key=name,
                        name=name,
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
                return redirect(reverse("admin:communication_raster_changelist"))

        else:
            form = BulkUploadForm()

        context = dict(
            self.admin_site.each_context(request),
            title="Bulk upload rasters",
            form=form,
        )
        return render(request, "admin/bulk_upload.html", context)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
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

class LegendEntryInline(admin.TabularInline):
    model = LegendEntry
    extra = 0
    fields = ["text", "color", "type"]

@admin.register(Legend)
class LegendAdmin(admin.ModelAdmin):
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
