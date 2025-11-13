# Netlify Environment Variables

## Erforderliche Environment Variables

### 1. VITE_API_BASE_URL (ERFORDERLICH)

**Beschreibung:** Die URL deines Backend-API-Servers

**Wert für Produktion:**
```
https://deine-api-domain.com
```

**Beispiele:**
- `https://api.telegram-bot.com`
- `https://backend.example.com`
- `https://telegram-api.herokuapp.com`

**Wichtig:**
- Muss mit `https://` beginnen (nicht `http://`)
- Kein abschließender Slash (`/`)
- Muss erreichbar sein und CORS für deine Netlify-Domain erlauben

---

## Optional: Weitere Environment Variables

Falls du weitere Konfigurationen benötigst, kannst du diese hinzufügen:

### Beispiel für Feature Flags:
```
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_DEBUG=false
```

---

## So setzt du Environment Variables in Netlify

### Methode 1: Über die Netlify-Web-Oberfläche

1. Gehe zu deiner Site in Netlify
2. Klicke auf **Site settings**
3. Gehe zu **Environment variables** (im Menü links)
4. Klicke auf **Add a variable**
5. Füge hinzu:
   - **Key:** `VITE_API_BASE_URL`
   - **Value:** `https://deine-api-domain.com`
6. Wähle **Scopes:**
   - ✅ **Production** (für Live-Site)
   - ✅ **Deploy previews** (optional, für Preview-Builds)
   - ✅ **Branch deploys** (optional, für andere Branches)
7. Klicke auf **Save**

### Methode 2: Über netlify.toml (nicht empfohlen für Secrets)

Du kannst auch in `netlify.toml` Environment Variables setzen:

```toml
[build.environment]
  VITE_API_BASE_URL = "https://deine-api-domain.com"
```

**⚠️ Warnung:** Diese Methode ist nicht sicher für sensible Daten, da die Datei im Repository liegt.

---

## Nach dem Setzen der Variables

1. **Trigger einen neuen Build:**
   - Gehe zu **Deploys** in Netlify
   - Klicke auf **Trigger deploy** → **Deploy site**

2. **Prüfe den Build-Log:**
   - Stelle sicher, dass die Variable korrekt geladen wird
   - Prüfe ob `VITE_API_BASE_URL` im Build-Log erscheint

3. **Teste die Anwendung:**
   - Öffne deine Netlify-Site
   - Öffne Browser-Console (F12)
   - Prüfe ob API-Calls zur korrekten URL gehen

---

## Troubleshooting

### Problem: API-Calls gehen zu `/api` statt zur konfigurierten URL

**Lösung:**
- Prüfe ob `VITE_API_BASE_URL` in Netlify gesetzt ist
- Stelle sicher, dass der Build nach dem Setzen neu gestartet wurde
- Prüfe Browser-Console für die tatsächlich verwendete URL

### Problem: CORS-Fehler

**Lösung:**
- Stelle sicher, dass dein Backend die Netlify-Domain in CORS-Origins erlaubt
- Prüfe Backend-Logs für CORS-Fehler
- Beispiel für FastAPI:
  ```python
  origins = [
      "https://deine-site.netlify.app",
      "https://deine-custom-domain.com"
  ]
  ```

### Problem: Variable wird nicht erkannt

**Lösung:**
- Variablen müssen mit `VITE_` beginnen, damit Vite sie erkennt
- Nach dem Setzen muss ein neuer Build gestartet werden
- Prüfe ob der Scope (Production/Preview) korrekt ist

---

## Beispiel-Konfiguration

**Für Produktion:**
```
VITE_API_BASE_URL=https://api.telegram-bot.com
```

**Für Staging (optional):**
```
VITE_API_BASE_URL=https://staging-api.telegram-bot.com
```

**Für lokale Entwicklung:**
Erstelle eine `.env` Datei im `frontend/` Verzeichnis:
```
VITE_API_BASE_URL=http://localhost:8000
```

---

## Sicherheit

- ✅ **Sicher:** Environment Variables in Netlify (verschlüsselt gespeichert)
- ❌ **Nicht sicher:** Secrets in `netlify.toml` oder `.env` Dateien im Repository
- ✅ **Best Practice:** Verwende Netlify Environment Variables für alle sensiblen Daten

