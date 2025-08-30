# AI-Powered Document Insight Tool

A full-stack app to upload **PDF resumes**, generate an **AI summary** (via Sarvam AI, if configured), or **fallback** to the **top 5 frequent words** when the AI is unavailable. Includes a **history** of uploads.

## Tech Stack
- **Backend:** FastAPI, PyPDF2, Requests
- **Frontend:** Vanilla HTML/CSS/JS
- **Storage:** JSON file (`backend/history.json`)

## Features
- Upload PDF, extract text
- Try **Sarvam AI** summarization (optional env config)
- Fallback: compute **top 5 frequent words**
- Persisted **history** with ID, filename, timestamp, summary type
- View past insights and open a specific one

## Run Locally

### 1) Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# OPTIONAL: set Sarvam AI details (replace with real values)
# export SARVAM_API_KEY=YOUR_KEY
# export SARVAM_BASE_URL=https://api.sarvam.ai/v1/text/summarize
# export SARVAM_MODEL=generic-summarizer

# start server
./run.sh     # or: uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
API:
- `POST /upload-resume` (multipart form, `file`: PDF)
- `GET /insights?id=<docId>` for a single insight, or `GET /insights` for all

### 2) Frontend
```bash
cd ../frontend
# open index.html in your browser (double-click or serve via any static server)
```
Make sure backend is running at **http://localhost:8000** (or change `API_BASE` in `frontend/script.js`).

## Notes on Sarvam AI
This project is **ready** to call Sarvam AI if you provide environment variables:
- `SARVAM_API_KEY` – your API key
- `SARVAM_BASE_URL` – summarization endpoint (example: `https://api.sarvam.ai/v1/text/summarize`)
- `SARVAM_MODEL` – optional model name

If credentials are missing or a request fails, the app **gracefully falls back** to top word frequencies.

## Project Structure
```
ai-doc-insight-tool/
  backend/
    main.py
    requirements.txt
    run.sh
    history.json  (auto-created)
  frontend/
    index.html
    script.js
    styles.css
  README.md
```

## Submission
Zip this folder and push to a Git repo. You're good to go 🚀

— Generated on 2025-08-29T18:08:28.940573Z
