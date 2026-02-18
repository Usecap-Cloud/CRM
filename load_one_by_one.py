import os
import django
import json
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from django.core import serializers

with open('initial_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total objects to load: {len(data)}")

for i, obj_dict in enumerate(data):
    try:
        json_str = json.dumps([obj_dict])
        for obj in serializers.deserialize('json', json_str):
            obj.save()
    except Exception as e:
        model = obj_dict.get('model')
        pk = obj_dict.get('pk')
        print(f"FAILED: Obj {i} | Model {model} | PK {pk} | Error: {str(e)}")

print("Process finished.")
