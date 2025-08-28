import os
import uuid
import asyncio
from typing import Any
import traceback
import logging

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from crewai import Crew, Process
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from task import analyze_financial_document as analyze_task, investment_analysis, risk_assessment, verification

app = FastAPI(title="Financial Document Analyzer")

# === Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

# === Crew setup at startup ===
financial_crew = Crew(
    agents=[financial_analyst, verifier, investment_advisor, risk_assessor],
    tasks=[analyze_task, investment_analysis, risk_assessment, verification],
    process=Process.sequential,
)


async def maybe_await(maybe_coro: Any) -> Any:
    """Handles both sync and async returns from Crew."""
    if asyncio.iscoroutine(maybe_coro):
        return await maybe_coro
    return maybe_coro


async def run_crew(query: str, file_path: str) -> Any:
    """Executes Crew workflow with given query + document path."""
    payload = {"query": query, "path": os.path.abspath(file_path)}
    logging.info(f"🚀 Running crew with payload: {payload}")
    try:
        result = financial_crew.kickoff(payload)
        result = await maybe_await(result)
        return result
    except Exception as e:
        logging.error(f" Crew execution failed: {e}")
        traceback.print_exc()
        raise


@app.get("/")
async def root():
    return {"message": "Financial Document Analyzer API is running"}


@app.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights")
):
    # --- Validate file extension ---
    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    # --- Ensure data directory exists ---
    os.makedirs("data", exist_ok=True)

    # --- Generate unique safe filename ---
    file_id = str(uuid.uuid4())
    ext = os.path.splitext(filename)[-1].lower()
    file_path = os.path.join("data", f"{file_id}{ext}")

    try:
        # --- Save file ---
        max_size = 10 * 1024 * 1024  # 10 MB
        size = 0
        with open(file_path, "wb") as f_out:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > max_size:
                    raise HTTPException(status_code=413, detail="Uploaded file too large (max 10 MB).")
                f_out.write(chunk)

        logging.info(f" File saved: {file_path} ({size/1024:.1f} KB)")

        # --- Normalize query ---
        query = (query or "").strip() or "Analyze this financial document for investment insights"

        # --- Run crew ---
        response = await run_crew(query=query, file_path=file_path)

        # --- Return formatted response ---
        return {
            "status": "success",
            "query": query,
            "analysis": response,
            "file_processed": filename
        }

    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        # HuggingFace API errors
        if "BadRequestError" in str(e) or "huggingface" in str(e).lower():
            return JSONResponse(
                status_code=422,
                content={
                    "detail": "Hugging Face API request failed",
                    "error": str(e)
                }
            )
        raise HTTPException(status_code=500, detail="Unexpected error processing document.") from e

    finally:
        # Cleanup uploaded file (optional - disable for debugging)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logging.info(f"🧹 Cleaned up file: {file_path}")
            except Exception:
                traceback.print_exc()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
