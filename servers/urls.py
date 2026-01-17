"""URL configuration for servers app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'servers', views.ServerViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'nginx-sites', views.NginxSiteViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'health-metrics', views.ServerHealthMetricsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
