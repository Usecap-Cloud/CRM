import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from backend.api.models import Cliente, Ejecutivo, Coordinador, Contrato, ContratoCurso, Curso, ContratoServicio, Servicio, ContratoProveedor, Proveedor
from django.core import serializers

def load_contracts():
    with open('initial_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    contracts_data = [obj for obj in data if obj['model'] == 'api.contrato']
    print(f"Found {len(contracts_data)} contracts in JSON.")
    
    for obj_dict in contracts_data:
        pk = obj_dict['pk']
        fields = obj_dict['fields']
        
        # Resolve Cliente
        cliente_id = fields.pop('cliente')
        cliente = Cliente.objects.filter(id=cliente_id).first()
        if not cliente:
            cliente = Cliente.objects.filter(razon_social__iexact=fields['empresa']).first()
        if not cliente:
            for c in Cliente.objects.all():
                if c.razon_social.upper() in fields['empresa'].upper() or fields['empresa'].upper() in c.razon_social.upper():
                    cliente = c
                    break
        
        if not cliente:
            print(f"  Error: Could not resolve client for {fields['empresa']}. Skipping.")
            continue
        
        fields['cliente'] = cliente
        
        # Resolve Ejecutivo
        ej_id = fields.pop('ejecutivo', None)
        ejecutivo = Ejecutivo.objects.filter(id=ej_id).first() if ej_id else Ejecutivo.objects.first()
        if not ejecutivo: ejecutivo = Ejecutivo.objects.first()
        fields['ejecutivo'] = ejecutivo
        
        # Resolve Coordinador
        coord_id = fields.pop('coordinador', None)
        if coord_id:
            fields['coordinador'] = Coordinador.objects.filter(id=coord_id).first()

        try:
            Contrato.objects.update_or_create(id=pk, defaults=fields)
            print(f"  Contract {pk} loaded for {cliente.razon_social}")
        except Exception as e:
            print(f"  Failed loading contract {pk}: {e}")

    print(f"Loading related items...")
    
    # Load ContratoCurso
    items_data = [obj for obj in data if obj['model'] == 'api.contratocurso']
    for obj_dict in items_data:
        pk, fields = obj_dict['pk'], obj_dict['fields']
        try:
            if Contrato.objects.filter(id=fields['contrato']).exists() and Curso.objects.filter(id=fields['curso']).exists():
                ContratoCurso.objects.update_or_create(id=pk, defaults=fields)
        except: pass
    print(f"Loaded ContratoCursos.")

    # Load ContratoServicio
    items_data = [obj for obj in data if obj['model'] == 'api.contratoservicio']
    for obj_dict in items_data:
        pk, fields = obj_dict['pk'], obj_dict['fields']
        try:
            if Contrato.objects.filter(id=fields['contrato']).exists() and Servicio.objects.filter(id=fields['servicio']).exists():
                ContratoServicio.objects.update_or_create(id=pk, defaults=fields)
        except: pass
    print(f"Loaded ContratoServicios.")

    # Load ContratoProveedor
    items_data = [obj for obj in data if obj['model'] == 'api.contratoproveedor']
    for obj_dict in items_data:
        pk, fields = obj_dict['pk'], obj_dict['fields']
        try:
            if Contrato.objects.filter(id=fields['contrato']).exists() and Proveedor.objects.filter(id=fields['proveedor']).exists() and Servicio.objects.filter(id=fields['servicio']).exists():
                ContratoProveedor.objects.update_or_create(id=pk, defaults=fields)
        except: pass
    print(f"Loaded ContratoProveedores.")

if __name__ == '__main__':
    load_contracts()
