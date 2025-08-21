from fastapi import FastAPI
import uvicorn
import socket
import sys
import os

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "FastAPI is working!",
        "python_version": sys.version,
        "python_executable": sys.executable,
        "current_directory": os.getcwd(),
        "hostname": socket.gethostname()
    }

if __name__ == "__main__":
    print("\n=== Starting FastAPI Test Server ===")
    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version}")
    print(f"Port: 8006")
    print("==============================\n")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8006, log_level="info")
    except Exception as e:
        print(f"Error starting server: {e}")
        raise
