import os
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_usecap.settings')
import django
django.setup()

try:
    from backend.api.models import Cliente
    print("SUCCESS: Imported Cliente from backend.api.models")
except Exception as e:
    import traceback
    print("FAILED: backend.api.models")
    traceback.print_exc()

try:
    from api.models import Cliente
    print("SUCCESS: Imported Cliente from api.models")
except Exception as e:
    import traceback
    print("FAILED: api.models")
    traceback.print_exc()
