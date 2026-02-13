import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from django.contrib.auth.models import User
from backend.api.models import Ejecutivo

def fix_usernames():
    print("Standardizing usernames for Ejecutivos...")
    ejs = Ejecutivo.objects.all()
    for ej in ejs:
        if ej.user and ej.email:
            new_username = ej.email.split('@')[0]
            old_username = ej.user.username
            if old_username != new_username:
                # Check if new_username is available
                if not User.objects.filter(username=new_username).exists():
                    print(f"Renaming '{old_username}' -> '{new_username}' (Email: {ej.email})")
                    ej.user.username = new_username
                    ej.user.save()
                else:
                    print(f"SKIPPING: '{new_username}' already exists, cannot rename '{old_username}'")
        elif not ej.user and ej.email:
            print(f"WARNING: Ejecutivo '{ej.nombre}' has no associated User account.")

if __name__ == "__main__":
    fix_usernames()
