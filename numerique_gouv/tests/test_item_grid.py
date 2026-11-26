import json

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from numerique_gouv.models import NumeriquePage

User = get_user_model()

# content_manager/blocks/item_grid.html is customized for numerique.gouv.fr ("Voir plus" button)


def item_grid(items_count, numbers_items_to_display=99, horizontal_align="left", vertical_align="middle"):
    return {
        "type": "item_grid",
        "value": {
            "column_width": "4",
            "horizontal_align": horizontal_align,
            "vertical_align": vertical_align,
            "numbers_items_to_display": numbers_items_to_display,
            "items": [{"type": "text", "value": f"<p>Élément {i}</p>"} for i in range(1, items_count + 1)],
        },
    }


class ItemGridTestCase(WagtailPageTestCase):
    def setUp(self):
        self.home = Page.objects.get(slug="home")
        self.admin = User.objects.create_superuser("test", "test@test.test", "pass")

    def get_response(self, *grids):
        page = self.home.add_child(
            instance=NumeriquePage(title="Grille", slug="grille", owner=self.admin, body=json.dumps(list(grids)))
        )
        response = self.client.get(page.url)
        self.assertEqual(response.status_code, 200)
        return response

    def test_alignment_classes(self):
        response = self.get_response(item_grid(3, horizontal_align="center", vertical_align="middle"))
        self.assertContains(response, "fr-grid-row--center")
        self.assertContains(response, "fr-grid-row--middle")

    def test_all_items_visible_without_show_more_button(self):
        response = self.get_response(item_grid(3))
        for i in range(1, 4):
            self.assertContains(response, f"Élément {i}")
        self.assertNotContains(response, "show-more-btn-")
        self.assertNotContains(response, "item-grid-element hidden")

    def test_items_beyond_limit_are_hidden_behind_show_more_button(self):
        response = self.get_response(item_grid(5, numbers_items_to_display=2))
        soup = BeautifulSoup(response.content, "html.parser")

        # Items 1 and 2 are visible, items 3 to 5 are rendered but hidden
        hidden_by_item = {int(el["data-item"]): "hidden" in el["class"] for el in soup.select(".item-grid-element")}
        self.assertEqual(hidden_by_item, {1: False, 2: False, 3: True, 4: True, 5: True})
        self.assertContains(response, "Élément 5")
        self.assertContains(response, "show-more-btn-", count=2)  # button id + script

    def test_no_button_when_items_count_equals_limit(self):
        response = self.get_response(item_grid(4, numbers_items_to_display=4))
        self.assertNotContains(response, "show-more-btn-")
