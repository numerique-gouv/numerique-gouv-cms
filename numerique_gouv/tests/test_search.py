from django.contrib.auth import get_user_model
from django.urls import reverse
from wagtail.models import Page, PageViewRestriction
from wagtail.test.utils import WagtailPageTestCase

from numerique_gouv.models import NumeriqueBlogEntryPage, NumeriqueBlogIndexPage, NumeriquePage

User = get_user_model()

# The search view (content_manager/views.py) is customized for numerique.gouv.fr:
# it searches a hard-coded list of numerique_gouv page types.


class SearchResultsViewTestCase(WagtailPageTestCase):
    def setUp(self):
        self.home = Page.objects.get(slug="home")
        self.admin = User.objects.create_superuser("test", "test@test.test", "pass")

    def add_page(self, parent, page_class, **kwargs):
        # The search index is updated by a task enqueued on transaction commit
        with self.captureOnCommitCallbacks(execute=True):
            return parent.add_child(instance=page_class(owner=self.admin, **kwargs))

    def search(self, query):
        response = self.client.get(reverse("cms_search"), {"q": query})
        self.assertEqual(response.status_code, 200)
        return [page.title for page in response.context["object_list"]]

    def test_empty_query_returns_nothing(self):
        self.add_page(self.home, NumeriquePage, title="Licorne", slug="licorne")
        response = self.client.get(reverse("cms_search"))
        self.assertEqual(list(response.context["object_list"]), [])

    def test_finds_live_numerique_pages(self):
        self.add_page(self.home, NumeriquePage, title="Licorne numérique", slug="licorne-numerique")
        blog = self.add_page(self.home, NumeriqueBlogIndexPage, title="Actualités", slug="actualites")
        self.add_page(blog, NumeriqueBlogEntryPage, title="Article sur la licorne", slug="article-licorne")

        self.assertCountEqual(self.search("licorne"), ["Licorne numérique", "Article sur la licorne"])

    def test_excludes_draft_pages(self):
        self.add_page(self.home, NumeriquePage, title="Licorne brouillon", slug="licorne-brouillon", live=False)
        self.assertEqual(self.search("licorne"), [])

    def test_excludes_private_pages(self):
        page = self.add_page(self.home, NumeriquePage, title="Licorne privée", slug="licorne-privee")
        PageViewRestriction.objects.create(page=page, restriction_type=PageViewRestriction.LOGIN)
        self.assertEqual(self.search("licorne"), [])
