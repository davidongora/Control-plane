# Quick Start Guide

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn
- SSH access to at least one Linux server

## Installation

### Option 1: Automated Setup (Recommended)

Run the setup script:

```bash
chmod +x setup.sh
./setup.sh
```

This script will:
1. Create a Python virtual environment
2. Install all Python dependencies
3. Run database migrations
4. Optionally create a Django superuser
5. Install all Node.js dependencies

### Option 2: Manual Setup

#### Backend Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create a superuser:
```bash
python manage.py createsuperuser
```

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd control-plane-frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Application

### Start the Backend

```bash
# Activate virtual environment
source venv/bin/activate

# Start Django development server
python manage.py runserver
```

The backend API will be available at: http://localhost:8000/api/
Django admin panel at: http://localhost:8000/admin/

### Start the Frontend

In a new terminal:

```bash
cd control-plane-frontend
npm start
```

The application will be available at: http://localhost:4200/

## First Steps

### 1. Login to Admin Panel

Navigate to http://localhost:8000/admin/ and login with your superuser credentials.

### 2. Add Your First Server

1. Open the frontend at http://localhost:4200/
2. Navigate to "Servers" in the navigation menu
3. Click "Add Server"
4. Fill in the server details:
   - **Name**: My Production Server
   - **Hostname**: example.com
   - **IP Address**: 192.168.1.100
   - **Port**: 22
   - **Username**: your_ssh_user
   - **SSH Key or Password**: (for authentication)
5. Click "Create Server"
6. Click "Test" to verify the connection

### 3. Monitor Services

Once a server is added:
1. Navigate to "Services" to see all discovered services
2. Start, stop, or restart services as needed
3. Monitor CPU and memory usage

### 4. View Server Health

1. From the Dashboard, click "View Health" on any server
2. See real-time CPU, memory, and disk usage
3. View historical metrics

### 5. Manage Nginx Sites

1. Navigate to "Nginx Sites"
2. Enable or disable sites
3. View site configurations

## Configuration

### Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` to configure:
- Secret key for Django
- Database settings (for production)
- CORS settings
- Redis settings (for production)

### Production Deployment

For production deployment:

1. Set `DEBUG=False` in Django settings
2. Configure a production database (PostgreSQL recommended)
3. Set up a proper web server (Nginx + Gunicorn)
4. Use environment variables for sensitive data
5. Enable HTTPS
6. Configure proper CORS settings

## Troubleshooting

### Backend Issues

**Cannot connect to server:**
- Verify SSH credentials
- Check firewall rules
- Ensure SSH is running on the target server

**Database errors:**
- Run `python manage.py migrate`
- Check database permissions

### Frontend Issues

**CORS errors:**
- Update CORS settings in Django settings
- Ensure backend is running

**API connection failed:**
- Verify backend is running on http://localhost:8000
- Check the API base URL in `src/app/services/api.ts`

## Next Steps

- Configure additional servers
- Set up monitoring for critical services
- Configure email alerts (custom development)
- Integrate with CI/CD pipelines
- Add custom service types

## Support

For issues and questions:
- Check the main README.md
- Open an issue on GitHub
- Review Django and Angular documentation

## Security Notes

⚠️ **Important Security Considerations:**

1. Never commit SSH keys or passwords to version control
2. Use environment variables for sensitive data
3. Enable HTTPS in production
4. Regularly update dependencies
5. Use strong passwords for the Django admin
6. Configure proper firewall rules
7. Limit SSH access to management servers only
8. Use SSH keys instead of passwords when possible
