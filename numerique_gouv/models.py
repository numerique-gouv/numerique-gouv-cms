from django.db import models
from django.utils.translation import gettext_lazy as _
from dsfr.constants import COLOR_CHOICES_ILLUSTRATION
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, HelpPanel, MultiFieldPanel, ObjectList, TabbedInterface
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.snippets.models import register_snippet

from content_manager.blocks import ButtonsHorizontalListBlock, TextAndCTA
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


class TextAndCTAStreamField(StreamField):
    def __init__(self, *args, **kwargs):
        block_types = [("text_and_cta", TextAndCTA())]
        super().__init__(block_types, *args)


class OffersEntryPage(NumeriqueBasePage):
    type = models.ForeignKey(
        "numerique_gouv.Offertype", blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_("Type")
    )

    categories = ParentalManyToManyField("numerique_gouv.OfferCategory", blank=True, verbose_name=_("Categories"))
    target_audiences = ParentalManyToManyField(
        "numerique_gouv.OfferTargetAudience", blank=True, verbose_name=_("Target Audience")
    )
    themes = ParentalManyToManyField("numerique_gouv.OfferTheme", blank=True, verbose_name=_("Theme"))
    buttons = ButtonsHorizontalListBlock(label=_("Buttons"))
    text_and_cta = TextAndCTAStreamField(blank=True, verbose_name=_("Text and cta"))

    card_description = models.TextField(blank=True, verbose_name=_("Description"))
    card_text = models.TextField(blank=True, verbose_name=_("Text"))
    card_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Card image"),
    )

    # organization
    organization_title = models.TextField(blank=True, verbose_name=_("Organization title"))
    block_one_title = models.TextField(blank=True, verbose_name=_("Block one title"))
    block_one_column_one = models.TextField(blank=True, verbose_name=_("Block one column one"))
    block_one_column_two = models.TextField(blank=True, verbose_name=_("Block one column two"))
    block_one_column_three = models.TextField(blank=True, verbose_name=_("Block one column three"))
    block_two_title = models.TextField(blank=True, verbose_name=_("Block two title"))
    block_two_column_one = models.TextField(blank=True, verbose_name=_("Block two column one"))
    block_two_column_two = models.TextField(blank=True, verbose_name=_("Block two column two"))
    block_two_column_three = models.TextField(blank=True, verbose_name=_("Block two column three"))
    block_three_title = models.TextField(blank=True, verbose_name=_("Block three title"))
    block_three_subtitle = models.TextField(blank=True, verbose_name=_("Block three subtitle"))
    block_three_column_one = models.TextField(blank=True, verbose_name=_("Block three column one"))
    block_three_column_two = models.TextField(blank=True, verbose_name=_("Block three column two"))
    block_three_column_three = models.TextField(blank=True, verbose_name=_("Block three column three"))

    parent_page_types = ["numerique_gouv.OffersIndexPage"]
    subpage_types = []

    header_panels = [
        FieldPanel(
            "type",
            heading=_("Offer type"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("categories"),
                FieldPanel("target_audiences"),
                FieldPanel("themes"),
                FieldPanel("text_and_cta"),
            ],
            heading=_("Header"),
        ),
    ]

    organization_panel = [
        FieldPanel(
            "organization_title",
            heading=_("title"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("block_one_title"),
                FieldPanel("block_one_column_one"),
                FieldPanel("block_one_column_two"),
                FieldPanel("block_one_column_three"),
            ],
            heading=_("Block one"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("block_two_title"),
                FieldPanel("block_two_column_one"),
                FieldPanel("block_two_column_two"),
                FieldPanel("block_two_column_three"),
            ],
            heading=_("Block two"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("block_three_title"),
                FieldPanel("block_three_subtitle"),
                FieldPanel("block_three_column_one"),
                FieldPanel("block_three_column_two"),
                FieldPanel("block_three_column_three"),
            ],
            heading=_("Block three"),
        ),
    ]

    card_panel = [
        HelpPanel(_("This is the card that will be displayed on the offer index page.")),
        FieldPanel("card_image"),
        FieldPanel("card_description"),
        FieldPanel("card_text"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(NumeriqueBasePage.content_panels, heading=_("Content")),
            ObjectList(header_panels, heading=_("Header")),
            ObjectList(organization_panel, heading=_("Organization")),
            ObjectList(card_panel, heading=_("Card")),
            ObjectList(NumeriqueBasePage.promote_panels, heading=_("Promote")),
            ObjectList(NumeriqueBasePage.settings_panels, heading=_("Settings")),
        ]
    )

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
