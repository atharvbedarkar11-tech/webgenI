"""FastAPI backend. Run:  uvicorn app.main:app --reload"""
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import OUTPUT_DIR
from .orchestrator import run_workflow

BASE = Path(__file__).parent
app = FastAPI(title="WebGenAI Prototype")


class RunRequest(BaseModel):
    request: str
    approved: bool = False


@app.post("/api/run")
def run(req: RunRequest):
    return run_workflow(req.request, req.approved)


@app.get("/api/download/{run_id}")
def download(run_id: str):
    if not run_id.isalnum():
        raise HTTPException(400, "bad id")
    p = OUTPUT_DIR / f"{run_id}.csv"
    if not p.exists():
        raise HTTPException(404, "not found")
    return FileResponse(p, filename=f"webgenai_{run_id}.csv", media_type="text/csv")


@app.get("/")
def index():
    return FileResponse(BASE / "static" / "index.html")


# built-in demo pages so the project works offline
app.mount("/demo", StaticFiles(directory=BASE / "demo"), name="demo")
