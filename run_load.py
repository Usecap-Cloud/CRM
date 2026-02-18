import subprocess
import sys

try:
    process = subprocess.Popen(
        ['python', 'manage.py', 'loaddata', 'initial_data.json'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    stdout, _ = process.communicate()
    lines = stdout.splitlines()
    for line in lines[-20:]:  # Last 20 lines usually contain the actual error
        print(line)
except Exception as e:
    print(f"Error: {e}")
