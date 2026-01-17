"""WebSocket consumers for real-time updates."""
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from .models import Server, Service, ServerHealthMetrics
from .ssh_manager import SSHConnectionManager


class HealthMonitorConsumer(AsyncWebsocketConsumer):
    """Consumer for real-time server health monitoring."""
    
    async def connect(self):
        """Accept WebSocket connection."""
        self.server_id = self.scope['url_route']['kwargs'].get('server_id')
        self.room_group_name = f'server_health_{self.server_id}'
        self.monitoring = False
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Start monitoring task
        self.monitoring = True
        asyncio.create_task(self.monitor_health())
    
    async def disconnect(self, close_code):
        """Leave room group and stop monitoring."""
        self.monitoring = False
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'get_health':
                # Manually trigger health check
                await self.send_health_update()
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def monitor_health(self):
        """Continuously monitor server health and send updates."""
        while self.monitoring:
            try:
                await self.send_health_update()
                await asyncio.sleep(10)  # Send updates every 10 seconds
            except Exception as e:
                print(f"Error in health monitoring: {e}")
                await asyncio.sleep(10)
    
    async def send_health_update(self):
        """Fetch and send current health metrics."""
        try:
            health_data = await self.get_server_health()
            
            if health_data:
                await self.send(text_data=json.dumps({
                    'type': 'health_update',
                    'data': health_data
                }))
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Unable to fetch health data'
                }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    @database_sync_to_async
    def get_server_health(self):
        """Get server health metrics via SSH."""
        try:
            server = Server.objects.get(id=self.server_id)
            
            with SSHConnectionManager(
                hostname=server.ip_address,
                port=server.port,
                username=server.username,
                password=server.password,
                ssh_key=server.ssh_key
            ) as ssh:
                if not ssh.client:
                    return {
                        'server_id': self.server_id,
                        'connected': False,
                        'error': 'Cannot connect to server'
                    }
                
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
                
                # Get network stats
                _, net_in, _ = ssh.execute_command(
                    "cat /sys/class/net/eth0/statistics/rx_bytes 2>/dev/null || echo 0"
                )
                _, net_out, _ = ssh.execute_command(
                    "cat /sys/class/net/eth0/statistics/tx_bytes 2>/dev/null || echo 0"
                )
                
                health_data = {
                    'server_id': self.server_id,
                    'connected': True,
                    'cpu_usage': float(cpu_out.strip()) if cpu_out.strip() else 0,
                    'memory_usage': float(mem_out.strip()) if mem_out.strip() else 0,
                    'disk_usage': float(disk_out.strip()) if disk_out.strip() else 0,
                    'network_in': float(net_in.strip()) if net_in.strip() else 0,
                    'network_out': float(net_out.strip()) if net_out.strip() else 0,
                }
                
                # Store metrics
                ServerHealthMetrics.objects.create(
                    server=server,
                    cpu_usage=health_data['cpu_usage'],
                    memory_usage=health_data['memory_usage'],
                    disk_usage=health_data['disk_usage'],
                    network_in=health_data['network_in'],
                    network_out=health_data['network_out']
                )
                
                return health_data
                
        except ObjectDoesNotExist:
            return {
                'server_id': self.server_id,
                'connected': False,
                'error': 'Server not found'
            }
        except Exception as e:
            return {
                'server_id': self.server_id,
                'connected': False,
                'error': str(e)
            }
    
    async def health_update(self, event):
        """Handle health update messages from channel layer."""
        await self.send(text_data=json.dumps({
            'type': 'health_update',
            'data': event['data']
        }))


class ServiceStatusConsumer(AsyncWebsocketConsumer):
    """Consumer for real-time service status updates."""
    
    async def connect(self):
        """Accept WebSocket connection."""
        self.server_id = self.scope['url_route']['kwargs'].get('server_id')
        self.room_group_name = f'service_status_{self.server_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial service status
        await self.send_service_status()
    
    async def disconnect(self, close_code):
        """Leave room group."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'get_status':
                await self.send_service_status()
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def send_service_status(self):
        """Fetch and send current service status."""
        try:
            services_data = await self.get_services_status()
            
            await self.send(text_data=json.dumps({
                'type': 'service_status',
                'data': services_data
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    @database_sync_to_async
    def get_services_status(self):
        """Get current status of all services on the server."""
        try:
            services = Service.objects.filter(server_id=self.server_id)
            
            return [
                {
                    'id': service.id,
                    'name': service.name,
                    'service_type': service.service_type,
                    'status': service.status,
                    'port': service.port,
                    'pid': service.pid,
                    'cpu_usage': service.cpu_usage,
                    'memory_usage': service.memory_usage,
                }
                for service in services
            ]
        except Exception as e:
            return []
    
    async def service_status_update(self, event):
        """Handle service status update messages from channel layer."""
        await self.send(text_data=json.dumps({
            'type': 'service_status',
            'data': event['data']
        }))


class ServerStatusConsumer(AsyncWebsocketConsumer):
    """Consumer for real-time server connection status."""
    
    async def connect(self):
        """Accept WebSocket connection."""
        self.room_group_name = 'server_status'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send initial server list status
        await self.send_server_status()
    
    async def disconnect(self, close_code):
        """Leave room group."""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'get_status':
                await self.send_server_status()
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def send_server_status(self):
        """Fetch and send all servers status."""
        try:
            servers_data = await self.get_all_servers()
            
            await self.send(text_data=json.dumps({
                'type': 'server_status',
                'data': servers_data
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
    
    @database_sync_to_async
    def get_all_servers(self):
        """Get all servers with their connection status."""
        try:
            servers = Server.objects.all()
            
            return [
                {
                    'id': server.id,
                    'name': server.name,
                    'ip_address': server.ip_address,
                    'is_active': server.is_active,
                }
                for server in servers
            ]
        except Exception as e:
            return []
    
    async def server_status_update(self, event):
        """Handle server status update messages from channel layer."""
        await self.send(text_data=json.dumps({
            'type': 'server_status',
            'data': event['data']
        }))
