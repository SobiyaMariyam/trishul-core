"""
Final CI Test - Clean Version
This test verifies that the "API process died before tests!" error has been resolved.
No emojis, just clean testing output.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def main():
    print(f"Python: {sys.executable}")
    print(f"Working directory: {Path.cwd()}")
    print(f"Test script: {__file__}")
    print()
    
    print("Final CI Pipeline Simulation Test")
    print("=" * 50)
    
    # Set environment variables exactly like CI
    os.environ["SECRET_KEY"] = "dev-secret-for-ci"
    os.environ["USE_INMEMORY_DB"] = "1"
    
    print("Environment variables configured:")
    print(f"  SECRET_KEY: {os.environ.get('SECRET_KEY')}")
    print(f"  USE_INMEMORY_DB: {os.environ.get('USE_INMEMORY_DB')}")
    print()
    
    # Start API server
    print("Starting API server process...")
    process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "app.main:app", "--host", "127.0.0.1", "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    print(f"API process started with PID: {process.pid}")
    print()
    
    try:
        # Phase 1: Wait for startup
        print("Phase 1: Waiting for server startup...")
        startup_time = 5
        for i in range(startup_time):
            if process.poll() is not None:
                print("ERROR: API process died during startup!")
                return False
            print(f"  Waiting... {i+1}/{startup_time}")
            time.sleep(1)
        print("PASS: Startup phase completed")
        print()
        
        # Phase 2: Health check
        print("Phase 2: Running health check...")
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=10)
            if response.status_code == 200:
                result = response.json()
                print(f"PASS: Health check successful: {result}")
            else:
                print(f"FAIL: Health check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"FAIL: Health check failed: {e}")
            return False
        print()
        
        # Phase 3: Process stability check
        print("Phase 3: Verifying process stability...")
        post_request_wait = 3
        for i in range(post_request_wait):
            if process.poll() is not None:
                print("ERROR: API process died after handling request!")
                return False
            print(f"  Process still alive... {i+1}/{post_request_wait}")
            time.sleep(1)
        print("PASS: Process remained stable after handling request")
        print()
        
        # Phase 4: Additional requests
        print("Phase 4: Running additional requests...")
        additional_requests = 3
        for i in range(additional_requests):
            try:
                response = requests.get("http://127.0.0.1:8000/health", timeout=5)
                if response.status_code == 200:
                    print(f"  PASS: Request {i+1}: {response.json()}")
                else:
                    print(f"  FAIL: Request {i+1} failed: HTTP {response.status_code}")
                    return False
            except Exception as e:
                print(f"  FAIL: Request {i+1} failed: {e}")
                return False
            
            # Check process is still alive after each request
            if process.poll() is not None:
                print(f"ERROR: API process died during request {i+1}!")
                return False
            
            time.sleep(0.5)  # Brief pause between requests
        
        print("PASS: All additional requests successful")
        print()
        
        # Final check
        if process.poll() is None:
            print("SUCCESS: API process survived complete CI test simulation!")
            print(f"   Process PID {process.pid} is still running")
            print(f"   The 'API process died before tests!' error should be resolved")
            return True
        else:
            print("ERROR: API process died at final check")
            return False
        
    finally:
        # Clean up
        if process.poll() is None:
            print(f"\\nCleaning up process {process.pid}...")
            process.terminate()
            try:
                process.wait(timeout=10)
                print("Process terminated")
            except subprocess.TimeoutExpired:
                process.kill()
                print("Process killed")

if __name__ == "__main__":
    success = main()
    print()
    if success:
        print("FINAL RESULT: SUCCESS!")
        print("The CI pipeline should now work correctly.")
        print("The 'API process died before tests!' error has been resolved.")
    else:
        print("FINAL RESULT: FAILURE!")
        print("The issue still needs to be resolved.")
    
    sys.exit(0 if success else 1)