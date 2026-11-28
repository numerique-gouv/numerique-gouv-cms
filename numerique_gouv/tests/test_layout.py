import unittest

from django.contrib.auth import get_user_model
from sites_conformes.core.models import CmsDsfrConfig
from sites_conformes.forms.models import FormField, FormPage
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from numerique_gouv.models import NumeriquePage

User = get_user_model()

# templates/sites_conformes_core/ overrides the Sites Conformes standalone.html and blocks/header.html

NUMERIQUE_CSS = "/static/css/numerique_gouv.css"


class LayoutTestCase(WagtailPageTestCase):
    def setUp(self):
        home = Page.objects.get(slug="home")
        admin = User.objects.create_superuser("test", "test@test.test", "pass")

        self.numerique_page = home.add_child(
            instance=NumeriquePage(title="Page numérique", slug="page-numerique", owner=admin)
        )
        self.form_page = home.add_child(
            instance=FormPage(title="Contact", slug="contact", owner=admin, thank_you_text="Merci")
        )
        FormField.objects.create(page=self.form_page, label="Message", field_type="multiline")

        CmsDsfrConfig.objects.update_or_create(site_id=1, defaults={"search_bar": True})

    def test_site_stylesheet_is_loaded(self):
        # ContentPage is swapped for NumeriquePage (SF_CONTENTPAGE_MODEL)
        response = self.client.get(self.numerique_page.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, NUMERIQUE_CSS)

    # The Sites Conformes form page overrides extra_css without {{ block.super }}.
    # Remove this decorator once the Sites Conformes release adding it is installed.
    @unittest.expectedFailure
    def test_site_stylesheet_is_loaded_on_form_page(self):
        response = self.client.get(self.form_page.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, NUMERIQUE_CSS)

    def test_header_search_form(self):
        response = self.client.get(self.numerique_page.url)
        self.assertContains(response, 'role="search"')
        self.assertContains(response, '<label class="fr-label" for="query">', html=False)
        self.assertContains(response, 'id="query"')
        self.assertContains(response, 'name="q"')

    def test_header_has_no_login_button(self):
        response = self.client.get(self.numerique_page.url)
        self.assertNotContains(response, "/admin/login/")
