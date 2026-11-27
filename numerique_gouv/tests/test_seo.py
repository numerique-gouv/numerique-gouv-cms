from io import StringIO

from django.core.management import call_command
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from numerique_gouv.models import ProductsEntryPage

SEARCH_DESCRIPTION = "Description pour les moteurs de recherche"


class SeoMetaTagsTestCase(WagtailPageTestCase):
    """The page templates extend the Sites Conformes ones, which provide the SEO and social media meta tags."""

    def setUp(self):
        call_command("create_e2e_pages", stdout=StringIO())
        Page.objects.filter(depth__gt=2).update(search_description=SEARCH_DESCRIPTION)

    def test_every_page_type_renders_seo_meta_tags(self):
        pages = Page.objects.live().filter(depth__gt=2).exclude(content_type__model="productsentrypage").specific()
        page_types = {}
        for page in pages:
            page_types.setdefault(type(page), page)

        # Product entry pages redirect to their parent
        self.assertNotIn(ProductsEntryPage, page_types)
        self.assertGreaterEqual(len(page_types), 6)

        for page_type, page in page_types.items():
            with self.subTest(page_type=page_type.__name__):
                response = self.client.get(page.url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, f'<meta name="description" content="{SEARCH_DESCRIPTION}" />', html=True)
                self.assertContains(
                    response, f'<meta property="og:title" content="{page.seo_title or page.title}" />', html=True
                )
                self.assertContains(response, "twitter:card")
