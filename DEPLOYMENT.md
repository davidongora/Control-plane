# Production Deployment Guide

## Infrastructure Requirements

- Linux server (Ubuntu 20.04+ or CentOS 8+ recommended)
- Python 3.8+
- PostgreSQL 12+
- Nginx
- Node.js 18+
- Redis (optional, for Celery/Channels)

## 1. Server Setup

### Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip python3-venv postgresql postgresql-contrib nginx redis-server

# CentOS/RHEL
sudo yum install python3 python3-pip postgresql-server postgresql-contrib nginx redis
```

## 2. Database Setup

### PostgreSQL Configuration

```bash
# Create database and user
sudo -u postgres psql

CREATE DATABASE control_plane;
CREATE USER control_plane_user WITH PASSWORD 'your_secure_password';
ALTER ROLE control_plane_user SET client_encoding TO 'utf8';
ALTER ROLE control_plane_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE control_plane_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE control_plane TO control_plane_user;
\q
```

## 3. Application Setup

### Clone and Setup Application

```bash
cd /opt
sudo git clone https://github.com/davidongora/Control-plane.git
cd Control-plane

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Configure Environment Variables

Create `/opt/Control-plane/.env`:

```bash
SECRET_KEY=your_random_secret_key_here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DB_NAME=control_plane
DB_USER=control_plane_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# CORS
CORS_ALLOWED_ORIGINS=https://your-domain.com

# Redis
REDIS_URL=redis://localhost:6379/0
```

### Run Migrations and Collect Static Files

```bash
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py createsuperuser
```

## 4. Gunicorn Configuration

Create `/etc/systemd/system/control-plane.service`:

```ini
[Unit]
Description=Control Plane Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/Control-plane
Environment="PATH=/opt/Control-plane/venv/bin"
ExecStart=/opt/Control-plane/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/opt/Control-plane/control-plane.sock \
    control_plane_backend.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start and enable the service:

```bash
sudo systemctl start control-plane
sudo systemctl enable control-plane
```

## 5. Nginx Configuration

Create `/etc/nginx/sites-available/control-plane`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location /static/ {
        alias /opt/Control-plane/staticfiles/;
    }

    location /api/ {
        proxy_pass http://unix:/opt/Control-plane/control-plane.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /admin/ {
        proxy_pass http://unix:/opt/Control-plane/control-plane.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        root /opt/Control-plane/control-plane-frontend/dist/control-plane-frontend;
        try_files $uri $uri/ /index.html;
    }
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/control-plane /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 6. SSL Configuration with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 7. Frontend Build

```bash
cd /opt/Control-plane/control-plane-frontend
npm install
npm run build
```

Update API base URL in production:
Edit `src/app/services/api.ts` before building:

```typescript
private baseUrl = 'https://your-domain.com/api';
```

## 8. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Firewalld (CentOS)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload
```

## 9. Monitoring and Logs

### View Application Logs

```bash
sudo journalctl -u control-plane -f
```

### View Nginx Logs

```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 10. Backup Strategy

### Database Backup

Create `/opt/scripts/backup-db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -U control_plane_user -h localhost control_plane > $BACKUP_DIR/control_plane_$DATE.sql
find $BACKUP_DIR -type f -mtime +7 -delete
```

Add to crontab:
```bash
0 2 * * * /opt/scripts/backup-db.sh
```

## 11. Security Hardening

1. **Change default SSH port**
2. **Use SSH keys only, disable password auth**
3. **Enable fail2ban**
4. **Keep system updated**
5. **Use strong passwords**
6. **Regular security audits**
7. **Monitor logs for suspicious activity**

## 12. Maintenance

### Update Application

```bash
cd /opt/Control-plane
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
cd control-plane-frontend
npm install
npm run build
sudo systemctl restart control-plane
sudo systemctl reload nginx
```

## Troubleshooting

### Service won't start
```bash
sudo systemctl status control-plane
sudo journalctl -u control-plane -n 50
```

### Permission issues
```bash
sudo chown -R www-data:www-data /opt/Control-plane
sudo chmod -R 755 /opt/Control-plane
```

### Database connection issues
- Verify PostgreSQL is running
- Check credentials in .env
- Verify pg_hba.conf settings
