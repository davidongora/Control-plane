# Authentication Setup

This document describes the authentication system implemented in the Control Plane application.

## Overview

The application uses Django session-based authentication with Angular frontend. When a user logs in, Django creates a session and sends a session cookie that is automatically included in subsequent requests.

## Backend Setup

### Authentication Endpoints

- `POST /api/auth/login/` - Login with username and password
- `POST /api/auth/logout/` - Logout (requires authentication)
- `GET /api/auth/user/` - Get current user info (requires authentication)
- `GET /api/auth/csrf/` - Get CSRF token (sets CSRF cookie)

### Creating Admin User

To create the default admin user for development:

```bash
python create_admin.py
```

Default credentials:
- Username: `admin`
- Password: `admin`

Or manually using Django shell:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
User.objects.create_superuser('admin', 'admin@example.com', 'admin')
```

### Settings

The following settings are configured in `control_plane_backend/settings.py`:

- **CORS**: Allows credentials from `http://localhost:4200`
- **CSRF**: Trusts origins from `http://localhost:4200`
- **Session Authentication**: Uses Django's session framework
- **Default Permission**: Requires authentication for all endpoints except login

## Frontend Setup

### Components

1. **Login Component** (`src/app/components/login/`)
   - Simple login form with username and password fields
   - Displays error messages
   - Redirects to dashboard on successful login
   - Redirects to returnUrl if provided in query params

2. **Auth Service** (`src/app/services/auth.service.ts`)
   - Manages authentication state
   - Stores user info in localStorage
   - Provides login/logout methods
   - Observable for current user state

3. **Auth Guard** (`src/app/guards/auth.guard.ts`)
   - Protects routes that require authentication
   - Redirects to login page if not authenticated
   - Preserves intended URL in returnUrl query param

4. **Auth Interceptor** (`src/app/interceptors/auth.interceptor.ts`)
   - Adds `withCredentials: true` to all requests (enables cookies)
   - Adds CSRF token to request headers
   - Reads CSRF token from cookie set by Django

### Protected Routes

All routes except `/login` are protected by the `authGuard`:

- `/dashboard`
- `/servers`
- `/services`
- `/nginx-sites`
- `/projects`
- `/server-health/:id`

### User Interface

When authenticated:
- Navbar displays user icon and username
- Logout button in navbar
- Footer visible

When not authenticated:
- Only login page is visible
- No navbar or footer
- Gradient background

## Usage

1. Start the Django backend:
   ```bash
   python manage.py runserver
   ```

2. Create admin user (if not exists):
   ```bash
   python create_admin.py
   ```

3. Start the Angular frontend:
   ```bash
   cd control-plane-frontend
   npm install  # First time only
   npm start
   ```

4. Navigate to `http://localhost:4200`

5. Login with credentials:
   - Username: `admin`
   - Password: `admin`

## Security Notes

- Session cookies are httpOnly and secure in production
- CSRF protection is enabled for all POST/PUT/DELETE requests
- Passwords are hashed using Django's PBKDF2 algorithm
- All API endpoints require authentication by default
- CORS is restricted to localhost:4200 in development

## Development vs Production

For production deployment:
- Change `SECRET_KEY` in settings.py
- Set `DEBUG = False`
- Update `ALLOWED_HOSTS`
- Update `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS`
- Use HTTPS
- Set `SESSION_COOKIE_SECURE = True`
- Set `CSRF_COOKIE_SECURE = True`
