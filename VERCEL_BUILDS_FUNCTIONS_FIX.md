# 🚨 Vercel Error: builds + functions Konflikt

## ❌ Fehler

```
The `functions` property cannot be used in conjunction with the `builds` property. 
Please remove one of them.
```

**Problem:** Die Root `vercel.json` enthält sowohl `builds` als auch `functions`, was nicht erlaubt ist.

---

## 🔍 Problem

**Aktuelle `vercel.json` (Root):**
```json
{
  "version": 2,
  "builds": [...],      // ❌ Konflikt!
  "functions": {...}    // ❌ Konflikt!
}
```

**Vercel erlaubt nur EINES:**
- Entweder `builds` (ältere Konfiguration)
- Oder `functions` (neuere Konfiguration)

---

## ✅ Lösung 1: Root vercel.json löschen (Empfohlen)

**Da Backend auf Railway läuft:**

Die Root `vercel.json` ist für Backend-Deployment auf Vercel. Da Backend bereits auf Railway läuft, ist sie nicht nötig.

### Schritt 1: Root vercel.json löschen oder umbenennen

```bash
cd /Users/rebelldesign/Documents/telegram-bot
mv vercel.json vercel.json.backup
```

**Oder:** Lösche sie komplett (falls nicht mehr nötig)

### Schritt 2: Git commit & push

```bash
git add vercel.json
git commit -m "Remove: Root vercel.json (Backend läuft auf Railway)"
git push
```

**Dann:**
- ✅ Frontend verwendet nur `frontend/vercel.json`
- ✅ Keine Konflikte mehr
- ✅ Backend bleibt auf Railway

---

## ✅ Lösung 2: vercel.json anpassen (nur functions)

**Falls Backend doch auf Vercel deployed werden soll:**

### Option A: Nur functions (neuere Syntax)

```json
{
  "version": 2,
  "functions": {
    "api/index.py": {
      "runtime": "python3.11",
      "maxDuration": 60
    }
  },
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### Option B: Nur builds (ältere Syntax)

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
  ]
}
```

**Aber:** Da Backend auf Railway läuft, ist Lösung 1 besser!

---

## ✅ Lösung 3: .vercelignore verwenden

**Falls Root vercel.json behalten werden soll:**

Die `.vercelignore` sollte bereits Root `vercel.json` ignorieren.

**Prüfe `.vercelignore`:**
```bash
cat .vercelignore | grep vercel.json
```

**Sollte zeigen:**
```
vercel.json
```

**Falls nicht vorhanden:**
```bash
echo "vercel.json" >> .vercelignore
git add .vercelignore
git commit -m "Ignore root vercel.json for frontend deployments"
git push
```

---

## 🎯 Empfehlung: Lösung 1

**Lösche Root `vercel.json`:**

1. **Backend läuft bereits auf Railway** ✅
2. **Frontend sollte nur `frontend/vercel.json` verwenden** ✅
3. **Keine Konflikte mehr** ✅

**Schritte:**
1. Root `vercel.json` löschen/umbenennen
2. Git commit & push
3. Vercel Frontend-Projekt neu deployen

---

## 📋 Schnell-Fix

```bash
cd /Users/rebelldesign/Documents/telegram-bot

# Root vercel.json umbenennen (als Backup)
mv vercel.json vercel.json.backup

# Git commit
git add vercel.json
git commit -m "Remove: Root vercel.json (Backend auf Railway, Frontend verwendet frontend/vercel.json)"
git push
```

**Dann:**
- Vercel Frontend-Projekt → Redeploy
- Fehler sollte verschwinden

