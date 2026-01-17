"""URL configuration for servers app."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import auth_views

router = DefaultRouter()
router.register(r'servers', views.ServerViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'nginx-sites', views.NginxSiteViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'health-metrics', views.ServerHealthMetricsViewSet)
router.register(r'database-clients', views.DatabaseClientViewSet)
router.register(r'users', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/csrf/', auth_views.csrf_token_view, name='csrf-token'),
    path('auth/login/', auth_views.login_view, name='login'),
    path('auth/logout/', auth_views.logout_view, name='logout'),
    path('auth/user/', auth_views.user_view, name='current-user'),
]
