import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Ejecutivo

def check():
    username = 'comercial'
    u = User.objects.filter(username=username).first()
    if not u:
        print(f"FAILED: User '{username}' not found.")
        # List all usernames to see if it's something else
        print("Existing users:", [user.username for user in User.objects.all()])
        return

    print(f"SUCCESS: User '{username}' found.")
    print(f"  Active: {u.is_active}")
    print(f"  Email: {u.email}")
    
    ej = Ejecutivo.objects.filter(user=u).first()
    if ej:
        print(f"  Associated Ejecutivo: {ej.nombre}")
        print(f"  RUT: {ej.rut_ejecutivo}")
        print(f"  Clean RUT for Pass: {ej.rut_ejecutivo.split('-')[0].replace('.', '')}")
    else:
        print("  WARNING: No Ejecutivo associated with this user.")

if __name__ == "__main__":
    check()
