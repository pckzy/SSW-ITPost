from django import template

register = template.Library()

@register.filter
def in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter
def ends_with(value, arg):
    return value.endswith(arg)

@register.filter
def remove_prefix(value, prefix):
    if value.startswith(prefix):
        return value[len(prefix):]
    return value