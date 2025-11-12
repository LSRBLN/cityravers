#!/bin/bash
# Startet das Backend

echo "🚀 Starte Telegram Mass Message Backend..."
python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

