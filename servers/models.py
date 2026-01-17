from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_ipv4_address
from cryptography.fernet import Fernet
from django.conf import settings
import base64
import hashlib

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


class DatabaseClient(models.Model):
    """Model representing a database connection for a server."""
    DB_TYPES = [
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('sqlite', 'SQLite'),
    ]
    
    DEFAULT_PORTS = {
        'postgresql': 5432,
        'mysql': 3306,
        'sqlite': None,
    }
    
    server = models.ForeignKey(Server, on_delete=models.CASCADE, related_name='database_clients')
    name = models.CharField(max_length=255, help_text="Connection name")
    db_type = models.CharField(max_length=20, choices=DB_TYPES)
    database_name = models.CharField(max_length=255)
    host = models.CharField(max_length=255, blank=True, null=True, help_text="Defaults to server IP")
    port = models.IntegerField(blank=True, null=True, help_text="Defaults based on db_type")
    username = models.CharField(max_length=100)
    password_encrypted = models.TextField(help_text="Encrypted password")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['server', 'name']
        ordering = ['server', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.db_type}) on {self.server.name}"
    
    def get_encryption_key(self):
        """Generate encryption key from Django SECRET_KEY."""
        secret = settings.SECRET_KEY.encode()
        key = base64.urlsafe_b64encode(hashlib.sha256(secret).digest())
        return key
    
    def set_password(self, raw_password):
        """Encrypt and store password."""
        if raw_password:
            cipher = Fernet(self.get_encryption_key())
            encrypted = cipher.encrypt(raw_password.encode())
            self.password_encrypted = encrypted.decode()
    
    def get_password(self):
        """Decrypt and return password."""
        if self.password_encrypted:
            try:
                cipher = Fernet(self.get_encryption_key())
                decrypted = cipher.decrypt(self.password_encrypted.encode())
                return decrypted.decode()
            except Exception:
                return None
        return None
    
    def get_host(self):
        """Return host, defaulting to server IP if not set."""
        return self.host or self.server.ip_address
    
    def get_port(self):
        """Return port, defaulting based on db_type if not set."""
        return self.port or self.DEFAULT_PORTS.get(self.db_type)

