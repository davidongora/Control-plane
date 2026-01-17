#!/usr/bin/env python
"""Script to create a default admin user for development."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'control_plane_backend.settings')
django.setup()

from django.contrib.auth.models import User

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin')
    print('Admin user created successfully (username: admin, password: admin)')
else:
    print('Admin user already exists')
