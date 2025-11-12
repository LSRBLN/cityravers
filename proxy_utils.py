"""
Hilfsfunktionen für Proxy-Verwaltung mit Verschlüsselung
"""
from encryption_utils import decrypt_string
from database import Proxy

def get_proxy_config_decrypted(proxy: Proxy) -> dict:
    """
    Gibt Proxy-Konfiguration mit entschlüsselten Passwörtern zurück
    (Nur für interne Verwendung, niemals in API-Responses!)
    
    Args:
        proxy: Proxy-Objekt aus Datenbank
        
    Returns:
        Dict mit Proxy-Konfiguration (Passwörter entschlüsselt)
    """
    if not proxy:
        return None
    
    return {
        "proxy_type": proxy.proxy_type,
        "host": proxy.host,
        "port": proxy.port,
        "username": proxy.username,
        "password": decrypt_string(proxy.password) if proxy.password else None,
        "secret": decrypt_string(proxy.secret) if proxy.secret else None
    }

