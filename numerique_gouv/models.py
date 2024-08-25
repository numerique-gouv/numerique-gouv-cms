from django.db import models
from django.utils.translation import gettext_lazy as _
from dsfr.constants import COLOR_CHOICES_ILLUSTRATION
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.images import get_image_model_string
from wagtail.snippets.models import register_snippet

from content_manager.blocks import ButtonsHorizontalListBlock
from numerique_gouv.abstract import NumeriqueBasePage


class NumeriquePage(NumeriqueBasePage):
    class Meta:
        verbose_name = _("Numerique page")


class OffersIndexPage(NumeriqueBasePage):
    subpage_types = ["numerique_gouv.OffersEntryPage"]

    class Meta:
        verbose_name = _("Offers index")

    # @property
    # def posts(self):
    #     # Get list of blog pages that are descendants of this page
    #     posts = BlogEntryPage.objects.descendant_of(self).live()
    #     posts = (
    #         posts.order_by("-date").select_related("owner").prefetch_related("tags", "blog_categories", "date__year")
    #     )
    #     return posts

    # def get_categories(self) -> QuerySet:
    #     ids = self.posts.specific().values_list("blog_categories", flat=True)
    #     return Category.objects.filter(id__in=ids).order_by("name")

    # def get_sources(self) -> QuerySet:
    #     ids = self.posts.specific().values_list("authors__organization", flat=True)
    #     return Organization.objects.filter(id__in=ids).order_by("name")
    #
    # def get_tags(self) -> QuerySet:
    #     ids = self.posts.specific().values_list("tags", flat=True)
    #     return Tag.objects.filter(id__in=ids).order_by("name")

    # def list_categories(self) -> list:
    #     posts = self.posts.specific()
    #     return (
    #         posts.values(
    #             cat_slug=F("blog_categories__slug"),
    #             cat_name=F("blog_categories__name"),
    #         )
    #         .annotate(cat_count=Count("cat_slug"))
    #         .filter(cat_count__gte=1)
    #         .order_by("-cat_count")
    #     )


class OffersEntryPage(NumeriqueBasePage):
    types = ParentalManyToManyField("numerique_gouv.Offertype", blank=True, verbose_name=_("Type"))

    categories = ParentalManyToManyField("numerique_gouv.OfferCategory", blank=True, verbose_name=_("Categories"))
    target_audiences = ParentalManyToManyField(
        "numerique_gouv.OfferTargetAudience", blank=True, verbose_name=_("Target Audience")
    )
    themes = ParentalManyToManyField("numerique_gouv.OfferTheme", blank=True, verbose_name=_("Theme"))
    buttons = ButtonsHorizontalListBlock(label=_("Buttons"))
    # introductory_text = StreamField(
    #     STREAMFIELD_COMMON_BLOCKS,
    #     blank=True,
    #     use_json_field=True,
    # )
    card_description = models.TextField(blank=True, verbose_name=_("Description"))
    card_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Card image"),
    )

    parent_page_types = ["numerique_gouv.OffersIndexPage"]
    subpage_types = []

    content_panels = NumeriqueBasePage.content_panels + [
        MultiFieldPanel(
            [
                # FieldPanel("types"),
            ],
            heading=_("General information"),
        ),
    ]
    settings_panels = NumeriqueBasePage.settings_panels + [
        MultiFieldPanel(
            [
                FieldPanel("types"),
            ],
            heading=_("General information"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("categories"),
                FieldPanel("target_audiences"),
                FieldPanel("themes"),
            ],
            heading=_("Header"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("card_image"),
                FieldPanel("card_description"),
            ],
            heading=_("card information"),
        ),
    ]

    def get_absolute_url(self):
        return self.url

    class Meta:
        verbose_name = _("Offer page")


class BaseCategory(models.Model):
    name = models.CharField(max_length=80, unique=True, verbose_name=_("Category name"))
    slug = models.SlugField(unique=True, max_length=80)
    color = models.CharField(choices=COLOR_CHOICES_ILLUSTRATION, verbose_name=_("Color"), default="blue")

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("color"),
    ]

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


@register_snippet
class OfferCategory(BaseCategory):
    class Meta:
        verbose_name = _("Offer Category")


@register_snippet
class OfferTargetAudience(BaseCategory):
    class Meta:
        verbose_name = _("Offer Target Audience")


@register_snippet
class OfferTheme(BaseCategory):
    class Meta:
        verbose_name = _("Offer Theme")


@register_snippet
class Offertype(BaseCategory):
    class Meta:
        verbose_name = _("Offer Type")
