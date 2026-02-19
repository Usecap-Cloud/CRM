import os
import django
from django.db import connection
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

def add_missing_column():
    with connection.cursor() as cursor:
        print("Checking api_seguimiento for cliente_id...")
        cursor.execute("SHOW COLUMNS FROM api_seguimiento LIKE 'cliente_id'")
        if not cursor.fetchone():
            print("Adding cliente_id to api_seguimiento...")
            # Add column
            cursor.execute("ALTER TABLE api_seguimiento ADD COLUMN cliente_id bigint")
            
            # Populate it if possible from existing contracts? 
            # In Seguimiento, we have contrato_id. We can find the client from the contract.
            print("Populating cliente_id from contrato_id...")
            cursor.execute("""
                UPDATE api_seguimiento s
                JOIN api_contrato c ON s.contrato_id = c.id
                SET s.cliente_id = c.cliente_id
                WHERE s.cliente_id IS NULL
            """)
            
            # Make it NOT NULL if appropriate
            cursor.execute("ALTER TABLE api_seguimiento MODIFY COLUMN cliente_id bigint NOT NULL")
            
            # Add Foreign Key
            cursor.execute("ALTER TABLE api_seguimiento ADD CONSTRAINT api_seguimiento_cliente_id_7a256920_fk_api_cliente_id FOREIGN KEY (cliente_id) REFERENCES api_cliente(id) ON DELETE CASCADE")
            print("Column added and populated.")
        else:
            print("Column already exists.")

if __name__ == "__main__":
    try:
        add_missing_column()
    except Exception as e:
        print(f"Error: {e}")
