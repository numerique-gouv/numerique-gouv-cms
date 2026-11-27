from django.contrib.auth import get_user_model
from sites_conformes.core.models import CmsDsfrConfig
from sites_conformes.forms.models import FormField, FormPage
from wagtail.models import Page
from wagtail.test.utils import WagtailPageTestCase

from numerique_gouv.models import NumeriquePage

User = get_user_model()

# templates/base.html and templates/blocks/header.html are customized for numerique.gouv.fr

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

    def test_site_stylesheet_is_loaded_on_every_page_type(self):
        # ContentPage is swapped for NumeriquePage (SF_CONTENTPAGE_MODEL)
        for page in [self.numerique_page, self.form_page]:
            with self.subTest(page=page.title):
                response = self.client.get(page.url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, NUMERIQUE_CSS)

    def test_header_search_form(self):
        response = self.client.get(self.numerique_page.url)
        self.assertContains(response, 'role="search"')
        self.assertContains(response, '<label class="fr-label" for="search-bar-input">', html=False)
        self.assertContains(response, 'id="search-bar-input"')
        self.assertContains(response, 'name="q"')

    def test_header_has_no_login_button(self):
        response = self.client.get(self.numerique_page.url)
        self.assertNotContains(response, "/admin/login/")
