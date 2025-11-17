#!/bin/bash
# Führt das Admin-Setup direkt auf Railway aus

echo "🚀 Führe Admin-Setup auf Railway aus..."
echo ""

cd /Users/rebelldesign/Documents/telegram-bot

# Versuche railway run
echo "1️⃣ Versuche über Railway CLI..."
if railway run python3 create_railway_admin.py 2>&1; then
    echo ""
    echo "✅ Admin-Setup erfolgreich über Railway CLI ausgeführt!"
    exit 0
fi

echo ""
echo "⚠️  Railway CLI nicht verfügbar oder Projekt nicht verlinkt"
echo ""
echo "2️⃣ Alternative: DATABASE_URL manuell setzen"
echo ""
echo "Bitte kopiere die DATABASE_URL von Railway Dashboard:"
echo "   1. Railway Dashboard → PostgreSQL Service"
echo "   2. Variables Tab → DATABASE_URL kopieren"
echo ""
echo "Dann führe aus:"
echo "   export DATABASE_URL='postgresql://...'"
echo "   python3 create_railway_admin.py"
echo ""

