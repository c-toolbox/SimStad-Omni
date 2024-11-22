from django.contrib import admin
from django.utils.html import format_html
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.utils import timezone
from adminsortable.admin import NonSortableParentAdmin, SortableStackedInline
from .models import (
    Service,
    City,
    Collection,
    CollectionScenario,
    Scenario,
    ScenarioRaster,
    Raster,
    Tag,
)
from .forms import BulkUploadForm


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "allow_public_code",
        "allow_multiple_hosts",
        "created_on",
    ]
    fields = [
        "title",
        "host_token",
        "client_token",
        "allow_public_code",
        "allow_multiple_hosts",
        "public_code",
    ]
    readonly_fields = [
        "created_on",
        "host_token",
        "client_token",
        "public_code",
    ]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "key",
        "service",
        "collection_count",
        "scenario_count",
        "raster_count",
        "create_time",
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


class CollectionScenarioInline(SortableStackedInline):
    verbose_name = "Scenario"
    verbose_name_plural = "Scenarios"
    model = CollectionScenario
    extra = 0
    fields = ["scenario"]


@admin.register(Collection)
class CollectionAdmin(NonSortableParentAdmin):
    inlines = [CollectionScenarioInline]
    list_filter = ["city"]
    list_display = [
        "name",
        "key",
        "city",
        "blocks_video",
        "scenario_count",
        "image_preview",
        "create_time",
    ]
    fields = [
        "name",
        "key",
        "city",
        "blocks_video",
        "image",
        "create_time",
    ]
    readonly_fields = [
        "create_time",
    ]

    def image_preview(self, obj: Collection):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return ""
    
    @admin.display(description="Scenarios")
    def scenario_count(self, obj: Collection):
        return obj.scenarios.count()


class ScenarioRasterInline(SortableStackedInline):
    verbose_name = "Raster"
    verbose_name_plural = "Rasters"
    model = ScenarioRaster
    extra = 0
    fields = ["raster"]


@admin.register(Scenario)
class ScenarioAdmin(NonSortableParentAdmin):
    inlines = [ScenarioRasterInline]
    list_filter = ["city", "collections"]
    list_display = [
        "name",
        "key",
        "city",
        "collection",
        "legend_title",
        "create_time",
    ]
    fields = [
        "name",
        "key",
        "description",
        "city",
        "legend_title",
        "legend_colors",
    ]

    @admin.display(description="Collection")
    def collection(self, obj: Scenario):
        return obj.collections.first()


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
        "create_time",
        "change_time",
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

    @admin.display(description="Image preview")
    def image_preview(self, obj: Raster):
        if obj.image and obj.minimap:
            return format_html(
                '<img src="{}" height="64" />',
                obj.minimap.url,
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
                        create_time=timezone.now(),
                        change_time=timezone.now(),
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
    list_display = ["name"]
    fields = ["name"]


# Return the installed apps in the order the user has registred them
def get_app_list(self, request, app_label=None):
    app_dict = self._build_app_dict(request, app_label)
    app_list = app_dict.values()

    return app_list


admin.AdminSite.get_app_list = get_app_list

