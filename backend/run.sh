#!/usr/bin/env bash
export PYTHONUNBUFFERED=1
# Optional: set these if you have Sarvam AI credentials
# export SARVAM_API_KEY=YOUR_KEY
# export SARVAM_BASE_URL=https://api.sarvam.ai/v1/text/summarize
# export SARVAM_MODEL=generic-summarizer
uvicorn main:app --reload --host 0.0.0.0 --port 8000
