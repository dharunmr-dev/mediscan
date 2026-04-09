from contextlib import asynccontextmanager
import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mlx_vlm import generate
from mlx_vlm.utils import load_image, load


class ExtractRequest(BaseModel):
    image_path: str
    prompt: str


class ExtractResponse(BaseModel):
    success: bool
    raw_response: str | None = None
    error: str | None = None


MODEL_NAME = os.environ.get("AI_MODEL", "mlx-community/Qwen3.5-9B-MLX-4bit")
MAX_TOKENS = int(os.environ.get("AI_MAX_TOKENS", "10000"))
PORT = int(os.environ.get("AI_PORT", "8001"))

model = None
processor = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, processor
    print(f"Loading model: {MODEL_NAME}...")
    model, processor = load(MODEL_NAME)
    print(f"Model loaded successfully!")
    print(f"Will listen on port: {PORT}")
    yield


app = FastAPI(
    title="Mediscan AI Server",
    description="MLX-VLM wrapper for prescription extraction",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/extract", response_model=ExtractResponse)
async def extract_prescription(request: ExtractRequest):
    global model, processor

    if not os.path.exists(request.image_path):
        raise HTTPException(
            status_code=400, detail=f"Image not found: {request.image_path}"
        )

    if model is None or processor is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    try:
        image = load_image(request.image_path)

        result = generate(
            model=model,
            processor=processor,
            prompt=request.prompt,
            image=image,
            max_tokens=MAX_TOKENS,
        )

        raw_response = result.strip()

        return ExtractResponse(
            success=True,
            raw_response=raw_response,
        )

    except Exception as e:
        return ExtractResponse(
            success=False,
            error=str(e),
        )


@app.get("/health")
async def health():
    return {"status": "healthy", "model": MODEL_NAME, "loaded": model is not None}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=PORT)
