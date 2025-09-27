import os
import sys
import traceback
import subprocess

# Set environment variables
os.environ['SECRET_KEY'] = 'dev-secret-for-ci'
os.environ['TENANT_DOMAIN'] = 'tenant1.lvh.me'
os.environ['USE_INMEMORY_DB'] = '1'

print('Environment variables set:', flush=True)
print(f'SECRET_KEY: {os.environ.get("SECRET_KEY")}', flush=True)
print(f'USE_INMEMORY_DB: {os.environ.get("USE_INMEMORY_DB")}', flush=True)

try:
    print('Starting uvicorn server...', flush=True)
    
    # Run uvicorn
    subprocess.run([
        sys.executable, '-m', 'uvicorn', 
        'app.main:app', 
        '--host', '127.0.0.1', 
        '--port', '8000',
        '--log-level', 'info'
    ])
    
except Exception as e:
    print(f'Error starting server: {e}', flush=True)
    traceback.print_exc()
    sys.exit(1)