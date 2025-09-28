#!/usr/bin/env python3
"""
Simulate the exact CI test scenario
"""
import os
import sys
import subprocess
import time
import requests
import signal

def test_ci_scenario():
    """Test the exact scenario that was failing in CI"""
    
    # Set CI environment variables
    env = os.environ.copy()
    env.update({
        'SECRET_KEY': 'dev-secret-for-ci',
        'USE_INMEMORY_DB': '1'
    })
    
    print("Starting API server (simulating CI environment)...")
    
    # Start the server
    process = subprocess.Popen([
        sys.executable, '-m', 'uvicorn', 
        'app.main:app', 
        '--host', '127.0.0.1', 
        '--port', '8000'
    ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    print(f"API process started with PID: {process.pid}")
    
    # Wait for startup
    time.sleep(3)
    
    # Check if process is still running
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        print("❌ API process died before tests!")
        print("STDOUT:", stdout)
        print("STDERR:", stderr)
        return False
    
    print(f"✅ API process is running (PID: {process.pid})")
    
    # Test health endpoint (simulating CI test)
    try:
        headers = {'Host': 'tenant1.lvh.me'}
        response = requests.get('http://127.0.0.1:8000/health', headers=headers, timeout=5)
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Check if process is still running after the request
    time.sleep(1)
    
    if process.poll() is None:
        print(f"✅ API process still running after health check (PID: {process.pid})")
        
        # Cleanup
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        
        print("✅ CI scenario test PASSED!")
        return True
    else:
        stdout, stderr = process.communicate()
        print("❌ API process died after health check!")
        print("Final API output:")
        print("=== STDOUT ===")
        print(stdout)
        print("=== STDERR ===")  
        print(stderr)
        return False

if __name__ == "__main__":
    success = test_ci_scenario()
    sys.exit(0 if success else 1)