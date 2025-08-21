"""
XSEMA Railway Deployment Entry Point
Minimal version for Railway deployment
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI(
    title="XSEMA",
    description="Advanced NFT Security & Analytics Platform",
    version="2.0.0"
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint serving XSEMA frontend."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>XSEMA - NFT Analytics Platform</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2563eb; text-align: center; }
            .status { background: #10b981; color: white; padding: 10px; border-radius: 5px; text-align: center; margin: 20px 0; }
            .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
            .feature { background: #f8fafc; padding: 20px; border-radius: 5px; border-left: 4px solid #2563eb; }
            .api-link { text-align: center; margin: 30px 0; }
            .api-link a { background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 XSEMA Platform</h1>
            <div class="status">
                ✅ Successfully Deployed on Railway!
            </div>
            
            <p>Welcome to XSEMA - Advanced NFT Security & Analytics Platform</p>
            
            <div class="features">
                <div class="feature">
                    <h3>🔒 Security Analysis</h3>
                    <p>Advanced contract security scanning</p>
                </div>
                <div class="feature">
                    <h3>📊 Portfolio Management</h3>
                    <p>Comprehensive NFT portfolio tracking</p>
                </div>
                <div class="feature">
                    <h3>🔍 Market Analytics</h3>
                    <p>Real-time market intelligence</p>
                </div>
                <div class="feature">
                    <h3>🎯 Trait Analysis</h3>
                    <p>Advanced NFT trait evaluation</p>
                </div>
            </div>
            
            <div class="api-link">
                <a href="/docs">📚 View API Documentation</a>
            </div>
            
            <p style="text-align: center; color: #6b7280; margin-top: 40px;">
                XSEMA v2.0.0 | Deployed on Railway | Production Ready
            </p>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "platform": "railway", "version": "2.0.0"}

@app.get("/docs")
async def docs():
    """API documentation endpoint."""
    return {"message": "API documentation available at /docs", "status": "operational"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
