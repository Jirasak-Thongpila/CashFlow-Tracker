#!/usr/bin/env python
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'CashFlow_Tracker.settings')
django.setup()

from accounts.models import CustomUser

# Create a test user
email = "admin@example.com"
password = "admin123"

if not CustomUser.objects.filter(email=email).exists():
    user = CustomUser.objects.create_user(
        username="admin",
        email=email,
        password=password,
        is_staff=True,
        is_superuser=True
    )
    print(f"User created successfully!")
    print(f"Email: {email}")
    print(f"Password: {password}")
else:
    print("User already exists!")