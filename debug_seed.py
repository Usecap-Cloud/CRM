import os
import subprocess
import sys

# Try to run the management command and capture the full error
try:
    # Use the venv python
    python_exe = os.path.join(os.getcwd(), 'venv', 'Scripts', 'python.exe')
    if not os.path.exists(python_exe):
        python_exe = 'python' # fallback
    
    result = subprocess.run([python_exe, 'manage.py', 'seed_data'], capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("EXIT CODE:", result.returncode)
except Exception as e:
    print("EXCEPTION:", str(e))
