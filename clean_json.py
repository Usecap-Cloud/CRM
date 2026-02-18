import json

with open('initial_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# valid fields for api.cliente according to models.py
valid_fields = {
    'rut_empresa', 'razon_social', 'estado', 'direccion', 'region', 
    'comuna', 'sector_industria', 'origen_referencia', 'fecha_creacion', 
    'observaciones', 'ejecutivo', 'cliente_padre'
}

cleaned_data = []
for obj in data:
    if obj['model'] == 'api.cliente':
        # Create a new dict with only valid fields
        new_fields = {k: v for k, v in obj['fields'].items() if k in valid_fields}
        obj['fields'] = new_fields
    
    # Also fix Contrato 'subtotal' if it has 'nan' or similar (though it looked ok)
    cleaned_data.append(obj)

with open('initial_data_cleaned.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_data, f, indent=2, ensure_ascii=False)

print("Cleaned JSON created: initial_data_cleaned.json")
