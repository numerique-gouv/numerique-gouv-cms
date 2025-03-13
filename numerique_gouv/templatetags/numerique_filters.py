from decimal import Decimal

from django import template

from numerique_gouv.models import NumeriqueBlogEntryPage

register = template.Library()


@register.filter
def replace(value, args=",|."):
    # Convertir Decimal en str si nécessaire
    if isinstance(value, Decimal):
        value = str(value)
    old_char, new_char = args.split("|")
    return value.replace(old_char, new_char)


@register.filter
def is_numerique_blog_entry_page(value):
    return isinstance(value, NumeriqueBlogEntryPage)


@register.filter
def first_item_id(items):
    if items and len(items) > 0:
        return str(items[0].id).replace("-", "")
    return None
