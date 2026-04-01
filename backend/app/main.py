from fastapi import FastAPI
from app.api.routes import router

# Create FastAPI instance
app = FastAPI(
    title="Mediscan IoT Backend",
    description="Edge backend running on Raspberry Pi for medical data processing",
    version="1.0.0"
)

# Include API routes
app.include_router(router)

# Root endpoint (test)
@app.get("/")
def root():
    return {
        "status": "running",
        "message": "Mediscan backend is working"
    }

# Health check (important for IoT systems)
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
