# 🚀 Quick Start - Hetzner Server

## Schnellste Installation (5 Minuten)

### 1. Script auf Server hochladen
```bash
# Auf lokalem Rechner:
scp setup_hetzner.sh root@deine-server-ip:/root/
scp -r telegram-bot root@deine-server-ip:/var/www/
```

### 2. Auf Server einloggen
```bash
ssh root@deine-server-ip
```

### 3. Setup ausführen
```bash
cd /root
chmod +x setup_hetzner.sh
./setup_hetzner.sh
```

### 4. .env Datei konfigurieren
```bash
nano /var/www/telegram-bot/.env
```

**Wichtig:**
- `TELEGRAM_API_ID` und `TELEGRAM_API_HASH` eintragen
- `FIVESIM_API_KEY` eintragen (falls verwendet)
- `ALLOWED_ORIGINS` mit deiner Domain aktualisieren

### 5. Service starten
```bash
systemctl start telegram-bot
systemctl status telegram-bot
```

### 6. SSL-Zertifikat installieren
```bash
certbot --nginx -d deine-domain.de
```

### 7. Fertig! 🎉
Öffne: `https://deine-domain.de`

---

## Manuelle Installation

Falls das Script nicht funktioniert, folge der detaillierten Anleitung:
```bash
cat HETZNER_SETUP.md
```

---

## Wichtige Befehle

### Service verwalten
```bash
systemctl start telegram-bot      # Starten
systemctl stop telegram-bot       # Stoppen
systemctl restart telegram-bot    # Neustart
systemctl status telegram-bot      # Status
journalctl -u telegram-bot -f     # Logs live
```

### Projekt aktualisieren
```bash
cd /var/www/telegram-bot
git pull  # oder manuell aktualisieren
source venv/bin/activate
pip install -r requirements.txt
cd frontend && npm install && npm run build && cd ..
systemctl restart telegram-bot
```

### Datenbank-Backup
```bash
sudo -u postgres pg_dump telegram_bot_db > backup_$(date +%Y%m%d).sql
```

### Datenbank wiederherstellen
```bash
sudo -u postgres psql telegram_bot_db < backup_20240101.sql
```

---

## Troubleshooting

### Service startet nicht
```bash
journalctl -u telegram-bot -n 50
# Prüfe .env Datei
# Prüfe PostgreSQL Verbindung
```

### Port bereits belegt
```bash
netstat -tulpn | grep 8000
# Prozess beenden oder Port ändern
```

### Nginx Fehler
```bash
nginx -t
tail -f /var/log/nginx/error.log
```

---

## Support

- **Hetzner Docs**: https://docs.hetzner.com
- **Hetzner Community**: https://community.hetzner.com

