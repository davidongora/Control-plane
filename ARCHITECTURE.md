# Control Plane Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Web Browser                               │
│                    (User Interface)                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ HTTP/HTTPS
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                 Angular Frontend (Port 4200)                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Components:                                             │   │
│  │  • Dashboard     • Servers      • Services              │   │
│  │  • Nginx Sites   • Projects     • Server Health         │   │
│  └─────────────────────┬───────────────────────────────────┘   │
│                        │                                         │
│  ┌─────────────────────▼───────────────────────────────────┐   │
│  │              API Service (HTTP Client)                   │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ REST API
                         │
┌────────────────────────▼────────────────────────────────────────┐
│              Django Backend (Port 8000)                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              REST API Endpoints                          │   │
│  │  • /api/servers/        • /api/services/                │   │
│  │  • /api/nginx-sites/    • /api/projects/                │   │
│  │  • /api/health-metrics/                                  │   │
│  └─────────────────────┬───────────────────────────────────┘   │
│                        │                                         │
│  ┌─────────────────────▼───────────────────────────────────┐   │
│  │              Business Logic Layer                        │   │
│  │  • Views & ViewSets  • Serializers  • Models            │   │
│  └─────────────────────┬───────────────────────────────────┘   │
│                        │                                         │
│  ┌─────────────────────▼───────────────────────────────────┐   │
│  │            Service Management Layer                      │   │
│  │  ┌──────────────┐ ┌────────────┐ ┌──────────────┐      │   │
│  │  │SSH Manager   │ │Service     │ │Nginx Manager │      │   │
│  │  │(Paramiko)    │ │Manager     │ │              │      │   │
│  │  └──────┬───────┘ └─────┬──────┘ └──────┬───────┘      │   │
│  │         │               │                │              │   │
│  │  ┌──────▼───────────────▼────────────────▼────────┐    │   │
│  │  │      Gunicorn Manager  │  Database Manager     │    │   │
│  │  └───────────────────────────────────────────────┘    │   │
│  └─────────────────────┬───────────────────────────────────┘   │
│                        │                                         │
│  ┌─────────────────────▼───────────────────────────────────┐   │
│  │              Database (SQLite/PostgreSQL)                │   │
│  │  • Server models  • Service data  • Health metrics      │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ SSH Connections
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                  Managed Linux Servers                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Server 1    │  │  Server 2    │  │  Server N    │         │
│  │              │  │              │  │              │         │
│  │ • Nginx      │  │ • Nginx      │  │ • Nginx      │         │
│  │ • Gunicorn   │  │ • Gunicorn   │  │ • Gunicorn   │         │
│  │ • PostgreSQL │  │ • MySQL      │  │ • Redis      │         │
│  │ • Projects   │  │ • Projects   │  │ • Projects   │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (Angular 21)
- **Technology**: TypeScript, Angular 21, CSS
- **Responsibilities**:
  - User interface and interaction
  - API communication
  - Real-time data display
  - Form handling and validation

### Backend (Django 4.2)
- **Technology**: Python, Django, Django REST Framework
- **Responsibilities**:
  - RESTful API endpoints
  - Business logic
  - Data persistence
  - Authentication and authorization
  - SSH connection management

### Service Management Layer
- **SSH Manager**: Handles secure SSH connections using Paramiko
- **Service Manager**: Manages systemd services (start, stop, restart)
- **Nginx Manager**: Handles Nginx configuration and site management
- **Gunicorn Manager**: Manages Gunicorn processes
- **Database Manager**: Interacts with PostgreSQL and MySQL

### Data Models
- **Server**: Linux server information and credentials
- **Service**: Services running on servers
- **NginxSite**: Nginx site configurations
- **Project**: Deployed application projects
- **ServerHealthMetrics**: Historical health data

## Data Flow

### Example: Viewing Server Health

1. User clicks "View Health" on a server in the frontend
2. Angular component calls `api.getServerHealth(serverId)`
3. HTTP GET request to `/api/servers/{id}/health/`
4. Django view receives request
5. SSH Manager establishes connection to target server
6. Service Manager executes system commands (top, free, df)
7. Metrics are parsed and formatted
8. Health metrics saved to database
9. Response sent back to frontend
10. Angular component displays metrics visually

### Example: Managing a Service

1. User clicks "Restart" on a service in the frontend
2. Angular component calls `api.restartService(serviceId)`
3. HTTP POST to `/api/services/{id}/restart/`
4. Django view retrieves service and server info
5. SSH Manager connects to server
6. Service Manager executes `systemctl restart {service}`
7. Service status updated in database
8. Success/failure response sent to frontend
9. Frontend updates UI with new status

## Security Layers

1. **Transport Security**: HTTPS in production
2. **Authentication**: Django session authentication / token auth
3. **Authorization**: Django permissions system
4. **SSH Security**: Key-based authentication preferred
5. **CORS Protection**: Configured allowed origins
6. **Input Validation**: Django and Angular form validation
7. **SQL Injection Protection**: Django ORM
8. **XSS Protection**: Angular's built-in sanitization

## Scalability Considerations

### Current Architecture (Single Server)
- Suitable for managing up to 100 servers
- SQLite for development
- Single Django process

### Future Scalability (If Needed)
- **Database**: PostgreSQL with connection pooling
- **Caching**: Redis for session storage and caching
- **Task Queue**: Celery for background tasks
- **WebSockets**: Django Channels for real-time updates
- **Load Balancing**: Multiple Django workers behind Nginx
- **Monitoring**: Prometheus + Grafana for metrics

## Technology Stack

### Backend
- Python 3.8+
- Django 4.2
- Django REST Framework 3.14
- Paramiko (SSH)
- psutil (System monitoring)

### Frontend
- Angular 21
- TypeScript
- RxJS
- CSS3

### Infrastructure
- Linux (Ubuntu/CentOS)
- Nginx (Reverse proxy)
- Gunicorn (WSGI server)
- PostgreSQL (Production database)
- SQLite (Development database)

## Directory Structure

```
Control-plane/
├── control_plane_backend/     # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── servers/                   # Main Django app
│   ├── models.py             # Data models
│   ├── views.py              # API views
│   ├── serializers.py        # DRF serializers
│   ├── ssh_manager.py        # SSH connection handler
│   ├── service_managers.py   # Service management logic
│   └── urls.py               # API routes
├── control-plane-frontend/    # Angular application
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/   # UI components
│   │   │   └── services/     # API services
│   │   └── styles.css        # Global styles
│   └── angular.json
├── requirements.txt           # Python dependencies
├── manage.py                  # Django management
├── setup.sh                   # Setup script
├── README.md                  # Main documentation
├── QUICKSTART.md             # Quick start guide
└── DEPLOYMENT.md             # Deployment guide
```
