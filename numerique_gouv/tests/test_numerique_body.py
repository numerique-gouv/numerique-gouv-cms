import json

from django.contrib.auth import get_user_model
from sites_conformes.blog.models import BlogEntryPage, BlogIndexPage
from sites_conformes.core.blocks import STREAMFIELD_COMMON_BLOCKS
from sites_conformes.events.models import EventEntryPage, EventsIndexPage
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from numerique_gouv.blocks import (
    STREAMFIELD_NUMERIQUE_BLOCKS,
    CustomBlogRecentEntriesBlock,
    CustomItemGridBlock,
)
from numerique_gouv.models import (
    NumeriqueBlogEntryPage,
    NumeriqueBlogIndexPage,
    NumeriqueEventPage,
    NumeriqueEventsIndexPage,
)

User = get_user_model()

# numerique.gouv.fr extends the Sites Conformes blog and events body with its own blocks (see numerique_gouv/apps.py)
EXTENDED_PAGE_CLASSES = [BlogIndexPage, BlogEntryPage, EventsIndexPage, EventEntryPage]


class BlogBodyBlocksTestCase(WagtailPageTestCase):
    def test_body_accepts_common_and_numerique_blocks(self):
        expected = {name for name, _block in STREAMFIELD_COMMON_BLOCKS + STREAMFIELD_NUMERIQUE_BLOCKS}
        for page_class in EXTENDED_PAGE_CLASSES:
            with self.subTest(page_class=page_class.__name__):
                child_blocks = page_class._meta.get_field("body").stream_block.child_blocks
                self.assertEqual(set(child_blocks), expected)

    def test_numerique_blocks_override_common_blocks_with_same_name(self):
        for page_class in EXTENDED_PAGE_CLASSES:
            with self.subTest(page_class=page_class.__name__):
                child_blocks = page_class._meta.get_field("body").stream_block.child_blocks
                self.assertIsInstance(child_blocks["blog_recent_entries"], CustomBlogRecentEntriesBlock)
                self.assertIsInstance(child_blocks["item_grid"], CustomItemGridBlock)

    def test_package_options_are_kept(self):
        for page_class in EXTENDED_PAGE_CLASSES:
            with self.subTest(page_class=page_class.__name__):
                stream_block = page_class._meta.get_field("body").stream_block
                self.assertTrue(stream_block.meta.collapsed)

    def test_extra_blocks_are_hidden_from_migrations(self):
        expected = [name for name, _block in STREAMFIELD_COMMON_BLOCKS]
        for page_class in EXTENDED_PAGE_CLASSES:
            with self.subTest(page_class=page_class.__name__):
                _name, _path, args, _kwargs = page_class._meta.get_field("body").deconstruct()
                self.assertEqual([name for name, _block in args[0]], expected)
                # The extended block is restored after deconstruction
                child_blocks = page_class._meta.get_field("body").stream_block.child_blocks
                self.assertIn("three_cards", child_blocks)


class NumeriqueBlogPagesRenderingTestCase(WagtailPageTestCase):
    def setUp(self):
        home = Page.objects.get(slug="home")
        admin = User.objects.create_superuser("test", "test@test.test", "pass")

        # Blocks actually used on the production blog pages
        body = [
            {"type": "spacer", "value": {"marginTop": "2"}},
            {
                "type": "stylized_column",
                "value": {
                    "bg_color_class": "",
                    "border": False,
                    "center_content": False,
                    "content": [{"type": "text", "value": "<p>Colonne stylisée du blog</p>"}],
                },
            },
            {
                "type": "slider",
                "value": {
                    "title": "Carrousel du blog",
                    "title_heading_tag": "h2",
                    "title_heading_size": "h2",
                    "blocks": [{"type": "text", "value": "<p>Diapositive du blog</p>"}],
                },
            },
        ]

        self.index = home.add_child(
            instance=NumeriqueBlogIndexPage(title="Actualités", slug="actualites", owner=admin, body=json.dumps(body))
        )
        self.post = self.index.add_child(
            instance=NumeriqueBlogEntryPage(title="Article", slug="article", owner=admin, body=json.dumps(body))
        )
        self.events_index = home.add_child(
            instance=NumeriqueEventsIndexPage(
                title="Événements", slug="evenements", owner=admin, body=json.dumps(body)
            )
        )
        self.event = self.events_index.add_child(
            instance=NumeriqueEventPage(title="Événement", slug="evenement", owner=admin, body=json.dumps(body))
        )
        self.pages = [self.index, self.post, self.events_index, self.event]

    def test_pages_are_renderable(self):
        for page in self.pages:
            with self.subTest(page=page.title):
                self.assertPageIsRenderable(page)

    def test_numerique_blocks_are_rendered(self):
        for page in self.pages:
            with self.subTest(page=page.title):
                response = self.client.get(page.url)
                self.assertContains(response, "margin-top: 2rem;")
                self.assertContains(response, "Colonne stylisée du blog")
                self.assertContains(response, "Carrousel du blog")
                self.assertContains(response, "Diapositive du blog")
