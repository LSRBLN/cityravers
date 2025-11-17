#!/usr/bin/env python3
"""
Generiert sichere Secrets für Environment Variables
"""
import secrets
import base64
import os

def generate_jwt_secret():
    """Generiert einen sicheren JWT Secret Key (min. 32 Zeichen)"""
    return secrets.token_urlsafe(32)

def generate_encryption_key():
    """Generiert einen Fernet-kompatiblen Encryption Key"""
    # Fernet benötigt 32 Bytes, base64-encoded
    key_bytes = secrets.token_bytes(32)
    return base64.urlsafe_b64encode(key_bytes).decode()

def main():
    print("=" * 60)
    print("🔐 SICHERE SECRETS GENERIEREN")
    print("=" * 60)
    print()
    
    jwt_secret = generate_jwt_secret()
    encryption_key = generate_encryption_key()
    
    print("✅ Generierte Secrets:")
    print()
    print("JWT_SECRET_KEY=" + jwt_secret)
    print()
    print("ENCRYPTION_KEY=" + encryption_key)
    print()
    print("=" * 60)
    print("⚠️  WICHTIG:")
    print("- Speichere diese Werte SICHER (nicht in Git!)")
    print("- Verwende diese Werte in Railway/Vercel Environment Variables")
    print("- TEILE diese Werte NIEMALS öffentlich!")
    print("=" * 60)
    print()
    print("📋 Für Telegram API Credentials:")
    print("1. Gehe zu: https://my.telegram.org/apps")
    print("2. Logge dich mit deiner Telefonnummer ein")
    print("3. Erstelle eine neue App")
    print("4. Kopiere API ID und API Hash")
    print()

if __name__ == "__main__":
    main()

