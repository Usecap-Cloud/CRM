import os
import django
from django.db import connection
from dotenv import load_dotenv

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()

def fix_constraints():
    with connection.cursor() as cursor:
        print("Fixing api_contrato...")
        cursor.execute("ALTER TABLE api_contrato DROP FOREIGN KEY api_contrato_cliente_id_43b3a6e4_fk_api_cliente_id")
        cursor.execute("ALTER TABLE api_contrato ADD CONSTRAINT api_contrato_cliente_id_43b3a6e4_fk_api_cliente_id FOREIGN KEY (cliente_id) REFERENCES api_cliente(id) ON DELETE CASCADE")
        
        cursor.execute("ALTER TABLE api_contrato DROP FOREIGN KEY api_contrato_ejecutivo_id_a6e5c0eb_fk_api_ejecutivo_id")
        cursor.execute("ALTER TABLE api_contrato ADD CONSTRAINT api_contrato_ejecutivo_id_a6e5c0eb_fk_api_ejecutivo_id FOREIGN KEY (ejecutivo_id) REFERENCES api_ejecutivo(id) ON DELETE CASCADE")

        cursor.execute("ALTER TABLE api_contrato DROP FOREIGN KEY api_contrato_coordinador_id_d43ae57d_fk_api_coordinador_id")
        cursor.execute("ALTER TABLE api_contrato ADD CONSTRAINT api_contrato_coordinador_id_d43ae57d_fk_api_coordinador_id FOREIGN KEY (coordinador_id) REFERENCES api_coordinador(id) ON DELETE SET NULL")

        print("Fixing api_coordinador...")
        cursor.execute("ALTER TABLE api_coordinador DROP FOREIGN KEY api_coordinador_cliente_id_6feaf450_fk_api_cliente_id")
        cursor.execute("ALTER TABLE api_coordinador ADD CONSTRAINT api_coordinador_cliente_id_6feaf450_fk_api_cliente_id FOREIGN KEY (cliente_id) REFERENCES api_cliente(id) ON DELETE CASCADE")

        print("Fixing api_seguimiento...")
        # Note: I need the exact constraint names from the previous output
        cursor.execute("ALTER TABLE api_seguimiento DROP FOREIGN KEY api_seguimiento_contrato_id_76009f78_fk_api_contrato_id")
        cursor.execute("ALTER TABLE api_seguimiento ADD CONSTRAINT api_seguimiento_contrato_id_76009f78_fk_api_contrato_id FOREIGN KEY (contrato_id) REFERENCES api_contrato(id) ON DELETE CASCADE")
        
        cursor.execute("ALTER TABLE api_seguimiento DROP FOREIGN KEY api_seguimiento_coordinador_id_e5bf41b6_fk_api_coordinador_id")
        cursor.execute("ALTER TABLE api_seguimiento ADD CONSTRAINT api_seguimiento_coordinador_id_e5bf41b6_fk_api_coordinador_id FOREIGN KEY (coordinador_id) REFERENCES api_coordinador(id) ON DELETE CASCADE")
        
        cursor.execute("ALTER TABLE api_seguimiento DROP FOREIGN KEY api_seguimiento_ejecutivo_id_d564f843_fk_api_ejecutivo_id")
        cursor.execute("ALTER TABLE api_seguimiento ADD CONSTRAINT api_seguimiento_ejecutivo_id_d564f843_fk_api_ejecutivo_id FOREIGN KEY (ejecutivo_id) REFERENCES api_ejecutivo(id) ON DELETE CASCADE")

        # Table api_seguimiento also has cliente_id in model but maybe not in DB
        try:
             # Check if column exists first
             cursor.execute("SHOW COLUMNS FROM api_seguimiento LIKE 'cliente_id'")
             if cursor.fetchone():
                 cursor.execute("ALTER TABLE api_seguimiento DROP FOREIGN KEY api_seguimiento_cliente_id_7a256920_fk_api_cliente_id")
                 cursor.execute("ALTER TABLE api_seguimiento ADD CONSTRAINT api_seguimiento_cliente_id_7a256920_fk_api_cliente_id FOREIGN KEY (cliente_id) REFERENCES api_cliente(id) ON DELETE CASCADE")
                 print("  api_seguimiento.cliente_id -> CASCADE")
             else:
                 print("  api_seguimiento.cliente_id column missing, skipping.")
        except Exception as e:
             print(f"  Skipping api_seguimiento.cliente_id: {e}")

        print("Fixing api_contratocurso...")
        cursor.execute("ALTER TABLE api_contratocurso DROP FOREIGN KEY api_contratocurso_contrato_id_dd62ec75_fk_api_contrato_id")
        cursor.execute("ALTER TABLE api_contratocurso ADD CONSTRAINT api_contratocurso_contrato_id_dd62ec75_fk_api_contrato_id FOREIGN KEY (contrato_id) REFERENCES api_contrato(id) ON DELETE CASCADE")

        print("Fixing api_contratoservicio...")
        cursor.execute("ALTER TABLE api_contratoservicio DROP FOREIGN KEY api_contratoservicio_contrato_id_927bec57_fk_api_contrato_id")
        cursor.execute("ALTER TABLE api_contratoservicio ADD CONSTRAINT api_contratoservicio_contrato_id_927bec57_fk_api_contrato_id FOREIGN KEY (contrato_id) REFERENCES api_contrato(id) ON DELETE CASCADE")

        print("Fixing api_contratoproveedor...")
        cursor.execute("ALTER TABLE api_contratoproveedor DROP FOREIGN KEY api_contratoproveedor_contrato_id_73f25b1d_fk_api_contrato_id")
        cursor.execute("ALTER TABLE api_contratoproveedor ADD CONSTRAINT api_contratoproveedor_contrato_id_73f25b1d_fk_api_contrato_id FOREIGN KEY (contrato_id) REFERENCES api_contrato(id) ON DELETE CASCADE")

        print("All constraints fixed!")

if __name__ == "__main__":
    try:
        fix_constraints()
    except Exception as e:
        print(f"Error during execution: {e}")
