"""
Vercel Serverless Entrypoint für FastAPI
"""
import sys
from pathlib import Path

# Füge das Root-Verzeichnis zum Python-Pfad hinzu
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Importiere die FastAPI-App
from api import app

# Exportiere die App für Vercel
__all__ = ["app"]

