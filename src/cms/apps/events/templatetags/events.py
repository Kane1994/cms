"""Template tags used by the events application."""


import datetime

from django import template

from cms.apps.events.models import Event


register = template.Library()


@register.inclusion_tag("events/upcoming_events.html")
def upcoming_events(count=5):
    """Renders a list of the upcoming events."""
    now = datetime.datetime.now()
    events = Event.published_objects.filter(start_date__gte=now.date())[:count]
    context = {"events": events}
    return context

