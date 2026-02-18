import os
import django
import json
import traceback
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from django.core import serializers

with open('initial_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total objects: {len(data)}")

with connection.cursor() as cursor:
    cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')

success_count = 0
for i, obj_dict in enumerate(data):
    try:
        json_str = json.dumps([obj_dict])
        for deserialized_obj in serializers.deserialize('json', json_str):
            deserialized_obj.save()
        success_count += 1
    except Exception:
        print(f"FAILED: Obj {i} | Model {obj_dict.get('model')} | PK {obj_dict.get('pk')}")
        traceback.print_exc()

with connection.cursor() as cursor:
    cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')

print(f"Successfully loaded {success_count} / {len(data)} objects.")
