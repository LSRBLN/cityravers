# 🔐 Environment Variables für Railway Deployment

## ✅ Generierte Secrets

**⚠️ WICHTIG: Diese Werte sind EINMALIG und SICHER. Teile sie NIEMALS öffentlich!**

### JWT_SECRET_KEY
```
V4bES5s_Ng_ShFwAKm4OZ7V2OlTc6vPfLzKkYgoFTec
```

### ENCRYPTION_KEY
```
BZIe671zDhcrrlA2h-C6tSDxvrGgmsVSPc4fFx8bxyE=
```

---

## 📋 Vollständige Environment Variables für Railway

### 1. DATABASE_URL
**Wird automatisch von Railway generiert** (nachdem du PostgreSQL hinzugefügt hast)

Format:
```
postgresql://user:password@host:port/database
```

**Aktion:** Railway erstellt diese automatisch, wenn du PostgreSQL hinzufügst.

---

### 2. JWT_SECRET_KEY
```
V4bES5s_Ng_ShFwAKm4OZ7V2OlTc6vPfLzKkYgoFTec
```

**Verwendung:** Für JWT-Token-Generierung (Authentifizierung)

---

### 3. ENCRYPTION_KEY
```
BZIe671zDhcrrlA2h-C6tSDxvrGgmsVSPc4fFx8bxyE=
```

**Verwendung:** Für Verschlüsselung sensibler Daten (Proxy-Passwörter, etc.)

---

### 4. TELEGRAM_API_ID
**Du musst diese selbst von Telegram holen:**

1. Gehe zu: **https://my.telegram.org/apps**
2. Logge dich mit deiner **Telefonnummer** ein
3. Erstelle eine **neue App** (falls noch nicht vorhanden)
4. Kopiere die **API ID** (Zahl, z.B. `12345678`)

**Format:**
```
TELEGRAM_API_ID=12345678
```

---

### 5. TELEGRAM_API_HASH
**Wird zusammen mit API ID von Telegram bereitgestellt:**

1. Auf der gleichen Seite wie API ID
2. Kopiere den **API Hash** (32 Zeichen Hex-String)

**Format:**
```
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
```

---

## 🚀 Railway Setup - Schritt für Schritt

### Schritt 1: PostgreSQL hinzufügen
1. Railway Dashboard → Dein Projekt
2. Klicke auf **"New"** → **"Database"** → **"Add PostgreSQL"**
3. Railway erstellt automatisch `DATABASE_URL`

### Schritt 2: Environment Variables setzen
1. Gehe zu **Settings** → **Variables**
2. Klicke auf **"New Variable"**
3. Füge jede Variable einzeln hinzu:

| Variable | Wert |
|----------|------|
| `JWT_SECRET_KEY` | `V4bES5s_Ng_ShFwAKm4OZ7V2OlTc6vPfLzKkYgoFTec` |
| `ENCRYPTION_KEY` | `BZIe671zDhcrrlA2h-C6tSDxvrGgmsVSPc4fFx8bxyE=` |
| `TELEGRAM_API_ID` | `[DEINE_API_ID_VON_TELEGRAM]` |
| `TELEGRAM_API_HASH` | `[DEIN_API_HASH_VON_TELEGRAM]` |

**Hinweis:** `DATABASE_URL` wird automatisch von Railway gesetzt (nicht manuell hinzufügen!)

---

## 📝 Vollständige Liste (zum Kopieren)

```bash
# Automatisch von Railway (nicht manuell setzen!)
DATABASE_URL=postgresql://user:password@host:port/database

# Generierte Secrets
JWT_SECRET_KEY=V4bES5s_Ng_ShFwAKm4OZ7V2OlTc6vPfLzKkYgoFTec
ENCRYPTION_KEY=BZIe671zDhcrrlA2h-C6tSDxvrGgmsVSPc4fFx8bxyE=

# Von Telegram (du musst diese holen!)
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
```

---

## 🔒 Sicherheitshinweise

1. **NIEMALS** diese Werte in Git committen
2. **NIEMALS** diese Werte öffentlich teilen
3. **NIEMALS** diese Werte in Logs ausgeben
4. **NUR** in Railway Environment Variables setzen
5. **BACKUP** dieser Werte an sicherer Stelle speichern

---

## 🆘 Neue Secrets generieren

Falls du neue Secrets brauchst:

```bash
python3 generate_secrets.py
```

Oder manuell:

```bash
# JWT_SECRET_KEY
openssl rand -hex 32

# ENCRYPTION_KEY (mit Python)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 📞 Telegram API Credentials holen

### Schritt-für-Schritt:

1. **Gehe zu:** https://my.telegram.org/apps
2. **Logge dich ein** mit deiner Telefonnummer
3. **Bestätige den Code** (wird per Telegram gesendet)
4. **Erstelle eine App:**
   - **App title:** z.B. "Berlin City Raver Bot"
   - **Short name:** z.B. "berlinraver"
   - **Platform:** Web
   - **Description:** (optional)
5. **Kopiere:**
   - **api_id:** (Zahl, z.B. `12345678`)
   - **api_hash:** (32 Zeichen Hex-String)

### Beispiel:
```
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
```

---

## ✅ Checkliste

- [ ] PostgreSQL in Railway hinzugefügt
- [ ] `DATABASE_URL` automatisch erstellt (von Railway)
- [ ] `JWT_SECRET_KEY` in Railway gesetzt
- [ ] `ENCRYPTION_KEY` in Railway gesetzt
- [ ] Telegram API Credentials geholt
- [ ] `TELEGRAM_API_ID` in Railway gesetzt
- [ ] `TELEGRAM_API_HASH` in Railway gesetzt
- [ ] Deployment getestet
- [ ] Backend-URL funktioniert (`/docs` aufrufbar)

---

## 🎯 Nächste Schritte

1. **Telegram API Credentials holen** (siehe oben)
2. **Alle Environment Variables in Railway setzen**
3. **Deployment prüfen** (Railway Dashboard → Deployments)
4. **Backend testen:** `https://dein-service.up.railway.app/docs`

