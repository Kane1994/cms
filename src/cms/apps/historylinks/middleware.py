"""Middleware used by the history links service."""

from django.shortcuts import redirect
from cms.apps.historylinks.models import HistoryLink


class PermalinkFallbackMiddleware(object):
    
    """Middleware that attempts to rescue 404 responses with a redirect to it's new location."""
    
    def process_response(self, request, response):
        """Attempts to rescue 404 responses."""
        if response.status_code == 404:
            # Try to rescue the response.
            try:
                link = HistoryLink.objects.get(path=request.path)
                return redirect(link.object, permanent=True)
            except HistoryLink.DoesNotExist:
                pass
        return response