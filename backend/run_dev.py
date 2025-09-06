#!/usr/bin/env python3
"""
Development server runner for Agendo backend.
Starts the FastAPI application with auto-reload enabled.
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

if __name__ == "__main__":
    # Load environment variables from .env file
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🚀 Starting Awendo Backend Development Server...")
    print("📝 Auto-reload enabled")
    print("🌐 API Documentation: http://localhost:8000/docs")
    print("📊 Health Check: http://localhost:8000/health")
    print("🔗 Webhook Endpoint: http://localhost:8000/api/v1/webhooks/evolution")
    print("-" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )
