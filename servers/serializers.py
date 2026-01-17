"""Serializers for the servers app."""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Server, Service, NginxSite, Project, ServerHealthMetrics, DatabaseClient


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class ServerSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    services_count = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Server
        fields = [
            'id', 'name', 'hostname', 'ip_address', 'port', 'username',
            'description', 'is_active', 'created_at', 'updated_at',
            'created_by', 'services_count', 'projects_count'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']
    
    def get_services_count(self, obj):
        return obj.services.count()
    
    def get_projects_count(self, obj):
        return obj.projects.count()


class ServerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating servers with sensitive credentials."""
    
    class Meta:
        model = Server
        fields = [
            'id', 'name', 'hostname', 'ip_address', 'port', 'username',
            'ssh_key', 'password', 'description', 'is_active'
        ]


class ServiceSerializer(serializers.ModelSerializer):
    server_name = serializers.CharField(source='server.name', read_only=True)
    
    class Meta:
        model = Service
        fields = [
            'id', 'server', 'server_name', 'name', 'service_type', 'status',
            'port', 'pid', 'cpu_usage', 'memory_usage', 'config_path', 'last_checked'
        ]
        read_only_fields = ['last_checked']


class NginxSiteSerializer(serializers.ModelSerializer):
    server_name = serializers.CharField(source='server.name', read_only=True)
    
    class Meta:
        model = NginxSite
        fields = [
            'id', 'server', 'server_name', 'site_name', 'domain', 'config_path',
            'is_enabled', 'has_ssl', 'ssl_cert_path', 'ssl_key_path',
            'upstream_port', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    server_name = serializers.CharField(source='server.name', read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'server', 'server_name', 'name', 'path', 'project_type',
            'branch', 'repository_url', 'is_active', 'last_deployed', 'created_at'
        ]
        read_only_fields = ['created_at']


class ServerHealthMetricsSerializer(serializers.ModelSerializer):
    server_name = serializers.CharField(source='server.name', read_only=True)
    
    class Meta:
        model = ServerHealthMetrics
        fields = [
            'id', 'server', 'server_name', 'cpu_usage', 'memory_usage',
            'disk_usage', 'network_in', 'network_out', 'timestamp'
        ]
        read_only_fields = ['timestamp']


class DatabaseClientSerializer(serializers.ModelSerializer):
    server_name = serializers.CharField(source='server.name', read_only=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = DatabaseClient
        fields = [
            'id', 'server', 'server_name', 'name', 'db_type', 'database_name',
            'host', 'port', 'username', 'password', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password', None)
        db_client = DatabaseClient(**validated_data)
        if password:
            db_client.set_password(password)
        db_client.save()
        return db_client
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
