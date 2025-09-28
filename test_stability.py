#!/usr/bin/env python3
"""
Minimal test to validate the API stays running and responds to requests
"""
import os
import sys
import subprocess
import time
import requests
from threading import Thread

def start_server():
    """Start the API server in background"""
    env = os.environ.copy()
    env.update({
        'SECRET_KEY': 'dev-secret-for-ci',
        'USE_INMEMORY_DB': '1'
    })
    
    process = subprocess.Popen([
        sys.executable, '-m', 'uvicorn', 
        'app.main:app', 
        '--host', '127.0.0.1', 
        '--port', '8000',
        '--log-level', 'info'
    ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    return process

def test_health_endpoint(max_attempts=10):
    """Test the health endpoint"""
    headers = {'Host': 'tenant1.lvh.me'}
    
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://127.0.0.1:8000/health', headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ Health check passed (attempt {attempt + 1}): {response.json()}")
                return True
            else:
                print(f"❌ Health check failed with status {response.status_code}")
        except Exception as e:
            print(f"⏳ Waiting for server (attempt {attempt + 1}): {e}")
        time.sleep(1)
    
    print("❌ Health check failed after all attempts")
    return False

if __name__ == "__main__":
    print("Starting API server test...")
    
    process = start_server()
    
    try:
        # Wait for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print("❌ Process died early!")
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            sys.exit(1)
        
        # Test health endpoint
        if test_health_endpoint():
            # Check if process is still running after health check
            if process.poll() is None:
                print("✅ API server is stable and responsive!")
                
                # Test multiple requests
                for i in range(3):
                    if test_health_endpoint(max_attempts=1):
                        print(f"✅ Additional request {i+1} succeeded")
                    else:
                        print(f"❌ Additional request {i+1} failed")
                        break
                    time.sleep(0.5)
                
                if process.poll() is None:
                    print("✅ Process remained stable throughout testing!")
                else:
                    print("❌ Process died during testing")
                    
            else:
                print("❌ Process died after health check")
        else:
            print("❌ Health endpoint test failed")
            
    finally:
        # Cleanup
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        print("Test completed.")