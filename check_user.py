import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from django.contrib.auth.models import User
from backend.api.models import Ejecutivo, Rol

def diag():
    u = User.objects.get(username='comercial')
    print(f"User: {u.username}")
    print(f"Is Staff: {u.is_staff}")
    print(f"Is Superuser: {u.is_superuser}")
    
    ej = Ejecutivo.objects.filter(user=u).first()
    if ej:
        print(f"Ejecutivo Name: {ej.nombre}")
        print(f"Rol Object: {ej.rol}")
        if ej.rol:
            print(f"Rol Name: '{ej.rol.nombre}'")
    else:
        print("No associated Ejecutivo record.")

    print("\nExisting Roles in DB:")
    for r in Rol.objects.all():
        print(f"- {r.nombre}")

if __name__ == "__main__":
    diag()
