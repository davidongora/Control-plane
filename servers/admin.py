from django.contrib import admin
from .models import Server, Service, NginxSite, Project, ServerHealthMetrics


@admin.register(Server)
class ServerAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'hostname', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'hostname', 'ip_address']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'server', 'service_type', 'status', 'pid', 'last_checked']
    list_filter = ['service_type', 'status']
    search_fields = ['name', 'server__name']


@admin.register(NginxSite)
class NginxSiteAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'server', 'domain', 'is_enabled', 'has_ssl']
    list_filter = ['is_enabled', 'has_ssl']
    search_fields = ['site_name', 'domain', 'server__name']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'server', 'project_type', 'is_active', 'last_deployed']
    list_filter = ['project_type', 'is_active']
    search_fields = ['name', 'server__name', 'path']


@admin.register(ServerHealthMetrics)
class ServerHealthMetricsAdmin(admin.ModelAdmin):
    list_display = ['server', 'cpu_usage', 'memory_usage', 'disk_usage', 'timestamp']
    list_filter = ['server', 'timestamp']
    readonly_fields = ['timestamp']
