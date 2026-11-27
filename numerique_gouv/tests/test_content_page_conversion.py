import json

from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.test import TestCase
from django.urls import reverse
from sites_conformes.core.models import ContentPage
from wagtail.models import Page, PageLogEntry, get_page_models

from numerique_gouv.content_page_conversion import (
    LEGACY_APP_LABEL,
    LEGACY_MODEL,
    LEGACY_TABLE,
    LEGACY_TAG_TABLE,
    convert_content_pages,
)
from numerique_gouv.models import NumeriqueBasePage, NumeriquePage
from numerique_gouv.tests.base import NumeriqueTestCase


def make_legacy_content_pages(page_ids: list[int]) -> ContentType:
    """
    Turn NumeriquePage pages back into legacy ContentPage pages, as found in the production database.

    ContentPage is swapped for NumeriquePage, so its table is not created by the migrations and the model
    cannot be instantiated: the legacy tables and rows are built with raw SQL. Returns the legacy content type.
    """
    old_ct, _created = ContentType.objects.get_or_create(app_label=LEGACY_APP_LABEL, model=LEGACY_MODEL)
    new_ct = ContentType.objects.get_for_model(NumeriquePage)
    str_ids = [str(page_id) for page_id in page_ids]
    base_table = NumeriqueBasePage._meta.db_table

    with connection.cursor() as cursor:
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {LEGACY_TABLE} (LIKE {base_table} INCLUDING DEFAULTS)")
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {LEGACY_TAG_TABLE} "
            "(id serial PRIMARY KEY, content_object_id integer NOT NULL, tag_id integer NOT NULL)"
        )
        cursor.execute(
            f"INSERT INTO {LEGACY_TABLE} SELECT * FROM {base_table} WHERE page_ptr_id = ANY(%s)", [page_ids]
        )
        cursor.execute(
            f"DELETE FROM {NumeriquePage._meta.db_table} WHERE numeriquebasepage_ptr_id = ANY(%s)", [page_ids]
        )
        cursor.execute(f"DELETE FROM {base_table} WHERE page_ptr_id = ANY(%s)", [page_ids])

        cursor.execute("UPDATE wagtailcore_page SET content_type_id = %s WHERE id = ANY(%s)", [old_ct.id, page_ids])
        cursor.execute(
            "UPDATE wagtailcore_revision "
            "SET content_type_id = %s, content = jsonb_set(content, '{content_type}', to_jsonb(%s)) "
            "WHERE content_type_id = %s AND object_id = ANY(%s)",
            [old_ct.id, old_ct.id, new_ct.id, str_ids],
        )
        cursor.execute(
            "UPDATE wagtailcore_pagelogentry SET content_type_id = %s "
            "WHERE content_type_id = %s AND page_id = ANY(%s)",
            [old_ct.id, new_ct.id, page_ids],
        )
        cursor.execute(
            "UPDATE wagtailsearch_indexentry SET content_type_id = %s "
            "WHERE content_type_id = %s AND object_id = ANY(%s)",
            [old_ct.id, new_ct.id, str_ids],
        )
    return old_ct


class ContentPageConversionTestCase(NumeriqueTestCase):
    def setUp(self):
        super().setUp()
        body = [{"type": "paragraph", "value": "<p>Éditeur du site : la DINUM</p>"}]

        # The search index is updated by a task enqueued on transaction commit
        with self.captureOnCommitCallbacks(execute=True):
            self.legal = self.home.add_child(
                instance=NumeriquePage(
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
                instance=NumeriquePage(title="Sous-page", slug="sous-page", owner=self.admin)
            )

        self.old_ct = make_legacy_content_pages([self.legal.id, self.child.id])
        self.new_ct = ContentType.objects.get_for_model(NumeriquePage)

    def convert(self):
        with self.captureOnCommitCallbacks(execute=True):
            return convert_content_pages(apps)

    def legacy_row_count(self, table: str) -> int:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            return cursor.fetchone()[0]

    def test_pages_become_numerique_pages(self):
        converted = self.convert()

        self.assertCountEqual(converted, [self.legal.id, self.child.id])
        self.assertEqual(self.legacy_row_count(LEGACY_TABLE), 0)

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

    def test_legacy_tag_links_are_dropped(self):
        with connection.cursor() as cursor:
            # The legacy tag table has no foreign key here: any tag id will do
            cursor.execute(
                f"INSERT INTO {LEGACY_TAG_TABLE} (content_object_id, tag_id) VALUES (%s, 1)", [self.legal.id]
            )
        with self.assertLogs("numerique_gouv.content_page_conversion", level="WARNING"):
            self.convert()
        self.assertEqual(self.legacy_row_count(LEGACY_TAG_TABLE), 0)

    def test_is_idempotent(self):
        self.convert()
        self.assertEqual(self.convert(), [])
        self.assertEqual(NumeriquePage.objects.filter(id__in=[self.legal.id, self.child.id]).count(), 2)


class ContentPageConversionWithoutLegacyTableTestCase(TestCase):
    def test_does_nothing_without_legacy_table(self):
        self.assertNotIn(LEGACY_TABLE, connection.introspection.table_names())
        self.assertEqual(convert_content_pages(apps), [])


class ContentPageSwapTestCase(TestCase):
    def test_content_page_is_swapped_for_numerique_page(self):
        self.assertEqual(ContentPage._meta.swapped, "numerique_gouv.NumeriquePage")
        self.assertNotIn(ContentPage, get_page_models())
