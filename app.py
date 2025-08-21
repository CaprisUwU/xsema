from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="XSEMA", version="2.0.0")

@app.get("/")
async def root():
    return HTMLResponse("""
    <html>
        <head><title>XSEMA Platform</title></head>
        <body>
            <h1>🚀 XSEMA Successfully Deployed on Railway!</h1>
            <p>Advanced NFT Security & Analytics Platform</p>
            <p>Status: ✅ Production Ready</p>
        </body>
    </html>
    """)

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "XSEMA is running"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
