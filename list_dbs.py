
import pymysql

def list_databases(user, password, host='localhost', port=3306):
    print(f"Connecting as {user}...")
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        print("Connected! Listing databases:")
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            for db in cursor.fetchall():
                print(f"- {db[0]}")
        connection.close()
    except Exception as e:
        print(f"FAILED: {e}")

list_databases('root', 'root')
