
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from backend.api.models import Servicio, Coordinador, Cliente
from django.test import RequestFactory
from backend.api.views import ServicioViewSet

def check_services():
    print("--- Verifying Services ---")
    try:
        count = Servicio.objects.count()
        print(f"Service count: {count}")
        
        # Test ViewSet
        factory = RequestFactory()
        request = factory.get('/api/servicios/')
        view = ServicioViewSet.as_view({'get': 'list'})
        response = view(request)
        
        if response.status_code == 200:
            print("API /api/servicios/ OK")
        else:
            print(f"API Error: {response.status_code}")
    except Exception as e:
        print(f"CRITICAL ERROR in Services: {e}")

def check_coordinadores():
    print("\n--- Verifying Coordinadores ---")
    try:
        # Check if we can create a duplicate RUT
        # First ensure we have a client
        cliente = Cliente.objects.first()
        if not cliente:
            print("Skipping Coordinador test (no clients)")
            return

        # Create a dummy coordinator
        rut = "99888777-6"
        if not Coordinador.objects.filter(rut_coordinador=rut).exists():
            Coordinador.objects.create(
                rut_coordinador=rut,
                nombre="Test Coord",
                email="test@coord.cl",
                cliente=cliente,
                estado="activo"
            )
            print("Created Test Coordinador")
        
        # Try to create duplicate
        try:
            Coordinador.objects.create(
                 rut_coordinador=rut,
                nombre="Test Duplicate",
                email="test2@coord.cl",
                cliente=cliente
            )
            print("ERROR: Duplicate RUT allowed!")
        except Exception as e:
             print(f"Success: Duplicate RUT blocked ({e})")
             
    except Exception as e:
        print(f"Error in Coordinadores check: {e}")

if __name__ == "__main__":
    check_services()
    check_coordinadores()
