from django import template

register = template.Library()


@register.inclusion_tag("components/range_control.html")
def range_control(value: int):
    return {"value": value}
