import json

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from wagtail.models import Page, PageLogEntry
from wagtail.test.utils import WagtailPageTestCase

from content_manager.models import ContentPage
from numerique_gouv.content_page_conversion import convert_content_pages
from numerique_gouv.models import NumeriquePage
from numerique_gouv.tests.base import NumeriqueTestCase


class ContentPageConversionTestCase(NumeriqueTestCase):
    def setUp(self):
        super().setUp()
        body = [{"type": "paragraph", "value": "<p>Éditeur du site : la DINUM</p>"}]

        # The search index is updated by a task enqueued on transaction commit
        with self.captureOnCommitCallbacks(execute=True):
            self.legal = self.home.add_child(
                instance=ContentPage(
                    title="Mentions légales",
                    slug="mentions-legales",
                    owner=self.admin,
                    body=json.dumps(body),
                    header_large=True,
                    header_with_title=True,
                )
            )
            self.legal.save_revision(user=self.admin).publish(user=self.admin)
            self.child = self.legal.add_child(
                instance=ContentPage(title="Sous-page", slug="sous-page", owner=self.admin)
            )

        self.old_ct = ContentType.objects.get_for_model(ContentPage)
        self.new_ct = ContentType.objects.get_for_model(NumeriquePage)

    def convert(self):
        with self.captureOnCommitCallbacks(execute=True):
            return convert_content_pages(apps)

    def test_pages_become_numerique_pages(self):
        converted = self.convert()

        self.assertCountEqual(converted, [self.legal.id, self.child.id])
        self.assertEqual(ContentPage.objects.count(), 0)

        legal = Page.objects.get(id=self.legal.id).specific
        self.assertIsInstance(legal, NumeriquePage)
        self.assertEqual(legal.title, "Mentions légales")
        self.assertEqual(legal.url, self.legal.url)
        self.assertTrue(legal.header_large)
        self.assertTrue(legal.header_with_title)
        self.assertEqual(legal.body[0].block_type, "paragraph")
        self.assertIsInstance(Page.objects.get(id=self.child.id).specific, NumeriquePage)

    def test_converted_page_is_renderable(self):
        self.convert()
        legal = NumeriquePage.objects.get(id=self.legal.id)
        self.assertPageIsRenderable(legal)
        response = self.client.get(legal.url)
        self.assertContains(response, "Éditeur du site : la DINUM")

    def test_revisions_and_history_follow_the_new_type(self):
        self.convert()
        legal = NumeriquePage.objects.get(id=self.legal.id)

        self.assertIsInstance(legal.latest_revision.as_object(), NumeriquePage)
        self.assertEqual(legal.latest_revision.content["content_type"], self.new_ct.id)
        self.assertFalse(PageLogEntry.objects.filter(page_id=legal.id, content_type=self.old_ct).exists())
        self.assertTrue(PageLogEntry.objects.filter(page_id=legal.id, content_type=self.new_ct).exists())

    def test_converted_page_is_found_by_search(self):
        self.convert()
        response = self.client.get(reverse("cms_search"), {"q": "mentions"})
        self.assertIn(self.legal.id, [page.id for page in response.context["object_list"]])

    def test_is_idempotent(self):
        self.convert()
        self.assertEqual(self.convert(), [])
        self.assertEqual(NumeriquePage.objects.filter(id__in=[self.legal.id, self.child.id]).count(), 2)


class ContentPageCreationTestCase(WagtailPageTestCase):
    def test_content_page_cannot_be_created_in_the_admin(self):
        self.assertFalse(ContentPage.is_creatable)
        for parent in [Page.objects.get(slug="home"), Page.get_first_root_node()]:
            with self.subTest(parent=parent.title):
                self.assertFalse(ContentPage.can_create_at(parent.specific))
