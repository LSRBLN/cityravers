"""
Erstellt Admin-User über die Backend-API
Falls Admin noch nicht existiert, wird er über die API registriert
"""
import requests
import json
import sys

RAILWAY_BACKEND_URL = "https://cityraver.up.railway.app"

def create_admin_via_api():
    """Erstellt Admin-User über die Backend-API"""
    
    admin_username = "admin"
    admin_email = "admin@telegram-bot.local"
    admin_password = "Sabine68#"
    
    print(f"🚀 Erstelle Admin-User über Backend-API...")
    print(f"   Backend: {RAILWAY_BACKEND_URL}")
    print("")
    
    # Versuche zuerst Login (falls Admin bereits existiert)
    print("1️⃣ Prüfe ob Admin bereits existiert...")
    login_url = f"{RAILWAY_BACKEND_URL}/api/auth/login"
    login_data = {
        "username": admin_username,
        "password": admin_password
    }
    
    try:
        response = requests.post(login_url, json=login_data, timeout=10)
        if response.status_code == 200:
            print("✅ Admin-User existiert bereits und Login funktioniert!")
            result = response.json()
            print(f"   Access Token erhalten")
            print(f"   User ID: {result.get('user', {}).get('id', 'N/A')}")
            return True
        else:
            print(f"   Login fehlgeschlagen (Status: {response.status_code})")
            print(f"   Versuche Admin zu registrieren...")
    except Exception as e:
        print(f"   Login-Fehler: {e}")
        print(f"   Versuche Admin zu registrieren...")
    
    # Versuche Admin zu registrieren
    print("")
    print("2️⃣ Registriere Admin-User...")
    register_url = f"{RAILWAY_BACKEND_URL}/api/auth/register"
    register_data = {
        "username": admin_username,
        "email": admin_email,
        "password": admin_password
    }
    
    try:
        response = requests.post(register_url, json=register_data, timeout=10)
        if response.status_code == 200:
            print("✅ Admin-User registriert!")
            result = response.json()
            print(f"   User ID: {result.get('user_id', 'N/A')}")
            print(f"   Username: {result.get('username', 'N/A')}")
            print("")
            print("⚠️  WICHTIG: User wurde als normaler User erstellt.")
            print("   Um Admin-Rechte zu setzen, muss das Script 'create_railway_admin.py'")
            print("   direkt auf Railway ausgeführt werden (mit DATABASE_URL).")
            return True
        elif response.status_code == 400:
            error = response.json().get('detail', 'Unbekannter Fehler')
            if "bereits registriert" in error.lower() or "bereits vergeben" in error.lower():
                print(f"⚠️  User existiert bereits: {error}")
                print("   Versuche Login erneut...")
                # Versuche Login nochmal
                login_response = requests.post(login_url, json=login_data, timeout=10)
                if login_response.status_code == 200:
                    print("✅ Login erfolgreich!")
                    return True
            else:
                print(f"❌ Registrierung fehlgeschlagen: {error}")
                return False
        else:
            print(f"❌ Registrierung fehlgeschlagen (Status: {response.status_code})")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Fehler bei Registrierung: {e}")
        return False

if __name__ == "__main__":
    success = create_admin_via_api()
    if success:
        print("")
        print("✅ Setup abgeschlossen!")
        print("")
        print("🧪 Teste Login:")
        print(f"curl -X POST {RAILWAY_BACKEND_URL}/api/auth/login \\")
        print("  -H 'Content-Type: application/json' \\")
        print("  -d '{\"username\": \"admin\", \"password\": \"Sabine68#\"}'")
    else:
        print("")
        print("❌ Setup fehlgeschlagen!")
        print("")
        print("💡 Alternative: Führe 'create_railway_admin.py' direkt auf Railway aus:")
        print("   railway run python3 create_railway_admin.py")
        sys.exit(1)

