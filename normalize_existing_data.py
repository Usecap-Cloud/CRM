"""
Script para normalizar todos los datos ya existentes en la BD.
Aplica el mismo normalize_text() de models.py a todos los registros.
"""
import os
import django
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from backend.api.models import (
    Cliente, Ejecutivo, Coordinador, Servicio, Proveedor, Curso, normalize_text, normalize_estado
)

def run():
    print("=== Normalizando Clientes ===")
    for obj in Cliente.objects.all():
        changed = False
        nt = normalize_text(obj.razon_social)
        if nt != obj.razon_social:
            obj.razon_social = nt
            changed = True
        for field in ['direccion', 'region', 'comuna', 'sector_industria', 'origen_referencia']:
            val = getattr(obj, field)
            if val:
                norm = normalize_text(val)
                if norm != val:
                    setattr(obj, field, norm)
                    changed = True
        ne = normalize_estado(obj.estado)
        if ne != obj.estado:
            obj.estado = ne
            changed = True
        if changed:
            obj.save()
            print(f"  Actualizado: {obj.razon_social}")

    print("=== Normalizando Ejecutivos ===")
    for obj in Ejecutivo.objects.all():
        changed = False
        for field in ['nombre', 'region', 'comuna']:
            val = getattr(obj, field)
            if val:
                norm = normalize_text(val)
                if norm != val:
                    setattr(obj, field, norm)
                    changed = True
        ne = normalize_estado(obj.estado)
        if ne != obj.estado:
            obj.estado = ne
            changed = True
        if changed:
            obj.save()
            print(f"  Actualizado: {obj.nombre}")

    print("=== Normalizando Coordinadores ===")
    for obj in Coordinador.objects.all():
        changed = False
        for field in ['nombre', 'cargo']:
            val = getattr(obj, field)
            if val:
                norm = normalize_text(val)
                if norm != val:
                    setattr(obj, field, norm)
                    changed = True
        ne = normalize_estado(obj.estado)
        if ne != obj.estado:
            obj.estado = ne
            changed = True
        if changed:
            obj.save()
            print(f"  Actualizado: {obj.nombre}")

    print("=== Normalizando Servicios ===")
    for obj in Servicio.objects.all():
        changed = False
        for field in ['nombre', 'tipo', 'rubro']:
            val = getattr(obj, field)
            if val:
                norm = normalize_text(val)
                if norm != val:
                    setattr(obj, field, norm)
                    changed = True
        ne = normalize_estado(obj.estado)
        if ne != obj.estado:
            obj.estado = ne
            changed = True
        if changed:
            obj.save()
            print(f"  Actualizado: {obj.nombre}")

    print("=== Normalizando Proveedores ===")
    for obj in Proveedor.objects.all():
        changed = False
        for field in ['nombre', 'tipo', 'contacto', 'region', 'comuna', 'rubro']:
            val = getattr(obj, field)
            if val:
                norm = normalize_text(val)
                if norm != val:
                    setattr(obj, field, norm)
                    changed = True
        ne = normalize_estado(obj.estado)
        if ne != obj.estado:
            obj.estado = ne
            changed = True
        if changed:
            obj.save()
            print(f"  Actualizado: {obj.nombre}")

    print("=== Normalizando Cursos ===")
    for obj in Curso.objects.all():
        changed = False
        for field in ['nombre', 'categoria']:
            val = getattr(obj, field)
            if val:
                norm = normalize_text(val)
                if norm != val:
                    setattr(obj, field, norm)
                    changed = True
        ne = normalize_estado(obj.estado)
        if ne != obj.estado:
            obj.estado = ne
            changed = True
        if changed:
            obj.save()
            print(f"  Actualizado: {obj.nombre}")

    print("\n✅ Normalización completada.")

if __name__ == "__main__":
    run()
