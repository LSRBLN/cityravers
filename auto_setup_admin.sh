#!/bin/bash
# Automatisches Admin-Setup für Railway
# Versucht DATABASE_URL automatisch zu holen und Admin-Setup auszuführen

echo "🚀 Automatisches Admin-Setup für Railway"
echo "========================================"
echo ""

cd /Users/rebelldesign/Documents/telegram-bot

# Methode 1: Versuche über railway run (DATABASE_URL ist automatisch verfügbar)
echo "1️⃣ Versuche über Railway CLI (railway run)..."
if command -v railway &> /dev/null; then
    echo "   Railway CLI gefunden"
    
    # Versuche direkt auf Railway auszuführen
    if railway run python3 create_railway_admin.py 2>&1; then
        echo ""
        echo "✅ Admin-Setup erfolgreich über Railway CLI ausgeführt!"
        exit 0
    else
        echo "   ⚠️  Railway run fehlgeschlagen (Projekt möglicherweise nicht verlinkt)"
    fi
else
    echo "   ⚠️  Railway CLI nicht installiert"
fi

echo ""
echo "2️⃣ Versuche DATABASE_URL aus Environment-Variablen..."
if [ -n "$DATABASE_URL" ]; then
    echo "   ✅ DATABASE_URL gefunden in Environment"
    echo "   Führe create_railway_admin.py aus..."
    python3 create_railway_admin.py
    exit $?
else
    echo "   ⚠️  DATABASE_URL nicht in Environment-Variablen"
fi

echo ""
echo "3️⃣ Versuche DATABASE_URL aus .env Datei..."
if [ -f .env ]; then
    source .env
    if [ -n "$DATABASE_URL" ]; then
        echo "   ✅ DATABASE_URL gefunden in .env"
        echo "   Führe create_railway_admin.py aus..."
        python3 create_railway_admin.py
        exit $?
    else
        echo "   ⚠️  DATABASE_URL nicht in .env gefunden"
    fi
else
    echo "   ⚠️  .env Datei nicht gefunden"
fi

echo ""
echo "❌ Konnte DATABASE_URL nicht automatisch finden"
echo ""
echo "📋 Manuelle Schritte:"
echo ""
echo "1. Öffne Railway Dashboard: https://railway.app"
echo "2. Gehe zu deinem Projekt → PostgreSQL Service"
echo "3. Klicke auf 'Variables' Tab"
echo "4. Kopiere die DATABASE_URL"
echo ""
echo "5. Führe dann aus:"
echo "   export DATABASE_URL='postgresql://user:pass@host:port/db'"
echo "   python3 create_railway_admin.py"
echo ""
echo "Oder direkt als Parameter:"
echo "   python3 create_railway_admin.py 'postgresql://user:pass@host:port/db'"
echo ""

exit 1

