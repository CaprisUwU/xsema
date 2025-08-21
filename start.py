#!/usr/bin/env python3
"""
XSEMA Railway Start Script
Simple startup script for Railway deployment
"""

import os
import uvicorn
from main_railway import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
