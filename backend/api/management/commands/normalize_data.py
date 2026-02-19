from django.core.management.base import BaseCommand
from backend.api.models import Cliente, Ejecutivo, Coordinador, Servicio, Proveedor, Curso, normalize_text


class Command(BaseCommand):
    help = 'Normaliza textos existentes en la BD a Title Case (sin afectar el campo estado)'

    def handle(self, *args, **options):
        self.stdout.write('Normalizando datos existentes...')

        modelos = [
            (Cliente,     ['razon_social', 'sector_industria', 'direccion', 'region', 'comuna', 'origen_referencia']),
            (Ejecutivo,   ['nombre', 'region', 'comuna']),
            (Coordinador, ['nombre', 'cargo']),
            (Servicio,    ['nombre', 'tipo', 'rubro']),
            (Proveedor,   ['nombre', 'tipo', 'contacto', 'region', 'comuna', 'rubro']),
            (Curso,       ['nombre', 'categoria']),
        ]

        total = 0
        for model, fields in modelos:
            count = 0
            for obj in model.objects.all():
                update_kwargs = {}
                for field in fields:
                    val = getattr(obj, field, None)
                    if val:
                        norm = normalize_text(val)
                        if norm != val:
                            update_kwargs[field] = norm
                if update_kwargs:
                    model.objects.filter(pk=obj.pk).update(**update_kwargs)
                    count += 1
            self.stdout.write(f'  {model.__name__}: {count} registros actualizados')
            total += count

        self.stdout.write(self.style.SUCCESS(f'✅ Completado. {total} registros normalizados en total.'))
