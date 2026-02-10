import pandas as pd
import requests

# 1. Create a sample Excel file
data = {
    'RUT': ['11.222.333-4', '55.666.777-8'],
    'RAZON_SOCIAL': ['Import Test Co', 'Batch Client Ltd'],
    'ESTADO': ['activo', 'activo']
}
df = pd.DataFrame(data)
df.to_excel('test_clients.xlsx', index=False)
print("Test Excel file created: test_clients.xlsx")

# 2. Upload to the API
# Note: We need to handle CSRF if it's protected, but for a quick test 
# we can check if it's even reachable or if we need to disable CSRF for this test.
# Since runserver is active, we try localhost.

url = 'http://127.0.0.1:8000/api/importar-clientes-excel/'
files = {'file': open('test_clients.xlsx', 'rb')}

try:
    # We might need to get a CSRF token first or use a session
    client = requests.Session()
    client.get('http://127.0.0.1:8000/') # Visit home to get cookie
    if 'csrftoken' in client.cookies:
        headers = {'X-CSRFToken': client.cookies['csrftoken']}
    else:
        headers = {}
        
    response = client.post(url, files=files, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error during upload: {str(e)}")
