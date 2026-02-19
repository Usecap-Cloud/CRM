import os
import django
from django.db import connection
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

def sync_seguimiento():
    with connection.cursor() as cursor:
        # 1. Check current columns
        cursor.execute("SHOW COLUMNS FROM api_seguimiento")
        cols = [r[0] for r in cursor.fetchall()]
        print(f"Current columns: {cols}")

        # 2. Rename columns if they still have old names
        if 'fecha_proxima_accion' in cols:
            print("Renaming fecha_proxima_accion -> fecha_envio...")
            cursor.execute("ALTER TABLE api_seguimiento CHANGE COLUMN fecha_proxima_accion fecha_envio date")
        
        if 'tipo_seguimiento' in cols:
            print("Renaming tipo_seguimiento -> accion...")
            cursor.execute("ALTER TABLE api_seguimiento CHANGE COLUMN tipo_seguimiento accion varchar(50) NOT NULL DEFAULT 'Sin Acción'")
        
        # 3. Add missing columns
        cursor.execute("SHOW COLUMNS FROM api_seguimiento")
        cols = [r[0] for r in cursor.fetchall()]

        if 'cliente_id' not in cols:
            print("Adding cliente_id column...")
            cursor.execute("ALTER TABLE api_seguimiento ADD COLUMN cliente_id bigint")
            print("Populating cliente_id from contrato...")
            cursor.execute("""
                UPDATE api_seguimiento s
                JOIN api_contrato c ON s.contrato_id = c.id
                SET s.cliente_id = c.cliente_id
            """)
            cursor.execute("ALTER TABLE api_seguimiento MODIFY COLUMN cliente_id bigint NULL")
            cursor.execute("""
                ALTER TABLE api_seguimiento
                ADD CONSTRAINT api_seguimiento_cliente_id_fk
                FOREIGN KEY (cliente_id) REFERENCES api_cliente(id) ON DELETE CASCADE
            """)
            print("cliente_id added, populated and FK created.")
        else:
            print("cliente_id already exists.")
            # Make sure FK is CASCADE
            try:
                cursor.execute("ALTER TABLE api_seguimiento DROP FOREIGN KEY api_seguimiento_cliente_id_fk")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE api_seguimiento DROP FOREIGN KEY api_seguimiento_cliente_id_7a256920_fk_api_cliente_id")
            except:
                pass
            cursor.execute("""
                ALTER TABLE api_seguimiento
                ADD CONSTRAINT api_seguimiento_cliente_id_fk
                FOREIGN KEY (cliente_id) REFERENCES api_cliente(id) ON DELETE CASCADE
            """)
            print("FK recreated as CASCADE.")

        if 'fecha_seguimiento' not in cols:
            print("Adding fecha_seguimiento...")
            cursor.execute("ALTER TABLE api_seguimiento ADD COLUMN fecha_seguimiento date")

        if 'respuesta_seguimiento' not in cols:
            print("Adding respuesta_seguimiento...")
            cursor.execute("ALTER TABLE api_seguimiento ADD COLUMN respuesta_seguimiento longtext")

        if 'fecha_respuesta_seguimiento' not in cols:
            print("Adding fecha_respuesta_seguimiento...")
            cursor.execute("ALTER TABLE api_seguimiento ADD COLUMN fecha_respuesta_seguimiento date")

        if 'tipo' not in cols:
            print("Adding tipo column...")
            cursor.execute("ALTER TABLE api_seguimiento ADD COLUMN tipo varchar(50) NOT NULL DEFAULT 'General'")

        print("\nAll done! Final columns:")
        cursor.execute("SHOW COLUMNS FROM api_seguimiento")
        for row in cursor.fetchall():
            print(f"  {row[0]} ({row[1]})")

if __name__ == "__main__":
    try:
        sync_seguimiento()
    except Exception as e:
        print(f"Error: {e}")
