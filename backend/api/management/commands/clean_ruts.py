
from django.core.management.base import BaseCommand
from backend.api.models import Cliente, Ejecutivo, Coordinador, Proveedor, normalize_rut_str

class Command(BaseCommand):
    help = 'Normaliza y limpia RUTs duplicados en la base de datos'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando normalización de RUTs...")
        
        for model in [Cliente, Ejecutivo, Coordinador, Proveedor]:
            field_name = 'rut_empresa' if model == Cliente else \
                         'rut_ejecutivo' if model == Ejecutivo else \
                         'rut_coordinador' if model == Coordinador else \
                         'rut_proveedor'
            
            self.stdout.write(f"Procesando {model.__name__}...")
            for obj in model.objects.all():
                old_rut = getattr(obj, field_name)
                new_rut = normalize_rut_str(old_rut)
                if old_rut != new_rut:
                    self.stdout.write(f"  Actualizando {old_rut} -> {new_rut}")
                    setattr(obj, field_name, new_rut)
                    try:
                        obj.save()
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"  ERROR al guardar {new_rut}: {e}"))
                        if "Duplicate entry" in str(e) or "already exists" in str(e) or "UNIQUE constraint failed" in str(e):
                            self.stdout.write(self.style.WARNING(f"  DUPLICADO DETECTADO: Borrando instancia duplicada de {old_rut}"))
                            obj.delete()
        
        self.stdout.write(self.style.SUCCESS("Limpieza completada."))
