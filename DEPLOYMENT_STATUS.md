# Vercel Deployment Status

## ✅ Vorbereitung abgeschlossen

- ✅ Code zu GitHub gepusht
- ✅ Vercel-Dateien erstellt:
  - `api/index.py` (Serverless Entrypoint)
  - `vercel.json` (Konfiguration)
  - `.vercelignore` (Ignore-Dateien)
  - `VERCEL_DEPLOY.md` (Anleitung)

## 🔧 Nächste Schritte

### Option 1: Vercel CLI (Empfohlen)

```bash
# 1. Login (falls noch nicht eingeloggt)
vercel login

# 2. Environment Variables setzen
vercel env add DATABASE_URL production
vercel env add JWT_SECRET_KEY production
vercel env add ENCRYPTION_KEY production

# 3. Deployment starten
vercel

# 4. Für Produktion
vercel --prod
```

### Option 2: Vercel Dashboard

1. Gehe zu [vercel.com](https://vercel.com)
2. Klicke auf **"Add New Project"**
3. Verbinde dein Git-Repository: `phnxvision-pixel/tele`
4. **Framework Preset:** Other
5. **Root Directory:** ./
6. **Build Command:** (leer lassen)
7. **Output Directory:** (leer lassen)
8. **Install Command:** (leer lassen)
9. **Environment Variables hinzufügen:**
   - `DATABASE_URL` = deine PostgreSQL Connection String
   - `JWT_SECRET_KEY` = min. 32 Zeichen
   - `ENCRYPTION_KEY` = Fernet Key (base64)
10. Klicke auf **"Deploy"**

## 📋 Erforderliche Environment Variables

Siehe `VERCEL_DEPLOY.md` für Details.

## 🔗 Nach dem Deployment

1. Notiere die Vercel-URL (z.B. `https://telegram-bot-api.vercel.app`)
2. Setze in Netlify: `VITE_API_BASE_URL` = deine Vercel-URL
3. Teste die API: `curl https://deine-url.vercel.app/api/health`

