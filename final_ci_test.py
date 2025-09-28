#!/usr/bin/env python3
"""
Final comprehensive test that simulates the exact CI pipeline behavior
"""
import os
import sys
import subprocess
import time
import requests
import json

def test_final_ci_pipeline():
    """Test that replicates the CI pipeline exactly"""
    
    print("Final CI Pipeline Simulation Test")
    print("="*50)
    
    # Set CI environment variables exactly like CI
    env = os.environ.copy()
    env.update({
        'SECRET_KEY': 'dev-secret-for-ci',
        'USE_INMEMORY_DB': '1'
    })
    
    print("Environment variables configured:")
    print(f"  SECRET_KEY: {env.get('SECRET_KEY')}")
    print(f"  USE_INMEMORY_DB: {env.get('USE_INMEMORY_DB')}")
    print()
    
    # Start the server (exactly like CI does)
    print("Starting API server process...")
    process = subprocess.Popen([
        sys.executable, '-m', 'uvicorn', 
        'app.main:app', 
        '--host', '127.0.0.1', 
        '--port', '8000'
    ], env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    print(f"API process started with PID: {process.pid}")
    print()
    
    try:
        # Phase 1: Wait for startup
        print("Phase 1: Waiting for server startup...")
        startup_time = 5  # CI might be slower
        
        for i in range(startup_time):
            if process.poll() is not None:
                output, _ = process.communicate()
                print("❌ API process died during startup!")
                print("Server output:")
                print(output)
                return False
            time.sleep(1)
            print(f"  ⏳ Waiting... {i+1}/{startup_time}")
        
        print("✅ Startup phase completed")
        print()
        
        # Phase 2: Health check (exactly like CI does)
        print("Phase 2: Running health check...")
        try:
            headers = {'Host': 'tenant1.lvh.me'}
            response = requests.get('http://127.0.0.1:8000/health', headers=headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Health check PASSED: {result}")
            else:
                print(f"❌ Health check FAILED: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Health check FAILED: {e}")
            return False
        
        print()
        
        # Phase 3: Check process is still alive after handling request
        print("Phase 3: Verifying process stability...")
        
        # Wait a bit to see if process dies after handling request
        post_request_wait = 3
        for i in range(post_request_wait):
            if process.poll() is not None:
                output, _ = process.communicate()
                print("❌ API process died after handling request!")
                print("Final server output:")
                print(output)
                return False
            time.sleep(1)
            print(f"  ⏳ Process still alive... {i+1}/{post_request_wait}")
        
        print("✅ Process remained stable after handling request")
        print()
        
        # Phase 4: Additional requests (like real tests would do)
        print("Phase 4: Running additional requests...")
        
        for i in range(3):
            try:
                response = requests.get('http://127.0.0.1:8000/health', headers=headers, timeout=5)
                if response.status_code == 200:
                    print(f"  ✅ Request {i+1}: {response.json()}")
                else:
                    print(f"  ❌ Request {i+1} failed: HTTP {response.status_code}")
                    return False
            except Exception as e:
                print(f"  ❌ Request {i+1} failed: {e}")
                return False
            
            # Check process is still alive
            if process.poll() is not None:
                output, _ = process.communicate()
                print(f"❌ API process died during request {i+1}!")
                print("Final server output:")
                print(output)
                return False
            
            time.sleep(0.5)
        
        print("✅ All additional requests successful")
        print()
        
        # Final check
        if process.poll() is None:
            print("🎉 SUCCESS: API process survived complete CI test simulation!")
            print(f"   Process PID {process.pid} is still running")
            print("   The 'API process died before tests!' error should be resolved")
            return True
        else:
            output, _ = process.communicate()
            print("❌ API process died at final check")
            print("Final server output:")
            print(output)
            return False
            
    finally:
        # Cleanup
        if process.poll() is None:
            print(f"\\nCleaning up process {process.pid}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            print("Process terminated")

if __name__ == "__main__":
    print(f"Python: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Test script: {__file__}")
    print()
    
    success = test_final_ci_pipeline()
    
    if success:
        print()
        print("🎉 FINAL RESULT: SUCCESS!")
        print("The CI pipeline should now work correctly.")
        print("The 'API process died before tests!' error has been resolved.")
        sys.exit(0)
    else:
        print()
        print("❌ FINAL RESULT: FAILURE")
        print("The CI pipeline issue persists.")
        sys.exit(1)