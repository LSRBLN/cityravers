# Vercel 500 Error - Troubleshooting

## Problem: FUNCTION_INVOCATION_FAILED

### Mögliche Ursachen

1. **Import-Fehler**
   - Module können nicht gefunden werden
   - Falsche Python-Pfade

2. **Fehlende Environment Variables**
   - `DATABASE_URL` nicht gesetzt
   - `JWT_SECRET_KEY` fehlt
   - `ENCRYPTION_KEY` fehlt

3. **Datenbank-Verbindungsfehler**
   - PostgreSQL nicht erreichbar
   - Falsche Connection String

4. **Timeout**
   - Funktion läuft zu lange
   - Cold Start zu langsam

## Lösungen

### 1. Logs prüfen

```bash
# Über Vercel CLI
vercel logs https://deine-url.vercel.app

# Oder im Vercel Dashboard
# Deployments → Wähle Deployment → Functions → Logs
```

### 2. Environment Variables prüfen

Stelle sicher, dass alle erforderlichen Variablen gesetzt sind:

**Erforderlich:**
- `DATABASE_URL` - PostgreSQL Connection String
- `JWT_SECRET_KEY` - min. 32 Zeichen
- `ENCRYPTION_KEY` - Fernet Key (base64)

**Optional (falls verwendet):**
- `TELEGRAM_API_ID`
- `TELEGRAM_API_HASH`
- `FIVESIM_API_KEY`
- etc.

### 3. Lokales Testen

```bash
# Vercel lokal testen
vercel dev

# Oder mit Python direkt
python3 -c "from api import app; print('OK')"
```

### 4. Import-Probleme beheben

Die `api/index.py` wurde aktualisiert mit:
- Bessere Fehlerbehandlung
- Korrekte Pfad-Konfiguration
- Debug-Output

### 5. Datenbank-Verbindung testen

```python
# Test-Script
import os
from database import init_db

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL nicht gesetzt")
else:
    print(f"DATABASE_URL: {DATABASE_URL[:20]}...")
    try:
        init_db()
        print("✅ Datenbank-Verbindung erfolgreich")
    except Exception as e:
        print(f"❌ Fehler: {e}")
```

### 6. Vercel Function Logs prüfen

Im Vercel Dashboard:
1. Gehe zu deinem Projekt
2. Klicke auf **Deployments**
3. Wähle das fehlgeschlagene Deployment
4. Klicke auf **Functions**
5. Klicke auf **View Function Logs**

### 7. Timeout erhöhen

Die `vercel.json` wurde aktualisiert mit:
```json
"functions": {
  "api/index.py": {
    "maxDuration": 60
  }
}
```

## Häufige Fehler

### Fehler: "ModuleNotFoundError"

**Lösung:**
- Prüfe ob alle Dependencies in `requirements.txt` sind
- Prüfe ob Python-Pfad in `api/index.py` korrekt ist

### Fehler: "Database connection failed"

**Lösung:**
- Prüfe `DATABASE_URL` Format: `postgresql://user:pass@host:port/db`
- Prüfe ob Datenbank erreichbar ist (nicht localhost!)
- Prüfe Firewall-Regeln

### Fehler: "JWT_SECRET_KEY not set"

**Lösung:**
- Setze `JWT_SECRET_KEY` in Vercel Environment Variables
- Mindestens 32 Zeichen lang

### Fehler: "Timeout"

**Lösung:**
- Timeout in `vercel.json` erhöht (60 Sekunden)
- Für längere Operationen: Background Jobs verwenden

## Debugging-Tipps

### 1. Einfache Test-Route hinzufügen

In `api.py`:
```python
@app.get("/api/test")
def test():
    return {
        "status": "ok",
        "database_url": "set" if os.getenv("DATABASE_URL") else "missing",
        "jwt_secret": "set" if os.getenv("JWT_SECRET_KEY") else "missing"
    }
```

### 2. Error Handler verbessern

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "traceback": traceback.format_exc()
        }
    )
```

### 3. Health Check Endpoint

```python
@app.get("/api/health")
def health():
    return {"status": "healthy"}
```

## Nächste Schritte

1. ✅ `api/index.py` wurde aktualisiert (bessere Fehlerbehandlung)
2. ✅ `vercel.json` wurde aktualisiert (Timeout erhöht)
3. ⏳ Prüfe Vercel Logs für genauen Fehler
4. ⏳ Stelle sicher, dass alle Environment Variables gesetzt sind
5. ⏳ Teste Datenbank-Verbindung

## Support

- [Vercel Function Logs](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python#function-logs)
- [Vercel Error Codes](https://vercel.com/docs/errors)

