# WebSocket Real-time Updates

This document describes the real-time WebSocket functionality implemented in the Control Plane application.

## Overview

The Control Plane application now supports real-time updates via WebSocket connections for:
- Server health metrics (CPU, memory, disk usage)
- Service status changes
- Server connection status

The system gracefully degrades to polling if WebSocket connections fail.

## Backend (Django Channels)

### Configuration

The backend uses Django Channels with Redis as the channel layer.

#### settings.py
```python
INSTALLED_APPS = [
    'daphne',  # ASGI server (must be first)
    'channels',
    # ... other apps
]

ASGI_APPLICATION = 'control_plane_backend.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

### WebSocket Endpoints

| Endpoint | Purpose | Update Interval |
|----------|---------|-----------------|
| `ws/health/<server_id>/` | Server health metrics | 10 seconds |
| `ws/services/<server_id>/` | Service status updates | On-demand |
| `ws/servers/` | All servers status | On-demand |

### Consumers

#### HealthMonitorConsumer
- **Path**: `ws/health/<server_id>/`
- **Purpose**: Real-time server health monitoring
- **Update Frequency**: Every 10 seconds
- **Message Format**:
```json
{
  "type": "health_update",
  "data": {
    "server_id": 1,
    "connected": true,
    "cpu_usage": 45.2,
    "memory_usage": 68.5,
    "disk_usage": 72.3,
    "network_in": 1234567,
    "network_out": 987654
  }
}
```

#### ServiceStatusConsumer
- **Path**: `ws/services/<server_id>/`
- **Purpose**: Real-time service status updates
- **Update Frequency**: On-demand (triggered by service actions)
- **Message Format**:
```json
{
  "type": "service_status",
  "data": [
    {
      "id": 1,
      "name": "nginx",
      "service_type": "nginx",
      "status": "running",
      "port": 80,
      "pid": 1234,
      "cpu_usage": 2.5,
      "memory_usage": 45.0
    }
  ]
}
```

#### ServerStatusConsumer
- **Path**: `ws/servers/`
- **Purpose**: Monitor all servers connection status
- **Update Frequency**: On-demand
- **Message Format**:
```json
{
  "type": "server_status",
  "data": [
    {
      "id": 1,
      "name": "Production Server",
      "ip_address": "192.168.1.100",
      "is_active": true
    }
  ]
}
```

### Running the Server

Use Daphne (ASGI server) instead of Django's development server:

```bash
# Development
daphne -b 0.0.0.0 -p 8000 control_plane_backend.asgi:application

# Production (with workers)
daphne -b 0.0.0.0 -p 8000 -w 4 control_plane_backend.asgi:application
```

Or use the standard Django runserver (which will use Daphne automatically):
```bash
python manage.py runserver
```

### Redis Requirement

Ensure Redis is running:
```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS

# Start Redis
redis-server
```

## Frontend (Angular)

### WebSocket Service

The `WebSocketService` handles all WebSocket connections with automatic reconnection.

#### Key Features
- Automatic reconnection (max 5 attempts)
- Connection status monitoring
- Multiple concurrent connections
- Graceful error handling

#### Usage Example

```typescript
import { WebSocketService, WebSocketMessage } from '../../services/websocket.service';

constructor(private wsService: WebSocketService) {}

ngOnInit() {
  // Connect to WebSocket
  this.wsService.connect('ws/health/1/').subscribe({
    next: (message: WebSocketMessage) => {
      if (message.type === 'health_update') {
        this.handleHealthUpdate(message.data);
      }
    }
  });

  // Monitor connection status
  this.wsService.getConnectionStatus('ws/health/1/').subscribe({
    next: (connected) => {
      this.wsConnected = connected;
    }
  });
}

ngOnDestroy() {
  // Clean up connection
  this.wsService.disconnect('ws/health/1/');
}
```

### Updated Components

#### Dashboard Component
- Displays connection status indicator
- Receives real-time server status updates
- Falls back to polling (30s) if WebSocket disconnects

#### ServerHealth Component
- Real-time health metrics updates (every 10 seconds)
- Live connection status indicator
- Automatic fallback to polling

#### Services Component
- Real-time service status updates
- Monitors multiple servers simultaneously
- Connection status per server

### Connection Status Indicator

All components display a visual connection status:
- 🟢 **Green (pulsing)**: Live Updates - WebSocket connected
- 🔴 **Red**: Offline Mode - Using polling fallback

## Message Types

### Client to Server

#### Request Health Update
```json
{
  "type": "get_health"
}
```

#### Request Service Status
```json
{
  "type": "get_status"
}
```

### Server to Client

#### Health Update
```json
{
  "type": "health_update",
  "data": { /* health metrics */ }
}
```

#### Service Status Update
```json
{
  "type": "service_status",
  "data": [ /* array of services */ ]
}
```

#### Server Status Update
```json
{
  "type": "server_status",
  "data": [ /* array of servers */ ]
}
```

#### Error Message
```json
{
  "type": "error",
  "message": "Error description"
}
```

## Graceful Degradation

If WebSocket connections fail:

1. **Frontend**: Automatically falls back to HTTP polling (30-second intervals)
2. **User Notification**: Connection status indicator shows "Offline Mode"
3. **Reconnection**: Attempts to reconnect up to 5 times with 5-second intervals
4. **Data Continuity**: REST API endpoints remain available as fallback

## Security Considerations

1. **Authentication**: WebSocket connections use Django session authentication
2. **CORS**: Configured for localhost:4200 (development)
3. **Origin Validation**: `AllowedHostsOriginValidator` prevents unauthorized connections
4. **SSL/TLS**: Use WSS protocol in production with proper certificates

## Performance

- **Update Frequency**: 10 seconds for health metrics (configurable)
- **Connection Pooling**: Redis handles multiple concurrent connections
- **Bandwidth**: ~200-500 bytes per health update
- **Scalability**: Redis channel layer supports horizontal scaling

## Troubleshooting

### WebSocket Connection Fails

1. **Check Redis**:
   ```bash
   redis-cli ping  # Should return PONG
   ```

2. **Check ASGI Server**:
   ```bash
   # Ensure Daphne is running
   ps aux | grep daphne
   ```

3. **Check Firewall**:
   ```bash
   # Ensure port 8000 is accessible
   sudo netstat -tlnp | grep 8000
   ```

### Frontend Connection Issues

1. **Check WebSocket URL**: Verify environment.apiUrl in Angular
2. **Browser Console**: Check for WebSocket errors
3. **Network Tab**: Verify WebSocket handshake (101 Switching Protocols)

### Redis Connection Issues

1. **Test Redis Connection**:
   ```python
   # In Django shell
   from channels.layers import get_channel_layer
   channel_layer = get_channel_layer()
   # Should not raise exceptions
   ```

## Environment Variables

### Backend (.env)
```env
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

### Frontend (environment.ts)
```typescript
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000'  // WebSocket will use ws://localhost:8000
};
```

## Testing

### Test WebSocket Connection

1. **Using Browser Console**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/health/1/');
ws.onopen = () => console.log('Connected');
ws.onmessage = (e) => console.log('Message:', JSON.parse(e.data));
```

2. **Using Python**:
```python
import websockets
import asyncio
import json

async def test():
    uri = "ws://localhost:8000/ws/health/1/"
    async with websockets.connect(uri) as websocket:
        message = await websocket.recv()
        print(json.loads(message))

asyncio.run(test())
```

## Production Deployment

1. **Use WSS (WebSocket Secure)**:
   - Configure Nginx/Apache as WebSocket proxy
   - Use SSL certificates

2. **Scale Redis**:
   - Use Redis Sentinel for high availability
   - Consider Redis Cluster for large deployments

3. **Monitor Connections**:
   - Track active WebSocket connections
   - Set connection limits
   - Implement rate limiting

4. **Daphne Configuration**:
```bash
# systemd service example
[Service]
ExecStart=/path/to/venv/bin/daphne -b 0.0.0.0 -p 8000 --workers 4 control_plane_backend.asgi:application
```

## Future Enhancements

- [ ] Add WebSocket authentication tokens
- [ ] Implement rate limiting for WebSocket messages
- [ ] Add broadcast notifications for system events
- [ ] Support for WebSocket compression
- [ ] Add reconnection backoff strategy
- [ ] Implement heartbeat/keepalive mechanism
