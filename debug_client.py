import os
import django
import json
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from django.core import serializers
from io import StringIO

with open('initial_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Focus only on api.cliente
client_data = [obj for obj in data if obj['model'] == 'api.cliente']

for obj_dict in client_data:
    try:
        json_str = json.dumps([obj_dict])
        for obj in serializers.deserialize('json', json_str):
            obj.save()
        print(f"Loaded client {obj_dict.get('pk')}")
    except Exception as e:
        print(f"Error loading client {obj_dict.get('pk')}:")
        print(traceback.format_exc())
