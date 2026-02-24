import os
import sys
import django

# Add current directory to path
sys.path.append(os.getcwd())

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.api.models import Rol, Ejecutivo, Cliente, Coordinador, Servicio, Proveedor, Curso, Contrato, Seguimiento

models_to_fix = [
    Rol, Ejecutivo, Cliente, Coordinador, Servicio, Proveedor, Curso, Contrato, Seguimiento
]

def migrate_status():
    print("Iniciando normalización de datos en la base de datos...")
    
    for model in models_to_fix:
        print(f"Procesando {model.__name__}...")
        count = 0
        objects = model.objects.all()
        for obj in objects:
            # El método save() de cada modelo ya llama a normalize_estado y normalize_text
            obj.save()
            count += 1
        print(f"  - {count} registros actualizados en {model.__name__}")

    print("\n¡Migración completada exitosamente!")

if __name__ == "__main__":
    migrate_status()
