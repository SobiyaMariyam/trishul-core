"""
Advanced CI Test Script - Simulates exact GitHub Actions environment
This script replicates the exact conditions and timing of the CI environment
to identify why the API process dies after handling health checks.
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def setup_ci_environment():
    """Setup exact CI environment variables"""
    print("Setting up CI environment variables...")
    
    # Set the exact environment that CI uses
    env_vars = {
        "SECRET_KEY": "dev-secret-for-ci",
        "TENANT_DOMAIN": "tenant1.lvh.me", 
        "USE_INMEMORY_DB": "1",
        "PYTHONPATH": str(Path.cwd()),
        "PYTHONUNBUFFERED": "1",  # Ensure output is not buffered
        "PYTHONIOENCODING": "utf-8",  # Handle encoding issues
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"  {key} = {value}")
    
    print("CI environment setup complete")
    return env_vars

def start_api_server():
    """Start the API server exactly like CI does"""
    print("\nStarting API server (CI mode)...")
    
    # Use the exact command that CI uses
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "app.main:app", 
        "--host", "127.0.0.1", 
        "--port", "8000",
        "--log-level", "info"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    # Start the process with proper stdout/stderr handling
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # Line buffered
        universal_newlines=True,
        cwd=str(Path.cwd())
    )
    
    print(f"API server started with PID: {process.pid}")
    return process

def wait_for_server_ready(timeout=30):
    """Wait for server to be ready with enhanced monitoring"""
    print(f"\nWaiting for server to be ready (timeout: {timeout}s)...")
    
    start_time = time.time()
    ready = False
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=5)
            if response.status_code == 200:
                print("Server is ready!")
                print(f"Health check response: {response.json()}")
                ready = True
                break
        except requests.exceptions.RequestException as e:
            pass  # Expected while server is starting
        
        time.sleep(1)
        elapsed = time.time() - start_time
        if elapsed % 5 == 0:  # Progress update every 5 seconds
            print(f"  Still waiting... ({elapsed:.1f}s elapsed)")
    
    if not ready:
        print("TIMEOUT: Server did not become ready in time")
        return False
    
    return True

def monitor_process_lifecycle(process, duration=60):
    """Monitor the process for unexpected termination"""
    print(f"\nMonitoring process lifecycle for {duration} seconds...")
    
    start_time = time.time()
    last_check_time = start_time
    
    stdout_lines = []
    stderr_lines = []
    
    while time.time() - start_time < duration:
        # Check if process is still running
        poll_result = process.poll()
        if poll_result is not None:
            print(f"CRITICAL: Process terminated unexpectedly with code {poll_result}")
            
            # Capture any remaining output
            try:
                remaining_stdout, remaining_stderr = process.communicate(timeout=5)
                if remaining_stdout:
                    stdout_lines.extend(remaining_stdout.split('\n'))
                if remaining_stderr:
                    stderr_lines.extend(remaining_stderr.split('\n'))
            except subprocess.TimeoutExpired:
                print("Warning: Could not capture remaining output")
            
            return False, stdout_lines, stderr_lines
        
        # Capture output non-blockingly
        try:
            # Read available stdout
            while True:
                try:
                    line = process.stdout.readline()
                    if not line:
                        break
                    line = line.strip()
                    if line:
                        stdout_lines.append(line)
                        print(f"STDOUT: {line}")
                except:
                    break
            
            # Read available stderr
            while True:
                try:
                    line = process.stderr.readline()
                    if not line:
                        break
                    line = line.strip()
                    if line:
                        stderr_lines.append(line)
                        print(f"STDERR: {line}")
                except:
                    break
                    
        except Exception as e:
            print(f"Error reading process output: {e}")
        
        # Progress update
        current_time = time.time()
        if current_time - last_check_time >= 10:
            elapsed = current_time - start_time
            print(f"Process still running after {elapsed:.1f}s")
            last_check_time = current_time
        
        time.sleep(0.5)  # Check twice per second
    
    print("Process survived the monitoring period")
    return True, stdout_lines, stderr_lines

def perform_api_tests():
    """Perform the exact API tests that CI does"""
    print("\nPerforming API tests...")
    
    tests = [
        {
            "name": "Health Check",
            "method": "GET",
            "url": "http://127.0.0.1:8000/health",
            "headers": {"Host": "tenant1.lvh.me"}
        },
        {
            "name": "Health Check (no host)",
            "method": "GET", 
            "url": "http://127.0.0.1:8000/health",
            "headers": {}
        }
    ]
    
    results = []
    
    for test in tests:
        print(f"\nRunning test: {test['name']}")
        
        try:
            if test['method'] == 'GET':
                response = requests.get(test['url'], headers=test['headers'], timeout=10)
            else:
                response = requests.request(test['method'], test['url'], headers=test['headers'], timeout=10)
            
            result = {
                "test": test['name'],
                "status_code": response.status_code,
                "success": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "content": response.text
            }
            
            print(f"  Status: {response.status_code}")
            print(f"  Response time: {result['response_time']:.3f}s")
            print(f"  Content: {response.text}")
            
            results.append(result)
            
        except Exception as e:
            result = {
                "test": test['name'],
                "success": False,
                "error": str(e)
            }
            print(f"  ERROR: {e}")
            results.append(result)
    
    return results

def main():
    """Main test execution"""
    print("=== Advanced CI Test Script ===")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {Path.cwd()}")
    print(f"Script path: {__file__}")
    
    # Setup environment
    env_vars = setup_ci_environment()
    
    # Start API server
    process = start_api_server()
    
    try:
        # Wait for server to be ready
        if not wait_for_server_ready():
            print("FAIL: Server did not start properly")
            return 1
        
        # Perform initial API tests
        test_results = perform_api_tests()
        
        # Monitor process for stability
        print(f"\nStarting extended monitoring...")
        process_survived, stdout_lines, stderr_lines = monitor_process_lifecycle(process, duration=30)
        
        if not process_survived:
            print("CRITICAL: Process died during monitoring")
            
            print("\nFinal process output:")
            print("=== STDOUT ===")
            for line in stdout_lines[-20:]:  # Last 20 lines
                print(line)
            print("\n=== STDERR ===") 
            for line in stderr_lines[-20:]:  # Last 20 lines
                print(line)
            
            return 1
        
        # Perform final API tests
        print("\nPerforming final API tests...")
        final_test_results = perform_api_tests()
        
        print("\nSUCCESS: Process remained stable throughout testing")
        print(f"Total tests performed: {len(test_results) + len(final_test_results)}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    finally:
        # Clean shutdown
        print("\nCleaning up...")
        try:
            if process and process.poll() is None:
                print(f"Terminating process {process.pid}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=10)
                    print("Process terminated gracefully")
                except subprocess.TimeoutExpired:
                    print("Process did not terminate gracefully, forcing kill")
                    process.kill()
                    process.wait()
        except Exception as e:
            print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)