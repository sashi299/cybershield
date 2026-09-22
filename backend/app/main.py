import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

import logging

from .database import init_db
from .ml_model import load_model
from .routes import router
from .rate_limiter import RateLimitMiddleware

# Configure logging for NPU modules
logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    load_model()
    
    # Initialize NPU config and vision classifier (non-blocking)
    try:
        from .npu_config import get_system_status
        status = get_system_status()
        print(f"[NPU] Execution Provider: {status['execution_provider']}")
        print(f"[NPU] NPU Available: {status['npu_available']}")
        print(f"[NPU] Models: {status['models_loaded']}")
    except Exception as e:
        print(f"[NPU] Config init skipped: {e}")
    
    try:
        from .vision_classifier import load_model as load_vision
        load_vision()
    except Exception as e:
        print(f"[Vision] Model init skipped: {e}")
    
    yield

app = FastAPI(title="Cyber Shield API", lifespan=lifespan)

# Add Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware, max_requests=60, window_seconds=60)

env_origins = os.getenv("ALLOWED_ORIGINS")
if env_origins:
    origins = [o.strip() for o in env_origins.split(",") if o.strip()]
else:
    origins = ["*"]  # Allow all origins for mobile app & local network development

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True if origins != ["*"] else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

# Mount static frontend build at root '/' (Single-Service Monolith Deployment)
from fastapi.staticfiles import StaticFiles
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist")
if not os.path.exists(frontend_dist):
    frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist")

if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    print(f"Mounted static Web Frontend from {frontend_dist}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
