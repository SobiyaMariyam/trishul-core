#!/usr/bin/env python3
"""
GitHub Actions compatible API wrapper
This script handles auto-restart in GitHub Actions environment
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def log(message):
    """Simple logging with timestamp"""
    timestamp = time.strftime("%H:%M:%S")
    print(f"[{timestamp}] WRAPPER: {message}", flush=True)

def is_github_actions():
    """Detect if running in GitHub Actions"""
    return (
        os.getenv("GITHUB_ACTIONS") == "true" or
        os.getenv("CI") == "true" or
        "hostedtoolcache" in sys.executable.lower() or
        "\\a\\" in os.getcwd() or
        "/home/runner" in os.getcwd().lower()
    )

def wait_for_api_ready(timeout=60):
    """Wait for API to become ready - longer timeout for GitHub Actions"""
    try:
        import requests
    except ImportError:
        log("Installing requests...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    for i in range(timeout):
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=3)
            if response.status_code == 200:
                log(f"API ready after {i} seconds")
                return True
        except:
            pass
        time.sleep(1)
    
    log(f"API not ready after {timeout} seconds")
    return False

def main():
    """Main wrapper for GitHub Actions"""
    log("Starting GitHub Actions API wrapper")
    
    # Set environment for CI
    os.environ["USE_INMEMORY_DB"] = "1"
    
    is_github = is_github_actions()
    log(f"GitHub Actions detected: {is_github}")
    
    max_attempts = 5 if is_github else 3
    timeout = 60 if is_github else 30
    
    for attempt in range(1, max_attempts + 1):
        log(f"Starting API (attempt {attempt}/{max_attempts})")
        
        # Start the API process
        api_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ], 
        env=os.environ.copy(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
        )
        
        log(f"API started with PID {api_process.pid}")
        
        # Write PID for external monitoring
        with open("api_process_id.txt", "w") as f:
            f.write(str(api_process.pid))
        
        # Wait for API to be ready
        if wait_for_api_ready(timeout):
            log("API is ready and healthy!")
            
            # For GitHub Actions, just keep it running
            if is_github:
                log("GitHub Actions mode: maintaining API process...")
                try:
                    # Keep the process alive and log output
                    while api_process.poll() is None:
                        time.sleep(10)
                        log(f"API PID {api_process.pid} is running")
                        
                        # Check health periodically
                        try:
                            import requests
                            requests.get("http://127.0.0.1:8000/health", timeout=2)
                            log("Health check passed")
                        except:
                            log("Health check failed - API may be dying")
                            break
                            
                except KeyboardInterrupt:
                    log("Shutdown requested")
                    break
                
                # Process died
                stdout, _ = api_process.communicate(timeout=5)
                log(f"API process died with exit code {api_process.returncode}")
                
                if stdout:
                    log(f"API output: {stdout[-500:]}")  # Last 500 chars
                    
            else:
                # Local mode - just wait indefinitely
                log("Local mode: API running successfully")
                try:
                    api_process.wait()
                except KeyboardInterrupt:
                    log("Shutdown requested")
                    break
        else:
            log("API failed to become ready")
            
        # Cleanup this attempt
        if api_process.poll() is None:
            api_process.terminate()
            time.sleep(3)
            if api_process.poll() is None:
                api_process.kill()
        
        if attempt < max_attempts:
            log(f"Retrying in 3 seconds...")
            time.sleep(3)
    
    log("Wrapper shutdown complete")

if __name__ == "__main__":
    main()