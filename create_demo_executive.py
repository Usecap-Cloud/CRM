
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
from backend.api.models import Ejecutivo, Rol

def create_demo_executive():
    username = 'ejecutivo_demo'
    password = 'password123'
    email = 'demo@crm-usecap.cl'
    
    print(f"Creando usuario y ejecutivo de prueba '{username}'...")

    # Crear Usuario Django
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f"El usuario '{username}' ya existe.")
    else:
        user = User.objects.create_user(username=username, email=email, password=password)
        # Darle permisos de Staff para entrar al Admin
        user.is_staff = True
        user.save()
        print(f"Usuario '{username}' creado (Staff=True).")

    # Buscar/Crear Rol
    rol_comercial = Rol.objects.filter(nombre__icontains="Ejecutivo").first()
    if not rol_comercial:
        rol_comercial = Rol.objects.create(nombre="Ejecutivo Comercial", estado="Activo")

    # Crear Ficha de Ejecutivo y vincular
    ejecutivo, created = Ejecutivo.objects.get_or_create(
        rut='99888777-6',
        defaults={
            'nombre': 'Ejecutivo Demo',
            'email': email,
            'telefono': '912345678',
            'rol': rol_comercial,
            'user': user  # VINCULACIÓN IMPORTANTE
        }
    )
    
    if not created:
        ejecutivo.user = user
        ejecutivo.save()
        print(f"Ficha de Ejecutivo vinculada al usuario '{username}'.")
    else:
        print(f"Nuevo Ejecutivo creado y vinculado a '{username}'.")

    print(f"\n listos! Credenciales de prueba:")
    print(f"Usuario: {username}")
    print(f"Clave: {password}")

if __name__ == "__main__":
    create_demo_executive()
