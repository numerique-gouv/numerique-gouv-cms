import json
from datetime import timedelta

from django.utils import timezone

from blog.models import Person
from numerique_gouv.blocks import CustomBlogRecentEntriesBlock
from numerique_gouv.models import NumeriqueBlogEntryPage, NumeriqueBlogIndexPage, NumeriquePage
from numerique_gouv.tests.base import NumeriqueTestCase


class CustomBlogRecentEntriesBlockTestCase(NumeriqueTestCase):
    def setUp(self):
        super().setUp()
        self.blog = self.add_page(self.home, NumeriqueBlogIndexPage, title="Actualités", slug="actualites")
        now = timezone.now()
        self.posts = []
        for i in range(4):
            post = self.add_page(
                self.blog,
                NumeriqueBlogEntryPage,
                title=f"Article {i}",
                slug=f"article-{i}",
                date=now - timedelta(days=i),
            )
            # Tag every other post
            if i % 2 == 0:
                post.page_tags.add(self.tag_ia)
                post.save()
            self.posts.append(post)

        self.block = CustomBlogRecentEntriesBlock()

    def get_value(self, **kwargs):
        return self.block.to_python({"blog": self.blog.id, **kwargs})

    def test_posts_are_ordered_by_date_desc_and_limited(self):
        value = self.get_value(entries_count=2)
        self.assertEqual(list(value.posts()), [self.posts[0], self.posts[1]])

    def test_posts_filtered_by_page_tag(self):
        value = self.get_value(entries_count=3, page_tag_filter=self.tag_ia.id)
        self.assertEqual(list(value.posts()), [self.posts[0], self.posts[2]])

    def test_current_filters_include_page_tag(self):
        value = self.get_value(page_tag_filter=self.tag_ia.id)
        self.assertEqual(value.current_filters(), {"page_tag": "ia"})

    def test_current_filters_empty_without_filters(self):
        self.assertEqual(self.get_value().current_filters(), {})

    def test_rendered_filter_link_keeps_page_tag(self):
        alice = Person.objects.create(name="Alice", role="Rédactrice", organization=self.dinum)
        bob = Person.objects.create(name="Bob", role="Rédacteur", organization=self.dinum)
        self.posts[0].authors.add(alice)
        self.posts[0].save()
        self.posts[1].authors.add(bob)
        self.posts[1].save()

        body = [
            {
                "type": "blog_recent_entries",
                "value": {
                    "blog": self.blog.id,
                    "page_tag_filter": self.tag_ia.id,
                    "author_filter": alice.id,
                    "show_filters": True,
                },
            }
        ]
        page = self.add_page(self.home, NumeriquePage, title="Filtres", slug="filtres", body=json.dumps(body))
        response = self.client.get(page.url)

        # Selecting another author keeps the page tag restriction
        self.assertContains(response, f'href="{self.blog.url}?author={bob.id}&amp;page_tag=ia"')


class NumeriqueBlocksRenderingTestCase(NumeriqueTestCase):
    def setUp(self):
        super().setUp()
        self.blog = self.add_page(self.home, NumeriqueBlogIndexPage, title="Actualités", slug="actualites")
        self.post = self.add_page(self.blog, NumeriqueBlogEntryPage, title="Article mis en avant", slug="article")

        body = [
            {"type": "spacer", "value": {"marginTop": "1.5"}},
            {
                "type": "stylized_column",
                "value": {
                    "bg_color_class": "",
                    "border": True,
                    "center_content": True,
                    "content": [{"type": "text", "value": "<p>Contenu de la colonne stylisée</p>"}],
                },
            },
            {
                "type": "slider",
                "value": {
                    "title": "Titre du carrousel",
                    "title_heading_tag": "h2",
                    "title_heading_size": "h2",
                    "blocks": [{"type": "text", "value": "<p>Diapositive</p>"}],
                },
            },
            {
                "type": "blog_recent_entries",
                "value": {"title": "Dernières actualités", "blog": self.blog.id, "entries_count": 3},
            },
        ]
        self.page = self.add_page(
            self.home, NumeriquePage, title="Page avec blocs", slug="page-avec-blocs", body=json.dumps(body)
        )

    def test_page_is_renderable(self):
        self.assertPageIsRenderable(self.page)

    def test_spacer_block(self):
        response = self.client.get(self.page.url)
        self.assertContains(response, "margin-top: 1.5rem;")

    def test_stylized_column_block(self):
        response = self.client.get(self.page.url)
        self.assertContains(response, "Contenu de la colonne stylisée")
        self.assertContains(response, "border: 1px solid var(--border-default-grey);")

    def test_slider_block(self):
        response = self.client.get(self.page.url)
        self.assertContains(response, "Titre du carrousel")
        self.assertContains(response, "Diapositive")

    def test_blog_recent_entries_block(self):
        response = self.client.get(self.page.url)
        self.assertContains(response, "Dernières actualités")
        self.assertContains(response, "Article mis en avant")
