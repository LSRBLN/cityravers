# 🐛 Railway Error Troubleshooting

## Problem: Error-Level Logs in Railway

Wenn du einen `error` Level Log siehst, folge diesen Schritten:

---

## 🔍 Schritt 1: Vollständige Logs anzeigen

### Im Railway Dashboard:

1. Gehe zu deinem Projekt → **Deployments**
2. Klicke auf das neueste Deployment
3. Klicke auf **View Logs** oder **Logs** Tab
4. Scrolle nach unten zu den neuesten Logs
5. Suche nach **ERROR** oder **Exception** Einträgen

### Vollständige Fehlermeldung finden:

Die vollständige Fehlermeldung sollte so aussehen:
```
ERROR - Fehler bei DB-Initialisierung: [DETAILS]
```

Oder:
```
ERROR - api - [FEHLERMELDUNG]
```

---

## 🔧 Häufige Fehler und Lösungen

### 1. ❌ Datenbank-Verbindungsfehler

**Fehlermeldung:**
```
ERROR - Fehler bei DB-Initialisierung: ...
```

**Mögliche Ursachen:**
- `DATABASE_URL` nicht gesetzt
- PostgreSQL Service nicht gestartet
- Falsche Connection String

**Lösung:**

1. **Prüfe Environment Variables:**
   - Railway Dashboard → Settings → Variables
   - Prüfe ob `DATABASE_URL` vorhanden ist
   - Format: `postgresql://user:password@host:port/database`

2. **Prüfe PostgreSQL Service:**
   - Railway Dashboard → Services
   - Prüfe ob PostgreSQL Service läuft (grüner Status)

3. **PostgreSQL neu erstellen (falls nötig):**
   - Railway Dashboard → New → Database → PostgreSQL
   - Railway erstellt automatisch `DATABASE_URL`

---

### 2. ❌ Fehlende Environment Variables

**Fehlermeldung:**
```
ERROR - JWT_SECRET_KEY nicht gesetzt
ERROR - ENCRYPTION_KEY nicht gesetzt
```

**Lösung:**

Setze in Railway Environment Variables:

```bash
JWT_SECRET_KEY=V4bES5s_Ng_ShFwAKm4OZ7V2OlTc6vPfLzKkYgoFTec
ENCRYPTION_KEY=BZIe671zDhcrrlA2h-C6tSDxvrGgmsVSPc4fFx8bxyE=
```

**Wo:** Railway Dashboard → Settings → Variables → New Variable

---

### 3. ❌ Import-Fehler

**Fehlermeldung:**
```
ModuleNotFoundError: No module named '...'
ImportError: ...
```

**Lösung:**

1. **Prüfe `requirements.txt`:**
   ```bash
   # Stelle sicher, dass alle Dependencies vorhanden sind
   ```

2. **Railway baut automatisch aus `requirements.txt`**
   - Prüfe ob Build erfolgreich war
   - Prüfe Build-Logs auf Fehler

3. **Manuell prüfen:**
   - Railway Dashboard → Deployments → Build Logs

---

### 4. ❌ Datenbank-Migration fehlgeschlagen

**Fehlermeldung:**
```
⚠️  Datenbank-Migration fehlgeschlagen
```

**Lösung:**

Dieser Fehler ist **normal**, wenn das Schema bereits aktuell ist. Falls nicht:

1. **Prüfe Migration-Script:**
   - `migrate_groups_schema.py` sollte vorhanden sein

2. **Manuell migrieren (falls nötig):**
   ```bash
   # Lokal testen
   python migrate_groups_schema.py
   ```

---

### 5. ❌ Services-Initialisierung fehlgeschlagen

**Fehlermeldung:**
```
WARNING - DB nicht verfügbar, Services werden nicht initialisiert
```

**Lösung:**

Dies ist eine **Warnung**, kein kritischer Fehler. Die App läuft weiterhin, aber:
- Scheduler funktioniert nicht
- Warming Service funktioniert nicht

**Ursache:** Datenbank-Verbindung fehlgeschlagen (siehe Punkt 1)

---

## 🔍 Schritt 2: Logs analysieren

### Vollständige Logs exportieren:

1. Railway Dashboard → Deployments → Neuestes Deployment
2. Klicke auf **View Logs**
3. Kopiere alle ERROR/WARNING Einträge

### Log-Format verstehen:

```
TIMESTAMP - MODULE - LEVEL - MESSAGE
```

**Beispiel:**
```
2025-11-12 19:42:47 - api - ERROR - Fehler bei DB-Initialisierung: connection refused
```

---

## ✅ Checkliste: Fehler beheben

### 1. Environment Variables prüfen

- [ ] `DATABASE_URL` vorhanden und korrekt
- [ ] `JWT_SECRET_KEY` vorhanden (min. 32 Zeichen)
- [ ] `ENCRYPTION_KEY` vorhanden (base64)
- [ ] `TELEGRAM_API_ID` vorhanden (falls verwendet)
- [ ] `TELEGRAM_API_HASH` vorhanden (falls verwendet)

### 2. Services prüfen

- [ ] PostgreSQL Service läuft (grüner Status)
- [ ] Backend Service läuft (grüner Status)
- [ ] Keine roten Fehler in Service-Status

### 3. Logs prüfen

- [ ] Vollständige Fehlermeldung gefunden
- [ ] Fehlerursache identifiziert
- [ ] Lösung angewendet

### 4. Testen

- [ ] Service neu gestartet (falls nötig)
- [ ] API-Dokumentation erreichbar: `https://cityraver.up.railway.app/docs`
- [ ] Login funktioniert

---

## 🚀 Schnell-Fix: Service neu starten

Falls der Fehler unklar ist:

1. Railway Dashboard → Dein Service
2. Klicke auf **Settings**
3. Scrolle zu **Restart Service**
4. Klicke auf **Restart**

---

## 📋 Debug-Informationen sammeln

### 1. Vollständige Logs kopieren

Aus Railway Dashboard:
- Alle ERROR/WARNING Einträge
- Letzte 50-100 Zeilen

### 2. Environment Variables prüfen

**WICHTIG:** Teile KEINE echten Secrets!

Prüfe nur ob sie gesetzt sind:
- `DATABASE_URL` - ✅ Gesetzt / ❌ Fehlt
- `JWT_SECRET_KEY` - ✅ Gesetzt / ❌ Fehlt
- `ENCRYPTION_KEY` - ✅ Gesetzt / ❌ Fehlt

### 3. Service-Status prüfen

- PostgreSQL: ✅ Läuft / ❌ Fehler
- Backend: ✅ Läuft / ❌ Fehler

---

## 🆘 Häufige Fehlermeldungen

### "Fehler bei DB-Initialisierung: connection refused"
**Ursache:** PostgreSQL nicht erreichbar  
**Lösung:** Prüfe PostgreSQL Service, prüfe `DATABASE_URL`

### "JWT_SECRET_KEY nicht gesetzt"
**Ursache:** Environment Variable fehlt  
**Lösung:** Setze `JWT_SECRET_KEY` in Railway Variables

### "ENCRYPTION_KEY nicht gesetzt"
**Ursache:** Environment Variable fehlt  
**Lösung:** Setze `ENCRYPTION_KEY` in Railway Variables

### "ModuleNotFoundError: No module named 'X'"
**Ursache:** Dependency fehlt in `requirements.txt`  
**Lösung:** Füge fehlende Dependency zu `requirements.txt` hinzu

### "Port already in use"
**Ursache:** Port-Konflikt (selten auf Railway)  
**Lösung:** Railway setzt `$PORT` automatisch, sollte nicht auftreten

---

## 📞 Nächste Schritte

1. **Vollständige Fehlermeldung kopieren** aus Railway Logs
2. **Environment Variables prüfen** (siehe Checkliste)
3. **Service neu starten** (falls nötig)
4. **Erneut testen**

Falls der Fehler weiterhin besteht:
- Kopiere die **vollständige Fehlermeldung** aus den Logs
- Prüfe ob alle Environment Variables gesetzt sind
- Prüfe ob PostgreSQL Service läuft

---

## 🔗 Nützliche Links

- **Railway Dashboard:** https://railway.app
- **Railway Docs:** https://docs.railway.app
- **API-Dokumentation:** https://cityraver.up.railway.app/docs

