
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

from backend.api.models import Cliente, Ejecutivo, Rol

def create_test_clients():
    # 1. Obtener el ejecutivo de prueba (Tu usuario)
    username = 'ejecutivo_demo'
    try:
        ejecutivo_propio = Ejecutivo.objects.get(user__username=username)
    except Ejecutivo.DoesNotExist:
        print(f"Error: No se encontro el ejecutivo para el usuario {username}. Corre el script create_demo_executive.py primero.")
        return

    # 2. Obtener o crear un Rol (necesario para crear ejecutivos)
    rol = Rol.objects.filter(nombre__icontains="Ejecutivo").first()
    if not rol:
        rol = Rol.objects.create(nombre="Ejecutivo Comercial", estado="Activo")

    # 3. Crear un ejecutivo "AJENO" (Para asignar el cliente que NO deberias ver)
    ejecutivo_ajeno, created = Ejecutivo.objects.get_or_create(
        rut='11111111-1',
        defaults={
            'nombre': 'Ejecutivo Ajeno',
            'email': 'ajeno@crm.cl',
            'estado': 'Activo',
            'rol': rol
        }
    )

    print("Creando clientes de prueba...")

    # 4. Crear un Cliente ASIGNADO A TI (Deberia verse)
    c1, created1 = Cliente.objects.get_or_create(
        rut='77777777-7',
        defaults={
            'razon_social': 'Empresa PROPIA S.A.',
            'nombre': 'Empresa Propia',
            'email': 'contacto@propia.cl',
            'estado': 'Activo',
            'ejecutivo': ejecutivo_propio
        }
    )
    if created1:
        print(f"Cliente creado: {c1.razon_social} (Asignado a ti)")
    else:
        print(f"Cliente ya existe: {c1.razon_social}")

    # 5. Crear un Cliente AJENO (No deberia verse)
    c2, created2 = Cliente.objects.get_or_create(
        rut='88888888-8',
        defaults={
            'razon_social': 'Empresa AJENA Ltda.',
            'nombre': 'Empresa Ajena',
            'email': 'contacto@ajena.cl',
            'estado': 'Activo',
            'ejecutivo': ejecutivo_ajeno
        }
    )
    if created2:
        print(f"Cliente creado: {c2.razon_social} (NO asignado a ti)")
    else:
        print(f"Cliente ya existe: {c2.razon_social}")

if __name__ == "__main__":
    create_test_clients()
