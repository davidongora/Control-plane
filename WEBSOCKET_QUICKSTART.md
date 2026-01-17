# Quick Start Guide for WebSocket Implementation

This guide helps you quickly set up and test the new WebSocket real-time updates feature.

## Prerequisites

1. **Redis Server** (required for Django Channels)
2. **Python 3.8+** with virtual environment
3. **Node.js 18+** and npm

## Backend Setup

### 1. Install Dependencies

Dependencies are already in `requirements.txt`:
```bash
cd /home/runner/work/Control-plane/Control-plane
pip install -r requirements.txt
```

Key packages:
- `channels>=4.0.0` - Django Channels framework
- `channels-redis>=4.1.0` - Redis channel layer
- `daphne>=4.0.0` - ASGI server

### 2. Start Redis

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

**macOS:**
```bash
brew install redis
brew services start redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 redis:alpine
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

### 3. Run Database Migrations

```bash
python manage.py migrate
```

### 4. Start the Backend Server

**Option A: Using Django's runserver (uses Daphne automatically)**
```bash
python manage.py runserver
```

**Option B: Using Daphne directly**
```bash
daphne -b 0.0.0.0 -p 8000 control_plane_backend.asgi:application
```

**With multiple workers (production):**
```bash
daphne -b 0.0.0.0 -p 8000 -w 4 control_plane_backend.asgi:application
```

The server should start on `http://localhost:8000`

## Frontend Setup

### 1. Install Dependencies

```bash
cd control-plane-frontend
npm install
```

### 2. Start the Development Server

```bash
npm start
# or
ng serve
```

The frontend will be available at `http://localhost:4200`

## Testing WebSocket Connections

### 1. Using Browser Console

Open browser console (F12) on `http://localhost:4200` and run:

```javascript
// Test health monitoring WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/health/1/');
ws.onopen = () => console.log('Connected to health monitor');
ws.onmessage = (e) => console.log('Health update:', JSON.parse(e.data));
ws.onerror = (e) => console.error('WebSocket error:', e);
```

### 2. Check Connection Status in UI

1. Navigate to the **Dashboard** (`http://localhost:4200`)
2. Look for the connection status indicator in the top-right corner:
   - 🟢 **"Live Updates"** - WebSocket connected
   - 🔴 **"Offline Mode"** - Polling fallback

3. Navigate to **Server Health** page for a server
4. You should see real-time updates every 10 seconds

### 3. Test Reconnection

1. Stop Redis: `sudo systemctl stop redis-server` (or `brew services stop redis`)
2. Watch the UI switch to "Offline Mode"
3. Start Redis again: `sudo systemctl start redis-server`
4. The UI should automatically reconnect and switch to "Live Updates"

## Verifying the Setup

### Check Backend is Running

```bash
# Check if Daphne is running
ps aux | grep daphne

# Check if port 8000 is listening
netstat -tlnp | grep 8000
# or on macOS:
lsof -i :8000
```

### Check Redis Connection

```bash
# Connect to Redis CLI
redis-cli

# Inside Redis CLI, test:
127.0.0.1:6379> ping
PONG

127.0.0.1:6379> keys *
# Should show some keys when WebSockets are active

127.0.0.1:6379> monitor
# Shows real-time Redis commands (useful for debugging)
```

### Check WebSocket Handshake

1. Open browser DevTools (F12)
2. Go to **Network** tab
3. Filter by **WS** (WebSocket)
4. Reload the page
5. You should see WebSocket connections with status "101 Switching Protocols"

## Common Issues and Solutions

### Issue: WebSocket Connection Fails

**Symptom:** Connection status shows "Offline Mode"

**Solutions:**
1. **Check Redis:**
   ```bash
   redis-cli ping
   ```
   If it fails, start Redis

2. **Check Backend Logs:**
   Look for errors in the terminal running Django/Daphne

3. **Check Firewall:**
   Ensure port 8000 is not blocked

4. **Check CORS Settings:**
   Verify `settings.py` has:
   ```python
   ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']
   ```

### Issue: "Cannot connect to Redis"

**Symptom:** Backend error about Redis connection

**Solutions:**
1. Check if Redis is running:
   ```bash
   sudo systemctl status redis-server
   ```

2. Check Redis configuration in `settings.py`:
   ```python
   CHANNEL_LAYERS = {
       'default': {
           'BACKEND': 'channels_redis.core.RedisChannelLayer',
           'CONFIG': {
               'hosts': [('127.0.0.1', 6379)],
           },
       },
   }
   ```

3. Test Redis connection manually:
   ```python
   # In Django shell: python manage.py shell
   from channels.layers import get_channel_layer
   channel_layer = get_channel_layer()
   ```

### Issue: No Real-time Updates

**Symptom:** WebSocket connects but no updates appear

**Solutions:**
1. Check if you have servers configured in the database
2. Verify servers have valid SSH credentials
3. Check backend console for SSH connection errors
4. Monitor Redis: `redis-cli monitor`

### Issue: Frontend Build Errors

**Symptom:** TypeScript compilation errors

**Solutions:**
1. Clear node_modules and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```

2. Check Angular version compatibility:
   ```bash
   ng version
   ```

## Development Tips

### Watch Backend Logs
```bash
# In the backend terminal, you'll see WebSocket connection logs:
python manage.py runserver
# Output should show:
# WebSocket CONNECT /ws/health/1/
# WebSocket DISCONNECT /ws/health/1/
```

### Monitor Redis Activity
```bash
# Terminal 1: Monitor Redis commands
redis-cli monitor

# Terminal 2: Check Redis info
redis-cli info
```

### Debug Frontend WebSocket
```javascript
// In browser console
// Enable verbose logging for WebSocketService
localStorage.setItem('debug', 'WebSocket*');
```

## Production Deployment

For production deployment:

1. **Use WSS (WebSocket Secure):**
   - Configure Nginx/Apache as WebSocket proxy
   - Use SSL certificates

2. **Scale Redis:**
   - Use Redis Sentinel for high availability
   - Consider Redis Cluster for large deployments

3. **Run Daphne with Workers:**
   ```bash
   daphne -b 0.0.0.0 -p 8000 -w 4 control_plane_backend.asgi:application
   ```

4. **Use Process Manager:**
   - Systemd for Linux
   - PM2 for Node.js-based deployments
   - Supervisor as an alternative

See `WEBSOCKET_IMPLEMENTATION.md` for detailed production setup.

## Next Steps

1. ✅ Verify WebSocket connections work
2. ✅ Add some servers via the UI
3. ✅ Watch real-time health updates
4. ✅ Test service status changes
5. ✅ Test reconnection by stopping/starting Redis

For detailed documentation, see:
- `WEBSOCKET_IMPLEMENTATION.md` - Comprehensive technical documentation
- `DEPLOYMENT.md` - Production deployment guide (if exists)
- `QUICKSTART.md` - General quickstart guide
