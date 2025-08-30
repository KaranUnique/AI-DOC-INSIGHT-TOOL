import os
import uuid
import json
import datetime
from collections import Counter
from typing import Optional, List, Dict, Any

import requests
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from PyPDF2 import PdfReader

APP_DATA = "history.json"

app = FastAPI(title="AI-Powered Document Insight Tool", version="1.0.0")

# Allow local dev frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _load_history() -> List[Dict[str, Any]]:
    if not os.path.exists(APP_DATA):
        return []
    try:
        with open(APP_DATA, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def _save_history(data: List[Dict[str, Any]]) -> None:
    with open(APP_DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def extract_text_from_pdf(upload_file: UploadFile) -> str:
    try:
        reader = PdfReader(upload_file.file)
        text_parts = []
        for page in reader.pages:
            t = page.extract_text() or ""
            text_parts.append(t)
        return "\n".join(text_parts).strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {e}")

def summarize_with_sarvam(text: str) -> Optional[str]:
    """
    Attempts to summarize with Sarvam AI.
    Configure via environment variables:
      SARVAM_API_KEY  - API key
      SARVAM_BASE_URL - Base URL to the summarize endpoint (e.g., https://api.sarvam.ai/v1/text/summarize)
      SARVAM_MODEL    - Optional model name
    Returns summary text if successful, else None.
    """
    api_key = os.getenv("SARVAM_API_KEY")
    base_url = os.getenv("SARVAM_BASE_URL")
    model = os.getenv("SARVAM_MODEL", "generic-summarizer")
    if not api_key or not base_url:
        return None
    try:
        payload = {
            "model": model,
            "input": text[:12000],  # safety trim
            "task": "summarize",
            "max_tokens": 256
        }
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        resp = requests.post(base_url, json=payload, headers=headers, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            # Try common fields; adapt as needed based on Sarvam's actual schema
            for key in ("summary", "output", "result", "text"):
                if isinstance(data, dict) and key in data and isinstance(data[key], str):
                    return data[key].strip()
            # Fallback if response is a list or nested object
            if isinstance(data, dict) and "choices" in data and isinstance(data["choices"], list):
                txt = data["choices"][0].get("text") or data["choices"][0].get("message", {}).get("content")
                if txt:
                    return str(txt).strip()
        return None
    except Exception:
        return None

def fallback_top_words(text: str, k: int = 5) -> List[List[Any]]:
    # Simple tokenization: keep purely alphabetic tokens, lowercase
    words = [w for w in "".join([c if c.isalpha() else " " for c in text.lower()]).split() if w]
    # Basic stopword removal
    stop = set("""a an the and or but if in on at of for to with from by as is be are was were been being it its itself himself herself themselves
                  this that these those i you he she we they them him her my your our their me us we ll ve d s t not no yes do does did done doing
                  have has had having can could should would may might must will just than then there here when where why how into out up down over under""".split())
    tokens = [w for w in words if w not in stop and len(w) > 2]
    counts = Counter(tokens).most_common(k)
    return [[w, c] for w, c in counts]

class Insight(BaseModel):
    id: str
    filename: str
    uploaded_at: str
    summary_type: str  # "ai" or "fallback"
    summary: str
    top_words: List[List[Any]] = []
    text_excerpt: str

@app.post("/upload-resume", response_model=Insight)
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    text = extract_text_from_pdf(file)
    if not text:
        raise HTTPException(status_code=400, detail="No readable text found in PDF.")

    # Try AI, else fallback
    summary = summarize_with_sarvam(text)
    if summary:
        summary_type = "ai"
        top_words = fallback_top_words(text, 5)  # also compute for display
    else:
        summary_type = "fallback"
        top_words = fallback_top_words(text, 5)
        summary = "Top 5 frequent words (fallback): " + ", ".join([f"{w} ({c})" for w, c in top_words])

    item = {
        "id": str(uuid.uuid4()),
        "filename": file.filename,
        "uploaded_at": datetime.datetime.utcnow().isoformat() + "Z",
        "summary_type": summary_type,
        "summary": summary,
        "top_words": top_words,
        "text_excerpt": text[:1000]
    }
    history = _load_history()
    history.insert(0, item)  # newest first
    _save_history(history)
    return item

@app.get("/insights")
def get_insights(id: Optional[str] = Query(default=None, description="Document ID")):
    history = _load_history()
    if id:
        for item in history:
            if item["id"] == id:
                return item
        raise HTTPException(status_code=404, detail="Document not found")
    return {"items": history}
