from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from wagtail.models import Page
from wagtail.rich_text import RichText
from wagtail.test.utils import WagtailPageTestCase
from wagtailmenus.models.menuitems import FlatMenuItem, MainMenuItem
from wagtailmenus.models.menus import FlatMenu, MainMenu

from content_manager.models import CatalogIndexPage, CmsDsfrConfig, ContentPage, MegaMenu, MegaMenuCategory
from content_manager.services.accessors import get_or_create_content_page
from content_manager.utils import get_default_site

User = get_user_model()


class ContentPageTestCase(WagtailPageTestCase):
    def setUp(self):
        home_page = Page.objects.get(slug="home")
        self.admin = User.objects.create_superuser("test", "test@test.test", "pass")
        self.admin.save()
        self.public_content_page = home_page.add_child(
            instance=ContentPage(
                title="Page de contenu publique",
                slug="public-content-page",
                owner=self.admin,
            )
        )
        self.public_content_page.save()
        self.private_content_page = get_or_create_content_page(
            "private-content-page",
            title="Page de contenu privée",
            body=[("subpageslist", None)],
            parent_page=home_page,
            restriction_type="login",
        )
        self.private_content_page.save()

    def test_content_page_is_renderable(self):
        self.assertPageIsRenderable(self.public_content_page)

    def test_content_page_has_minimal_content(self):
        response = self.client.get(self.public_content_page.url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(
            response,
            "<title>Page de contenu publique — Titre du site</title>",
        )

    def test_public_content_page_is_in_the_site_map(self):
        url = reverse("readable_sitemap")
        response = self.client.get(url)

        self.assertContains(
            response,
            """<a href="/public-content-page/">Page de contenu publique</a>""",
        )

    def test_private_content_page_is_not_rendered_when_logged_out(self):
        response = self.client.get(self.private_content_page.url)
        self.assertEqual(response.status_code, 302)

    def test_private_content_page_is_not_in_the_site_map_when_logged_out(self):
        url = reverse("readable_sitemap")
        response = self.client.get(url)

        self.assertNotContains(
            response,
            """<a href="/private-content-page/">Page de contenu privée</a>""",
        )

    def test_private_content_page_is_in_the_site_map_when_logged_in(self):
        self.client.login(username="test", password="pass")
        url = reverse("readable_sitemap")
        response = self.client.get(url)

        self.assertContains(
            response,
            """<a href="/private-content-page/">Page de contenu privée</a>""",
        )


class ConfigTestCase(WagtailPageTestCase):
    def setUp(self):
        home = Page.objects.get(slug="home")
        self.admin = User.objects.create_superuser("test", "test@test.test", "pass")
        self.admin.save()
        self.content_page = home.add_child(
            instance=ContentPage(
                title="Page de contenu",
                slug="content-page",
                owner=self.admin,
            )
        )
        self.content_page.save()

        self.config, _created = CmsDsfrConfig.objects.update_or_create(
            site_id=1,
            defaults={
                "site_title": "Site title",
                "site_tagline": "Site tagline",
                "header_brand": "République française",
                "header_brand_html": "République<br />française",
                "footer_brand": "République française",
                "footer_brand_html": "République<br />française",
                "footer_description": "Site <b>description</b>.",
            },
        )
        self.config.save()

    def test_header_brand_block_uses_conf(self):
        url = self.content_page.url
        response = self.client.get(url)

        self.assertInHTML(
            """<p class="fr-logo">République<br />française</p>""",
            response.content.decode(),
        )

    def test_footer_brand_block_uses_conf(self):
        url = self.content_page.url
        response = self.client.get(url)

        self.assertInHTML(
            """<div class="fr-footer__brand fr-enlarge-link">
                    <a id="footer-operator"
                    href="/"
                    title="Retourner à l’accueil - Site title - République française">
                    <p class="fr-logo">
                        République<br />française
                    </p>
                </a>
            </div>""",
            response.content.decode(),
        )

    def test_header_title_block_uses_conf(self):
        url = self.content_page.url
        response = self.client.get(url)

        self.assertInHTML(
            """<div class="fr-header__service">
                <a href="/" title="Accueil — Site title">
                    <p class="fr-header__service-title">Site title</p>
                </a>
                <p class="fr-header__service-tagline">Site tagline</p>
            </div>""",
            response.content.decode(),
        )

    def test_notice_is_not_set_by_default(self):
        url = self.content_page.url
        response = self.client.get(url)

        self.assertNotContains(
            response,
            "fr-notice__body",
        )

    def test_notice_can_be_set(self):
        self.config.notice_title = "Ceci est une information <b>importante</b> et <i>temporaire</i>."
        self.config.save()

        url = self.content_page.url
        response = self.client.get(url)

        self.assertContains(response, self.config.notice_title)

    def test_beta_tag_is_not_set_by_default(self):
        url = self.content_page.url
        response = self.client.get(url)

        self.assertNotContains(
            response,
            '<span class="fr-badge fr-badge--sm fr-badge--green-emeraude">BETA</span>',
        )

    def test_beta_tag_can_be_set(self):
        self.config.beta_tag = True
        self.config.save()

        url = self.content_page.url
        response = self.client.get(url)

        self.assertContains(
            response,
            '<span class="fr-badge fr-badge--sm fr-badge--green-emeraude">BETA</span>',
        )

    def test_footer_description_uses_conf(self):
        url = self.content_page.url
        response = self.client.get(url)

        self.config.refresh_from_db()

        self.assertContains(response, self.config.footer_description)


class MenusTestCase(WagtailPageTestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        call_command("collectstatic", interactive=False)
        call_command("create_starter_pages")

    def setUp(self) -> None:
        self.site = get_default_site()
        self.home_page = self.site.root_page

        self.main_menu = MainMenu.objects.first()

        body = []

        text_raw = """<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>"""
        body.append(("paragraph", RichText(text_raw)))

        self.publications_page = self.home_page.add_child(
            instance=ContentPage(title="Publications", body=body, show_in_menus=True)
        )

        self.example_publication_page = self.publications_page.add_child(
            instance=ContentPage(title="Publication 1", body=body, show_in_menus=True)
        )
        self.publications_menu_item = MainMenuItem.objects.create(
            link_page=self.publications_page, menu=self.main_menu, sort_order=2
        )

    def test_basic_menu_is_rendered(self):
        self.assertPageIsRenderable(self.home_page)
        response = self.client.get(self.home_page.url)

        # Selected menu item : home page
        self.assertInHTML(
            '<a class="fr-nav__link" href="/" aria-current="page" target="_self">Accueil</a>',
            response.content.decode(),
        )

        self.assertInHTML(
            f"""<button class="fr-nav__btn"
                aria-expanded="false"
                aria-controls="menu-{self.publications_menu_item.link_page.pk}">
                Publications
            </button>""",
            response.content.decode(),
        )

        self.assertInHTML(
            '<a class="fr-nav__link" href="/publications/publication-1/" target="_self">Publication 1</a>',
            response.content.decode(),
        )

        # Selected menu item : publication 1
        response = self.client.get(self.example_publication_page.url)
        self.assertInHTML(
            '<a class="fr-nav__link" href="/" target="_self">Accueil</a>',
            response.content.decode(),
        )

        self.assertInHTML(
            f"""<button class="fr-nav__btn"
                aria-current="true"
                aria-expanded="false"
                aria-controls="menu-{self.publications_menu_item.link_page.pk}">
                    Publications
            </button>""",
            response.content.decode(),
        )

        self.assertInHTML(
            """<a class="fr-nav__link"
                aria-current="page"
                href="/publications/publication-1/"
                target="_self">
                Publication 1
            </a>""",
            response.content.decode(),
        )

    def test_mega_menu_is_rendered(self):
        publications_mega_menu = MegaMenu.objects.create(
            name="Méga-menu publications",
            parent_menu_item=self.publications_menu_item,
            description="Ceci est une description",
        )

        menu_category_menu = FlatMenu.objects.create(
            site_id=self.site.id,
            title="Menu publications > Catégorie 1",
            handle="mega_menu_section_1",
            heading="Colonne 1",
        )

        MegaMenuCategory.objects.create(mega_menu=publications_mega_menu, sort_order=0, category=menu_category_menu)

        FlatMenuItem.objects.get_or_create(
            link_page=self.example_publication_page, menu=menu_category_menu, sort_order=0
        )

        self.assertPageIsRenderable(self.example_publication_page)
        response = self.client.get(self.example_publication_page.url)

        self.assertInHTML(
            '<p class="fr-hidden fr-displayed-lg">Ceci est une description</p>',
            response.content.decode(),
        )

        self.assertInHTML(
            f"""<button class="fr-nav__btn"
                        aria-expanded="false"
                        aria-current="true"
                        aria-controls="mega-menu-{self.publications_menu_item.id}">Publications</button>
            """,
            response.content.decode(),
        )

        self.assertInHTML(
            """<a class="fr-nav__link"
                aria-current="page"
                href="/publications/publication-1/"
                target="_self">
                    Publication 1
                </a>""",
            response.content.decode(),
        )


class CatalogIndexPageTestCase(WagtailPageTestCase):
    def setUp(self):
        home = Page.objects.get(slug="home")
        self.admin = User.objects.create_superuser("test", "test@test.test", "pass")
        self.admin.save()
        self.catalog_index_page = home.add_child(
            instance=CatalogIndexPage(
                title="Index de catalogue",
                slug="catalog-index",
                owner=self.admin,
            )
        )
        self.catalog_index_page.save()

        self.catalog_entry = self.catalog_index_page.add_child(
            instance=ContentPage(
                title="Entrée de catalogue",
                slug="catalog-entry",
                owner=self.admin,
            )
        )

        self.catalog_entry.save()

    def test_catalog_index_page_is_renderable(self):
        self.assertPageIsRenderable(self.catalog_index_page)

    def test_catalog_index_page_has_minimal_content(self):
        url = self.catalog_index_page.url
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertInHTML(
            "<title>Index de catalogue — Titre du site</title>",
            response.content.decode(),
        )

        self.assertInHTML(
            '<a href="/catalog-index/catalog-entry/">Entrée de catalogue</a>',
            response.content.decode(),
        )


class ErrorPagesTestCase(TestCase):
    def test_404_error_page(self):
        response = self.client.get("/404/")
        self.assertEqual(response.status_code, 404)
        self.assertInHTML(
            "<title>Erreur 404 — Page non trouvée — Titre du site</title>",
            response.content.decode(),
        )

    def test_500_error_page(self):
        response = self.client.get("/500/")
        self.assertEqual(response.status_code, 500)
        # Site settings are not available in a error 500 page so the site title is not there
        self.assertInHTML(
            "<title>Erreur 500 — Erreur inattendue</title>",
            response.content.decode(),
        )
