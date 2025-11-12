#!/bin/bash
# Deployment-Script für Linux-Server

set -e

echo "🚀 Starte Deployment..."

# Variablen
PROJECT_DIR="/var/www/telegram-bot"
SERVICE_NAME="telegram-bot"
DOMAIN="${1:-localhost}"

# 1. Projekt aktualisieren
echo "📥 Aktualisiere Projekt..."
cd "$PROJECT_DIR"
git pull || echo "⚠️  Git pull fehlgeschlagen (kein Git-Repo?)"

# 2. Python Dependencies
echo "📦 Installiere Python Dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# 3. Frontend bauen
echo "🏗️  Baue Frontend..."
cd frontend
npm install
npm run build
cd ..

# 4. Datenbank migrieren
echo "🗄️  Aktualisiere Datenbank..."
python3 -c "from database import init_db; init_db(); print('✅ Datenbank aktualisiert')"

# 5. Service neu starten
echo "🔄 Starte Service neu..."
sudo systemctl restart $SERVICE_NAME
sudo systemctl status $SERVICE_NAME

echo "✅ Deployment abgeschlossen!"
echo "🌐 Frontend: http://$DOMAIN"
echo "🔌 API: http://$DOMAIN/api"

