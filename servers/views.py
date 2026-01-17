"""Views for the servers app REST API."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Server, Service, NginxSite, Project, ServerHealthMetrics, DatabaseClient
from .serializers import (
    ServerSerializer, ServerCreateSerializer, ServiceSerializer,
    NginxSiteSerializer, ProjectSerializer, ServerHealthMetricsSerializer,
    DatabaseClientSerializer
)
from .ssh_manager import SSHConnectionManager
from .service_managers import ServiceManager, NginxManager, GunicornManager, DatabaseManager
from .database_manager import DatabaseQueryManager


class ServerViewSet(viewsets.ModelViewSet):
    """ViewSet for managing servers."""
    queryset = Server.objects.all()
    permission_classes = []  # AllowAny for demo
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ServerCreateSerializer
        return ServerSerializer
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test SSH connection to a server."""
        server = self.get_object()
        ssh = SSHConnectionManager(
            hostname=server.ip_address,
            port=server.port,
            username=server.username,
            password=server.password,
            ssh_key=server.ssh_key
        )
        
        if ssh.connect():
            exit_code, stdout, stderr = ssh.execute_command('uname -a')
            ssh.disconnect()
            
            if exit_code == 0:
                return Response({
                    'success': True,
                    'message': 'Connection successful',
                    'system_info': stdout
                })
        
        return Response({
            'success': False,
            'message': 'Connection failed'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def health(self, request, pk=None):
        """Get real-time health metrics for a server."""
        server = self.get_object()
        
        with SSHConnectionManager(
            hostname=server.ip_address,
            port=server.port,
            username=server.username,
            password=server.password,
            ssh_key=server.ssh_key
        ) as ssh:
            if not ssh.client:
                return Response({'error': 'Cannot connect to server'}, 
                              status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # Get CPU usage
            _, cpu_out, _ = ssh.execute_command(
                "top -bn1 | grep 'Cpu(s)' | sed 's/.*, *\\([0-9.]*\\)%* id.*/\\1/' | awk '{print 100 - $1}'"
            )
            
            # Get memory usage
            _, mem_out, _ = ssh.execute_command(
                "free | grep Mem | awk '{print ($3/$2) * 100.0}'"
            )
            
            # Get disk usage
            _, disk_out, _ = ssh.execute_command(
                "df -h / | tail -1 | awk '{print $5}' | sed 's/%//'"
            )
            
            try:
                health_data = {
                    'cpu_usage': float(cpu_out.strip()) if cpu_out.strip() else 0,
                    'memory_usage': float(mem_out.strip()) if mem_out.strip() else 0,
                    'disk_usage': float(disk_out.strip()) if disk_out.strip() else 0,
                }
                
                # Store metrics
                ServerHealthMetrics.objects.create(
                    server=server,
                    **health_data
                )
                
                return Response(health_data)
            except ValueError:
                return Response({'error': 'Failed to parse health metrics'}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def services_status(self, request, pk=None):
        """Get status of all services on a server."""
        server = self.get_object()
        
        with SSHConnectionManager(
            hostname=server.ip_address,
            port=server.port,
            username=server.username,
            password=server.password,
            ssh_key=server.ssh_key
        ) as ssh:
            if not ssh.client:
                return Response({'error': 'Cannot connect to server'}, 
                              status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            service_manager = ServiceManager(ssh)
            services_data = []
            
            # Check common services
            for service_name in ['nginx', 'gunicorn', 'postgresql', 'mysql', 'redis-server']:
                service_status = service_manager.get_service_status(service_name)
                if service_status['status'] != 'unknown':
                    services_data.append(service_status)
            
            return Response(services_data)


class ServiceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing services."""
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = []  # AllowAny for demo
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a service."""
        service = self.get_object()
        server = service.server
        
        with SSHConnectionManager(
            hostname=server.ip_address,
            port=server.port,
            username=server.username,
            password=server.password,
            ssh_key=server.ssh_key
        ) as ssh:
            if ssh.client:
                service_manager = ServiceManager(ssh)
                success = service_manager.start_service(service.name)
                
                if success:
                    service.status = 'running'
                    service.save()
                    return Response({'success': True, 'message': 'Service started'})
        
        return Response({'success': False, 'message': 'Failed to start service'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def stop(self, request, pk=None):
        """Stop a service."""
        service = self.get_object()
        server = service.server
        
        with SSHConnectionManager(
            hostname=server.ip_address,
            port=server.port,
            username=server.username,
            password=server.password,
            ssh_key=server.ssh_key
        ) as ssh:
            if ssh.client:
                service_manager = ServiceManager(ssh)
                success = service_manager.stop_service(service.name)
                
                if success:
                    service.status = 'stopped'
                    service.save()
                    return Response({'success': True, 'message': 'Service stopped'})
        
        return Response({'success': False, 'message': 'Failed to stop service'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def restart(self, request, pk=None):
        """Restart a service."""
        service = self.get_object()
        server = service.server
        
        with SSHConnectionManager(
            hostname=server.ip_address,
            port=server.port,
            username=server.username,
            password=server.password,
            ssh_key=server.ssh_key
        ) as ssh:
            if ssh.client:
                service_manager = ServiceManager(ssh)
                success = service_manager.restart_service(service.name)
                
                if success:
                    service.status = 'running'
                    service.save()
                    return Response({'success': True, 'message': 'Service restarted'})
        
        return Response({'success': False, 'message': 'Failed to restart service'}, 
                       status=status.HTTP_400_BAD_REQUEST)


class NginxSiteViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Nginx sites."""
    queryset = NginxSite.objects.all()
    serializer_class = NginxSiteSerializer
    permission_classes = []  # AllowAny for demo
    
    @action(detail=True, methods=['post'])
    def enable(self, request, pk=None):
        """Enable an Nginx site."""
        site = self.get_object()
        server = site.server
        
        with SSHConnectionManager(
            hostname=server.ip_address,
            port=server.port,
            username=server.username,
            password=server.password,
            ssh_key=server.ssh_key
        ) as ssh:
            if ssh.client:
                nginx_manager = NginxManager(ssh)
                success = nginx_manager.enable_site(site.site_name)
                
                if success:
                    site.is_enabled = True
                    site.save()
                    return Response({'success': True, 'message': 'Site enabled'})
        
        return Response({'success': False, 'message': 'Failed to enable site'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def disable(self, request, pk=None):
        """Disable an Nginx site."""
        site = self.get_object()
        server = site.server
        
        with SSHConnectionManager(
            hostname=server.ip_address,
            port=server.port,
            username=server.username,
            password=server.password,
            ssh_key=server.ssh_key
        ) as ssh:
            if ssh.client:
                nginx_manager = NginxManager(ssh)
                success = nginx_manager.disable_site(site.site_name)
                
                if success:
                    site.is_enabled = False
                    site.save()
                    return Response({'success': True, 'message': 'Site disabled'})
        
        return Response({'success': False, 'message': 'Failed to disable site'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def config(self, request, pk=None):
        """Get site configuration content."""
        site = self.get_object()
        server = site.server
        
        with SSHConnectionManager(
            hostname=server.ip_address,
            port=server.port,
            username=server.username,
            password=server.password,
            ssh_key=server.ssh_key
        ) as ssh:
            if ssh.client:
                nginx_manager = NginxManager(ssh)
                config = nginx_manager.get_site_config(site.site_name)
                
                if config:
                    return Response({'config': config})
        
        return Response({'error': 'Failed to get configuration'}, 
                       status=status.HTTP_400_BAD_REQUEST)


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for managing projects."""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = []  # AllowAny for demo


class ServerHealthMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing server health metrics."""
    queryset = ServerHealthMetrics.objects.all()
    serializer_class = ServerHealthMetricsSerializer
    permission_classes = []  # AllowAny for demo
    
    def get_queryset(self):
        queryset = super().get_queryset()
        server_id = self.request.query_params.get('server_id', None)
        if server_id:
            queryset = queryset.filter(server_id=server_id)
        return queryset[:100]  # Limit to last 100 records


class DatabaseClientViewSet(viewsets.ModelViewSet):
    """ViewSet for managing database clients."""
    queryset = DatabaseClient.objects.all()
    serializer_class = DatabaseClientSerializer
    permission_classes = []  # AllowAny for demo
    
    def get_queryset(self):
        queryset = super().get_queryset()
        server_id = self.request.query_params.get('server_id', None)
        if server_id:
            queryset = queryset.filter(server_id=server_id)
        return queryset
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test database connection."""
        db_client = self.get_object()
        
        try:
            db_manager = DatabaseQueryManager(
                db_type=db_client.db_type,
                host=db_client.get_host(),
                port=db_client.get_port(),
                database=db_client.database_name,
                username=db_client.username,
                password=db_client.get_password()
            )
            
            success, message = db_manager.test_connection()
            
            if success:
                return Response({
                    'success': True,
                    'message': message
                })
            else:
                return Response({
                    'success': False,
                    'message': message
                }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'success': False,
                'message': f"Connection test failed: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def tables(self, request, pk=None):
        """List all tables in the database."""
        db_client = self.get_object()
        
        try:
            db_manager = DatabaseQueryManager(
                db_type=db_client.db_type,
                host=db_client.get_host(),
                port=db_client.get_port(),
                database=db_client.database_name,
                username=db_client.username,
                password=db_client.get_password()
            )
            
            result = db_manager.list_tables()
            
            if result['success']:
                return Response(result)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'tables': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def table_schema(self, request, pk=None):
        """Get schema for a specific table."""
        db_client = self.get_object()
        table_name = request.query_params.get('table_name')
        
        if not table_name:
            return Response({
                'success': False,
                'error': 'table_name parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            db_manager = DatabaseQueryManager(
                db_type=db_client.db_type,
                host=db_client.get_host(),
                port=db_client.get_port(),
                database=db_client.database_name,
                username=db_client.username,
                password=db_client.get_password()
            )
            
            result = db_manager.get_table_schema(table_name)
            
            if result['success']:
                return Response(result)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'columns': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def query(self, request, pk=None):
        """Execute a database query."""
        db_client = self.get_object()
        query = request.data.get('query', '').strip()
        allow_write = request.data.get('allow_write', False)
        page = int(request.data.get('page', 1))
        page_size = int(request.data.get('page_size', 100))
        
        if not query:
            return Response({
                'success': False,
                'error': 'Query is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            db_manager = DatabaseQueryManager(
                db_type=db_client.db_type,
                host=db_client.get_host(),
                port=db_client.get_port(),
                database=db_client.database_name,
                username=db_client.username,
                password=db_client.get_password()
            )
            
            result = db_manager.execute_query(
                query=query,
                allow_write=allow_write,
                page=page,
                page_size=page_size
            )
            
            if result['success']:
                return Response(result)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'columns': [],
                'rows': [],
                'total_rows': 0
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def records(self, request, pk=None):
        """Get records from a table with pagination."""
        db_client = self.get_object()
        table_name = request.query_params.get('table_name')
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 100))
        
        if not table_name:
            return Response({
                'success': False,
                'error': 'table_name parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Construct a safe SELECT query
        query = f"SELECT * FROM {table_name}"
        
        try:
            db_manager = DatabaseQueryManager(
                db_type=db_client.db_type,
                host=db_client.get_host(),
                port=db_client.get_port(),
                database=db_client.database_name,
                username=db_client.username,
                password=db_client.get_password()
            )
            
            result = db_manager.execute_query(
                query=query,
                allow_write=False,
                page=page,
                page_size=page_size
            )
            
            if result['success']:
                return Response(result)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e),
                'columns': [],
                'rows': [],
                'total_rows': 0
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
