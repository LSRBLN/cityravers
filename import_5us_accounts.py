#!/usr/bin/env python3
"""
Importiert 5 Accounts aus der 5us.zip Datei zum Admin-Account
"""
import os
import sys
import asyncio
import shutil
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

from database import init_db, get_session, Account, User, Proxy
from account_manager import AccountManager
from encryption_utils import encrypt_string

# Initialisiere Datenbank
db_engine = init_db()

# Verzeichnisse
UPLOAD_DIR = Path("uploads")
SESSIONS_DIR = Path("sessions")
TDATA_DIR = Path("tdata_storage")
TDATA_DIR.mkdir(exist_ok=True)
SESSIONS_DIR.mkdir(exist_ok=True)

# ZIP-Datei
ZIP_PATH = UPLOAD_DIR / "5us.zip"
EXTRACT_DIR = Path("temp_5us")

async def import_account_from_tdata(phone_number: str, tdata_path: Path, two_factor_password: str = None, admin_user_id: int = None, proxy_id: int = None):
    """
    Importiert einen Account aus einem tdata-Ordner
    
    Args:
        phone_number: Telefonnummer (als Account-Name)
        tdata_path: Pfad zum tdata-Ordner
        two_factor_password: 2FA-Passwort (optional)
        admin_user_id: ID des Admin-Users
        proxy_id: Proxy-ID (optional)
    """
    db = get_session(db_engine)
    account_manager = AccountManager()
    
    try:
        # Prüfe ob Account bereits existiert
        existing = db.query(Account).filter(Account.name == phone_number).first()
        if existing:
            print(f"⚠️  Account '{phone_number}' existiert bereits (ID: {existing.id})")
            # Weise dem Admin zu, falls noch nicht
            if existing.user_id != admin_user_id:
                existing.user_id = admin_user_id
                db.commit()
                print(f"  ✅ Account dem Admin zugewiesen")
            
            # Aktualisiere tdata-Pfad falls nötig (wird später gesetzt)
            pass  # account_tdata_dir wird später erstellt
            
            # Aktualisiere 2FA falls vorhanden
            if two_factor_password and two_factor_password.strip():
                try:
                    encrypted_2fa = encrypt_string(two_factor_password.strip())
                    if not existing.two_factor_password or existing.two_factor_password != encrypted_2fa:
                        existing.two_factor_password = encrypted_2fa
                        db.commit()
                        print(f"  ✅ 2FA-Passwort aktualisiert")
                except Exception as e:
                    print(f"  ⚠️  Fehler beim Aktualisieren des 2FA-Passworts: {e}")
            
            # Verwende bestehenden Account für Verbindung
            db_account = existing
            session_name = existing.session_name or f"{phone_number}_{datetime.now().strftime('%Y%m%d')}"
            if not db_account.session_name:
                db_account.session_name = session_name
                db.commit()
        else:
            # Erstelle neuen Account (wie vorher)
            db_account = None
        
        # API Credentials aus Umgebungsvariablen
        api_id = os.getenv('TELEGRAM_API_ID')
        api_hash = os.getenv('TELEGRAM_API_HASH')
        
        if not api_id or not api_hash:
            print(f"❌ API Credentials fehlen (TELEGRAM_API_ID, TELEGRAM_API_HASH)")
            return None
        
        # Kopiere tdata-Ordner (verwende temporären Namen, wird später aktualisiert)
        account_tdata_dir = TDATA_DIR / phone_number
        if account_tdata_dir.exists():
            shutil.rmtree(account_tdata_dir)
        shutil.copytree(tdata_path, account_tdata_dir)
        print(f"  ✅ tdata kopiert nach: {account_tdata_dir}")
        
        # Generiere Session-Name (wird später mit echter Telefonnummer aktualisiert)
        session_name = f"{phone_number}_{datetime.now().strftime('%Y%m%d')}"
        
        # Erstelle Account nur wenn nicht vorhanden
        if not db_account:
            # Verschlüssele 2FA-Passwort falls vorhanden
            encrypted_2fa = None
            if two_factor_password and two_factor_password.strip():
                try:
                    encrypted_2fa = encrypt_string(two_factor_password.strip())
                except Exception as e:
                    print(f"  ⚠️  Fehler beim Verschlüsseln des 2FA-Passworts: {e}")
            
            # Erstelle Account in Datenbank
            db_account = Account(
                name=phone_number,
                account_type="user",
                api_id=api_id,
                api_hash=api_hash,
                phone_number=phone_number,
                session_name=session_name,
                tdata_path=str(account_tdata_dir),
                two_factor_password=encrypted_2fa,
                user_id=admin_user_id,
                proxy_id=proxy_id,
                is_active=True
            )
            db.add(db_account)
            db.commit()
            db.refresh(db_account)
            
            print(f"  ✅ Account erstellt: ID={db_account.id}, Name={phone_number}")
        else:
            print(f"  🔄 Verwende bestehenden Account: ID={db_account.id}")
            # Aktualisiere tdata-Pfad für bestehenden Account
            if not existing.tdata_path or not Path(existing.tdata_path).exists():
                existing.tdata_path = str(account_tdata_dir)
                db.commit()
                print(f"  ✅ tdata-Pfad aktualisiert")
        
        # Versuche tdata zu Session zu konvertieren und Account automatisch zu verbinden
        print(f"  🔄 Konvertiere tdata zu Session und verbinde Account automatisch...")
        print(f"  🔐 2FA-Passwort: {two_factor_password if two_factor_password else 'Keines'}")
        
        try:
            # Verwende direkte tdata-Konvertierung mit opentele
            # opentele wurde für Python 3.14 gepatcht
            print(f"  📦 Verwende opentele für tdata-Konvertierung...")
            
            # Versuche opentele mit Event Loop Fix
            import nest_asyncio
            nest_asyncio.apply()
            
            from opentele.td import TDesktop
            from opentele.api import API, CreateNewSession
            from telethon import TelegramClient
            
            print(f"  🔄 Lade tdata...")
            tdesk = TDesktop(str(account_tdata_dir))
            
            if not tdesk.isLoaded():
                raise Exception("tdata konnte nicht geladen werden")
            
            print(f"  🔄 Konvertiere tdata zu Telethon Session...")
            session_file_path = str(SESSIONS_DIR / phone_number)
            api = API.TelegramDesktop.Generate()
            
            # Konvertiere zu Telethon
            telethon_client = await tdesk.ToTelethon(session_file_path, CreateNewSession, api)
            await telethon_client.connect()
            
            if await telethon_client.is_user_authorized():
                # Hole User-Info
                me = await telethon_client.get_me()
                final_phone = me.phone or phone_number
                
                print(f"  ✅ Telethon-Verbindung erfolgreich!")
                print(f"     Name: {me.first_name} {me.last_name or ''}")
                print(f"     Username: @{me.username or 'N/A'}")
                print(f"     Telefon: {final_phone}")
                
                # Aktualisiere Account mit echter Telefonnummer
                if final_phone and final_phone != db_account.phone_number:
                    db_account.name = final_phone
                    db_account.phone_number = final_phone
                    db.commit()
                    print(f"  ✅ Account-Name aktualisiert: {final_phone}")
                
                # Speichere Session-Pfad
                db_account.session_file_path = session_file_path
                db.commit()
                
                print(f"  ✅ Telethon Session erstellt: {session_file_path}")
                
                # Verbinde Account direkt mit der Session
                result = await account_manager.add_account(
                    account_id=db_account.id,
                    api_id=api_id,
                    api_hash=api_hash,
                    session_name=final_phone or session_name,
                    session_file_path=session_file_path
                )
                
                if result.get("status") == "connected":
                    user_info = result.get('info', {})
                    print(f"  ✅ Account erfolgreich verbunden!")
                    print(f"     Name: {user_info.get('first_name', 'N/A')} {user_info.get('last_name', '')}")
                    print(f"     Username: @{user_info.get('username', 'N/A')}")
                    print(f"     Telefon: {user_info.get('phone', final_phone)}")
                    
                    # Finale Telefonnummer aktualisieren
                    final_phone_from_info = user_info.get('phone') or final_phone
                    if final_phone_from_info and final_phone_from_info != db_account.phone_number:
                        db_account.phone_number = final_phone_from_info
                        db_account.name = final_phone_from_info
                        db.commit()
                else:
                    print(f"  ⚠️  Verbindungsstatus: {result.get('status', 'unknown')}")
                    if result.get("error"):
                        print(f"     Fehler: {result.get('error')}")
                
                await telethon_client.disconnect()
            else:
                await telethon_client.disconnect()
                raise Exception("Konnte nicht autorisieren")
        
        except Exception as convert_error:
            error_msg = str(convert_error)
            print(f"  ⚠️  Fehler bei tdata-Konvertierung: {error_msg}")
            import traceback
            traceback.print_exc()
            print(f"     Account wurde erstellt, aber automatisches Login fehlgeschlagen")
            print(f"     Versuchen Sie manuelles Login im Frontend mit 2FA-Passwort: {two_factor_password}")
        
        except Exception as e:
            print(f"  ⚠️  Fehler beim Verbinden: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"     Account wurde erstellt, muss aber manuell eingeloggt werden")
        
        return db_account.id
    
    except Exception as e:
        db.rollback()
        print(f"  ❌ Fehler beim Erstellen des Accounts: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

async def main():
    """Hauptfunktion"""
    print("🚀 Starte Import von 5 Accounts aus 5us.zip...\n")
    
    # Prüfe ob ZIP-Datei existiert
    if not ZIP_PATH.exists():
        print(f"❌ ZIP-Datei nicht gefunden: {ZIP_PATH}")
        return
    
    # Entpacke ZIP-Datei
    print("📦 Entpacke ZIP-Datei...")
    import zipfile
    if EXTRACT_DIR.exists():
        shutil.rmtree(EXTRACT_DIR)
    EXTRACT_DIR.mkdir(exist_ok=True)
    
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)
    
    accounts_dir = EXTRACT_DIR / "5us"
    if not accounts_dir.exists():
        print(f"❌ Erwarteter Ordner '5us' nicht gefunden in ZIP")
        return
    
    # Finde Admin-User
    db = get_session(db_engine)
    try:
        admin_user = db.query(User).filter(User.is_admin == True).first()
        if not admin_user:
            print("❌ Kein Admin-User gefunden!")
            return
        
        print(f"✅ Admin-User gefunden: {admin_user.username} (ID: {admin_user.id})\n")
        admin_user_id = admin_user.id
        
        # Prüfe ob Proxy vorhanden (verwende ersten verfügbaren)
        proxy = db.query(Proxy).filter(Proxy.is_active == True).first()
        proxy_id = proxy.id if proxy else None
        if proxy_id:
            print(f"✅ Verwende Proxy ID {proxy_id}\n")
        else:
            print(f"⚠️  Kein Proxy gefunden - Accounts werden ohne Proxy erstellt\n")
    
    finally:
        db.close()
    
    # Finde alle Account-Ordner (auch wenn keine Nummer im Namen)
    account_dirs = [d for d in accounts_dir.iterdir() if d.is_dir() and not d.name.startswith('__')]
    
    if not account_dirs:
        print("❌ Keine Account-Ordner gefunden")
        return
    
    print(f"📋 Gefundene Accounts: {len(account_dirs)}\n")
    
    imported = []
    for idx, account_dir in enumerate(sorted(account_dirs), 1):
        # Verwende Ordnername als Account-Name (kann Nummer oder anderer Name sein)
        account_name = account_dir.name
        print(f"📱 Verarbeite Account {idx}/{len(account_dirs)}: {account_name}")
        
        # Lade 2FA-Passwort (Standard: "Ms" falls nicht vorhanden)
        two_factor_password = "Ms"  # Standard 2FA-Passwort
        two_fa_file = account_dir / "2FA.txt"
        if two_fa_file.exists():
            try:
                file_content = two_fa_file.read_text().strip()
                if file_content:
                    two_factor_password = file_content
                    print(f"  ✅ 2FA-Passwort aus Datei: {two_factor_password}")
                else:
                    print(f"  ⚠️  2FA.txt ist leer, verwende Standard: {two_factor_password}")
            except Exception as e:
                print(f"  ⚠️  Fehler beim Lesen von 2FA.txt: {e}, verwende Standard: {two_factor_password}")
        else:
            print(f"  ℹ️  2FA.txt nicht gefunden, verwende Standard: {two_factor_password}")
        
        # Finde tdata-Ordner
        tdata_path = account_dir / "tdata"
        if not tdata_path.exists() or not tdata_path.is_dir():
            print(f"  ❌ tdata-Ordner nicht gefunden")
            continue
        
        # Prüfe ob tdata-Ordner Dateien enthält
        tdata_files = list(tdata_path.iterdir())
        if len(tdata_files) < 2:
            print(f"  ⚠️  tdata-Ordner scheint unvollständig zu sein")
        
        # Importiere Account (phone_number wird später aus tdata extrahiert)
        account_id = await import_account_from_tdata(
            phone_number=account_name,  # Temporärer Name, wird später durch echte Telefonnummer ersetzt
            tdata_path=tdata_path,
            two_factor_password=two_factor_password,
            admin_user_id=admin_user_id,
            proxy_id=proxy_id
        )
        
        if account_id:
            imported.append(account_id)
        
        print()  # Leerzeile
    
    # Aufräumen
    print("🧹 Räume temporäre Dateien auf...")
    if EXTRACT_DIR.exists():
        shutil.rmtree(EXTRACT_DIR)
    
    print(f"\n✅ Import abgeschlossen: {len(imported)} Account(s) importiert")
    if imported:
        print(f"   Account-IDs: {', '.join(map(str, imported))}")
        print(f"\n📝 Nächste Schritte:")
        print(f"   1. Öffne das Frontend und gehe zu 'Accounts'")
        print(f"   2. Für jeden Account: Klicke auf 'Verbinden' oder 'Login'")
        print(f"   3. Falls Code erforderlich: Verwende die Login-Funktion mit der Telefonnummer")
        print(f"   4. Die Accounts sind bereits dem Admin-User zugewiesen")

if __name__ == "__main__":
    asyncio.run(main())

