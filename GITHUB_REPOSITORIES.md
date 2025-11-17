# 📦 GitHub Repositories - Übersicht

## Aktuelle Repositories

### 1. Origin (phnxvision-pixel/tele)
```
https://github.com/phnxvision-pixel/tele.git
```
**Remote:** `origin`

### 2. Cityravers (LSRBLN/cityravers)
```
https://github.com/LSRBLN/cityravers.git
```
**Remote:** `cityravers`

---

## 🔄 Code zu beiden Repositories pushen

### Beide gleichzeitig pushen:

```bash
cd /Users/rebelldesign/Documents/telegram-bot

# Zu beiden Repositories pushen
git push origin main
git push cityravers main
```

### Oder als Alias einrichten:

```bash
# Alias für beide Repositories
git config alias.pushall '!git push origin main && git push cityravers main'

# Verwendung:
git pushall
```

---

## 📋 Remote-Konfiguration

**Aktuelle Remotes:**
```bash
git remote -v
```

**Ausgabe:**
```
cityravers	https://github.com/LSRBLN/cityravers.git (fetch)
cityravers	https://github.com/LSRBLN/cityravers.git (push)
origin	https://github.com/phnxvision-pixel/tele.git (fetch)
origin	https://github.com/phnxvision-pixel/tele.git (push)
```

**Hinweis:** Origin verwendet aktuell HTTPS mit Token. Für SSH siehe `GITHUB_SSH_KEY.md`.

---

## 🚀 Deployment-Status

### ✅ Origin (phnxvision-pixel/tele)
- **Status:** Aktiv
- **Letzter Push:** Erfolgreich
- **Verwendung:** Haupt-Repository

### ✅ Cityravers (LSRBLN/cityravers)
- **Status:** Aktiv
- **Letzter Push:** Erfolgreich (gerade eben)
- **Verwendung:** Deployment-Repository

---

## 🔧 Remote ändern oder entfernen

### Remote entfernen:
```bash
git remote remove cityravers
```

### Remote URL ändern:
```bash
git remote set-url cityravers https://github.com/NEUER-USER/NEUES-REPO.git
```

### Neuen Remote hinzufügen:
```bash
git remote add [name] https://github.com/USER/REPO.git
```

---

## 📝 Workflow-Empfehlung

### Option 1: Beide synchron halten
```bash
# Nach jedem Commit beide pushen
git add .
git commit -m "Update"
git push origin main
git push cityravers main
```

### Option 2: Nur ein Repository verwenden
```bash
# Origin als Haupt-Repository
git push origin main

# Cityravers nur bei Bedarf
git push cityravers main
```

### Option 3: Automatisches Push-All Script
```bash
# Script erstellen: push-all.sh
#!/bin/bash
git push origin main && git push cityravers main

# Ausführbar machen
chmod +x push-all.sh

# Verwenden
./push-all.sh
```

---

## 🔗 Repository-Links

- **Origin:** https://github.com/phnxvision-pixel/tele
- **Cityravers:** https://github.com/LSRBLN/cityravers

---

## ✅ Checkliste

- [x] Origin Repository konfiguriert
- [x] Cityravers Repository hinzugefügt
- [x] Code zu beiden Repositories gepusht
- [ ] Push-All Alias eingerichtet (optional)
- [ ] Workflow definiert (beide oder nur eines)

---

## 🎯 Nächste Schritte

1. **Netlify Deployment:** Verbinde Netlify mit `LSRBLN/cityravers`
2. **Azure Deployment:** Verbinde Azure mit `LSRBLN/cityravers`
3. **CI/CD:** Konfiguriere GitHub Actions für automatisches Deployment

