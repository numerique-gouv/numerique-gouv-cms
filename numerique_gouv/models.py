from django.db import models
from django.db.models import Case, IntegerField, QuerySet, Value, When
from django.shortcuts import get_object_or_404, redirect
from django.utils.translation import gettext_lazy as _
from dsfr.constants import COLOR_CHOICES_ILLUSTRATION
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import FieldPanel, FieldRowPanel, HelpPanel, MultiFieldPanel, ObjectList, TabbedInterface
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.snippets.models import register_snippet

from blog.models import BlogEntryPage, BlogIndexPage
from content_manager.blocks import ButtonsHorizontalListBlock, TextAndCTA
from events.models import EventEntryPage, EventsIndexPage
from numerique_gouv.abstract import NumeriqueBasePage


class NumeriquePage(NumeriqueBasePage):
    subpage_types = [
        "numerique_gouv.NumeriquePage",
        "numerique_gouv.NumeriqueBlogIndexPage",
        "numerique_gouv.HubPages",
        "numerique_gouv.OffersIndexPage",
        "numerique_gouv.ProductsIndexPage",
        "numerique_gouv.NumeriqueEventsIndexPage",
    ]

    class Meta:
        verbose_name = _("Numerique page")


class OffersIndexPage(NumeriqueBasePage):
    subpage_types = ["numerique_gouv.OffersEntryPage"]

    class Meta:
        verbose_name = _("Offers index")

    def get_tool_subpages(self):
        return self.get_children().live().specific().filter(numeriquebasepage__offersentrypage__type__slug="outil")

    def get_financement_subpages(self):
        return (
            self.get_children().live().specific().filter(numeriquebasepage__offersentrypage__type__slug="financement")
        )

    def get_expertise_subpages(self):
        return (
            self.get_children()
            .live()
            .specific()
            .filter(models.Q(numeriquebasepage__offersentrypage__type__slug="expertise"))
        )

    def get_pilotage_subpages(self):
        return (
            self.get_children()
            .live()
            .specific()
            .filter(
                models.Q(numeriquebasepage__offersentrypage__type__slug="pilotage")
                | models.Q(numeriquebasepage__offersentrypage__type__slug="observatoire")
            )
        )

    def get_document_subpages(self):
        return self.get_children().live().specific().filter(numeriquebasepage__offersentrypage__type__slug="document")

    def get_all_subpages(self):
        return self.get_children().live().specific()

    def get_page_tags(self):
        return PageTag.objects.all()

    def get_target_audiences(self):
        return TargetAudience.objects.all()


class TextAndCTAStreamField(StreamField):
    def __init__(self, *args, **kwargs):
        block_types = [("text_and_cta", TextAndCTA())]
        super().__init__(block_types, *args)


class OffersEntryPage(NumeriqueBasePage):
    type = models.ForeignKey(
        "numerique_gouv.Offertype", blank=True, null=True, on_delete=models.SET_NULL, verbose_name=_("Type")
    )

    page_tags = ParentalManyToManyField("numerique_gouv.PageTag", blank=True, verbose_name=_("Page tags"))
    # a supprimer
    target_audiences_old = ParentalManyToManyField(
        "numerique_gouv.OfferTargetAudience", blank=True, verbose_name=_("Target Audience")
    )
    target_audiences = ParentalManyToManyField(
        "numerique_gouv.TargetAudience", blank=True, verbose_name=_("Target Audience")
    )
    major_areas = ParentalManyToManyField("numerique_gouv.MajorArea", blank=True, verbose_name=_("Dinum Tags"))
    themes = ParentalManyToManyField("numerique_gouv.DinumTag", blank=True, verbose_name=_("Theme"))
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
    card_alt_image = models.CharField(max_length=255, blank=True, verbose_name=_("Image alt"))

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
                FieldPanel("page_tags"),
                FieldPanel("target_audiences"),
                FieldPanel("major_areas"),
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
        FieldPanel("card_alt_image"),
        FieldPanel("card_text"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(NumeriqueBasePage.content_panels, heading=_("Content")),
            ObjectList(header_panels, heading=_("Header")),
            ObjectList(organization_panel, heading=_("Organization")),
            ObjectList(card_panel, heading=_("Card")),
            ObjectList(NumeriqueBasePage.promote_panels, heading=_("Promote")),
        ]
    )

    def get_absolute_url(self):
        return self.url

    class Meta:
        verbose_name = _("Offer page")


class ProductsEntryPage(NumeriqueBasePage):
    target_audiences = ParentalManyToManyField(
        "numerique_gouv.TargetAudience", blank=True, null=True, verbose_name=_("Target Audiences")
    )
    page_tags = ParentalManyToManyField("numerique_gouv.PageTag", blank=True, verbose_name=_("Categories"))
    major_areas = ParentalManyToManyField("numerique_gouv.MajorArea", blank=True, verbose_name=_("Dinum Tags"))

    product_url = models.URLField(blank=True, verbose_name=_("Product URL"))
    the_service = models.TextField(blank=True, verbose_name=_("The service"))
    the_problem = models.TextField(blank=True, verbose_name=_("The problem"))
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("Card image"),
    )
    image_alt = models.CharField(max_length=255, blank=True, verbose_name=_("Image alt"))
    position = models.IntegerField(default=0)

    parent_page_types = ["numerique_gouv.ProductsIndexPage"]
    subpage_types = []

    content_panels = NumeriqueBasePage.content_panels + [
        FieldPanel("target_audiences"),
        FieldPanel("position"),
        FieldPanel("product_url"),
        FieldPanel("the_service"),
        FieldPanel("the_problem"),
        FieldPanel("major_areas"),
        FieldPanel("page_tags"),
        FieldPanel("image"),
        FieldPanel("image_alt"),
    ]

    def serve(self, request):
        parent = self.get_parent().specific
        return redirect(parent.url)

    class Meta:
        verbose_name = _("Product page")


class ProductsIndexPage(NumeriqueBasePage):
    subpage_types = ["numerique_gouv.ProductsEntryPage"]

    class Meta:
        verbose_name = _("Products index")

    def get_context(self, request, *args, **kwargs):
        context = super(ProductsIndexPage, self).get_context(request, *args, **kwargs)

        context["agents_publics_subpages"] = self.get_agents_publics_subpages()
        context["citizens_subpages"] = self.get_citizens_subpages()
        context["companies_subpages"] = self.get_companies_subpages()

        return context

    def get_agents_publics_subpages(self):
        return (
            self.get_children()
            .live()
            .specific()
            .filter(numeriquebasepage__productsentrypage__target_audiences__slug="agents_public")
            .annotate(
                custom_order=Case(
                    When(numeriquebasepage__productsentrypage__position=0, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            .order_by("custom_order", "numeriquebasepage__productsentrypage__position")
        )

    def get_citizens_subpages(self):
        return (
            self.get_children()
            .live()
            .specific()
            .filter(numeriquebasepage__productsentrypage__target_audiences__slug="citoyens")
            .annotate(
                custom_order=Case(
                    When(numeriquebasepage__productsentrypage__position=0, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            .order_by("custom_order", "numeriquebasepage__productsentrypage__position")
        )

    def get_companies_subpages(self):
        return (
            self.get_children()
            .live()
            .specific()
            .filter(numeriquebasepage__productsentrypage__target_audiences__slug="entreprises")
            .annotate(
                custom_order=Case(
                    When(numeriquebasepage__productsentrypage__position=0, then=Value(1)),
                    default=Value(0),
                    output_field=IntegerField(),
                )
            )
            .order_by("custom_order", "numeriquebasepage__productsentrypage__position")
        )


class NumeriqueBlogEntryPage(BlogEntryPage):
    major_areas = ParentalManyToManyField(
        "numerique_gouv.MajorArea", blank=True, verbose_name=_("Major Areas of Actions")
    )
    dinum_tags = ParentalManyToManyField("numerique_gouv.DinumTag", blank=True, verbose_name=_("Dinum Tags"))
    page_tags = ParentalManyToManyField("numerique_gouv.PageTag", blank=True, verbose_name=_("Page tags"))
    target_audiences = ParentalManyToManyField(
        "numerique_gouv.TargetAudience", blank=True, verbose_name=_("Target Audiences")
    )

    parent_page_types = ["numerique_gouv.NumeriqueBlogIndexPage"]

    template = "numerique_gouv/blog_entry_page.html"

    settings_panels = NumeriqueBasePage.settings_panels + [
        FieldPanel("date"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("go_live_at"),
                        FieldPanel("expire_at"),
                    ],
                    classname="label-above",
                ),
            ],
            _("Scheduled publishing"),
            classname="publishing",
        ),
        MultiFieldPanel(
            [
                FieldPanel("blog_categories"),
                FieldPanel("page_tags"),
                FieldPanel("major_areas"),
                FieldPanel("dinum_tags"),
                FieldPanel("target_audiences"),
            ],
            heading=_("Tags and Categories"),
        ),
        FieldPanel("authors"),
    ]

    class Meta:
        verbose_name = _("Numerique blog entry page")


class NumeriqueBlogIndexPage(BlogIndexPage):
    subpage_types = ["numerique_gouv.NumeriqueBlogEntryPage"]

    template = "numerique_gouv/blog_index_page.html"

    class Meta:
        verbose_name = _("Numerique blog index page")

    @property
    def posts(self):
        posts = NumeriqueBlogEntryPage.objects.descendant_of(self).live()
        posts = posts.select_related("owner").prefetch_related("major_areas", "page_tags", "date__year")
        return posts

    def get_context(self, request, page_tag=None, major_area=None, year=None, *args, **kwargs):
        context = super(BlogIndexPage, self).get_context(request, *args, **kwargs)
        posts = self.posts

        if page_tag is None:
            page_tag = request.GET.get("page_tag")
        if page_tag:
            page_tag = get_object_or_404(PageTag, slug=page_tag)
            posts = posts.filter(page_tags=page_tag)

        if major_area is None:
            major_area = request.GET.get("major_area")
        if major_area:
            major_area = get_object_or_404(MajorArea, slug=major_area)
            posts = posts.filter(major_areas=major_area)

        if year:
            posts = posts.filter(date__year=year)

        context["posts"] = posts.order_by("-date")
        context["current_page_tag"] = page_tag
        context["current_major_area"] = major_area
        context["year"] = year

        # Filters
        context["page_tags"] = self.get_page_tags()
        context["major_areas"] = self.get_major_areas()

        return context

    def get_page_tags(self) -> QuerySet:
        ids = self.posts.specific().values_list("page_tags", flat=True)
        return PageTag.objects.filter(id__in=ids).order_by("name")

    def get_major_areas(self) -> QuerySet:
        ids = self.posts.specific().values_list("major_areas", flat=True)
        return MajorArea.objects.filter(id__in=ids).order_by("name")


class HubPages(NumeriqueBasePage):
    subpage_types = [
        "numerique_gouv.ProductsIndexPage",
        "numerique_gouv.OffersIndexPage",
        "numerique_gouv.NumeriquePage",
    ]
    display_actualites = models.BooleanField(default=True, verbose_name=_("Display actualites"))
    display_events = models.BooleanField(default=True, verbose_name=_("Display events"))
    display_products = models.BooleanField(default=True, verbose_name=_("Display products"))
    display_offers = models.BooleanField(default=True, verbose_name=_("Display offers"))

    major_area = models.ForeignKey(
        "numerique_gouv.MajorArea",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Major Area of Actions"),
    )
    dinum_tag = models.ForeignKey(
        "numerique_gouv.DinumTag",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Dinum Tags"),
    )
    page_tag = models.ForeignKey(
        "numerique_gouv.PageTag",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Page tags"),
    )
    target_audience = models.ForeignKey(
        "numerique_gouv.TargetAudience",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Target Audience"),
    )

    CHOICES = [
        ("major_area", _("Major Areas of Actions")),
        ("dinum_tag", _("Dinum Tags")),
        ("page_tag", _("Page tags")),
        ("target_audience", _("Target Audiences")),
    ]
    content_source = models.CharField(max_length=20, choices=CHOICES, verbose_name=_("Content Source"))
    introduction_text = models.TextField(blank=True, verbose_name=_("Introduction text"))

    def get_context(self, request, *args, **kwargs):
        context = super(HubPages, self).get_context(request, *args, **kwargs)

        context["news"] = self.get_entries("blog")
        context["offers"] = self.get_entries("offers")
        context["products"] = self.get_entries("products")

        return context

    class Meta:
        verbose_name = _("Hub page")

    configuration_panels = [
        MultiFieldPanel(
            [
                FieldPanel("display_actualites"),
                FieldPanel("display_events"),
                FieldPanel("display_products"),
                FieldPanel("display_offers"),
                FieldPanel("content_source"),
                FieldPanel("major_area"),
                FieldPanel("dinum_tag"),
                FieldPanel("page_tag"),
                FieldPanel("target_audience"),
            ],
        ),
    ]
    promote_panels = NumeriqueBasePage.promote_panels + [
        FieldPanel("introduction_text"),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(NumeriqueBasePage.content_panels, heading=_("Content")),
            ObjectList(configuration_panels, heading=_("Configuration")),
            ObjectList(promote_panels, heading=_("Promote")),
        ]
    )

    def get_entries(self, entry_type):
        if entry_type == "blog":
            entries = NumeriqueBlogEntryPage.objects.live().specific()
        elif entry_type == "offers":
            entries = OffersEntryPage.objects.live().specific()
        elif entry_type == "products":
            entries = ProductsEntryPage.objects.live().specific()

        if self.content_source == "major_area":
            return entries.filter(major_areas=self.major_area).order_by("-id")[:3]
        elif self.content_source == "dinum_tag":
            return entries.filter(dinum_tags=self.dinum_tag).order_by("-id")[:3]
        elif self.content_source == "page_tag":
            return entries.filter(page_tags=self.page_tag).order_by("-id")[:3]
        elif self.content_source == "target_audience":
            return entries.filter(target_audiences=self.target_audience).order_by("-id")[:3]

    def get_content_source_name(self):
        if self.content_source == "major_area":
            return self.major_area.name.lower()
        elif self.content_source == "dinum_tag":
            return self.dinum_tag.name.lower()
        elif self.content_source == "page_tag":
            return self.page_tag.name.lower()
        elif self.content_source == "target_audience":
            return self.target_audience.name.lower()


class NumeriqueEventsIndexPage(EventsIndexPage):
    subpage_types = ["numerique_gouv.NumeriqueEventPage"]
    template = "events/events_index_page.html"

    class Meta:
        verbose_name = _("Numerique events index page")


class NumeriqueEventPage(EventEntryPage):
    major_areas = ParentalManyToManyField(
        "numerique_gouv.MajorArea", blank=True, verbose_name=_("Major Areas of Actions")
    )
    dinum_tags = ParentalManyToManyField("numerique_gouv.DinumTag", blank=True, verbose_name=_("Dinum Tags"))
    page_tags = ParentalManyToManyField("numerique_gouv.PageTag", blank=True, verbose_name=_("Page tags"))
    target_audiences = ParentalManyToManyField(
        "numerique_gouv.TargetAudience", blank=True, verbose_name=_("Target Audiences")
    )
    parent_page_types = ["numerique_gouv.NumeriqueEventsIndexPage"]
    subpage_types = []

    template = "numerique_gouv/event_entry_page.html"

    settings_panels = NumeriqueBasePage.settings_panels + [
        FieldPanel("authors"),
        FieldPanel("date"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("event_date_start"),
                        FieldPanel("event_date_end"),
                    ],
                    classname="label-above",
                ),
                FieldPanel("location"),
                FieldPanel("registration_url"),
            ],
            _("Event date and place"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("go_live_at"),
                        FieldPanel("expire_at"),
                    ],
                    classname="label-above",
                ),
            ],
            _("Scheduled publishing"),
            classname="publishing",
        ),
        MultiFieldPanel(
            [
                FieldPanel("event_categories"),
                FieldPanel("page_tags"),
                FieldPanel("major_areas"),
                FieldPanel("dinum_tags"),
                FieldPanel("target_audiences"),
            ],
            heading=_("Tags and Categories"),
        ),
    ]

    class Meta:
        verbose_name = _("Numerique event page")


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
class PageTag(BaseCategory):
    class Meta:
        verbose_name = _("Page tag")


# A supprimer
@register_snippet
class OfferTargetAudience(BaseCategory):
    class Meta:
        verbose_name = _("Offer Target Audience ( a supprimer )")


@register_snippet
class MajorArea(BaseCategory):
    class Meta:
        verbose_name = _("Major Area of Action")


@register_snippet
class Offertype(BaseCategory):
    class Meta:
        verbose_name = _("Offer Type")


@register_snippet
class TargetAudience(BaseCategory):
    class Meta:
        verbose_name = _("Target Audience")


@register_snippet
class DinumTag(BaseCategory):
    class Meta:
        verbose_name = _("Dinum Tag")
