
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

from backend.api.models import Rol

def populate_roles():
    roles_to_create = [
        {"nombre": "Administrador", "descripcion": "Acceso total al sistema y gestión de usuarios."},
        {"nombre": "Ejecutivo Comercial", "descripcion": "Encargado de gestionar clientes y ventas."},
        {"nombre": "Coordinador Académico", "descripcion": "Gestiona cursos y relatores."},
        {"nombre": "Gerencia", "descripcion": "Visión global de reportes y estados."},
    ]

    print("Creando roles iniciales...")

    for data in roles_to_create:
        rol, created = Rol.objects.get_or_create(
            nombre=data["nombre"],
            defaults={
                "estado": "Activo",
                "descripcion": data["descripcion"]
            }
        )
        if created:
            print(f"ROL CREADO: {rol.nombre}")
        else:
            print(f"YA EXISTE: {rol.nombre}")

if __name__ == "__main__":
    populate_roles()
