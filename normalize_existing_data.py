"""
Normaliza TODOS los registros existentes en la BD (fuerza actualización sin chequear diferencias).
"""
import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from backend.api.models import Cliente, Ejecutivo, Coordinador, Servicio, Proveedor, Curso, normalize_text

def force_normalize(model, text_fields, label_field='id'):
    count = 0
    for obj in model.objects.all():
        for field in text_fields:
            val = getattr(obj, field, None)
            if val:
                setattr(obj, field, normalize_text(val))
        # Usar update() directo para no disparar validaciones de choices
        update_kwargs = {f: getattr(obj, f) for f in text_fields if getattr(obj, f)}
        model.objects.filter(pk=obj.pk).update(**update_kwargs)
        count += 1
    return count

print("=== Normalizando Clientes ===")
n = force_normalize(Cliente, ['razon_social', 'sector_industria', 'direccion', 'region', 'comuna', 'origen_referencia'])
print(f"  {n} registros actualizados.")

print("=== Normalizando Ejecutivos ===")
n = force_normalize(Ejecutivo, ['nombre', 'region', 'comuna'])
print(f"  {n} registros actualizados.")

print("=== Normalizando Coordinadores ===")
n = force_normalize(Coordinador, ['nombre', 'cargo'])
print(f"  {n} registros actualizados.")

print("=== Normalizando Servicios ===")
n = force_normalize(Servicio, ['nombre', 'tipo', 'rubro'])
print(f"  {n} registros actualizados.")

print("=== Normalizando Proveedores ===")
n = force_normalize(Proveedor, ['nombre', 'tipo', 'contacto', 'region', 'comuna', 'rubro'])
print(f"  {n} registros actualizados.")

print("=== Normalizando Cursos ===")
n = force_normalize(Curso, ['nombre', 'categoria'])
print(f"  {n} registros actualizados.")

print("\n✅ Normalización completada.")
