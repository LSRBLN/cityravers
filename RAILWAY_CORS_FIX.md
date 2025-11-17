# 🔧 CORS Variable am richtigen Ort setzen

## ⚠️ Problem

`ALLOWED_ORIGINS` ist im **Postgres-Service** gesetzt, aber es muss im **Backend-Service ("tele")** sein!

**Aktuell (FALSCH):**
- ❌ Postgres-Service → Variables → `ALLOWED_ORIGINS`

**Richtig:**
- ✅ Backend-Service ("tele") → Variables → `ALLOWED_ORIGINS`

---

## ✅ Lösung: Variable im Backend-Service setzen

### Schritt 1: Backend-Service öffnen

1. **Railway Dashboard** → Projekt "attractive-kindness"
2. Klicke auf **"tele"** Service (nicht Postgres!)
3. Klicke auf **"Variables"** Tab

### Schritt 2: ALLOWED_ORIGINS hinzufügen

1. Klicke auf **"+ New Variable"**
2. Setze:
   - **Key:** `ALLOWED_ORIGINS`
   - **Value:** 
     ```
     https://frontend-26h8m7t6r-jans-projects-10df1634.vercel.app,https://frontend-three-pi-61.vercel.app,http://localhost:3000,http://localhost:5173
     ```
3. Klicke auf **"Add"**

### Schritt 3: Service neu starten

1. Service "tele" → **Settings**
2. Klicke auf **"Restart Service"**

---

## 📋 Korrekte Variable-Werte

### ALLOWED_ORIGINS (im Backend-Service "tele"):

```
https://frontend-26h8m7t6r-jans-projects-10df1634.vercel.app,https://frontend-three-pi-61.vercel.app,http://localhost:3000,http://localhost:5173
```

**Wichtig:**
- Trenne mehrere URLs mit Komma (keine Leerzeichen!)
- Verwende exakt `https://` oder `http://`
- Keine abschließenden Slashes

---

## 🔍 Warum im Backend-Service?

**CORS** (Cross-Origin Resource Sharing) wird vom **Backend** kontrolliert, nicht von der Datenbank!

- **Postgres:** Speichert nur Daten
- **Backend ("tele"):** Verarbeitet API-Requests und kontrolliert CORS

Daher muss `ALLOWED_ORIGINS` im **Backend-Service** sein!

---

## ✅ Checkliste

- [ ] `ALLOWED_ORIGINS` im **Backend-Service ("tele")** gesetzt
- [ ] Variable aus **Postgres-Service** entfernt (optional, stört nicht)
- [ ] Backend-Service neu gestartet
- [ ] Frontend testen (keine CORS-Fehler mehr)

---

## 🎯 Schnell-Fix

1. **Railway Dashboard** → Service **"tele"** (nicht Postgres!)
2. **Variables** Tab
3. **"+ New Variable"**
4. **Key:** `ALLOWED_ORIGINS`
5. **Value:** `https://frontend-26h8m7t6r-jans-projects-10df1634.vercel.app,https://frontend-three-pi-61.vercel.app,http://localhost:3000,http://localhost:5173`
6. **Add**
7. **Settings** → **Restart Service**

**Fertig!** 🎉

---

## 📝 Zusammenfassung

**Problem:** `ALLOWED_ORIGINS` ist im Postgres-Service, muss aber im Backend-Service sein!

**Lösung:**
1. ✅ Variable im Backend-Service ("tele") setzen
2. ✅ Service neu starten
3. ✅ Testen

**CORS wird vom Backend kontrolliert, nicht von der Datenbank!**

