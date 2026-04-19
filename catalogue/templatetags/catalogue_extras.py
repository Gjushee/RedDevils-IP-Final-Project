from django import template

register = template.Library()


@register.filter
def discounted(price, percent):
    try:
        return round(float(price) * (1 - float(percent) / 100), 2)
    except (TypeError, ValueError):
        return price
