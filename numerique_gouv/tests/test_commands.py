from io import StringIO

from django.core.management import call_command
from sites_conformes.core.models import CmsDsfrConfig
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from numerique_gouv.models import (
    HubPages,
    NumeriqueBlogEntryPage,
    NumeriquePage,
    OffersEntryPage,
    PageTag,
    ProductsEntryPage,
)


class CreateE2EPagesTestCase(WagtailPageTestCase):
    def call_command(self):
        call_command("create_e2e_pages", stdout=StringIO())

    def test_creates_renderable_pages(self):
        self.call_command()

        self.assertEqual(NumeriqueBlogEntryPage.objects.live().count(), 4)
        self.assertEqual(OffersEntryPage.objects.live().count(), 11)
        self.assertEqual(ProductsEntryPage.objects.live().count(), 3)

        for slug in [
            "actualites",
            "offre-accompagnement",
            "services-numeriques",
            "hub-intelligence-artificielle",
            "rejoignez-nous",
            "numerique-etat",
        ]:
            with self.subTest(slug=slug):
                page = Page.objects.get(slug=slug).specific
                self.assertPageIsRenderable(page)

    def test_creates_the_content_used_on_numerique_gouv(self):
        self.call_command()

        self.assertTrue(CmsDsfrConfig.objects.get().search_bar)
        self.assertGreater(OffersEntryPage.objects.live().filter(type__slug="expertise").count(), 6)

        slider = NumeriquePage.objects.get(slug="rejoignez-nous").body[0].value["content"][0]
        self.assertEqual(slider.block_type, "slider")
        self.assertEqual(len(slider.value["blocks"]), 3)

        grid = NumeriquePage.objects.get(slug="numerique-etat").body[0].value
        self.assertEqual(len(grid["items"]), 10)
        self.assertEqual(grid["numbers_items_to_display"], 4)

    def test_hub_lists_tagged_content(self):
        self.call_command()

        hub = HubPages.objects.get()
        self.assertEqual(len(hub.get_entries("blog")), 2)
        self.assertEqual(len(hub.get_entries("offers")), 2)
        self.assertEqual(len(hub.get_entries("products")), 1)

    def test_is_idempotent(self):
        self.call_command()
        page_count = Page.objects.count()

        self.call_command()

        self.assertEqual(Page.objects.count(), page_count)
        self.assertEqual(PageTag.objects.filter(slug="ia").count(), 1)
