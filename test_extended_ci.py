#!/usr/bin/env python3
"""
Extended CI simulation test with longer wait periods to match CI behavior
"""
import os
import sys
import subprocess
import time
import requests

def test_extended_ci_scenario():
    """Test the scenario with extended wait periods like CI"""
    
    # Set CI environment variables
    env = os.environ.copy()
    env.update({
        'SECRET_KEY': 'dev-secret-for-ci',
        'USE_INMEMORY_DB': '1'
    })
    
    print("Starting extended CI simulation test...")
    
    # Start the server
    process = subprocess.Popen([
        sys.executable, '-m', 'uvicorn', 
        'app.main:app', 
        '--host', '127.0.0.1', 
        '--port', '8000'
    ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    print(f"API process started with PID: {process.pid}")
    
    try:
        # Wait for startup (CI environments might be slower)
        print("Waiting for server startup...")
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            print("❌ API process died during startup!")
            print("STDOUT:", stdout)
            print("STDERR:", stderr)
            return False
        
        print(f"✅ API process is running after startup (PID: {process.pid})")
        
        # Test health endpoint
        headers = {'Host': 'tenant1.lvh.me'}
        response = requests.get('http://127.0.0.1:8000/health', headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"✅ Health check passed: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        
        # Extended wait period (simulating CI test execution)
        print("Waiting for extended period to simulate CI test execution...")
        for i in range(10):  # 10 seconds, checking every second
            time.sleep(1)
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                print(f"❌ API process died after {i+1} seconds post-request!")
                print("Final API output:")
                print("=== STDOUT ===")
                print(stdout)
                print("=== STDERR ===")
                print(stderr)
                return False
            
            print(f"⏳ Process still alive after {i+1} seconds")
        
        # Final health check
        try:
            response = requests.get('http://127.0.0.1:8000/health', headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"✅ Final health check passed: {response.json()}")
            else:
                print(f"❌ Final health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Final health check error: {e}")
            return False
        
        # Check one more time if process is still running
        if process.poll() is None:
            print(f"✅ API process survived extended testing (PID: {process.pid})")
            print("✅ Extended CI scenario test PASSED!")
            return True
        else:
            stdout, stderr = process.communicate()
            print("❌ API process died at the end of testing!")
            print("Final API output:")
            print("=== STDOUT ===")
            print(stdout)
            print("=== STDERR ===")
            print(stderr)
            return False
            
    finally:
        # Cleanup
        if process.poll() is None:
            print("Terminating process...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    success = test_extended_ci_scenario()
    sys.exit(0 if success else 1)