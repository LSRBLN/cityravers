#!/bin/bash
# Vollständiges Backup-Script für Telegram Bot

BACKUP_DIR="backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="telegram-bot-backup-${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

echo "🔄 Erstelle vollständiges Backup..."

# Erstelle Backup-Verzeichnis
mkdir -p "${BACKUP_PATH}"

# Backup: Python-Dateien
echo "📦 Sichere Python-Dateien..."
mkdir -p "${BACKUP_PATH}/code"
cp *.py "${BACKUP_PATH}/code/" 2>/dev/null || true

# Backup: Datenbank
echo "💾 Sichere Datenbank..."
if [ -f "telegram_bot.db" ]; then
    cp telegram_bot.db "${BACKUP_PATH}/telegram_bot.db"
    echo "✅ SQLite-Datenbank gesichert"
fi

# Backup: Konfigurationsdateien
echo "⚙️  Sichere Konfigurationsdateien..."
cp requirements.txt "${BACKUP_PATH}/" 2>/dev/null || true
cp env.example "${BACKUP_PATH}/" 2>/dev/null || true
if [ -f ".env" ]; then
    # .env ohne Passwörter (nur Struktur)
    grep -v "API_KEY\|SECRET\|PASSWORD\|TOKEN" .env > "${BACKUP_PATH}/.env.example" 2>/dev/null || true
    echo "✅ .env Struktur gesichert (ohne sensible Daten)"
fi

# Backup: Frontend
echo "🎨 Sichere Frontend..."
if [ -d "frontend" ]; then
    mkdir -p "${BACKUP_PATH}/frontend"
    cp -r frontend/src "${BACKUP_PATH}/frontend/" 2>/dev/null || true
    cp frontend/package.json "${BACKUP_PATH}/frontend/" 2>/dev/null || true
    echo "✅ Frontend gesichert"
fi

# Backup: Sessions (falls vorhanden)
echo "📁 Sichere Sessions..."
if [ -d "sessions" ]; then
    mkdir -p "${BACKUP_PATH}/sessions"
    cp -r sessions/* "${BACKUP_PATH}/sessions/" 2>/dev/null || true
    echo "✅ Sessions gesichert"
fi

# Backup: Uploads (falls vorhanden)
echo "📤 Sichere Uploads..."
if [ -d "uploads" ]; then
    mkdir -p "${BACKUP_PATH}/uploads"
    cp -r uploads/* "${BACKUP_PATH}/uploads/" 2>/dev/null || true
    echo "✅ Uploads gesichert"
fi

# Backup: Logs
echo "📋 Sichere Logs..."
if [ -f "backend.log" ]; then
    cp backend.log "${BACKUP_PATH}/" 2>/dev/null || true
fi

# Erstelle Info-Datei
cat > "${BACKUP_PATH}/BACKUP_INFO.txt" << EOF
Backup erstellt: $(date)
Backup-Name: ${BACKUP_NAME}
Backup-Pfad: ${BACKUP_PATH}

Enthaltene Komponenten:
- Python-Code (*.py)
- Datenbank (telegram_bot.db)
- Konfigurationsdateien
- Frontend-Code
- Sessions (falls vorhanden)
- Uploads (falls vorhanden)
- Logs (falls vorhanden)

WICHTIG: .env Datei enthält sensible Daten und wurde NICHT gesichert!
Bitte .env manuell sichern falls nötig.
EOF

# Erstelle komprimiertes Archiv
echo "🗜️  Erstelle komprimiertes Archiv..."
cd "${BACKUP_DIR}"
tar -czf "${BACKUP_NAME}.tar.gz" "${BACKUP_NAME}" 2>/dev/null || zip -r "${BACKUP_NAME}.zip" "${BACKUP_NAME}" 2>/dev/null || true
cd ..

# Zeige Backup-Info
echo ""
echo "✅ Backup erfolgreich erstellt!"
echo "📁 Backup-Verzeichnis: ${BACKUP_PATH}"
echo "📦 Archiv: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz (oder .zip)"
echo ""
du -sh "${BACKUP_PATH}" 2>/dev/null || echo "Backup-Größe konnte nicht ermittelt werden"

