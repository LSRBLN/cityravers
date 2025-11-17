#!/bin/bash
# Setzt Admin-Rechte für den User "admin" auf Railway
# Benötigt DATABASE_URL von Railway

echo "🔧 Setze Admin-Rechte für User 'admin'..."
echo ""

BACKEND_URL="https://cityraver.up.railway.app"
USERNAME="admin"
PASSWORD="Sabine68#"

# Hole Access Token
echo "1️⃣ Hole Access Token..."
TOKEN=$(curl -s -X POST "$BACKEND_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}" | \
  python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "❌ Konnte keinen Access Token erhalten"
    exit 1
fi

echo "✅ Token erhalten"
echo ""

# Prüfe ob User Admin ist
echo "2️⃣ Prüfe aktuelle Admin-Rechte..."
USER_INFO=$(curl -s -X GET "$BACKEND_URL/api/auth/me" \
  -H "Authorization: Bearer $TOKEN")

IS_ADMIN=$(echo "$USER_INFO" | python3 -c "import sys, json; print(json.load(sys.stdin).get('is_admin', False))" 2>/dev/null)

if [ "$IS_ADMIN" = "True" ]; then
    echo "✅ User ist bereits Admin!"
    exit 0
fi

echo "⚠️  User ist noch kein Admin"
echo ""

# Versuche Admin-Rechte über API zu setzen (falls Endpoint existiert)
echo "3️⃣ Versuche Admin-Rechte über API zu setzen..."
UPDATE_RESPONSE=$(curl -s -X PUT "$BACKEND_URL/api/admin/users/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"is_admin": true}' 2>&1)

if echo "$UPDATE_RESPONSE" | grep -q "is_admin.*true"; then
    echo "✅ Admin-Rechte erfolgreich gesetzt!"
    exit 0
fi

echo "❌ Konnte Admin-Rechte nicht über API setzen"
echo ""
echo "💡 Lösung: Führe 'create_railway_admin.py' direkt auf Railway aus:"
echo "   railway run python3 create_railway_admin.py"
echo ""
echo "   Oder setze DATABASE_URL und führe aus:"
echo "   export DATABASE_URL='postgresql://...'"
echo "   python3 create_railway_admin.py"

