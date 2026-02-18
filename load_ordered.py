import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

from django.core import serializers
from io import StringIO

with open('initial_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Sort models by dependency
order = [
    'auth.user',
    'api.rol',
    'api.ejecutivo',
    'api.cliente',
    'api.curso',
    'api.coordinador',
    'api.contrato',
    'sessions.session'
]

# Group objects by model
grouped = {}
for obj in data:
    model = obj['model']
    if model not in grouped:
        grouped[model] = []
    grouped[model].append(obj)

# Load in order
for model_name in order:
    if model_name in grouped:
        print(f"Loading {model_name}...")
        json_str = json.dumps(grouped[model_name])
        stream = StringIO(json_str)
        try:
            for obj in serializers.deserialize('json', stream):
                obj.save()
            print(f"  Successfully loaded {len(grouped[model_name])} objects.")
        except Exception as e:
            print(f"  Error loading {model_name}: {e}")

print("Done.")
