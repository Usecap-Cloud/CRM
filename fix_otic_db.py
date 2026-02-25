import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from api.models import Cliente

def fix_otic():
    clients = Cliente.objects.filter(tipo_convenio__iexact='otec') | Cliente.objects.filter(tipo_convenio__iexact='otech')
    count = clients.count()
    for client in clients:
        client.tipo_convenio = 'OTIC'
        client.save()
    print(f"Updated {count} clients from OTEC/OTECH to OTIC")

if __name__ == "__main__":
    fix_otic()
