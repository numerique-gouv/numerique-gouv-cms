import json

from django.apps import apps
from django.test import SimpleTestCase
from wagtail.images import get_image_model
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Revision

from numerique_gouv.models import NumeriquePage
from numerique_gouv.services.legacy_blocks_cleanup import clean_all, clean_legacy_blocks
from numerique_gouv.tests.base import NumeriqueTestCase


def legacy_image(alt="Une description", image=3):
    return {
        "type": "image",
        "id": "img-1",
        "value": {"alt": alt, "url": "", "image": image, "title": "", "caption": ""},
    }


def legacy_text_cta():
    return {
        "type": "text_cta",
        "id": "cta-1",
        "value": {
            "text": "<p>Texte</p>",
            "cta_label": "Ancien libellé",
            "cta_url": "https://example.com/",
            "cta_buttons": [],
        },
    }


class CleanLegacyBlocksTestCase(SimpleTestCase):
    def test_image_alt_is_moved_into_the_image_block(self):
        data = [legacy_image()]

        self.assertTrue(clean_legacy_blocks(data))
        self.assertNotIn("alt", data[0]["value"])
        self.assertEqual(data[0]["value"]["image"], {"image": 3, "decorative": False, "alt_text": "Une description"})

    def test_empty_image_alt_becomes_decorative(self):
        data = [legacy_image(alt="")]

        clean_legacy_blocks(data)

        self.assertEqual(data[0]["value"]["image"], {"image": 3, "decorative": True, "alt_text": ""})

    def test_image_alt_does_not_override_an_existing_alt_text(self):
        data = [legacy_image(image={"image": 3, "decorative": False, "alt_text": "Existant"})]

        self.assertTrue(clean_legacy_blocks(data))
        self.assertEqual(data[0]["value"]["image"]["alt_text"], "Existant")

    def test_nested_image_is_cleaned(self):
        data = [{"type": "fullwidthbackground", "id": "bg", "value": {"content": [legacy_image()]}}]

        self.assertTrue(clean_legacy_blocks(data))
        self.assertNotIn("alt", data[0]["value"]["content"][0]["value"])

    def test_obsolete_cta_fields_are_removed(self):
        data = [legacy_text_cta()]

        self.assertTrue(clean_legacy_blocks(data))
        self.assertEqual(set(data[0]["value"]), {"text", "cta_buttons"})

    def test_obsolete_cta_fields_can_be_kept(self):
        data = [legacy_text_cta()]

        self.assertFalse(clean_legacy_blocks(data, clean_cta=False))
        self.assertIn("cta_label", data[0]["value"])

    def test_current_values_are_untouched(self):
        data = [
            {"type": "image", "id": "img", "value": {"image": {"image": 3, "decorative": True, "alt_text": ""}}},
            {"type": "paragraph", "id": "p", "value": "<p>alt</p>"},
        ]
        expected = json.loads(json.dumps(data))

        self.assertFalse(clean_legacy_blocks(data))
        self.assertEqual(data, expected)


class CleanAllTestCase(NumeriqueTestCase):
    def setUp(self):
        super().setUp()
        # The image must exist: Wagtail empties an ImageBlock whose image is missing when saving it
        self.image = get_image_model().objects.create(title="Image", file=get_test_image_file())
        self.page = self.add_page(self.home, NumeriquePage, title="Page", slug="page")
        self.old_revision = self.page.save_revision()
        self.latest_revision = self.page.save_revision()

        legacy_body = [legacy_image(image=self.image.pk), legacy_text_cta()]
        NumeriquePage.objects.filter(pk=self.page.pk).update(body=legacy_body)
        for revision in [self.old_revision, self.latest_revision]:
            content = dict(revision.content, body=json.dumps(legacy_body))
            Revision.objects.filter(pk=revision.pk).update(content=content)

    def get_live_body(self):
        return list(NumeriquePage.objects.get(pk=self.page.pk).body.raw_data)

    def get_revision_body(self, revision):
        return json.loads(Revision.objects.get(pk=revision.pk).content["body"])

    def test_legacy_values_are_stored_before_cleanup(self):
        self.assertIn("alt", self.get_live_body()[0]["value"])
        self.assertIn("cta_label", self.get_live_body()[1]["value"])

    def test_live_content_is_cleaned(self):
        clean_all(apps)

        body = self.get_live_body()
        self.assertEqual(body[0]["value"]["image"]["alt_text"], "Une description")
        self.assertNotIn("alt", body[0]["value"])
        self.assertNotIn("cta_label", body[1]["value"])

    def test_latest_revision_is_fully_cleaned(self):
        clean_all(apps)

        body = self.get_revision_body(self.latest_revision)
        self.assertEqual(body[0]["value"]["image"]["alt_text"], "Une description")
        self.assertNotIn("cta_label", body[1]["value"])

    def test_old_revisions_only_get_the_image_alt_moved(self):
        clean_all(apps)

        body = self.get_revision_body(self.old_revision)
        self.assertEqual(body[0]["value"]["image"]["alt_text"], "Une description")
        self.assertIn("cta_label", body[1]["value"])

    def test_cleaned_page_keeps_the_alt_when_saved_from_the_editor(self):
        clean_all(apps)

        page = NumeriquePage.objects.get(pk=self.page.pk).get_latest_revision_as_object()
        page.save_revision().publish()

        body = self.get_live_body()
        self.assertEqual(body[0]["value"]["image"]["alt_text"], "Une description")
