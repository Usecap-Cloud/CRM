
import pymysql
import sys

def run_diagnostics():
    user = 'root'
    password = 'root'
    host = 'localhost'
    port = 3306
    target_db = 'crm_usecap'

    print("=== DIAGNOSTICS START ===")
    
    # 1. Basic Connection
    print(f"1. Attempting connection as {user} (no DB)...")
    try:
        conn = pymysql.connect(host=host, user=user, password=password, port=port)
        print("   SUCCESS.")
    except Exception as e:
        print(f"   FAILED: {e}")
        return

    # 2. List Databases
    print("2. Listing databases...")
    try:
        with conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            dbs = [d[0] for d in cursor.fetchall()]
            print(f"   Success. Found {len(dbs)} databases: {', '.join(dbs)}")
            
            if target_db in dbs:
                print(f"   Target '{target_db}' ALREADY EXISTS.")
            else:
                print(f"   Target '{target_db}' DOES NOT EXIST.")
    except Exception as e:
        print(f"   FAILED: {e}")

    # 3. Create Database (if needed)
    print(f"3. Attempting to create/ensure '{target_db}'...")
    try:
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {target_db}")
            print("   SUCCESS: Database created or verified.")
    except Exception as e:
        print(f"   FAILED to create: {e}")

    # 4. Connect to details
    print(f"4. Attempting to connect to '{target_db}'...")
    conn.close()
    try:
        conn = pymysql.connect(host=host, user=user, password=password, database=target_db, port=port)
        print("   SUCCESS.")
        conn.close()
    except Exception as e:
        print(f"   FAILED: {e}")

    print("=== DIAGNOSTICS END ===")

if __name__ == "__main__":
    run_diagnostics()
