
import pymysql
import sys

def check_creds():
    candidates = [
        ('root', ''),
        ('root', 'root'),
        ('root', 'admin'),
        ('root', 'password'),
        ('root', '123456'),
        ('admin', 'admin'),
    ]

    print("STARTING BRUTE FORCE CHECK...", flush=True)

    for user, password in candidates:
        print(f"Testing user='{user}' password='{password}'...", end=" ", flush=True)
        try:
            conn = pymysql.connect(host='localhost', user=user, password=password, port=3306)
            print("SUCCESS!", flush=True)
            print(f"FOUND WORKING CREDENTIALS: DB_USER={user} DB_PASSWORD={password}", flush=True)
            conn.close()
            return
        except Exception as e:
            print(f"FAILED. ({e})", flush=True)
            
    print("ALL ATTEMPTS FAILED.", flush=True)

if __name__ == "__main__":
    check_creds()
