from django import template
from datetime import timedelta
from django.utils import timezone

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

@register.simple_tag
def update_query(request, **kwargs):
    query = request.GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()

@register.filter
def time_since(value):
    if not isinstance(value, timezone.datetime): # Check if value isn't a datetime
        return value

    now = timezone.now()
    time_ago = now - value

    if time_ago < timedelta(minutes=1):
        return "ตอนนี้"
    elif time_ago < timedelta(hours=1):
        minutes = int(time_ago.total_seconds() / 60)
        return f"{minutes} นาทีที่แล้ว"
    elif time_ago < timedelta(days=1):
        hours = int(time_ago.total_seconds() / 3600)
        return f"{hours} ชั่วโมงที่แล้ว"
    elif time_ago < timedelta(days=30):
        days = time_ago.days
        return f"{days} วันที่แล้ว"
    else:
        return value.strftime("%d %B %Y %H:%M")