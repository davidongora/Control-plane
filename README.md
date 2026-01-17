# Control-plane

Unified web dashboard built with Python Django and Angular for centralized Linux server management via SSH.

## Screenshots

### Dashboard
![Dashboard](https://github.com/user-attachments/assets/9ca08760-3af2-407e-b666-2b15384f9706)
*Main dashboard showing server statistics and overview*

### Servers Management
![Servers](https://github.com/user-attachments/assets/eb13df3c-1890-419d-9ac8-e330c50efacd)
*Server list with connection details and management options*

### Services Management
![Services](https://github.com/user-attachments/assets/e560539b-4750-4349-9db8-7238dd749a14)
*Service control panel with start/stop/restart capabilities*

### Server Health Monitoring
![Health Monitoring](https://github.com/user-attachments/assets/8ba353ce-bc82-4dda-b049-9e83441406d6)
*Real-time CPU, memory, and disk usage monitoring*

## Overview

Control-plane is a comprehensive server management platform that provides:

- **Centralized Server Management**: Manage multiple Linux servers from a single interface
- **Real-time WebSocket Updates**: Live monitoring with sub-10-second updates for health metrics and service status
- **Service Monitoring**: Real-time monitoring of Nginx, Gunicorn, PostgreSQL, MySQL, Redis and other services
- **Configuration Management**: Configure Nginx sites, SSL certificates, and Gunicorn processes
- **Health Monitoring**: Track CPU, memory, and disk usage across all servers with live updates
- **Project Inventory**: Keep track of deployed projects and applications
- **Database Client**: Web-based SQL query interface for PostgreSQL, MySQL, and SQLite
- **Secure SSH Access**: All operations performed securely via SSH

## Architecture

### Backend (Django)
- **REST API**: Full RESTful API built with Django REST Framework
- **WebSocket Support**: Real-time updates via Django Channels and Redis
- **SSH Management**: Secure SSH connections using Paramiko
- **Service Managers**: Specialized managers for Nginx, Gunicorn, and databases
- **Real-time Monitoring**: Health metrics collection and storage with live streaming
- **Database**: SQLite (development) / PostgreSQL (production)

### Frontend (Angular 21)
- **Modern UI**: Responsive dashboard built with Angular 21
- **WebSocket Integration**: Live updates with automatic reconnection and fallback to polling
- **Real-time Updates**: Live health monitoring and service status (10-second intervals)
- **Connection Status**: Visual indicators showing live/offline mode
- **CRUD Operations**: Full create, read, update, delete for all resources
- **Visual Management**: Intuitive interfaces for server and service management

## Features

### Server Management
- Add and manage multiple Linux servers
- Test SSH connections
- View server inventory and statistics
- Monitor server health in real-time

### Service Management
- List all services across servers
- Start, stop, and restart services
- View service status and resource usage
- Monitor CPU and memory consumption

### Nginx Management
- List all Nginx sites
- Enable/disable sites
- View site configurations
- Manage SSL certificates

### Project Tracking
- Inventory of deployed projects
- Track project types (Django, Flask, Node.js, Angular, etc.)
- Monitor deployment status
- View project paths and repositories

### Health Monitoring
- Real-time CPU usage tracking (WebSocket updates every 10 seconds)
- Memory usage monitoring with live updates
- Disk space utilization tracking
- Network I/O statistics
- Historical metrics storage
- Visual health indicators
- Connection status display (live/offline mode)
- Automatic fallback to polling if WebSocket fails

## Installation

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn
- **Redis Server** (for WebSocket real-time updates)
- SSH access to target servers

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/davidongora/Control-plane.git
cd Control-plane
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Install and start Redis (required for WebSocket support):
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# macOS
brew install redis
brew services start redis

# Docker
docker run -d -p 6379:6379 redis:alpine
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create a superuser:
```bash
python manage.py createsuperuser
```

6. Start the development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`
WebSocket endpoints will be available at `ws://localhost:8000/ws/`
```

5. Start the development server:
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd control-plane-frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will be available at `http://localhost:4200/`

## Usage

### Adding a Server

1. Navigate to the "Servers" page
2. Click "Add Server"
3. Fill in the server details:
   - Name: Friendly name for the server
   - Hostname: Server hostname or domain
   - IP Address: Server IP address
   - Port: SSH port (default: 22)
   - Username: SSH username
   - Authentication: SSH key or password
4. Click "Create Server"
5. Test the connection using the "Test" button

### Monitoring Services

1. Navigate to the "Services" page
2. View all discovered services across your servers
3. Use the action buttons to:
   - Start a stopped service
   - Stop a running service
   - Restart a service
4. Monitor CPU and memory usage in real-time

### Managing Nginx Sites

1. Navigate to the "Nginx Sites" page
2. View all Nginx site configurations
3. Enable or disable sites
4. View site configurations
5. Check SSL status

### Viewing Server Health

1. From the Dashboard or Servers page, click "View Health"
2. See real-time metrics with WebSocket updates every 10 seconds:
   - CPU usage percentage
   - Memory usage percentage
   - Disk usage percentage
   - Network I/O statistics
3. View historical metrics in table format
4. Monitor connection status indicator (green=live, red=offline)

## API Documentation

### REST API Endpoints

### Servers
- `GET /api/servers/` - List all servers
- `POST /api/servers/` - Create a new server
- `GET /api/servers/{id}/` - Get server details
- `PUT /api/servers/{id}/` - Update server
- `DELETE /api/servers/{id}/` - Delete server
- `POST /api/servers/{id}/test_connection/` - Test SSH connection
- `GET /api/servers/{id}/health/` - Get current health metrics
- `GET /api/servers/{id}/services_status/` - Get all services status

### Services
- `GET /api/services/` - List all services
- `POST /api/services/` - Create a service entry
- `GET /api/services/{id}/` - Get service details
- `POST /api/services/{id}/start/` - Start service
- `POST /api/services/{id}/stop/` - Stop service
- `POST /api/services/{id}/restart/` - Restart service

### Nginx Sites
- `GET /api/nginx-sites/` - List all Nginx sites
- `POST /api/nginx-sites/` - Create site entry
- `GET /api/nginx-sites/{id}/` - Get site details
- `POST /api/nginx-sites/{id}/enable/` - Enable site
- `POST /api/nginx-sites/{id}/disable/` - Disable site
- `GET /api/nginx-sites/{id}/config/` - Get site configuration

### Projects
- `GET /api/projects/` - List all projects
- `POST /api/projects/` - Create project entry
- `GET /api/projects/{id}/` - Get project details

### Health Metrics
- `GET /api/health-metrics/?server_id={id}` - Get historical metrics

### WebSocket Endpoints

Real-time updates via WebSocket connections:

- `ws://localhost:8000/ws/health/{server_id}/` - Real-time health monitoring (10-second updates)
- `ws://localhost:8000/ws/services/{server_id}/` - Real-time service status updates
- `ws://localhost:8000/ws/servers/` - All servers connection status

**Message Format:**
```json
{
  "type": "health_update|service_status|server_status",
  "data": { /* update data */ }
}
```

For detailed WebSocket documentation, see [WEBSOCKET_IMPLEMENTATION.md](WEBSOCKET_IMPLEMENTATION.md)

## Security Considerations

1. **SSH Keys**: Store SSH private keys securely, consider using Django's encryption
2. **Passwords**: Passwords should be encrypted before storage
3. **API Authentication**: Use session authentication or token-based auth in production
4. **CORS**: Configure CORS settings for production deployment
5. **HTTPS**: Always use HTTPS in production
6. **Firewall**: Ensure proper firewall rules on managed servers
7. **User Permissions**: Use Django's permission system for access control

## Configuration

### Django Settings
Edit `control_plane_backend/settings.py`:
- `SECRET_KEY`: Change for production
- `DEBUG`: Set to False in production
- `ALLOWED_HOSTS`: Add your domain
- `DATABASES`: Configure PostgreSQL for production
- `CORS_ALLOWED_ORIGINS`: Update for your frontend URL
- `CHANNEL_LAYERS`: Configure Redis for WebSocket support (default: localhost:6379)

### Angular Environment
Edit `control-plane-frontend/src/app/services/api.ts`:
- Update `baseUrl` to your production API URL

## Deployment

### Backend Deployment
1. Set environment variables
2. Configure PostgreSQL database
3. **Install and configure Redis server**
4. Run `python manage.py collectstatic`
5. Use **Daphne** (ASGI server) instead of Gunicorn for WebSocket support
6. Configure Nginx as reverse proxy with WebSocket support

**Start with Daphne:**
```bash
daphne -b 0.0.0.0 -p 8000 control_plane_backend.asgi:application
```

For detailed deployment instructions, see [WEBSOCKET_IMPLEMENTATION.md](WEBSOCKET_IMPLEMENTATION.md#production-deployment)

### Frontend Deployment
1. Build the production bundle: `npm run build`
2. Deploy the `dist/` folder to your web server
3. Configure routing for single-page application

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Quick setup guide
- **[FEATURES.md](FEATURES.md)** - Detailed feature list
- **[WEBSOCKET_IMPLEMENTATION.md](WEBSOCKET_IMPLEMENTATION.md)** - WebSocket real-time updates documentation
- **[WEBSOCKET_QUICKSTART.md](WEBSOCKET_QUICKSTART.md)** - Quick guide to setup WebSocket functionality
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[DATABASE_CLIENT.md](DATABASE_CLIENT.md)** - Database client feature documentation
