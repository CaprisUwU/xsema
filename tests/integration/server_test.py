from fastapi import FastAPI
import uvicorn
import socket
import sys
import os

app = FastAPI()

@app.get("/")
async def root():
    return {
        "message": "FastAPI Server is running!",
        "python_version": sys.version,
        "python_executable": sys.executable,
        "working_directory": os.getcwd(),
        "hostname": socket.gethostname(),
        "status": "success"
    }

if __name__ == "__main__":
    port = 8000
    print(f"\n=== Starting FastAPI Test Server ===")
    print(f"Python: {sys.executable}")
    print(f"Port: {port}")
    print("==============================\n")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    except Exception as e:
        print(f"Error starting server: {e}")
        raise
