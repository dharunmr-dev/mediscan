import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routes import router
from app.services.database import init_db


class PrettyJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(content, indent=2, ensure_ascii=False).encode("utf-8")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Mediscan IoT Backend",
    description="Edge backend running on Raspberry Pi for medical data processing",
    version="1.0.0",
    lifespan=lifespan,
    default_response_class=PrettyJSONResponse,
)

app.include_router(router)

# Add CORS middleware (for teammates to access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint (test)
@app.get("/")
def root():
    return {"status": "running", "message": "Mediscan backend is working"}


# Health check (important for IoT systems)
@app.get("/health")
def health_check():
    return {"status": "healthy"}
