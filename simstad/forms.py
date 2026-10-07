from django import forms
from django.core.exceptions import ValidationError
from .models import City, Tag


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs.update({"accept": ".png,.jpg,.jpeg"})  # client-side filter
        super().__init__(attrs)


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean

        if isinstance(data, (list, tuple)):
            result = [self._validate_file(single_file_clean(d, initial)) for d in data]
        else:
            result = self._validate_file(single_file_clean(data, initial))
        return result

    def _validate_file(self, file):
        valid_extensions = ["png", "jpg", "jpeg"]
        if file:
            ext = file.name.split(".")[-1].lower()
            if ext not in valid_extensions:
                raise ValidationError(
                    f"Unsupported file type: {ext}. Allowed types: PNG, JPG, JPEG."
                )
        return file


class BulkUploadForm(forms.Form):
    images = MultipleFileField(
        required=True,
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
    )
    notes = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Describe the rasters. What do they represent? What is the source?",
    )


class LegendJsonImportForm(forms.Form):
    key = forms.CharField(label="Legend key", max_length=64)
    json_data = forms.CharField(
        label="Legend entries (JSON array)",
        widget=forms.Textarea(attrs={"rows": 10, "cols": 80}),
    )
