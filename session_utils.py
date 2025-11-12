"""
Utilities für Session-Dateien und tdata
"""

import os
import shutil
import json
from pathlib import Path
from typing import Optional, Tuple
try:
    from Cryptodome.Cipher import AES
    from Cryptodome.Protocol.KDF import PBKDF2
except ImportError:
    # Fallback für pycryptodome
    from Crypto.Cipher import AES
    from Crypto.Protocol.KDF import PBKDF2


def find_session_files(directory: str) -> list:
    """
    Findet alle .session Dateien in einem Verzeichnis
    
    Args:
        directory: Verzeichnis zum Durchsuchen
        
    Returns:
        Liste von Session-Dateipfaden
    """
    session_files = []
    directory_path = Path(directory)
    
    if not directory_path.exists():
        return session_files
    
    # Suche nach .session Dateien
    for file_path in directory_path.rglob("*.session"):
        session_files.append(str(file_path))
    
    return session_files


def extract_session_info(session_path: str) -> Optional[dict]:
    """
    Extrahiert Informationen aus einer Session-Datei
    
    Args:
        session_path: Pfad zur Session-Datei
        
    Returns:
        Dict mit Session-Informationen oder None
    """
    try:
        session_file = Path(session_path)
        if not session_file.exists():
            return None
        
        # Telethon Session-Dateien sind SQLite-Datenbanken
        # Wir können nur den Dateinamen und Pfad zurückgeben
        return {
            "path": str(session_path),
            "name": session_file.stem,
            "size": session_file.stat().st_size,
            "type": "telethon"
        }
    except Exception as e:
        return None


def copy_session_file(source_path: str, target_name: str, target_dir: str = "sessions") -> Optional[str]:
    """
    Kopiert eine Session-Datei in das Zielverzeichnis
    
    Args:
        source_path: Quellpfad der Session-Datei
        target_name: Name für die neue Session-Datei (ohne .session)
        target_dir: Zielverzeichnis
        
    Returns:
        Pfad zur kopierten Datei (ohne .session) oder None
    """
    try:
        target_dir_path = Path(target_dir)
        target_dir_path.mkdir(exist_ok=True)
        
        source_file = Path(source_path)
        if not source_file.exists():
            return None
        
        # Entferne .session Endung falls vorhanden
        if target_name.endswith('.session'):
            target_name = target_name[:-8]
        
        target_path = target_dir_path / f"{target_name}.session"
        
        # Kopiere Datei
        shutil.copy2(source_path, target_path)
        
        # Gib Session-Name zurück (ohne .session, wie Telethon es erwartet)
        return str(target_dir_path / target_name)
    except Exception as e:
        print(f"Fehler beim Kopieren der Session-Datei: {e}")
        return None


def find_tdata_folder(directory: str) -> Optional[str]:
    """
    Findet tdata-Ordner in einem Verzeichnis
    
    Args:
        directory: Verzeichnis zum Durchsuchen
        
    Returns:
        Pfad zum tdata-Ordner oder None
    """
    directory_path = Path(directory)
    
    if not directory_path.exists():
        return None
    
    # Suche nach tdata-Ordnern
    for item in directory_path.rglob("tdata"):
        if item.is_dir():
            return str(item)
    
    # Suche auch nach typischen Telegram Desktop Pfaden
    common_paths = [
        directory_path / "tdata",
        directory_path / "Telegram Desktop" / "tdata",
    ]
    
    for path in common_paths:
        if path.exists() and path.is_dir():
            return str(path)
    
    return None


def convert_tdata_to_session(tdata_path: str, session_name: str, api_id: str, api_hash: str) -> Optional[str]:
    """
    Konvertiert tdata zu einer Telethon Session-Datei
    
    Hinweis: Dies ist eine vereinfachte Implementierung.
    Vollständige tdata-Konvertierung erfordert komplexe Logik.
    
    Args:
        tdata_path: Pfad zum tdata-Ordner
        session_name: Name für die Session-Datei
        api_id: Telegram API ID
        api_hash: Telegram API Hash
        
    Returns:
        Pfad zur erstellten Session-Datei oder None
    """
    try:
        from telethon import TelegramClient
        
        tdata_dir = Path(tdata_path)
        if not tdata_dir.exists():
            return None
        
        # Versuche Session-Datei zu erstellen
        # Hinweis: Vollständige tdata-Konvertierung ist komplex
        # Diese Funktion ist ein Platzhalter für die Implementierung
        
        # Für jetzt: Erstelle eine neue Session und informiere den Benutzer
        # dass tdata manuell konvertiert werden muss
        return None
        
    except Exception as e:
        return None


def validate_session_file(session_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validiert eine Session-Datei
    
    Args:
        session_path: Pfad zur Session-Datei
        
    Returns:
        Tuple (is_valid, error_message)
    """
    try:
        session_file = Path(session_path)
        
        if not session_file.exists():
            return False, "Session-Datei existiert nicht"
        
        if not session_file.is_file():
            return False, "Pfad ist keine Datei"
        
        if session_file.suffix != ".session":
            return False, "Datei hat nicht die .session Endung"
        
        # Prüfe ob Datei lesbar ist
        if not os.access(session_path, os.R_OK):
            return False, "Session-Datei ist nicht lesbar"
        
        # Prüfe minimale Dateigröße (Session-Dateien sind SQLite-DBs)
        if session_file.stat().st_size < 100:
            return False, "Session-Datei scheint zu klein zu sein"
        
        return True, None
        
    except Exception as e:
        return False, f"Fehler beim Validieren: {str(e)}"

