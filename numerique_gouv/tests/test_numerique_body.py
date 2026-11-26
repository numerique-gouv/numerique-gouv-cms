import json

from django.contrib.auth import get_user_model
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from blog.models import BlogEntryPage, BlogIndexPage
from content_manager.blocks import STREAMFIELD_COMMON_BLOCKS
from numerique_gouv.blocks import (
    STREAMFIELD_NUMERIQUE_BLOCKS,
    CustomBlogRecentEntriesBlock,
    CustomItemGridBlock,
)
from numerique_gouv.models import NumeriqueBlogEntryPage, NumeriqueBlogIndexPage

User = get_user_model()

# numerique.gouv.fr extends the blog body with its own blocks (local customization of blog/models.py)


class BlogBodyBlocksTestCase(WagtailPageTestCase):
    def test_body_accepts_common_and_numerique_blocks(self):
        expected = {name for name, _block in STREAMFIELD_COMMON_BLOCKS + STREAMFIELD_NUMERIQUE_BLOCKS}
        for page_class in [BlogIndexPage, BlogEntryPage]:
            with self.subTest(page_class=page_class.__name__):
                child_blocks = page_class._meta.get_field("body").stream_block.child_blocks
                self.assertEqual(set(child_blocks), expected)

    def test_numerique_blocks_override_common_blocks_with_same_name(self):
        for page_class in [BlogIndexPage, BlogEntryPage]:
            with self.subTest(page_class=page_class.__name__):
                child_blocks = page_class._meta.get_field("body").stream_block.child_blocks
                self.assertIsInstance(child_blocks["blog_recent_entries"], CustomBlogRecentEntriesBlock)
                self.assertIsInstance(child_blocks["item_grid"], CustomItemGridBlock)


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

    def test_pages_are_renderable(self):
        self.assertPageIsRenderable(self.index)
        self.assertPageIsRenderable(self.post)

    def test_numerique_blocks_are_rendered(self):
        for page in [self.index, self.post]:
            with self.subTest(page=page.title):
                response = self.client.get(page.url)
                self.assertContains(response, "margin-top: 2rem;")
                self.assertContains(response, "Colonne stylisée du blog")
                self.assertContains(response, "Carrousel du blog")
                self.assertContains(response, "Diapositive du blog")
