import os
import django
from django.db import connection
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

def check_table(table_name):
    with connection.cursor() as cursor:
        cursor.execute(f"SHOW CREATE TABLE {table_name}")
        row = cursor.fetchone()
        return f"\n--- {table_name} ---\n{row[1]}\n"

tables = [
    'api_contrato', 'api_seguimiento', 'api_coordinador', 
    'api_contratocurso', 'api_contratoservicio', 'api_contratoproveedor'
]

try:
    with open('constraints_extended.txt', 'w', encoding='utf-8') as f:
        for t in tables:
            try:
                f.write(check_table(t))
            except:
                f.write(f"\n--- {t} (Not found) ---\n")
    print("Done")
except Exception as e:
    print(f"Error: {e}")
