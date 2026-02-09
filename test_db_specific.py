
import pymysql
import sys

def test_db_connection(user, password, db_name, host='localhost', port=3306):
    print(f"Testing connection to DB '{db_name}' with user: {user}...")
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
            port=port
        )
        print("SUCCESS: Connected to database!")
        connection.close()
        return True
    except pymysql.err.OperationalError as e:
        print(f"FAILED: {e}")
        # Check error code for "Unknown database"
        if e.args[0] == 1049:
            print("DIAGNOSIS: Database does not exist.")
        elif e.args[0] == 1045:
            print("DIAGNOSIS: Access denied.")
        return False
    except Exception as e:
        print(f"FAILED: {e}")
        return False

test_db_connection('root', 'root', 'crm_usecap')
