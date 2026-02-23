from django.core.management.base import BaseCommand
from django.apps import apps
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Seeds the database with test data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # Get models dynamically to avoid import errors
        Rol = apps.get_model('api', 'Rol')
        Ejecutivo = apps.get_model('api', 'Ejecutivo')
        Cliente = apps.get_model('api', 'Cliente')
        Coordinador = apps.get_model('api', 'Coordinador')
        Servicio = apps.get_model('api', 'Servicio')
        Proveedor = apps.get_model('api', 'Proveedor')
        Contrato = apps.get_model('api', 'Contrato')
        Curso = apps.get_model('api', 'Curso')

        # 1. Roles
        rol_admin, _ = Rol.objects.get_or_create(nombre='Administrador', defaults={'estado': 'activo'})
        rol_ventas, _ = Rol.objects.get_or_create(nombre='Vendedor', defaults={'estado': 'activo'})

        # 2. Ejecutivos
        user1, _ = User.objects.get_or_create(username='ejecutivo1', defaults={'email': 'ejecutivo1@usecap.cl'})
        if _: user1.set_password('pass1234'); user1.save()
        
        ej1, _ = Ejecutivo.objects.get_or_create(
            rut_ejecutivo='12.345.678-5',
            defaults={
                'nombre': 'Juan Pérez',
                'email': 'jperez@usecap.cl',
                'telefono': '+56912345678',
                'estado': 'activo',
                'rol': rol_admin,
                'user': user1
            }
        )

        # 3. Clientes
        c1, _ = Cliente.objects.get_or_create(
            rut_empresa='76.543.210-K',
            defaults={
                'razon_social': 'Empresa Test S.A.',
                'estado': 'activo',
                'ejecutivo': ej1,
                'direccion': 'Av. Providencia 123',
                'comuna': 'Providencia',
                'region': 'Metropolitana',
                'telefono_empresarial': '223456789',
                'tipo_convenio': 'sence'
            }
        )

        # 4. Coordinadores
        coord1, _ = Coordinador.objects.get_or_create(
            rut_coordinador='15.678.901-2',
            defaults={
                'nombre': 'Carlos Ruiz',
                'email': 'cruiz@empresatest.cl',
                'telefono': '+56955544332',
                'cargo': 'Gerente RRHH',
                'estado': 'activo',
                'cliente': c1,
                'ejecutivo': ej1
            }
        )
        c1.contacto_principal = coord1
        c1.save()

        # 5. Cursos
        Curso.objects.get_or_create(
            nombre='Excel Avanzado para Empresas',
            defaults={
                'codigo': 'EXC-ADV-01',
                'estado': 'Activo',
                'categoria': 'Computación',
                'codigo_sence': '1234567890'
            }
        )

        # 6. Servicios
        Servicio.objects.get_or_create(
            nombre='Consultoría RRHH',
            defaults={
                'tipo': 'Asesoría',
                'estado': 'activo',
                'rubro': 'Recursos Humanos'
            }
        )

        # 7. Proveedores
        Proveedor.objects.get_or_create(
            rut_proveedor='77.666.555-4',
            defaults={
                'nombre': 'Suministros Globales Ltda',
                'tipo': 'Materiales',
                'estado': 'activo',
                'email': 'ventas@suministros.cl',
                'telefono': '225556677'
            }
        )

        # 8. Contratos
        Contrato.objects.get_or_create(
            empresa='Empresa Test S.A.',
            defaults={
                'estado': 'activo',
                'tipo_registro': 'OTEC',
                'fecha_recepcion': '2024-01-15',
                'fecha_emision': '2024-01-16',
                'fecha_inicio': '2024-02-01',
                'fecha_vencimiento': '2025-02-01',
                'subtotal': 1500000,
                'cliente': c1,
                'ejecutivo': ej1
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded test data'))
