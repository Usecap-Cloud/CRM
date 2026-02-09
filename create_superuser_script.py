
import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
try:
    django.setup()
except Exception as e:
    print(f"Error checking django setup: {e}")
    sys.exit(1)

from django.contrib.auth.models import User

def create_admin():
    username = 'admin'
    email = 'admin@example.com'
    password = 'admin'
    
    try:
        if not User.objects.filter(username=username).exists():
            print(f"Creating superuser '{username}'...")
            User.objects.create_superuser(username, email, password)
            print(f"SUCCESS: Superuser '{username}' created with password '{password}'.")
        else:
            print(f"INFO: Superuser '{username}' already exists.")
            # Optional: Reset password if exists? Better not to mess with it unless asked.
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    create_admin()
