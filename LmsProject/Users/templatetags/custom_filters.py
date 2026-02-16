from django import template

register = template.Library()

@register.filter
def dict_key(d, key):
    """Safely get a dictionary value by key in templates"""
    if d and key in d:
        return d.get(key)
    return None
