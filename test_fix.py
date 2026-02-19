import os
import django
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from backend.api.models import Cliente, Contrato, Ejecutivo, Rol

def test_delete():
    # Find a client with contracts
    client = Cliente.objects.filter(contrato__isnull=False).first()
    if not client:
        print("No client with contracts found for testing. Creating one...")
        ej = Ejecutivo.objects.first()
        client = Cliente.objects.create(
            rut_empresa="12.345.678-5",
            razon_social="Test Delete Client",
            estado="activo",
            ejecutivo=ej
        )
        Contrato.objects.create(
            tipo_registro="Servicio",
            empresa=client.razon_social,
            estado="Finalizado",
            cliente=client,
            ejecutivo=ej
        )
        print(f"Created Test Client: {client.id} with 1 contract.")
    
    client_id = client.id
    contract_count = client.contrato_set.count()
    print(f"Deleting Client {client.razon_social} (ID: {client_id}) which has {contract_count} contracts.")
    
    try:
        client.delete()
        print("Deletion successful!")
        # Verify contracts are gone
        remaining_contracts = Contrato.objects.filter(cliente_id=client_id).count()
        print(f"Remaining contracts for this client ID: {remaining_contracts}")
    except Exception as e:
        print(f"Deletion FAILED: {e}")

if __name__ == "__main__":
    test_delete()
