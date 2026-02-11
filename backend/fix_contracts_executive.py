import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from api.models import Contrato, Ejecutivo

def assign_executives():
    default_ej = Ejecutivo.objects.first()
    if not default_ej:
        print("No executives found in the database.")
        return
    
    contracts_to_update = Contrato.objects.all()
    count = contracts_to_update.count()
    
    for contract in contracts_to_update:
        contract.ejecutivo = default_ej
        contract.save()
        
    print(f"Successfully assigned executive '{default_ej.nombre}' to {count} contracts.")

if __name__ == "__main__":
    assign_executives()
