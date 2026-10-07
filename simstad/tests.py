import json
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import City, Legend, LegendEntry, LegendSymbol, Raster


class RasterBulkUploadTests(TestCase):
	def setUp(self):
		self.city = City.objects.create(key="test-city", name="Test city")
		self.user = get_user_model().objects.create_superuser(
			username="admin", email="admin@example.com", password="test-password"
		)
		self.client.force_login(self.user)
		self.url = reverse("admin:raster_bulk_upload")

	def test_notes_render_as_required_textarea(self):
		response = self.client.get(self.url)

		self.assertEqual(response.status_code, 200)
		field = response.context["form"]["notes"]
		self.assertTrue(field.field.required)
		self.assertIn("<textarea", str(field))
		self.assertIn("required", str(field))

	def test_missing_or_blank_notes_reject_upload(self):
		for notes in (None, "", "   "):
			with self.subTest(notes=notes):
				data = {
					"city": self.city.pk,
					"images": SimpleUploadedFile("first.png", b"image"),
				}
				if notes is not None:
					data["notes"] = notes
				response = self.client.post(self.url, data)

				self.assertEqual(response.status_code, 200)
				self.assertIn("notes", response.context["form"].errors)
				self.assertEqual(Raster.objects.count(), 0)

	def test_notes_apply_to_every_uploaded_raster(self):
		with TemporaryDirectory() as media_root:
			with self.settings(MEDIA_ROOT=media_root), patch.object(
				Raster, "_handle_image"
			):
				response = self.client.post(
					self.url,
					{
						"city": self.city.pk,
						"notes": "Source: City survey, 2026",
						"images": [
							SimpleUploadedFile("first.png", b"image"),
							SimpleUploadedFile("second.png", b"image"),
						],
					},
				)

		self.assertRedirects(response, reverse("admin:simstad_raster_changelist"))
		self.assertEqual(
			list(Raster.objects.values_list("notes", flat=True)),
			["Source: City survey, 2026", "Source: City survey, 2026"],
		)


class LegendJsonImportTests(TestCase):
	def setUp(self):
		user = get_user_model().objects.create_superuser(
			username="admin", email="admin@example.com", password="test-password"
		)
		self.client.force_login(user)
		self.url = reverse("admin:legend_json_import")
		self.symbol = LegendSymbol.objects.create(
			key="rectangle", image="legendsymbols/rectangle.png"
		)

	def test_import_matches_symbol_key_case_insensitively(self):
		response = self.client.post(self.url, {
			"key": "test-legend",
			"json_data": json.dumps([
				{"text": "Label 1", "color": "#FF0000", "type": "RECTANGLE"}
			]),
		})

		legend = Legend.objects.get(key="test-legend")
		self.assertEqual(legend.title_sv, "test-legend")
		self.assertEqual(legend.title_en, "test-legend")
		self.assertRedirects(
			response, reverse("admin:simstad_legend_change", args=[legend.pk])
		)
		entry = legend.entries.get()
		self.assertEqual(entry.symbol, self.symbol)
		self.assertEqual(entry.text_en, "Label 1")
		self.assertEqual(entry.text_sv, "Label 1")
		self.assertEqual(entry.color, "#FF0000")
		self.assertEqual(entry.order, 1)

	def test_failed_import_rolls_back_legend_and_previous_entries(self):
		response = self.client.post(self.url, {
			"key": "failed-legend",
			"json_data": json.dumps([
				{"text": "Label 1", "color": "#FF0000", "type": "rectangle"},
				None,
			]),
		})

		self.assertEqual(response.status_code, 200)
		self.assertIn("json_data", response.context["form"].errors)
		self.assertFalse(Legend.objects.exists())
		self.assertFalse(LegendEntry.objects.exists())

	def test_import_without_symbols_leaves_no_legend(self):
		LegendSymbol.objects.all().delete()
		response = self.client.post(self.url, {
			"key": "failed-legend",
			"json_data": json.dumps([{"text": "Label 1", "type": "rectangle"}]),
		})

		self.assertEqual(response.status_code, 200)
		self.assertIn(
			"Create a legend symbol", response.context["form"].errors["json_data"][0]
		)
		self.assertFalse(Legend.objects.exists())
