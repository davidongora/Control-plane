"""WebSocket routing configuration."""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/health/(?P<server_id>\d+)/$', consumers.HealthMonitorConsumer.as_asgi()),
    re_path(r'ws/services/(?P<server_id>\d+)/$', consumers.ServiceStatusConsumer.as_asgi()),
    re_path(r'ws/servers/$', consumers.ServerStatusConsumer.as_asgi()),
]
