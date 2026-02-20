import os
import django
import json
import traceback
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from django.core import serializers
from backend.api.models import Cliente, Ejecutivo

def fix_load():
    with open('initial_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    clients = [obj for obj in data if obj['model'] == 'api.cliente']
    print(f"Attempting to load {len(clients)} clients...")
    
    for obj_dict in clients:
        pk = obj_dict.get('pk')
        fields = obj_dict.get('fields')
        print(f"Processing Client PK {pk}: {fields.get('razon_social')}")
        
        # Ensure executive exists or use a default
        ej_id = fields.get('ejecutivo')
        if not Ejecutivo.objects.filter(id=ej_id).exists():
             first_ej = Ejecutivo.objects.first()
             if first_ej:
                 print(f"  Warning: Executive {ej_id} not found, using {first_ej.id}")
                 fields['ejecutivo'] = first_ej.id
             else:
                 print(f"  Error: No executives in DB. Skipping.")
                 continue

        try:
            json_str = json.dumps([obj_dict])
            for deserialized_obj in serializers.deserialize('json', json_str):
                deserialized_obj.save()
            print(f"  SUCCESS")
        except Exception as e:
            print(f"  FAILED: {e}")
            # Try manual create if deserialization fails
            try:
                # Remove client_padre if it might cause issues (dependency)
                cp_id = fields.pop('cliente_padre', None)
                Cliente.objects.update_or_create(id=pk, defaults=fields)
                print(f"  SUCCESS (via update_or_create)")
            except Exception as e2:
                print(f"  CRITICAL FAILURE: {e2}")

if __name__ == "__main__":
    fix_load()
