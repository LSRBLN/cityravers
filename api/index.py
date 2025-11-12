"""
Vercel Serverless Entrypoint für FastAPI
"""
import sys
import os
from pathlib import Path

# Füge das Root-Verzeichnis zum Python-Pfad hinzu
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Stelle sicher, dass wir im richtigen Verzeichnis sind
os.chdir(root_dir)

# Importiere die FastAPI-App
try:
    from api import app
except Exception as e:
    # Fehlerbehandlung für besseres Debugging
    import traceback
    error_msg = f"Error importing app: {str(e)}\n{traceback.format_exc()}"
    print(error_msg, file=sys.stderr)
    raise

# Exportiere die App für Vercel
__all__ = ["app"]

