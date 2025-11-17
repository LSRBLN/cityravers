#!/bin/bash
echo "🚀 Erstelle Admin-User auf Railway..."
echo ""

BACKEND_URL="https://cityraver.up.railway.app"
USERNAME="admin"
EMAIL="admin@telegram-bot.local"
PASSWORD="Sabine68#"

echo "1️⃣ Prüfe ob Admin bereits existiert..."
LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo "✅ Admin-User existiert bereits und Login funktioniert!"
    echo "$LOGIN_RESPONSE" | python3 -m json.tool 2>/dev/null | head -10
    exit 0
fi

echo "   Login fehlgeschlagen, versuche Registrierung..."
echo ""

echo "2️⃣ Registriere Admin-User..."
REGISTER_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

if echo "$REGISTER_RESPONSE" | grep -q "user_id"; then
    echo "✅ Admin-User registriert!"
    echo "$REGISTER_RESPONSE" | python3 -m json.tool 2>/dev/null
    echo ""
    echo "⚠️  WICHTIG: User wurde als normaler User erstellt."
    echo "   Um Admin-Rechte zu setzen, führe 'create_railway_admin.py' auf Railway aus."
else
    echo "❌ Registrierung fehlgeschlagen:"
    echo "$REGISTER_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$REGISTER_RESPONSE"
fi
