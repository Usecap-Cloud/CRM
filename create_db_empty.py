
import pymysql

def create_database(user, password, db_name, host='localhost', port=3306):
    print(f"Connecting as {user} to create '{db_name}'...")
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"SUCCESS: Database '{db_name}' created or already exists.")
        connection.close()
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

# Try with empty password
create_database('root', '', 'crm_usecap')
