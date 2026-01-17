from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_ipv4_address

class Server(models.Model):
    """Model representing a managed Linux server."""
    name = models.CharField(max_length=255, unique=True)
    hostname = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(validators=[validate_ipv4_address])
    port = models.IntegerField(default=22)
    username = models.CharField(max_length=100)
    ssh_key = models.TextField(blank=True, null=True, help_text="SSH private key for authentication")
    password = models.CharField(max_length=255, blank=True, null=True, help_text="Password (encrypted)")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='servers')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.ip_address})"


class Service(models.Model):
    """Model representing a service running on a server."""
    SERVICE_TYPES = [
        ('nginx', 'Nginx'),
        ('gunicorn', 'Gunicorn'),
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('redis', 'Redis'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('stopped', 'Stopped'),
        ('failed', 'Failed'),
        ('unknown', 'Unknown'),
    ]
    
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=255)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    port = models.IntegerField(null=True, blank=True)
    pid = models.IntegerField(null=True, blank=True, help_text="Process ID")
    cpu_usage = models.FloatField(null=True, blank=True, help_text="CPU usage percentage")
    memory_usage = models.FloatField(null=True, blank=True, help_text="Memory usage in MB")
    config_path = models.CharField(max_length=512, blank=True, null=True)
    last_checked = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['server', 'name']
        ordering = ['server', 'name']

    def __str__(self):
        return f"{self.name} on {self.server.name}"


class NginxSite(models.Model):
    """Model representing an Nginx site configuration."""
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='nginx_sites')
    site_name = models.CharField(max_length=255)
    domain = models.CharField(max_length=255)
    config_path = models.CharField(max_length=512)
    is_enabled = models.BooleanField(default=False)
    has_ssl = models.BooleanField(default=False)
    ssl_cert_path = models.CharField(max_length=512, blank=True, null=True)
    ssl_key_path = models.CharField(max_length=512, blank=True, null=True)
    upstream_port = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['server', 'site_name']
        ordering = ['server', 'site_name']

    def __str__(self):
        return f"{self.site_name} on {self.server.name}"


class Project(models.Model):
    """Model representing a deployed project on a server."""
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=512)
    project_type = models.CharField(max_length=50, choices=[
        ('django', 'Django'),
        ('flask', 'Flask'),
        ('node', 'Node.js'),
        ('react', 'React'),
        ('angular', 'Angular'),
        ('other', 'Other'),
    ])
    branch = models.CharField(max_length=100, blank=True, null=True)
    repository_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_deployed = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['server', 'name']
        ordering = ['server', 'name']

    def __str__(self):
        return f"{self.name} on {self.server.name}"


class ServerHealthMetrics(models.Model):
    """Model for storing server health metrics over time."""
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='health_metrics')
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    disk_usage = models.FloatField()
    network_in = models.FloatField(default=0)
    network_out = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['server', '-timestamp']),
        ]

    def __str__(self):
        return f"{self.server.name} metrics at {self.timestamp}"

