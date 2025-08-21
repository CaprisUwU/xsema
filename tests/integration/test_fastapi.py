from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    print("Starting FastAPI server on http://localhost:8005/")
    uvicorn.run(app, host="0.0.0.0", port=8005, log_level="info")
