from django import template

register = template.Library()


@register.inclusion_tag("components/range_control.html")
def range_control(value: int):
    return {"value": value}


@register.inclusion_tag("components/logout_button.html")
def logout_button():
    return {}
