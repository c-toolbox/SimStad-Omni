from django import forms
from .models import City, Tag


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


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


class LegendJsonImportForm(forms.Form):
    title = forms.CharField(label="Legend title", max_length=32)
    json_data = forms.CharField(
        label="Legend entries (JSON array)",
        widget=forms.Textarea(attrs={"rows": 10, "cols": 80}),
    )
