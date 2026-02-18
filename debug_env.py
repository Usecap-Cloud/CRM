import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

print(f"BASE_DIR: {BASE_DIR}")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"MYSQL_HOST: {os.getenv('MYSQL_HOST')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD')}")
