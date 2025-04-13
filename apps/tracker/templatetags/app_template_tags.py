from django import template

register = template.Library()


@register.inclusion_tag("components/range_control.html")
def range_control(value: int, control_name: str):
    return {"value": value, "control_name": control_name}


@register.inclusion_tag("components/logout_button.html")
def logout_button():
    return {}


@register.inclusion_tag("components/todays_entries.html")
def todays_entries(entries):
    return {"entries": entries}
