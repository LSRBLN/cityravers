# 🔧 Admin-User auf Railway erstellen

## Übersicht

Dieses Script erstellt den Admin-User auf Railway und kopiert alle lokalen Accounts.

---

## 📋 Voraussetzungen

1. **DATABASE_URL von Railway**
2. **Lokale Datenbank** mit Accounts (`telegram_bot.db`)

---

## 🚀 Methode 1: Über Railway CLI (Empfohlen)

### Schritt 1: Railway CLI installieren

```bash
# macOS
brew install railway

# Oder: https://docs.railway.app/develop/cli
```

### Schritt 2: Login

```bash
railway login
```

### Schritt 3: Projekt verbinden

```bash
cd /Users/rebelldesign/Documents/telegram-bot
railway link
```

### Schritt 4: DATABASE_URL abrufen

```bash
railway variables
# Suche nach DATABASE_URL und kopiere den Wert
```

### Schritt 5: Script ausführen

```bash
# Setze DATABASE_URL
export DATABASE_URL="postgresql://user:pass@host:port/db"

# Führe Script aus
python3 create_railway_admin.py
```

---

## 🚀 Methode 2: DATABASE_URL direkt übergeben

### Schritt 1: DATABASE_URL von Railway Dashboard kopieren

1. **Railway Dashboard** → Dein Projekt → PostgreSQL Service
2. **Variables** Tab
3. **DATABASE_URL** kopieren

### Schritt 2: Script ausführen

```bash
cd /Users/rebelldesign/Documents/telegram-bot

python3 create_railway_admin.py "postgresql://user:pass@host:port/db"
```

**⚠️ WICHTIG:** Ersetze `postgresql://user:pass@host:port/db` mit deiner echten DATABASE_URL!

---

## 🚀 Methode 3: Über Railway One-Click Deploy

### Schritt 1: Script zu Railway pushen

```bash
git add create_railway_admin.py
git commit -m "Railway Admin Setup Script"
git push origin main
```

### Schritt 2: Railway Shell öffnen

```bash
railway shell
```

### Schritt 3: Script ausführen

```bash
python3 create_railway_admin.py
```

---

## ✅ Was das Script macht

1. **Erstellt Admin-User:**
   - Username: `admin`
   - Email: `admin@telegram-bot.local`
   - Passwort: `Sabine68#`
   - Admin-Rechte: ✅

2. **Erstellt Enterprise Subscription:**
   - Unbegrenzte Accounts (999)
   - Unbegrenzte Gruppen (999)
   - Unbegrenzte Nachrichten (9999/Tag)
   - Alle Features aktiviert

3. **Kopiert lokale Accounts:**
   - Liest alle Accounts aus lokaler `telegram_bot.db`
   - Kopiert sie zu Railway-Datenbank
   - Überspringt bereits vorhandene Accounts

---

## 🧪 Testen

Nach dem Ausführen:

```bash
# Login testen
curl -X POST https://cityraver.up.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "Sabine68#"}'
```

**Erwartete Antwort:**
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "email": "admin@telegram-bot.local",
    "is_admin": true
  }
}
```

---

## 🐛 Troubleshooting

### Problem: "DATABASE_URL nicht gefunden"

**Lösung:**
- Prüfe ob DATABASE_URL als Argument übergeben wurde
- Oder setze als Environment Variable: `export DATABASE_URL="..."`

### Problem: "Connection refused"

**Lösung:**
- Prüfe ob DATABASE_URL korrekt ist
- Prüfe ob Railway PostgreSQL Service läuft
- Prüfe Firewall/Netzwerk

### Problem: "ModuleNotFoundError: dotenv"

**Lösung:**
- Script wurde angepasst, braucht kein dotenv mehr
- Falls andere Module fehlen: `pip install -r requirements.txt`

---

## 📝 Notizen

- **Passwort:** `Sabine68#` (kann später geändert werden)
- **Accounts:** Werden von lokaler DB kopiert
- **Session-Dateien:** Werden nicht kopiert (nur Metadaten)

---

## ✅ Checkliste

- [ ] DATABASE_URL von Railway kopiert
- [ ] Script ausgeführt
- [ ] Admin-User erstellt
- [ ] Accounts kopiert
- [ ] Login getestet

