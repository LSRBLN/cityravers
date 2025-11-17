#!/bin/bash
# Script zum Ausführen des Admin-Setups auf Railway

echo "🚀 Railway Admin Setup"
echo "===================="
echo ""

# Prüfe ob Railway CLI installiert ist
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI nicht gefunden"
    echo "   Installiere mit: brew install railway"
    exit 1
fi

echo "✅ Railway CLI gefunden"
echo ""

# Prüfe ob Projekt verlinkt ist
if ! railway status &> /dev/null; then
    echo "⚠️  Projekt nicht verlinkt"
    echo "   Führe aus: railway link"
    echo "   Oder: railway run python3 create_railway_admin.py"
    exit 1
fi

echo "✅ Projekt verlinkt"
echo ""

# Führe Script auf Railway aus
echo "🔄 Führe Admin-Setup auf Railway aus..."
echo ""

railway run python3 create_railway_admin.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Admin-Setup erfolgreich abgeschlossen!"
    echo ""
    echo "🧪 Teste Login:"
    echo "curl -X POST https://cityraver.up.railway.app/api/auth/login \\"
    echo "  -H 'Content-Type: application/json' \\"
    echo "  -d '{\"username\": \"admin\", \"password\": \"Sabine68#\"}'"
else
    echo ""
    echo "❌ Fehler beim Ausführen des Scripts"
    exit 1
fi

