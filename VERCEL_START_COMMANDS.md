# Vercel Start Commands

## Wichtig: Vercel hat KEINEN Start-Command!

Vercel ist ein **Serverless-Platform**. Die Functions werden automatisch deployed und ausgeführt. Es gibt **keinen klassischen Start-Command** wie bei traditionellen Servern.

## Lokale Entwicklung

### Option 1: Vercel CLI (Empfohlen)

```bash
# Installiere Vercel CLI (falls nicht vorhanden)
npm install -g vercel

# Starte lokalen Development-Server
vercel dev
```

Dies startet:
- Lokalen Server auf `http://localhost:3000`
- Simuliert Vercel-Umgebung
- Lädt Environment Variables aus `.env`

### Option 2: Direkt mit Python (für Entwicklung)

```bash
# Installiere Dependencies
pip install -r requirements.txt

# Starte FastAPI mit uvicorn
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

**Hinweis:** Dies ist für lokale Entwicklung. Für Produktion wird Vercel verwendet.

## Vercel Deployment

### Automatisches Deployment

Vercel deployed automatisch bei:
- Push auf `main` Branch (wenn GitHub verbunden)
- Manuelles Deployment über Vercel Dashboard
- Vercel CLI: `vercel --prod`

### Kein Start-Command nötig

Nach dem Deployment:
1. Vercel erkennt automatisch `api/index.py` als Entrypoint
2. Functions werden automatisch ausgeführt bei Requests
3. Kein Start-Command erforderlich

## Vercel.json Konfiguration

```json
{
  "version": 2,
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ],
  "functions": {
    "api/index.py": {
      "maxDuration": 60
    }
  }
}
```

**Wichtig:** Kein `start` oder `build` Command nötig - Vercel macht das automatisch!

## Environment Variables

Für lokale Entwicklung (`.env`):
```bash
DATABASE_URL=postgresql://...
JWT_SECRET_KEY=...
ENCRYPTION_KEY=...
```

Für Vercel Production:
- Vercel Dashboard → Settings → Environment Variables
- Oder: `vercel env add VARIABLE_NAME`

## Vergleich: Lokal vs. Vercel

| Aspekt | Lokal | Vercel |
|--------|-------|--------|
| Start-Command | `uvicorn api:app` | Kein Command nötig |
| Port | 8000 (oder frei wählbar) | Automatisch |
| Environment | `.env` Datei | Dashboard/CLI |
| Deployment | Manuell | Automatisch bei Push |

## Troubleshooting

### "Function not found"
- Prüfe ob `api/index.py` existiert
- Prüfe `vercel.json` Konfiguration

### "Module not found"
- Prüfe `requirements.txt`
- Prüfe ob alle Dependencies installiert sind

### "Environment variable not set"
- Setze Variables in Vercel Dashboard
- Oder: `vercel env pull` für lokale Entwicklung

## Zusammenfassung

**Vercel benötigt KEINEN Start-Command!**

- ✅ Lokal: `vercel dev` oder `uvicorn api:app`
- ✅ Production: Automatisch nach Deployment
- ❌ Kein `start` Command in `vercel.json` nötig

