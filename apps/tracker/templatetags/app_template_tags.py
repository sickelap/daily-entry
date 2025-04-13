from django import template

register = template.Library()


@register.inclusion_tag("components/weight_entry_form.html")
def weight_entry_form(value: int):
    return {"value": value}


@register.inclusion_tag("components/logout_button.html")
def logout_button():
    return {}


@register.inclusion_tag("components/todays_entries.html")
def todays_entries(entries):
    return {"entries": entries}
