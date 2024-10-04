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
def get_entries(value, key):
    return value.get_entries(key)


@register.filter
def is_numerique_blog_entry_page(value):
    return isinstance(value, NumeriqueBlogEntryPage)
