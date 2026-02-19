
import os
import sys
import django

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from api.models import Cliente, Ejecutivo, Coordinador, Proveedor, normalize_rut_str

def clean_duplicates():
    print("Normalizando y limpiando RUTs existentes...")
    
    # 1. Normalizar todos los RUTs existentes primero
    for model in [Cliente, Ejecutivo, Coordinador, Proveedor]:
        field_name = 'rut_empresa' if model == Cliente else \
                     'rut_ejecutivo' if model == Ejecutivo else \
                     'rut_coordinador' if model == Coordinador else \
                     'rut_proveedor'
        
        print(f"Procesando {model.__name__}...")
        for obj in model.objects.all():
            old_rut = getattr(obj, field_name)
            new_rut = normalize_rut_str(old_rut)
            if old_rut != new_rut:
                print(f"  Actualizando {old_rut} -> {new_rut}")
                setattr(obj, field_name, new_rut)
                try:
                    obj.save()
                except Exception as e:
                    print(f"  ERROR al guardar {new_rut}: {e}")
                    # Probablemente un duplicado real que ahora choca por el unique constraint
                    if "Duplicate entry" in str(e) or "already exists" in str(e):
                        print(f"  DUPLICADO DETECTADO: Borrando instancia duplicada de {old_rut}")
                        obj.delete()

if __name__ == "__main__":
    clean_duplicates()
    print("Limpieza completada.")
