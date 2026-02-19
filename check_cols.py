import os
import django
from django.db import connection
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("DESCRIBE api_seguimiento")
    with open('seguimiento_cols.txt', 'w') as f:
        for row in cursor.fetchall():
            f.write(f"{row}\n")
print("Done")
