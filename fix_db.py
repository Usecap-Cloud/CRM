import sys
import os
import django

print(f"Python: {sys.executable}")
print(f"Path: {sys.path}")
try:
    from django.core.management import execute_from_command_line
    print("Django management imported successfully")
except ImportError as e:
    print(f"Failed to import Django management: {e}")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
django.setup()
print("Django setup successful")

from django.core.management import call_command
print("Creating migrations...")
call_command('makemigrations', 'api')
print("Applying migrations...")
call_command('migrate', 'api')
print("Done")
