"""
Verschlüsselungs-Utilities für sensible Daten (Proxy-Passwörter, Secrets, etc.)
"""
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

# Lade oder generiere Verschlüsselungsschlüssel
def get_encryption_key() -> bytes:
    """
    Lädt den Verschlüsselungsschlüssel aus Umgebungsvariablen oder generiert einen neuen
    
    WICHTIG: In Produktion muss ENCRYPTION_KEY in Umgebungsvariablen gesetzt sein!
    Generiere einen Key mit: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    """
    key_str = os.getenv("ENCRYPTION_KEY")
    
    if key_str:
        return key_str.encode()
    else:
        # Fallback: Generiere Key aus JWT_SECRET_KEY (nicht ideal, aber besser als nichts)
        # WARNUNG: In Produktion sollte ENCRYPTION_KEY gesetzt sein!
        secret = os.getenv("JWT_SECRET_KEY")
        if not secret:
            raise RuntimeError(
                "ENCRYPTION_KEY oder JWT_SECRET_KEY muss gesetzt sein für Verschlüsselung. "
                "Generiere ENCRYPTION_KEY mit: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        
        # Erstelle Key aus Secret (PBKDF2)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'telegram_bot_salt',  # In Produktion sollte das auch aus Env-Var kommen
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
        return key

# Globale Fernet-Instanz
_fernet = None

def get_fernet() -> Fernet:
    """Gibt die Fernet-Verschlüsselungsinstanz zurück"""
    global _fernet
    if _fernet is None:
        key = get_encryption_key()
        _fernet = Fernet(key)
    return _fernet

def encrypt_string(plaintext: str) -> str:
    """
    Verschlüsselt einen String
    
    Args:
        plaintext: Zu verschlüsselnder Text
        
    Returns:
        Verschlüsselter String (base64)
    """
    if not plaintext:
        return ""
    
    fernet = get_fernet()
    encrypted = fernet.encrypt(plaintext.encode())
    return encrypted.decode()

def decrypt_string(ciphertext: str) -> str:
    """
    Entschlüsselt einen String
    
    Args:
        ciphertext: Verschlüsselter Text (base64)
        
    Returns:
        Entschlüsselter String
    """
    if not ciphertext:
        return ""
    
    try:
        fernet = get_fernet()
        decrypted = fernet.decrypt(ciphertext.encode())
        return decrypted.decode()
    except Exception as e:
        # Falls Entschlüsselung fehlschlägt (z.B. alter Key), gib leeren String zurück
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Fehler beim Entschlüsseln: {e}")
        return ""

