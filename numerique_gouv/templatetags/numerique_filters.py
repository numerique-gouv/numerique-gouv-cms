from decimal import Decimal

from django import template

register = template.Library()


@register.filter
def replace(value, args=",|."):
    # Convertir Decimal en str si nécessaire
    if isinstance(value, Decimal):
        value = str(value)
    old_char, new_char = args.split("|")
    return value.replace(old_char, new_char)
