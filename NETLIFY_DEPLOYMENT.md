# 🚀 Netlify Deployment - Schnellstart

## ✅ GitHub Push erfolgreich!

Code wurde auf GitHub gepusht: `https://github.com/phnxvision-pixel/tele.git`

---

## 📋 Netlify Deployment (5 Minuten)

### Schritt 1: Netlify Account & Repository verbinden

1. **Gehe zu:** https://app.netlify.com
2. **Logge dich ein** (oder erstelle Account)
3. **"Add new site"** → **"Import an existing project"**
4. **"Deploy with GitHub"** wählen
5. **Repository auswählen:** `phnxvision-pixel/tele` (oder `telegram-bot`)

---

### Schritt 2: Build-Einstellungen

Netlify sollte automatisch die `netlify.toml` erkennen. Falls nicht, setze manuell:

**Base directory:**
```
frontend
```

**Build command:**
```
npm install && npm run build
```

**Publish directory:**
```
frontend/dist
```

---

### Schritt 3: Environment Variable setzen

**WICHTIG:** Diese Variable muss gesetzt werden, sonst funktioniert die API nicht!

1. **Site settings** → **Environment variables**
2. **"Add a variable"** klicken
3. **Key:** `VITE_API_BASE_URL`
4. **Value:** `https://cityraver.up.railway.app`
5. **Scopes:** ✅ Production, ✅ Deploy previews
6. **"Save"**

---

### Schritt 4: Deploy!

1. **"Deploy site"** klicken
2. Warte auf Build (ca. 2-3 Minuten)
3. **Fertig!** Deine Site ist live

---

## 🔗 Deine URLs

**Frontend (Netlify):**
```
https://[deine-site].netlify.app
```

**Backend (Railway):**
```
https://cityraver.up.railway.app
```

**API-Dokumentation:**
```
https://cityraver.up.railway.app/docs
```

---

## ✅ Checkliste

- [x] Code auf GitHub gepusht
- [ ] Netlify Account erstellt/angemeldet
- [ ] Repository verbunden
- [ ] Build-Einstellungen gesetzt
- [ ] `VITE_API_BASE_URL` Environment Variable gesetzt
- [ ] Deployment gestartet
- [ ] Frontend-URL getestet
- [ ] Login funktioniert

---

## 🐛 Troubleshooting

### Problem: Build schlägt fehl

**Lösung:**
- Prüfe Build-Logs in Netlify
- Stelle sicher, dass `base = "frontend"` in `netlify.toml` ist
- Prüfe ob `package.json` im `frontend/` Verzeichnis existiert

### Problem: API-Calls gehen zu `/api` statt Railway

**Lösung:**
- Prüfe ob `VITE_API_BASE_URL` in Netlify Environment Variables gesetzt ist
- Stelle sicher, dass nach dem Setzen ein neuer Build gestartet wurde
- Prüfe Browser-Console (F12) für die tatsächlich verwendete URL

### Problem: CORS-Fehler

**Lösung:**
- Stelle sicher, dass Railway die Netlify-Domain erlaubt
- In Railway Environment Variables:
  ```
  ALLOWED_ORIGINS=https://[deine-site].netlify.app,https://*.netlify.app
  ```

---

## 📞 Hilfe

- **Netlify Docs:** https://docs.netlify.com
- **Netlify Dashboard:** https://app.netlify.com
- **Railway Dashboard:** https://railway.app
- **Backend API Docs:** https://cityraver.up.railway.app/docs

---

## 🎯 Nächste Schritte

1. ✅ Code auf GitHub gepusht
2. ⏳ Netlify Deployment starten
3. ⏳ Environment Variable setzen
4. ⏳ Frontend testen
5. ⏳ CORS konfigurieren (falls nötig)

