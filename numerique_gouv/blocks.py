from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from content_manager.blocks import (
    AdjustableColumnBlock,
    ColumnBlock,
    FullWidthBackgroundBlock,
    FullWidthBlock,
    HorizontalCardBlock,
    MultiColumnsBlock,
    MultiColumnsWithTitleBlock,
)


class ThreeCardsBlock(blocks.StructBlock):
    # Bloc avec trois cartes, une principale à gauche et deux secondaires à droite
    main_image = ImageChooserBlock(required=True, label=_("Main card image"))
    main_title = blocks.TextBlock(required=True, label=_("Main card title"))
    main_text = blocks.RichTextBlock(required=True, label=_("Main card text"))
    main_page_link = blocks.PageChooserBlock(
        required=False, help_text=_("Link to a page"), label=_("Main card page link")
    )
    main_url_link = blocks.URLBlock(
        required=False, help_text=_("Link to an external URL"), label=_("Main card URL link")
    )

    top_right_image = ImageChooserBlock(required=False, label=_("Top right card image"))
    top_right_title = blocks.TextBlock(required=False, label=_("Top right card title"))
    top_right_text = blocks.RichTextBlock(required=True, label=_("Top right card text"))
    top_right_button_label = blocks.TextBlock(required=False, label=_("Top right card button label"))
    top_right_page_link = blocks.PageChooserBlock(
        required=False, help_text=_("Link to a page"), label=_("Top right card page link")
    )
    top_right_url_link = blocks.URLBlock(
        required=False, help_text=_("Link to an external URL"), label=_("Top right card URL link")
    )

    bottom_right_image = ImageChooserBlock(required=False, label=_("Bottom right card image"))
    bottom_right_title = blocks.TextBlock(required=False, label=_("Bottom right card title"))
    bottom_right_text = blocks.RichTextBlock(required=True, label=_("Bottom right card text"))
    bottom_right_button_label = blocks.TextBlock(required=False, label=_("Bottom right card button label"))
    bottom_right_page_link = blocks.PageChooserBlock(
        required=False, help_text=_("Link to a page"), label=_("Bottom right card page link")
    )
    bottom_right_url_link = blocks.URLBlock(
        required=False, help_text=_("Link to an external URL"), label=_("Bottom right card URL link")
    )

    class Meta:
        template = "numerique_gouv/blocks/three_cards.html"
        icon = "image"
        label = "Headline cards"


class NumericDirectionCardBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True, label=_("Image"))
    alt = blocks.CharBlock(required=True, label=_("Alt text"))
    text = blocks.RichTextBlock(required=True, label=_("Text"))
    main_link = blocks.PageChooserBlock(required=True, label=_("Main link"))
    secondary_link = blocks.URLBlock(required=True, help_text=_("Link to an external URL"), label=_("Secondary link"))

    class Meta:
        template = "numerique_gouv/blocks/numeric_direction_card.html"
        icon = "tablet-alt"
        label = "Numeric direction card"


class CustomColumnBlock(ColumnBlock):
    html = blocks.RawHTMLBlock(
        required=False,
        help_text=_("Warning: Use HTML block with caution. Malicious code can compromise the security of the site."),
        group=_("Expert syntax"),
    )
    numeric_direction_card = NumericDirectionCardBlock(
        required=False, label=_("Numeric direction card"), group=_("Numerique components")
    )
    horizontal_card = HorizontalCardBlock(label=_("Horizontal card"), group=_("DSFR components"))


class CustomAdjustableColumnBlock(AdjustableColumnBlock):
    content = CustomColumnBlock(label=_("Column content"))

    class Meta:
        icon = "order-down"


class CustomMultiColumnsBlock(MultiColumnsBlock):
    html = blocks.RawHTMLBlock(
        required=False,
        help_text=_("Warning: Use HTML block with caution. Malicious code can compromise the security of the site."),
        group=_("Expert syntax"),
    )
    numeric_direction_card = NumericDirectionCardBlock(
        required=False, label=_("Numeric direction card"), group=_("Numerique components")
    )
    custom_ajustable_column = CustomAdjustableColumnBlock(
        required=False, label=_("Custom adjustable column"), group=_("Numerique components")
    )
    horizontal_card = HorizontalCardBlock(label=_("Horizontal card"), group=_("DSFR components"))


class CustomMultiColumnsWithTitleBlock(MultiColumnsWithTitleBlock):
    columns = CustomMultiColumnsBlock(label=_("Columns"))

    class Meta:
        icon = "dots-horizontal"


class CustomFullWidthBlock(FullWidthBlock):
    html = blocks.RawHTMLBlock(
        required=False,
        help_text=_("Warning: Use HTML block with caution. Malicious code can compromise the security of the site."),
        group=_("Expert syntax"),
    )
    numeric_direction_card = NumericDirectionCardBlock(
        required=False, label=_("Numeric direction card"), group=_("Numerique components")
    )
    custom_ajustable_column = CustomAdjustableColumnBlock(
        required=False, label=_("Custom adjustable column"), group=_("Numerique components")
    )
    horizontal_card = HorizontalCardBlock(label=_("Horizontal card"), group=_("DSFR components"))
    multicolumns = MultiColumnsWithTitleBlock(
        required=False, label=_("Multi columns"), group=_("Numerique components")
    )


class CustomFullWidthBackgroundBlock(FullWidthBackgroundBlock):
    content = CustomFullWidthBlock(label=_("Content"))


class SpacerBlock(blocks.StructBlock):
    marginTop = blocks.DecimalBlock(required=False, label=_("Margin top"), help_text=_("In rem"))
    marginBottom = blocks.DecimalBlock(required=False, label=_("Margin bottom"), help_text=_("In rem"))

    class Meta:
        template = "numerique_gouv/blocks/spacer.html"
        icon = "dots-horizontal"
        label = "Spacer"


STREAMFIELD_NUMERIQUE_BLOCKS = [
    ("three_cards", ThreeCardsBlock(label=_("Headline cards"), group=_("Numerique components"))),
    ("multicolumns", CustomMultiColumnsWithTitleBlock(label=_("Multi columns"), group=_("Page structure"))),
    (
        "numeric_direction_card",
        NumericDirectionCardBlock(label=_("Numeric direction card"), group=_("Numerique components")),
    ),
    (
        "fullwidthbackground",
        CustomFullWidthBackgroundBlock(label=_("Full width background"), group=_("Page structure")),
    ),
    ("spacer", SpacerBlock(label=_("Spacer"), group=_("Page structure"))),
]
