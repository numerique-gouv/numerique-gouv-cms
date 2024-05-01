from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class ThreeCardsBlock(blocks.StructBlock):
    # Bloc avec trois cartes, une principale à gauche et deux secondaires à droite
    carte_une_titre = blocks.TextBlock(required=True)
    carte_une_texte = blocks.RichTextBlock(required=True)
    carte_une_lien_page = blocks.PageChooserBlock(required=False)
    carte_une_lien_url = blocks.URLBlock(required=False)
    carte_une_image = ImageChooserBlock(required=True)

    carte_deux_label_bouton = blocks.TextBlock(required=True)
    carte_deux_texte = blocks.RichTextBlock(required=True)
    carte_deux_lien_page = blocks.PageChooserBlock(required=False)
    carte_deux_lien_url = blocks.URLBlock(required=False)
    carte_deux_image = ImageChooserBlock(required=True)

    carte_trois_label_bouton = blocks.TextBlock(required=True)
    carte_trois_texte = blocks.RichTextBlock(required=True)
    carte_trois_lien_page = blocks.PageChooserBlock(required=False)
    carte_trois_lien_url = blocks.URLBlock(required=False)
    carte_trois_image = ImageChooserBlock(required=True)

    class Meta:
        template = "numerique_gouv/blocks/three_cards.html"
        icon = "edit"
        label = "Custom Block"


STREAMFIELD_NUMERIQUE_BLOCKS = [("three_cards", ThreeCardsBlock(label=_("Trois cartes")))]
