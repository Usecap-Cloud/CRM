
import pymysql
import sys

def test_connection(user, password, host='localhost', port=3306):
    print(f"Testing connection for user: {user}, password: '{password}'...")
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            port=port
        )
        print("SUCCESS: Connected!")
        connection.close()
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False

# Test common defaults
if test_connection('root', ''):
    print("RECOMMENDATION: Use DB_USER=root and DB_PASSWORD=")
    sys.exit(0)

if test_connection('root', 'root'):
    print("RECOMMENDATION: Use DB_USER=root and DB_PASSWORD=root")
    sys.exit(0)

print("Could not connect with common defaults.")
