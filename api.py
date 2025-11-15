"""
FastAPI Backend für Berlin City Raver - Marketing Tool
"""

from fastapi import FastAPI, HTTPException, Depends, Query, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import and_
import os
import shutil
from pathlib import Path
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from dotenv import load_dotenv

# Lade Umgebungsvariablen aus .env
load_dotenv()

from database import init_db, get_session, Account, Group, ScheduledMessage, ScrapedUser, AccountWarming, WarmingActivity, MessageTemplate, SentMessage, AccountStatistic, Proxy, User, Subscription, PhoneNumberPurchase, SystemSettings
from auth import get_current_active_user, get_current_admin, create_access_token, get_password_hash, verify_password, check_subscription, check_account_limit, check_group_limit, ACCESS_TOKEN_EXPIRE_MINUTES
from phone_providers import FiveSimProvider, SMSActivateProvider, SMSManagerProvider, GetSMSCodeProvider, OnlineSimProvider
from account_manager import AccountManager
from bot_manager import BotManager
from scheduler_service import SchedulerService
from warming_service import WarmingService
from message_storage import save_sent_message, get_account_statistics
from session_utils import validate_session_file, copy_session_file, find_tdata_folder
from encryption_utils import encrypt_string, decrypt_string
from proxy_utils import get_proxy_config_decrypted
import json
import logging

# Logging konfigurieren
# Auf Vercel gibt es kein persistentes Dateisystem, daher nur StreamHandler
handlers = [logging.StreamHandler()]
try:
    # Versuche FileHandler nur wenn möglich (nicht auf Vercel)
    handlers.append(logging.FileHandler('backend.log'))
except (OSError, PermissionError):
    # Auf Vercel/Serverless wird FileHandler ignoriert
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

# FastAPI App
app = FastAPI(title="Berlin City Raver - Marketing Tool API", version="1.0.0")

# Rate Limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS für React Frontend
# Lade erlaubte Origins aus Umgebungsvariablen
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:5173"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

# Globale Instanzen
# Initialisiere DB mit Fehlerbehandlung
try:
    db_engine = init_db()
except Exception as e:
    logger.error(f"Fehler bei DB-Initialisierung: {e}")
    db_engine = None

account_manager = AccountManager()
bot_manager = BotManager()

# Services nur initialisieren wenn DB verfügbar
if db_engine:
    scheduler_service = SchedulerService(account_manager, bot_manager, db_engine)
    warming_service = WarmingService(account_manager, db_engine)
else:
    logger.warning("DB nicht verfügbar, Services werden nicht initialisiert")
    scheduler_service = None
    warming_service = None

# Upload-Verzeichnisse erstellen (nur wenn möglich)
UPLOAD_DIR = Path("uploads")
SESSIONS_DIR = Path("sessions")
try:
    UPLOAD_DIR.mkdir(exist_ok=True)
    SESSIONS_DIR.mkdir(exist_ok=True)
except (OSError, PermissionError):
    # Auf Vercel/Serverless nicht möglich
    logger.warning("Upload-Verzeichnisse können nicht erstellt werden (Serverless)")

# Pydantic Models
class AccountCreate(BaseModel):
    name: str
    account_type: str = "user"  # 'user' oder 'bot'
    api_id: Optional[str] = None  # Nur für User
    api_hash: Optional[str] = None  # Nur für User
    bot_token: Optional[str] = None  # Nur für Bot
    phone_number: Optional[str] = None  # Nur für User
    session_name: Optional[str] = None  # Nur für User
    proxy_id: Optional[int] = None  # Optional: Proxy-ID
    session_file_path: Optional[str] = None  # Pfad zur hochgeladenen Session-Datei
    tdata_path: Optional[str] = None  # Pfad zum tdata-Ordner

class AccountLogin(BaseModel):
    account_id: int
    code: Optional[str] = None
    password: Optional[str] = None
    phone_code_hash: Optional[str] = None  # Wird beim request-code zurückgegeben

class GroupCreate(BaseModel):
    name: str
    chat_id: Optional[str] = None  # Optional wenn name/username verwendet wird
    chat_type: Optional[str] = None
    username: Optional[str] = None

class BulkBotCreate(BaseModel):
    bots: List[dict]  # Liste von {"name": "...", "bot_token": "..."}

class BulkGroupCreate(BaseModel):
    account_id: int
    group_names: List[str]  # Liste von Gruppennamen oder Usernames (@username)

class ScheduledMessageCreate(BaseModel):
    account_id: int
    group_ids: List[int]  # Mehrere Gruppen
    message: str
    scheduled_time: datetime
    delay: float = Field(default=1.0, ge=0.1, le=60.0)
    batch_size: int = Field(default=10, ge=1, le=100)
    batch_delay: float = Field(default=5.0, ge=0, le=300.0)
    repeat_count: int = Field(default=1, ge=1, le=1000)
    group_delay: float = Field(default=2.0, ge=0, le=300.0)  # Delay zwischen Gruppen

class ScheduledMessageUpdate(BaseModel):
    message: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    delay: Optional[float] = Field(None, ge=0.1, le=60.0)
    batch_size: Optional[int] = Field(None, ge=1, le=100)
    batch_delay: Optional[float] = Field(None, ge=0, le=300.0)
    repeat_count: Optional[int] = Field(None, ge=1, le=1000)

# Dependency für DB Session
def get_db():
    db = get_session(db_engine)
    try:
        yield db
    finally:
        db.close()

# Startup Event
@app.on_event("startup")
async def startup_event():
    """Lädt ausstehende Nachrichten beim Start"""
    # Führe Datenbank-Migration aus (fügt fehlende Spalten hinzu)
    try:
        from migrate_groups_schema import migrate_groups_table
        migrate_groups_table()
        logger.info("✅ Datenbank-Migration erfolgreich")
    except Exception as e:
        logger.warning(f"⚠️  Datenbank-Migration fehlgeschlagen (kann ignoriert werden wenn Schema aktuell): {e}")
    
    if scheduler_service and warming_service:
        scheduler_service.start()
        await scheduler_service.load_pending_messages()
        await warming_service.start_all_active_warmings()
    else:
        logger.warning("Services nicht verfügbar (DB-Problem), überspringe Startup")

@app.on_event("shutdown")
async def shutdown_event():
    """Beendet Services beim Shutdown"""
    await account_manager.disconnect_all()
    await bot_manager.disconnect_all()
    if warming_service:
        await warming_service.stop_all_warmings()
    if scheduler_service:
        scheduler_service.shutdown()

# Account Endpoints
@app.post("/api/accounts", response_model=dict)
async def create_account(
    account: AccountCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Erstellt einen neuen Account (User oder Bot)"""
    # Prüfe Account-Limit
    account_count = db.query(Account).filter(Account.user_id == current_user.id).count()
    if not check_account_limit(current_user, account_count):
        raise HTTPException(
            status_code=403,
            detail=f"Account-Limit erreicht. Maximal {current_user.subscription.max_accounts if current_user.subscription else 1} Accounts erlaubt."
        )
    
    if account.account_type == "bot":
        if not account.bot_token:
            raise HTTPException(status_code=400, detail="Bot-Token erforderlich für Bot-Accounts")
        
        db_account = Account(
            user_id=current_user.id,
            name=account.name,
            account_type="bot",
            bot_token=account.bot_token
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        # Verbinde Bot
        result = await bot_manager.add_bot(
            bot_id=db_account.id,
            bot_token=account.bot_token
        )
        
        return {"account_id": db_account.id, **result}
    
    else:  # User Account
        if not account.session_name:
            raise HTTPException(status_code=400, detail="Session-Name erforderlich für User-Accounts")
        
        # API ID/Hash sind optional wenn Session-Datei vorhanden ist
        # Prüfe ob API Credentials vorhanden sind (entweder explizit oder in Umgebungsvariablen)
        if not account.api_id or not account.api_hash:
            # Versuche aus Umgebungsvariablen zu laden
            account.api_id = account.api_id or os.getenv('TELEGRAM_API_ID')
            account.api_hash = account.api_hash or os.getenv('TELEGRAM_API_HASH')
            
            if not account.api_id or not account.api_hash:
                # Versuche aus Session-Datei zu extrahieren (wird in add_account gemacht)
                if not account.session_file_path:
                    raise HTTPException(
                        status_code=400, 
                        detail="API ID/Hash oder Session-Datei erforderlich. Bitte API Credentials angeben oder Session-Datei hochladen."
                    )
        
        # Lade Proxy falls angegeben (mit entschlüsselten Passwörtern für interne Verwendung)
        proxy_config = None
        if account.proxy_id:
            proxy = db.query(Proxy).filter(Proxy.id == account.proxy_id).first()
            if proxy:
                proxy_config = get_proxy_config_decrypted(proxy)
                # Aktualisiere Proxy-Statistiken
                proxy.usage_count += 1
                proxy.last_used = datetime.utcnow()
                db.commit()
        
        db_account = Account(
            user_id=current_user.id,
            name=account.name,
            account_type="user",
            api_id=account.api_id,
            api_hash=account.api_hash,
            phone_number=account.phone_number,
            session_name=account.session_name,
            session_file_path=account.session_file_path,
            tdata_path=account.tdata_path,
            proxy_id=account.proxy_id
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        # Versuche Verbindung
        # API ID/Hash können None sein, werden in add_account aus Session oder Umgebungsvariablen geladen
        result = await account_manager.add_account(
            account_id=db_account.id,
            api_id=db_account.api_id,
            api_hash=db_account.api_hash,
            session_name=db_account.session_name,
            phone_number=db_account.phone_number,
            session_file_path=db_account.session_file_path,
            proxy_config=proxy_config
        )
        
        return {"account_id": db_account.id, **result}

@app.post("/api/accounts/{account_id}/request-code", response_model=dict)
async def request_code(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Fordert einen Login-Code für einen Account an"""
    try:
        db_account = db.query(Account).filter(Account.id == account_id).first()
        if not db_account:
            logger.error(f"Account {account_id} nicht gefunden")
            raise HTTPException(status_code=404, detail="Account nicht gefunden")
        
        # Prüfe ob Account dem User gehört
        if db_account.user_id and db_account.user_id != current_user.id:
            logger.error(f"Zugriff verweigert: Account {account_id} gehört nicht zu User {current_user.id}")
            raise HTTPException(status_code=403, detail="Zugriff verweigert: Account gehört nicht zu diesem Benutzer")
        
        if not db_account.phone_number:
            logger.error(f"Telefonnummer fehlt für Account {account_id}")
            raise HTTPException(status_code=400, detail="Telefonnummer fehlt. Bitte zuerst Telefonnummer setzen.")
        
        logger.info(f"Fordere Code an für Account {account_id} (Telefonnummer: {db_account.phone_number})")
        
        # Lade Proxy falls vorhanden (mit entschlüsselten Passwörtern)
        proxy_config = None
        if db_account.proxy_id:
            proxy = db.query(Proxy).filter(Proxy.id == db_account.proxy_id).first()
            if proxy:
                proxy_config = get_proxy_config_decrypted(proxy)
                logger.info(f"Proxy {db_account.proxy_id} wird verwendet")
        
        # Prüfe API Credentials
        api_id = db_account.api_id or os.getenv('TELEGRAM_API_ID')
        api_hash = db_account.api_hash or os.getenv('TELEGRAM_API_HASH')
        
        if not api_id or not api_hash:
            logger.error(f"API Credentials fehlen für Account {account_id}")
            raise HTTPException(
                status_code=400, 
                detail="API ID und API Hash fehlen. Bitte in den Account-Einstellungen setzen oder als Umgebungsvariablen konfigurieren."
            )
        
        logger.info(f"API ID vorhanden: {bool(api_id)}, API Hash vorhanden: {bool(api_hash)}")
        
        # Versuche Verbindung - wenn Session nicht autorisiert, wird Code angefordert
        result = await account_manager.add_account(
            account_id=account_id,
            api_id=api_id,
            api_hash=api_hash,
            session_name=db_account.session_name,
            phone_number=db_account.phone_number,
            session_file_path=db_account.session_file_path,
            proxy_config=proxy_config
        )
        
        logger.info(f"Code-Anfrage Ergebnis für Account {account_id}: {result.get('status')}")
        
        # Speichere phone_code_hash in der Datenbank für späteren Login
        if result.get('status') == 'code_required' and result.get('phone_code_hash'):
            # Speichere Hash temporär (kann auch in Account-Tabelle gespeichert werden)
            # Für jetzt verwenden wir die Session-Datei, Telethon speichert es automatisch
            logger.info(f"phone_code_hash erhalten: {result.get('phone_code_hash')[:10]}...")
        
        # Wenn Fehler, logge Details
        if result.get('status') == 'error':
            logger.error(f"Fehler bei Code-Anfrage für Account {account_id}: {result.get('error')}")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unerwarteter Fehler bei Code-Anfrage für Account {account_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fehler beim Anfordern des Codes: {str(e)}")

@app.post("/api/accounts/{account_id}/login", response_model=dict)
async def login_account(account_id: int, login: AccountLogin, db: Session = Depends(get_db)):
    """Loggt einen Account ein"""
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    # Lade Proxy falls vorhanden (mit entschlüsselten Passwörtern)
    proxy_config = None
    if db_account.proxy_id:
        proxy = db.query(Proxy).filter(Proxy.id == db_account.proxy_id).first()
        if proxy:
            proxy_config = get_proxy_config_decrypted(proxy)
    
    # Verwende gespeichertes 2FA-Passwort falls vorhanden und kein Passwort übergeben wurde
    final_password = login.password
    if not final_password and db_account.two_factor_password:
        try:
            final_password = decrypt_string(db_account.two_factor_password)
        except Exception as e:
            logger.warning(f"Fehler beim Entschlüsseln des 2FA-Passworts für Account {account_id}: {str(e)}")
    
    # API ID/Hash können None sein, werden in add_account aus Session oder Umgebungsvariablen geladen
    # phone_code_hash wird von Telethon automatisch in der Session gespeichert, aber wir können ihn auch explizit übergeben
    result = await account_manager.add_account(
        account_id=account_id,
        api_id=db_account.api_id,
        api_hash=db_account.api_hash,
        session_name=db_account.session_name,
        phone_number=db_account.phone_number,
        code=login.code,
        password=final_password,  # Verwende gespeichertes 2FA-Passwort falls vorhanden
        session_file_path=db_account.session_file_path,
        proxy_config=proxy_config,
        phone_code_hash=login.phone_code_hash  # Falls explizit übergeben
    )
    
    if result.get("status") == "connected":
        db_account.last_used = datetime.utcnow()
        db.commit()
    
    return result

@app.get("/api/accounts", response_model=List[dict])
async def list_accounts(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listet alle Accounts des aktuellen Benutzers"""
    try:
        accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
        result = []
        
        for acc in accounts:
            try:
                if acc.account_type == "bot":
                    info = await bot_manager.get_bot_info(acc.id)
                    result.append({
                        "id": acc.id,
                        "name": acc.name,
                        "account_type": "bot",
                        "is_active": acc.is_active,
                        "created_at": acc.created_at.isoformat() if acc.created_at else None,
                        "last_used": acc.last_used.isoformat() if acc.last_used else None,
                        "connected": info is not None,
                        "info": info
                    })
                else:
                    info = await account_manager.get_account_info(acc.id)
                    proxy_info = None
                    if acc.proxy_id:
                        proxy = db.query(Proxy).filter(Proxy.id == acc.proxy_id).first()
                        if proxy:
                            proxy_info = {
                                "id": proxy.id,
                                "name": proxy.name,
                                "host": proxy.host,
                                "port": proxy.port,
                                "proxy_type": proxy.proxy_type
                            }
                    
                    result.append({
                        "id": acc.id,
                        "name": acc.name,
                        "account_type": "user",
                        "phone_number": acc.phone_number,
                        "is_active": acc.is_active,
                        "proxy_id": acc.proxy_id,
                        "proxy": proxy_info,
                        "created_at": acc.created_at.isoformat() if acc.created_at else None,
                        "last_used": acc.last_used.isoformat() if acc.last_used else None,
                        "connected": info is not None,
                        "info": info
                    })
            except Exception as e:
                logger.error(f"Fehler beim Verarbeiten von Account {acc.id}: {e}", exc_info=True)
                # Füge Account trotzdem hinzu, aber ohne Info
                result.append({
                    "id": acc.id,
                    "name": acc.name,
                    "account_type": acc.account_type or "user",
                    "is_active": acc.is_active,
                    "created_at": acc.created_at.isoformat() if acc.created_at else None,
                    "last_used": acc.last_used.isoformat() if acc.last_used else None,
                    "connected": False,
                    "error": str(e)
                })
        
        return result
    except Exception as e:
        logger.error(f"Fehler in list_accounts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Accounts: {str(e)}")

@app.get("/api/accounts/{account_id}", response_model=dict)
async def get_account(account_id: int, db: Session = Depends(get_db)):
    """Gibt Account-Details zurück"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    info = await account_manager.get_account_info(account_id)
    
    return {
        "id": account.id,
        "name": account.name,
        "phone_number": account.phone_number,
        "is_active": account.is_active,
        "connected": info is not None,
        "info": info
    }

@app.delete("/api/accounts/{account_id}")
async def delete_account(account_id: int, db: Session = Depends(get_db)):
    """Löscht einen Account"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.account_type == "bot":
        await bot_manager.remove_bot(account_id)
    else:
        await account_manager.remove_account(account_id)
    
    db.delete(account)
    db.commit()
    
    return {"success": True}

@app.get("/api/accounts/{account_id}/dialogs", response_model=List[dict])
async def get_account_dialogs(account_id: int):
    """Ruft alle Dialoge eines Accounts ab"""
    dialogs = await account_manager.get_dialogs(account_id)
    return dialogs

@app.get("/api/accounts/{account_id}/dialogs/{dialog_id}/messages", response_model=dict)
async def get_dialog_messages(
    account_id: int,
    dialog_id: str,
    limit: int = Query(100, ge=1, le=1000)
):
    """Ruft Nachrichten aus einem Dialog ab"""
    result = await account_manager.get_group_messages(
        account_id=account_id,
        group_entity=dialog_id,
        limit=limit,
        auto_join=False
    )
    
    if result.get("error"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error")
        )
    
    return result

@app.post("/api/accounts/{account_id}/dialogs/{dialog_id}/send", response_model=dict)
async def send_dialog_message(
    account_id: int,
    dialog_id: str,
    request: SendDialogMessageRequest
):
    """Sendet eine Nachricht an einen Dialog"""
    result = await account_manager.send_message(
        account_id=account_id,
        entity=dialog_id,
        message=request.message,
        delay=0
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Fehler beim Senden der Nachricht")
        )
    
    return result

@app.post("/api/upload/session", response_model=dict)
@limiter.limit("10/hour")
async def upload_session_file(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lädt eine Session-Datei hoch"""
    try:
        # Validiere Dateityp
        if not file.filename or not file.filename.endswith('.session'):
            raise HTTPException(status_code=400, detail="Nur .session Dateien sind erlaubt")
        
        # Validiere Dateigröße (max 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
        file_content = await file.read()
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"Datei zu groß. Maximum: {MAX_FILE_SIZE / 1024 / 1024}MB")
        
        # Speichere Datei
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Validiere Session-Datei
        is_valid, error = validate_session_file(str(file_path))
        if not is_valid:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail=error or "Ungültige Session-Datei")
        
        return {
            "success": True,
            "file_path": str(file_path),
            "filename": file.filename,
            "size": file_path.stat().st_size
        }
    
    except HTTPException:
        raise
    except Exception as e:
        # Logge den vollständigen Fehler für Debugging, aber sende generische Meldung an Client
        logger.error(f"Fehler beim Hochladen der Session-Datei: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Fehler beim Hochladen der Datei. Bitte versuchen Sie es erneut.")

@app.post("/api/upload/tdata", response_model=dict)
@limiter.limit("5/hour")
async def upload_tdata(
    request: Request,
    file: Optional[UploadFile] = File(None),  # ZIP-Datei
    files: Optional[List[UploadFile]] = File(None, alias="files"),  # Einzelne Dateien
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Lädt tdata-Ordner hoch (als ZIP oder einzelne Dateien)"""
    try:
        # Erstelle tdata-Ordner
        tdata_id = f"tdata_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        tdata_dir = UPLOAD_DIR / tdata_id
        tdata_dir.mkdir(exist_ok=True)
        
        saved_files = []
        
        # Prüfe ob ZIP-Datei hochgeladen wurde
        if file and file.filename and file.filename.endswith('.zip'):
            import zipfile
            # Speichere ZIP-Datei temporär
            zip_path = tdata_dir / file.filename
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Entpacke ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tdata_dir)
            
            # Prüfe ob tdata-Ordner im ZIP enthalten ist
            tdata_folder = find_tdata_folder(str(tdata_dir))
            if tdata_folder:
                # Verschiebe tdata-Ordner-Inhalt in den Hauptordner
                tdata_source = Path(tdata_folder)
                for item in tdata_source.iterdir():
                    shutil.move(str(item), str(tdata_dir / item.name))
                # Lösche leeren tdata-Ordner
                if tdata_source.parent != tdata_dir:
                    shutil.rmtree(tdata_source, ignore_errors=True)
            
            # Lösche ZIP-Datei
            zip_path.unlink()
            
            # Liste alle Dateien im tdata-Ordner
            for item in tdata_dir.iterdir():
                if item.is_file():
                    saved_files.append(item.name)
        elif files:
            # Einzelne Dateien hochladen
            for file in files:
                file_path = tdata_dir / file.filename
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                saved_files.append(file.filename)
        else:
            raise HTTPException(status_code=400, detail="Bitte ZIP-Datei oder einzelne Dateien hochladen")
        
        # Prüfe ob tdata-Ordner korrekt strukturiert ist (sollte mindestens 3 Dateien enthalten)
        if len(saved_files) < 3:
            logger.warning(f"tdata-Ordner enthält nur {len(saved_files)} Dateien. Normalerweise sollten es mindestens 3 sein.")
        
        return {
            "success": True,
            "tdata_path": str(tdata_dir),
            "files": saved_files,
            "file_count": len(saved_files),
            "message": f"✅ tdata erfolgreich hochgeladen ({len(saved_files)} Dateien). Du kannst jetzt einen Account erstellen."
        }
    
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Ungültige ZIP-Datei")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Hochladen von tdata: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fehler beim Hochladen der Dateien: {str(e)}")

@app.post("/api/accounts/from-tdata", response_model=dict)
async def create_account_from_tdata(
    name: str = Form(...),
    api_id: Optional[str] = Form(None),
    api_hash: Optional[str] = Form(None),
    tdata_path: str = Form(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Erstellt einen Account aus einem tdata-Ordner
    
    Hinweis: tdata wird gespeichert, aber für die Verwendung mit Telethon muss der Account
    manuell über Telegram Desktop eingeloggt werden, oder die tdata muss zu einer Session konvertiert werden.
    """
    try:
        # Prüfe Account-Limit
        account_count = db.query(Account).filter(Account.user_id == current_user.id).count()
        if not check_account_limit(current_user, account_count):
            raise HTTPException(
                status_code=403,
                detail=f"Account-Limit erreicht. Maximal {current_user.subscription.max_accounts if current_user.subscription else 1} Accounts erlaubt."
            )
        
        # Validiere tdata-Ordner
        tdata_dir = Path(tdata_path)
        if not tdata_dir.exists() or not tdata_dir.is_dir():
            raise HTTPException(status_code=404, detail="tdata-Ordner nicht gefunden")
        
        # Prüfe ob tdata-Ordner Dateien enthält
        tdata_files = [f for f in tdata_dir.iterdir() if f.is_file()]
        if len(tdata_files) < 3:
            raise HTTPException(
                status_code=400, 
                detail=f"tdata-Ordner scheint unvollständig zu sein. Erwartet: mindestens 3 Dateien, gefunden: {len(tdata_files)}"
            )
        
        # Generiere Session-Name (wird später für Konvertierung verwendet)
        session_name = f"{name.lower().replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d')}"
        
        # Versuche API Credentials aus Umgebungsvariablen
        final_api_id = api_id or os.getenv('TELEGRAM_API_ID')
        final_api_hash = api_hash or os.getenv('TELEGRAM_API_HASH')
        
        # Erstelle Account mit tdata-Pfad
        db_account = Account(
            user_id=current_user.id,
            name=name,
            account_type="user",
            api_id=final_api_id,
            api_hash=final_api_hash,
            session_name=session_name,  # Für spätere Konvertierung
            tdata_path=tdata_path
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        return {
            "success": True,
            "account_id": db_account.id,
            "tdata_path": tdata_path,
            "file_count": len(tdata_files),
            "message": "✅ Account aus tdata erstellt. Hinweis: Für die Verwendung mit diesem Tool muss die tdata zu einer Telethon-Session konvertiert werden. Siehe Anleitung im Modal.",
            "status": "tdata_imported"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Accounts aus tdata: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen des Accounts: {str(e)}")

@app.post("/api/accounts/from-complete-package", response_model=dict)
async def create_account_from_complete_package(
    name: str = Form(...),
    session_file: Optional[UploadFile] = File(None),
    tdata_zip: Optional[UploadFile] = File(None),
    json_file: Optional[UploadFile] = File(None),
    two_factor_password: Optional[str] = Form(None),
    api_id: Optional[str] = Form(None),
    api_hash: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Erstellt einen Account aus einem kompletten Paket (TDATA + SESSION + JSON + 2FA)
    
    Unterstützt:
    - TDATA (als ZIP oder einzelne Dateien)
    - SESSION (.session Datei)
    - JSON (Metadaten-Datei)
    - 2FA-Passwort
    """
    try:
        # Prüfe Account-Limit
        account_count = db.query(Account).filter(Account.user_id == current_user.id).count()
        if not check_account_limit(current_user, account_count):
            raise HTTPException(
                status_code=403,
                detail=f"Account-Limit erreicht. Maximal {current_user.subscription.max_accounts if current_user.subscription else 1} Accounts erlaubt."
            )
        
        # Erstelle Upload-Ordner für dieses Paket
        package_id = f"package_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        package_dir = UPLOAD_DIR / package_id
        package_dir.mkdir(exist_ok=True)
        
        session_file_path = None
        tdata_path = None
        json_metadata_path = None
        encrypted_2fa = None
        
        # Verarbeite Session-Datei
        if session_file:
            session_path = package_dir / session_file.filename
            with open(session_path, "wb") as buffer:
                shutil.copyfileobj(session_file.file, buffer)
            
            # Validiere Session
            is_valid, error = validate_session_file(str(session_path))
            if not is_valid:
                raise HTTPException(status_code=400, detail=error or "Ungültige Session-Datei")
            
            # Kopiere Session zu sessions/ Verzeichnis
            session_name = f"{name.lower().replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d')}"
            copied_path = copy_session_file(str(session_path), session_name, str(SESSIONS_DIR))
            if copied_path:
                session_file_path = copied_path
        
        # Verarbeite TDATA (ZIP)
        if tdata_zip and tdata_zip.filename.endswith('.zip'):
            import zipfile
            zip_path = package_dir / tdata_zip.filename
            with open(zip_path, "wb") as buffer:
                shutil.copyfileobj(tdata_zip.file, buffer)
            
            # Entpacke ZIP
            tdata_dir = package_dir / "tdata"
            tdata_dir.mkdir(exist_ok=True)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tdata_dir)
            
            # Prüfe ob tdata-Ordner im ZIP enthalten ist
            found_tdata = find_tdata_folder(str(tdata_dir))
            if found_tdata:
                tdata_path = found_tdata
            else:
                # Prüfe ob Dateien direkt im tdata_dir sind
                tdata_files = [f for f in tdata_dir.iterdir() if f.is_file()]
                if len(tdata_files) >= 3:
                    tdata_path = str(tdata_dir)
        
        # Verarbeite JSON-Datei
        if json_file:
            json_path = package_dir / json_file.filename
            with open(json_path, "wb") as buffer:
                shutil.copyfileobj(json_file.file, buffer)
            
            # Validiere JSON
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    # Extrahiere Account-Informationen aus JSON
                    if not name or name == json_file.filename:
                        # Versuche Namen aus JSON zu extrahieren
                        name = json_data.get('phone') or json_data.get('name') or json_data.get('username') or name
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Ungültige JSON-Datei")
            
            json_metadata_path = str(json_path)
        
        # Verschlüssele 2FA-Passwort falls vorhanden
        if two_factor_password:
            encrypted_2fa = encrypt_string(two_factor_password)
        
        # Versuche API Credentials zu bestimmen
        final_api_id = api_id or os.getenv('TELEGRAM_API_ID')
        final_api_hash = api_hash or os.getenv('TELEGRAM_API_HASH')
        
        # Extrahiere API Credentials aus JSON falls vorhanden
        if json_metadata_path and not final_api_id:
            try:
                with open(json_metadata_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    final_api_id = json_data.get('api_id') or final_api_id
                    final_api_hash = json_data.get('api_hash') or final_api_hash
            except:
                pass
        
        # Generiere Session-Name
        session_name = f"{name.lower().replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d')}"
        
        # Extrahiere Telefonnummer aus JSON falls vorhanden
        phone_number = None
        if json_metadata_path:
            try:
                with open(json_metadata_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                    phone_number = json_data.get('phone') or json_data.get('phone_number')
            except:
                pass
        
        # Erstelle Account
        db_account = Account(
            user_id=current_user.id,
            name=name,
            account_type="user",
            api_id=final_api_id,
            api_hash=final_api_hash,
            phone_number=phone_number,
            session_name=session_name,
            session_file_path=session_file_path,
            tdata_path=tdata_path,
            json_metadata_path=json_metadata_path,
            two_factor_password=encrypted_2fa
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        # Versuche automatische Verbindung wenn Session vorhanden
        connection_status = None
        if session_file_path:
            try:
                proxy_config = None
                if db_account.proxy_id:
                    proxy = db.query(Proxy).filter(Proxy.id == db_account.proxy_id).first()
                    if proxy:
                        proxy_config = get_proxy_config_decrypted(proxy)
                
                result = await account_manager.add_account(
                    account_id=db_account.id,
                    api_id=final_api_id,
                    api_hash=final_api_hash,
                    session_name=session_name,
                    session_file_path=session_file_path,
                    phone_number=phone_number,
                    password=two_factor_password,  # 2FA-Passwort für Login
                    proxy_config=proxy_config
                )
                connection_status = result.get('status')
            except Exception as e:
                logger.warning(f"Automatische Verbindung fehlgeschlagen: {str(e)}")
                connection_status = "error"
        
        return {
            "success": True,
            "account_id": db_account.id,
            "session_file_path": session_file_path,
            "tdata_path": tdata_path,
            "json_metadata_path": json_metadata_path,
            "has_2fa": bool(encrypted_2fa),
            "connection_status": connection_status,
            "message": "✅ Account aus komplettem Paket erstellt!",
            "status": "imported"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Accounts aus komplettem Paket: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen des Accounts: {str(e)}")

@app.post("/api/accounts/from-session", response_model=dict)
async def create_account_from_session(
    name: str = Form(...),
    api_id: Optional[str] = Form(None),
    api_hash: Optional[str] = Form(None),
    session_file_path: str = Form(...),
    db: Session = Depends(get_db)
):
    """Erstellt einen Account aus einer hochgeladenen Session-Datei
    
    API ID und Hash sind optional - werden aus Session-Datei oder Umgebungsvariablen geladen.
    """
    try:
        # Validiere Session-Datei
        if not os.path.exists(session_file_path):
            raise HTTPException(status_code=404, detail="Session-Datei nicht gefunden")
        
        is_valid, error = validate_session_file(session_file_path)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error or "Ungültige Session-Datei")
        
        # Generiere Session-Name
        session_name = f"{name.lower().replace(' ', '_')}_{datetime.utcnow().strftime('%Y%m%d')}"
        
        # Kopiere Session-Datei zu sessions/ Verzeichnis
        copied_path = copy_session_file(session_file_path, session_name, str(SESSIONS_DIR))
        if not copied_path:
            raise HTTPException(status_code=500, detail="Fehler beim Kopieren der Session-Datei")
        
        # Versuche API Credentials aus Session zu extrahieren oder aus Umgebungsvariablen
        final_api_id = api_id or os.getenv('TELEGRAM_API_ID')
        final_api_hash = api_hash or os.getenv('TELEGRAM_API_HASH')
        
        # Versuche aus Session-Datei zu extrahieren (wird in add_account gemacht)
        # Für jetzt: Erstelle Account auch ohne API Credentials
        # Die werden beim Verbinden aus Session oder Umgebungsvariablen geladen
        
        # Erstelle Account
        db_account = Account(
            name=name,
            account_type="user",
            api_id=final_api_id,  # Kann None sein, wird beim Verbinden geladen
            api_hash=final_api_hash,  # Kann None sein, wird beim Verbinden geladen
            session_name=session_name,
            session_file_path=copied_path  # Verwende kopierten Pfad
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        # Lade Proxy falls vorhanden
        proxy_config = None
        if db_account.proxy_id:
            proxy = db.query(Proxy).filter(Proxy.id == db_account.proxy_id).first()
            if proxy:
                proxy_config = {
                    "proxy_type": proxy.proxy_type,
                    "host": proxy.host,
                    "port": proxy.port,
                    "username": proxy.username,
                    "password": proxy.password,
                    "secret": proxy.secret
                }
        
        # Versuche Verbindung (verwende kopierten Pfad)
        # API ID/Hash können None sein, werden in add_account aus Session oder Umgebungsvariablen geladen
        result = await account_manager.add_account(
            account_id=db_account.id,
            api_id=final_api_id,
            api_hash=final_api_hash,
            session_name=session_name,
            session_file_path=copied_path,
            proxy_config=proxy_config
        )
        
        return {"account_id": db_account.id, **result}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Accounts aus Session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Fehler beim Erstellen des Accounts. Bitte versuchen Sie es erneut.")

# Group Endpoints
@app.post("/api/groups", response_model=dict)
async def create_group(
    group: GroupCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Erstellt eine neue Gruppe"""
    # Wenn chat_id nicht gegeben, versuche durch name/username zu finden
    chat_id = group.chat_id
    if not chat_id:
        # Versuche durch Account zu finden
        if group.username:
            chat_id = group.username
        else:
            raise HTTPException(status_code=400, detail="chat_id oder username erforderlich")
    
    # Prüfe Gruppen-Limit
    group_count = db.query(Group).filter(Group.user_id == current_user.id).count()
    if not check_group_limit(current_user, group_count):
        raise HTTPException(
            status_code=403,
            detail=f"Gruppen-Limit erreicht. Maximal {current_user.subscription.max_groups if current_user.subscription else 5} Gruppen erlaubt."
        )
    
    db_group = Group(
        user_id=current_user.id,
        name=group.name,
        chat_id=chat_id,
        chat_type=group.chat_type,
        username=group.username
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    
    return {
        "id": db_group.id,
        "name": db_group.name,
        "chat_id": db_group.chat_id,
        "chat_type": db_group.chat_type,
        "username": db_group.username
    }

@app.get("/api/accounts/{account_id}/groups", response_model=List[dict])
async def get_account_groups(
    account_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listet alle Gruppen eines Accounts (aus Dialogen)"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Account gehört nicht zum aktuellen Benutzer")
    
    # Prüfe ob Account verbunden ist
    account_info = await account_manager.get_account_info(account_id)
    if not account_info:
        raise HTTPException(status_code=400, detail="Account nicht verbunden. Bitte zuerst verbinden.")
    
    # Lade Dialoge des Accounts
    try:
        dialogs = await account_manager.get_dialogs(account_id)
        # Filtere nur Gruppen/Kanäle (keine privaten Chats)
        groups = []
        for dialog in dialogs:
            if dialog.get("type") in ["group", "channel", "supergroup"]:
                groups.append({
                    "id": dialog.get("id"),
                    "name": dialog.get("name"),
                    "chat_id": str(dialog.get("id")),
                    "chat_type": dialog.get("type"),
                    "username": dialog.get("username"),
                    "member_count": dialog.get("member_count"),
                    "is_public": dialog.get("username") is not None
                })
        return groups
    except Exception as e:
        logger.error(f"Fehler beim Laden der Gruppen für Account {account_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Gruppen: {str(e)}")

@app.get("/api/groups", response_model=List[dict])
async def list_groups(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Listet alle Gruppen des aktuellen Benutzers"""
    try:
        groups = db.query(Group).filter(
            Group.user_id == current_user.id,
            Group.is_active == True
        ).all()
        result = []
        for g in groups:
            try:
                result.append({
                    "id": g.id,
                    "name": g.name,
                    "chat_id": g.chat_id,
                    "chat_type": g.chat_type,
                    "username": g.username,
                    "is_active": g.is_active,
                    "member_count": g.member_count if hasattr(g, 'member_count') else None,
                    "is_public": g.is_public if hasattr(g, 'is_public') else None,
                    "bot_invite_allowed": g.bot_invite_allowed if hasattr(g, 'bot_invite_allowed') else None,
                    "description": g.description if hasattr(g, 'description') else None,
                    "invite_link": g.invite_link if hasattr(g, 'invite_link') else None,
                    "last_checked": g.last_checked.isoformat() if hasattr(g, 'last_checked') and g.last_checked else None,
                    "created_at": g.created_at.isoformat() if g.created_at else None
                })
            except Exception as e:
                logger.error(f"Fehler beim Verarbeiten von Gruppe {g.id}: {e}", exc_info=True)
                # Füge Gruppe trotzdem hinzu, aber ohne optionale Felder
                result.append({
                    "id": g.id,
                    "name": g.name,
                    "chat_id": g.chat_id,
                    "chat_type": g.chat_type,
                    "username": g.username,
                    "is_active": g.is_active,
                    "created_at": g.created_at.isoformat() if g.created_at else None
                })
        return result
    except Exception as e:
        logger.error(f"Fehler in list_groups: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Gruppen: {str(e)}")

@app.delete("/api/groups/{group_id}")
async def delete_group(group_id: int, db: Session = Depends(get_db)):
    """Löscht eine Gruppe"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Gruppe nicht gefunden")
    
    group.is_active = False
    db.commit()
    
    return {"success": True}

@app.post("/api/accounts/bulk-bots", response_model=dict)
async def bulk_create_bots(bulk: BulkBotCreate, db: Session = Depends(get_db)):
    """Erstellt mehrere Bot-Accounts auf einmal"""
    results = {
        "total": len(bulk.bots),
        "success": 0,
        "failed": 0,
        "errors": []
    }
    
    for bot_data in bulk.bots:
        try:
            if not bot_data.get("name") or not bot_data.get("bot_token"):
                results["failed"] += 1
                results["errors"].append({
                    "bot": bot_data.get("name", "Unbekannt"),
                    "error": "Name und bot_token erforderlich"
                })
                continue
            
            db_account = Account(
                name=bot_data["name"],
                account_type="bot",
                bot_token=bot_data["bot_token"]
            )
            db.add(db_account)
            db.commit()
            db.refresh(db_account)
            
            # Verbinde Bot
            result = await bot_manager.add_bot(
                bot_id=db_account.id,
                bot_token=bot_data["bot_token"]
            )
            
            if result.get("status") == "connected":
                results["success"] += 1
            else:
                results["failed"] += 1
                results["errors"].append({
                    "bot": bot_data["name"],
                    "error": result.get("error", "Unbekannter Fehler")
                })
        
        except Exception as e:
            logger.error(f"Fehler beim Erstellen von Bot '{bot_data.get('name', 'Unbekannt')}': {str(e)}", exc_info=True)
            results["failed"] += 1
            results["errors"].append({
                "bot": bot_data.get("name", "Unbekannt"),
                "error": "Fehler beim Erstellen des Bots"
            })
    
    return results

class GroupSearchRequest(BaseModel):
    account_id: int
    group_names: List[str]

class ScrapeGroupMembersRequest(BaseModel):
    account_id: int
    group_id: Optional[int] = None  # Optional, wenn group_entity gesetzt ist
    group_entity: Optional[str] = None  # Chat-ID oder Username (wird bevorzugt wenn gesetzt)
    limit: int = 10000

class InviteUsersRequest(BaseModel):
    account_id: int
    group_id: Optional[int] = None  # Optional, wenn group_entity gesetzt ist
    group_entity: Optional[str] = None  # Chat-ID oder Username (wird bevorzugt wenn gesetzt)
    user_ids: Optional[List[str]] = None  # Optional, wenn usernames gesetzt ist
    usernames: Optional[List[str]] = None  # Liste von Usernamen (mit oder ohne @)
    delay: float = 2.0
    invite_method: str = "admin"  # "admin" oder "invite_link"

class InviteFromScrapedRequest(BaseModel):
    account_id: int
    group_id: int
    scraped_user_ids: List[int]
    delay: float = 2.0

class ForwardMessageRequest(BaseModel):
    account_id: int
    source_group_id: int
    message_ids: List[int]
    target_group_ids: List[int]
    delay: float = 2.0

class ForwardMessageByIdRequest(BaseModel):
    account_id: int
    source_group_entity: Optional[str] = None  # Chat-ID, Username oder Einladungslink
    source_group_id: Optional[int] = None  # Optional, wenn source_group_entity gesetzt ist
    message_id: str  # Message-ID als String (kann sehr groß sein)
    target_group_ids: List[int]
    delay: float = 2.0

class GetGroupMessagesRequest(BaseModel):
    account_id: int
    group_id: Optional[int] = None  # Optional, wenn manual_group_entity gesetzt ist
    manual_group_entity: Optional[str] = None  # Manuelle Eingabe: Chat-ID, Username oder Einladungslink
    limit: int = 100

class WarmingConfigCreate(BaseModel):
    account_id: int
    read_messages_per_day: int = 20
    scroll_dialogs_per_day: int = 10
    reactions_per_day: int = 5
    small_messages_per_day: int = 3
    start_time: str = "09:00"
    end_time: str = "22:00"
    min_delay: float = 30.0
    max_delay: float = 300.0
    max_warming_days: int = 14

class WarmingConfigUpdate(BaseModel):
    is_active: Optional[bool] = None
    read_messages_per_day: Optional[int] = None
    scroll_dialogs_per_day: Optional[int] = None
    reactions_per_day: Optional[int] = None
    small_messages_per_day: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    min_delay: Optional[float] = None
    max_delay: Optional[float] = None
    max_warming_days: Optional[int] = None

class MessageTemplateCreate(BaseModel):
    name: str
    message: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class SendDialogMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4096)

class CreateTemplateFromMessageRequest(BaseModel):
    account_id: int
    source_group: str  # Chat-ID oder Username
    message_id: str  # Message ID als String (kann sehr groß sein)
    template_name: str
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class MessageTemplateUpdate(BaseModel):
    name: Optional[str] = None
    message: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None

class ProxyCreate(BaseModel):
    name: str
    proxy_type: str  # 'socks5', 'http', 'https', 'mtproto'
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    secret: Optional[str] = None  # Für MTProto
    country: Optional[str] = None
    notes: Optional[str] = None

class ProxyUpdate(BaseModel):
    name: Optional[str] = None
    proxy_type: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    secret: Optional[str] = None
    country: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    notes: Optional[str] = None

class BulkProxyCreate(BaseModel):
    proxies: List[dict]  # Liste von Proxy-Dicts

class CreateBotViaAccountRequest(BaseModel):
    account_id: int
    bot_name: str
    bot_username: str

class BulkCreateBotsViaAccountRequest(BaseModel):
    account_id: int
    count: int = Field(default=10, ge=1, le=50)  # Anzahl Bots (1-50)
    name_prefix: str = "Group Bot"  # Präfix für Bot-Namen
    username_prefix: str = "group_bot"  # Präfix für Bot-Usernames
    delay_between_bots: float = Field(default=3.0, ge=1.0, le=60.0)  # Delay zwischen Bot-Erstellungen

class CheckGroupRequest(BaseModel):
    account_id: int
    group_entity: str  # Chat-ID, Username oder Entity

class CheckBotCanBeAddedRequest(BaseModel):
    account_id: int
    group_entity: str
    bot_username: Optional[str] = None
    bot_id: Optional[int] = None

class AddAccountToGroupsRequest(BaseModel):
    account_id: int
    group_ids: List[int]  # Liste von Group-IDs aus der Datenbank
    delay: float = 3.0  # Verzögerung zwischen Gruppen

# Auth Models
class UserRegister(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    username: str  # Kann Email oder Username sein
    password: str

class SubscriptionUpdate(BaseModel):
    plan_type: str  # 'free_trial', 'basic', 'pro', 'enterprise'
    duration_days: int = 30  # Dauer in Tagen

class PurchaseSubscriptionRequest(BaseModel):
    plan_type: str  # 'basic', 'pro', 'enterprise'
    payment_method: str = "stripe"  # 'stripe', 'paypal', etc.
    payment_token: Optional[str] = None  # Payment Token von Stripe/PayPal

# Phone Provider Models
class BuyPhoneNumberRequest(BaseModel):
    provider: str = "5sim"  # '5sim', 'sms-activate', 'sms-manager', 'getsmscode', 'onlinesim'
    country: str = "germany"
    service: str = "telegram"
    operator: Optional[str] = None

class AutoCreateAccountsRequest(BaseModel):
    provider: str = "5sim"  # Provider-Name
    country: str = "germany"
    service: str = "telegram"
    max_accounts: int = 5  # Maximale Anzahl zu erstellender Accounts
    min_balance: Optional[float] = None  # Mindest-Guthaben (optional)

# Auth Endpoints
@app.post("/api/auth/register", response_model=dict)
@limiter.limit("3/hour")
async def register_user(request: Request, user_data: UserRegister, db: Session = Depends(get_db)):
    """Registriert einen neuen Benutzer mit Free Trial"""
    # Prüfe ob Email oder Username bereits existiert
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email bereits registriert")
    
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username bereits vergeben")
    
    # Erstelle Benutzer
    password_hash = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=password_hash,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Erstelle Free Trial Abonnement
    trial_subscription = Subscription(
        user_id=new_user.id,
        plan_type="free_trial",
        status="active",
        started_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=7),  # 7 Tage Free Trial
        max_accounts=2,  # 2 Accounts im Free Trial
        max_groups=5,
        max_messages_per_day=10,
        features=json.dumps({"auto_number_purchase": False})
    )
    db.add(trial_subscription)
    db.commit()
    
    # Erstelle Access Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(new_user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "success": True,
        "user_id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "is_admin": new_user.is_admin,
        "access_token": access_token,
        "token_type": "bearer",
        "subscription": {
            "plan_type": trial_subscription.plan_type,
            "expires_at": trial_subscription.expires_at.isoformat() if trial_subscription.expires_at else None
        }
    }

@app.post("/api/auth/login", response_model=dict)
@limiter.limit("5/minute")
async def login_user(request: Request, user_data: UserLogin, db: Session = Depends(get_db)):
    """Loggt einen Benutzer ein"""
    # Suche nach Email oder Username
    user = db.query(User).filter(
        (User.email == user_data.username) | (User.username == user_data.username)
    ).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    
    if not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Ungültige Anmeldedaten")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account deaktiviert")
    
    # Aktualisiere last_login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Erstelle Access Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    subscription_info = None
    if user.subscription:
        subscription_info = {
            "plan_type": user.subscription.plan_type,
            "status": user.subscription.status,
            "expires_at": user.subscription.expires_at.isoformat() if user.subscription.expires_at else None,
            "max_accounts": user.subscription.max_accounts,
            "max_groups": user.subscription.max_groups,
            "max_messages_per_day": user.subscription.max_messages_per_day
        }
    
    return {
        "success": True,
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
        "access_token": access_token,
        "token_type": "bearer",
        "subscription": subscription_info
    }

@app.get("/api/auth/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Gibt Informationen über den aktuellen Benutzer zurück"""
    subscription_info = None
    if current_user.subscription:
        subscription_info = {
            "plan_type": current_user.subscription.plan_type,
            "status": current_user.subscription.status,
            "is_active": current_user.subscription.is_active(),
            "expires_at": current_user.subscription.expires_at.isoformat() if current_user.subscription.expires_at else None,
            "max_accounts": current_user.subscription.max_accounts,
            "max_groups": current_user.subscription.max_groups,
            "max_messages_per_day": current_user.subscription.max_messages_per_day,
            "features": json.loads(current_user.subscription.features) if current_user.subscription.features else {}
        }
    
    # Zähle Accounts und Gruppen
    account_count = db.query(Account).filter(Account.user_id == current_user.id).count()
    group_count = db.query(Group).filter(Group.user_id == current_user.id).count()
    
    return {
        "user_id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "is_admin": current_user.is_admin,
        "subscription": subscription_info,
        "stats": {
            "account_count": account_count,
            "group_count": group_count
        }
    }

@app.post("/api/phone/buy-number", response_model=dict)
async def buy_phone_number(
    request: BuyPhoneNumberRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Kauft eine Telefonnummer über 5sim.net oder ähnliche Anbieter
    und erstellt automatisch einen Telegram-Account
    """
    # Prüfe ob Feature verfügbar ist
    if not check_subscription(current_user, "auto_number_purchase"):
        raise HTTPException(
            status_code=403,
            detail="Automatischer Nummernkauf ist in deinem Paket nicht enthalten. Bitte upgraden."
        )
    
    # Prüfe Account-Limit
    account_count = db.query(Account).filter(Account.user_id == current_user.id).count()
    if not check_account_limit(current_user, account_count):
        raise HTTPException(
            status_code=403,
            detail=f"Account-Limit erreicht. Maximal {current_user.subscription.max_accounts if current_user.subscription else 1} Accounts erlaubt."
        )
    
    # Lade API Key aus Umgebungsvariablen oder SystemSettings
    provider_api_key = None
    
    # Prüfe zuerst SystemSettings, dann Umgebungsvariablen
    if request.provider == "5sim":
        setting = db.query(SystemSettings).filter(SystemSettings.key == "fivesim_api_key").first()
        provider_api_key = setting.value if setting else os.getenv("FIVESIM_API_KEY")
        if not provider_api_key:
            raise HTTPException(status_code=500, detail="5sim API Key nicht konfiguriert")
        provider = FiveSimProvider(provider_api_key)
    elif request.provider == "sms-activate":
        setting = db.query(SystemSettings).filter(SystemSettings.key == "sms_activate_api_key").first()
        provider_api_key = setting.value if setting else os.getenv("SMS_ACTIVATE_API_KEY")
        if not provider_api_key:
            raise HTTPException(status_code=500, detail="SMS-Activate API Key nicht konfiguriert")
        provider = SMSActivateProvider(provider_api_key)
    elif request.provider == "sms-manager":
        setting = db.query(SystemSettings).filter(SystemSettings.key == "sms_manager_api_key").first()
        provider_api_key = setting.value if setting else os.getenv("SMS_MANAGER_API_KEY")
        if not provider_api_key:
            raise HTTPException(status_code=500, detail="SMS-Manager API Key nicht konfiguriert")
        provider = SMSManagerProvider(provider_api_key)
    elif request.provider == "getsmscode":
        setting = db.query(SystemSettings).filter(SystemSettings.key == "getsmscode_api_key").first()
        provider_api_key = setting.value if setting else os.getenv("GETSMSCODE_API_KEY")
        if not provider_api_key:
            raise HTTPException(status_code=500, detail="GetSMSCode API Key nicht konfiguriert")
        provider = GetSMSCodeProvider(provider_api_key)
    elif request.provider == "onlinesim":
        setting = db.query(SystemSettings).filter(SystemSettings.key == "onlinesim_api_key").first()
        provider_api_key = setting.value if setting else os.getenv("ONLINESIM_API_KEY")
        if not provider_api_key:
            raise HTTPException(status_code=500, detail="OnlineSim API Key nicht konfiguriert")
        provider = OnlineSimProvider(provider_api_key)
    else:
        raise HTTPException(status_code=400, detail=f"Unbekannter Provider: {request.provider}. Verfügbar: 5sim, sms-activate, sms-manager, getsmscode, onlinesim")
    
    # Kaufe Nummer
    buy_result = await provider.buy_number(
        country=request.country,
        service=request.service,
        operator=request.operator
    )
    
    if not buy_result.get("success"):
        error_msg = buy_result.get('error', 'Unbekannter Fehler')
        is_retryable = buy_result.get('retryable', False)
        
        # Verbesserte Fehlermeldung
        if "TRY_AGAIN_LATER" in error_msg.upper():
            error_msg = f"Rate-Limit erreicht. OnlineSim.io hat temporär keine Nummern verfügbar. Bitte in ein paar Minuten erneut versuchen. (Original: {error_msg})"
        elif "NO_NUMBERS" in error_msg.upper():
            error_msg = f"Keine Nummern verfügbar für {request.country} bei OnlineSim.io. Bitte später erneut versuchen oder ein anderes Land wählen. (Original: {error_msg})"
        elif "NO_BALANCE" in error_msg.upper():
            error_msg = f"Nicht genug Guthaben bei OnlineSim.io. Bitte Guthaben aufladen. (Original: {error_msg})"
        
        status_code = 429 if is_retryable else 400
        raise HTTPException(
            status_code=status_code,
            detail=f"Fehler beim Kauf der Nummer: {error_msg}"
        )
    
    # Speichere Kauf in Datenbank
    purchase = PhoneNumberPurchase(
        user_id=current_user.id,
        provider=request.provider,
        phone_number=buy_result.get("phone_number"),
        country=request.country,
        service=request.service,
        purchase_id=str(buy_result.get("purchase_id")),
        cost=buy_result.get("cost"),
        status="pending",
        expires_at=buy_result.get("expires_at")
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    
    # Warte auf SMS-Code (Polling)
    # In Produktion sollte dies über Webhooks oder Background-Tasks erfolgen
    sms_code = None
    max_wait = 300  # 5 Minuten
    wait_time = 0
    while wait_time < max_wait:
        await asyncio.sleep(10)  # Warte 10 Sekunden
        wait_time += 10
        
        code_result = await provider.get_sms_code(str(buy_result.get("purchase_id")))
        if code_result.get("success") and code_result.get("sms_code"):
            sms_code = code_result.get("sms_code")
            purchase.sms_code = sms_code
            purchase.status = "active"
            db.commit()
            break
    
    if not sms_code:
        raise HTTPException(
            status_code=408,
            detail="SMS-Code nicht innerhalb der Wartezeit erhalten. Bitte manuell prüfen."
        )
    
    # Erstelle Telegram-Account automatisch
    try:
        phone_number = buy_result.get("phone_number")
        
        # Lade API Credentials
        api_id = os.getenv('TELEGRAM_API_ID')
        api_hash = os.getenv('TELEGRAM_API_HASH')
        
        if not api_id or not api_hash:
            raise HTTPException(
                status_code=500,
                detail="TELEGRAM_API_ID und TELEGRAM_API_HASH müssen in Umgebungsvariablen gesetzt sein"
            )
        
        # Erstelle Account-Name
        account_name = f"Auto_{phone_number.replace('+', '').replace(' ', '')}"
        
        # Erstelle Session-Name (ohne .session Endung, Telethon fügt das automatisch hinzu)
        session_name = f"sessions/auto_{phone_number.replace('+', '').replace(' ', '').replace('-', '')}"
        
        # Erstelle Account in Datenbank
        db_account = Account(
            user_id=current_user.id,
            name=account_name,
            account_type="user",
            api_id=api_id,
            api_hash=api_hash,
            phone_number=phone_number,
            session_name=session_name
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        # Verbinde Account mit Telethon
        # Lade Proxy falls vorhanden
        proxy_config = None
        if db_account.proxy_id:
            proxy = db.query(Proxy).filter(Proxy.id == db_account.proxy_id).first()
            if proxy:
                proxy_config = {
                    "proxy_type": proxy.proxy_type,
                    "host": proxy.host,
                    "port": proxy.port,
                    "username": proxy.username,
                    "password": proxy.password,
                    "secret": proxy.secret
                }
        
        # Verbinde Account mit SMS-Code
        result = await account_manager.add_account(
            account_id=db_account.id,
            api_id=api_id,
            api_hash=api_hash,
            session_name=session_name,
            phone_number=phone_number,
            code=sms_code,  # SMS-Code verwenden
            proxy_config=proxy_config
        )
        
        # Verknüpfe Purchase mit Account
        purchase.account_id = db_account.id
        purchase.status = "used"
        purchase.used_at = datetime.utcnow()
        db.commit()
        
        if result.get("status") == "connected":
            return {
                "success": True,
                "purchase_id": purchase.id,
                "phone_number": phone_number,
                "account_id": db_account.id,
                "account_name": account_name,
                "status": "active",
                "message": f"✅ Account '{account_name}' erfolgreich erstellt und verbunden!"
            }
        else:
            return {
                "success": True,
                "purchase_id": purchase.id,
                "phone_number": phone_number,
                "account_id": db_account.id,
                "account_name": account_name,
                "status": "pending",
                "message": f"⚠️ Account erstellt, aber Verbindung fehlgeschlagen: {result.get('error', 'Unbekannter Fehler')}"
            }
            
    except Exception as e:
        # Fehler beim Account-Erstellen
        error_msg = str(e)
        logger.error(f"Fehler beim Erstellen des Accounts nach Nummernkauf: {error_msg}", exc_info=True)
        
        return {
            "success": False,
            "purchase_id": purchase.id,
            "phone_number": buy_result.get("phone_number"),
            "sms_code": sms_code,
            "status": "error",
            "error": "Account-Erstellung fehlgeschlagen. Bitte Support kontaktieren.",
            "message": "❌ Nummer gekauft, aber Account-Erstellung fehlgeschlagen"
        }

@app.get("/api/phone/countries-prices", response_model=dict)
async def get_countries_prices(
    provider: str = Query("onlinesim", description="Provider: onlinesim, 5sim, etc."),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Gibt alle verfügbaren Länder mit Preisen zurück"""
    try:
        # Lade Provider
        if provider == "onlinesim":
            setting = db.query(SystemSettings).filter(SystemSettings.key == "onlinesim_api_key").first()
            provider_api_key = setting.value if setting else os.getenv("ONLINESIM_API_KEY")
            if not provider_api_key:
                raise HTTPException(status_code=500, detail="OnlineSim API Key nicht konfiguriert")
            provider = OnlineSimProvider(provider_api_key)
            
            # Hole Tarife
            tariffs_result = await provider.get_tariffs()
            if not tariffs_result.get("success"):
                raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Tarife: {tariffs_result.get('error')}")
            
            tariffs = tariffs_result.get("tariffs", {})
            
            # Länder-Mapping für bessere Darstellung
            country_names = {
                "49": {"name": "Deutschland", "code": "DE"},
                "1": {"name": "USA", "code": "US"},
                "7": {"name": "Russland", "code": "RU"},
                "380": {"name": "Ukraine", "code": "UA"},
                "48": {"name": "Polen", "code": "PL"},
                "84": {"name": "Vietnam", "code": "VN"}
            }
            
            # Formatiere Daten
            countries_list = []
            if isinstance(tariffs, dict):
                for country_code, services in tariffs.items():
                    country_info = country_names.get(str(country_code), {"name": f"Land {country_code}", "code": country_code})
                    telegram_price = None
                    whatsapp_price = None
                    
                    if isinstance(services, dict):
                        telegram_price = services.get("telegram")
                        whatsapp_price = services.get("whatsapp")
                    elif isinstance(services, list):
                        for service in services:
                            if isinstance(service, dict):
                                if service.get("service") == "telegram":
                                    telegram_price = service.get("price")
                                elif service.get("service") == "whatsapp":
                                    whatsapp_price = service.get("price")
                    
                    countries_list.append({
                        "country_code": str(country_code),
                        "country_name": country_info["name"],
                        "iso_code": country_info["code"],
                        "telegram_price": telegram_price,
                        "whatsapp_price": whatsapp_price
                    })
            
            return {
                "success": True,
                "provider": "onlinesim",
                "countries": countries_list
            }
        else:
            # Für andere Provider: Standard-Länderliste
            return {
                "success": True,
                "provider": provider,
                "countries": [
                    {"country_code": "49", "country_name": "Deutschland", "iso_code": "DE", "telegram_price": None, "whatsapp_price": None},
                    {"country_code": "1", "country_name": "USA", "iso_code": "US", "telegram_price": None, "whatsapp_price": None},
                    {"country_code": "7", "country_name": "Russland", "iso_code": "RU", "telegram_price": None, "whatsapp_price": None},
                    {"country_code": "380", "country_name": "Ukraine", "iso_code": "UA", "telegram_price": None, "whatsapp_price": None},
                    {"country_code": "48", "country_name": "Polen", "iso_code": "PL", "telegram_price": None, "whatsapp_price": None},
                    {"country_code": "84", "country_name": "Vietnam", "iso_code": "VN", "telegram_price": None, "whatsapp_price": None}
                ]
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Länder/Preise: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Länder/Preise: {str(e)}")

class CreateSingleAccountRequest(BaseModel):
    provider: str = "onlinesim"
    country: str
    service: str = "telegram"

@app.post("/api/accounts/create-single", response_model=dict)
async def create_single_account(
    request: CreateSingleAccountRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Erstellt einen einzelnen Account mit automatischem Nummernkauf"""
    # Prüfe ob Feature verfügbar ist
    if not check_subscription(current_user, "auto_number_purchase"):
        raise HTTPException(
            status_code=403,
            detail="Automatischer Nummernkauf ist in deinem Paket nicht enthalten. Bitte upgraden."
        )
    
    # Prüfe Account-Limit
    account_count = db.query(Account).filter(Account.user_id == current_user.id).count()
    if not check_account_limit(current_user, account_count):
        raise HTTPException(
            status_code=403,
            detail=f"Account-Limit erreicht. Maximal {current_user.subscription.max_accounts if current_user.subscription else 1} Accounts erlaubt."
        )
    
    # Lade Provider
    if request.provider == "onlinesim":
        setting = db.query(SystemSettings).filter(SystemSettings.key == "onlinesim_api_key").first()
        provider_api_key = setting.value if setting else os.getenv("ONLINESIM_API_KEY")
        if not provider_api_key:
            raise HTTPException(status_code=500, detail="OnlineSim API Key nicht konfiguriert")
        provider = OnlineSimProvider(provider_api_key)
    else:
        raise HTTPException(status_code=400, detail=f"Provider {request.provider} für einzelne Account-Erstellung noch nicht unterstützt")
    
    # Kaufe Nummer
    buy_result = await provider.buy_number(
        country=request.country,
        service=request.service,
        operator=None
    )
    
    if not buy_result.get("success"):
        error_msg = buy_result.get('error', 'Unbekannter Fehler')
        is_retryable = buy_result.get('retryable', False)
        
        if "TRY_AGAIN_LATER" in error_msg.upper():
            error_msg = f"Rate-Limit erreicht. OnlineSim.io hat temporär keine Nummern verfügbar. Bitte in ein paar Minuten erneut versuchen."
        elif "NO_NUMBERS" in error_msg.upper():
            error_msg = f"Keine Nummern verfügbar für {request.country}. Bitte später erneut versuchen oder ein anderes Land wählen."
        elif "NO_BALANCE" in error_msg.upper():
            error_msg = f"Nicht genug Guthaben bei OnlineSim.io. Bitte Guthaben aufladen."
        
        status_code = 429 if is_retryable else 400
        raise HTTPException(status_code=status_code, detail=f"Fehler beim Kauf der Nummer: {error_msg}")
    
    phone_number = buy_result.get("phone_number")
    purchase_id = str(buy_result.get("purchase_id"))
    cost = buy_result.get("cost")
    
    # Speichere Kauf in Datenbank
    purchase = PhoneNumberPurchase(
        user_id=current_user.id,
        provider=request.provider,
        phone_number=phone_number,
        country=request.country,
        service=request.service,
        purchase_id=purchase_id,
        cost=cost,
        status="pending",
        expires_at=buy_result.get("expires_at")
    )
    db.add(purchase)
    db.commit()
    db.refresh(purchase)
    
    # Warte auf SMS-Code
    sms_code = None
    max_wait = 300  # 5 Minuten
    wait_time = 0
    while wait_time < max_wait:
        await asyncio.sleep(10)
        wait_time += 10
        
        code_result = await provider.get_sms_code(purchase_id)
        if code_result.get("success") and code_result.get("sms_code"):
            sms_code = code_result.get("sms_code")
            purchase.sms_code = sms_code
            purchase.status = "active"
            db.commit()
            break
    
    if not sms_code:
        return {
            "success": False,
            "purchase_id": purchase.id,
            "phone_number": phone_number,
            "status": "sms_timeout",
            "message": "SMS-Code nicht innerhalb der Wartezeit erhalten. Bitte manuell prüfen."
        }
    
    # Erstelle Telegram-Account
    try:
        api_id = os.getenv('TELEGRAM_API_ID')
        api_hash = os.getenv('TELEGRAM_API_HASH')
        
        if not api_id or not api_hash:
            raise HTTPException(
                status_code=500,
                detail="TELEGRAM_API_ID und TELEGRAM_API_HASH müssen in Umgebungsvariablen gesetzt sein"
            )
        
        account_name = f"Auto_{phone_number.replace('+', '').replace(' ', '')}"
        session_name = f"sessions/auto_{phone_number.replace('+', '').replace(' ', '').replace('-', '')}"
        
        db_account = Account(
            user_id=current_user.id,
            name=account_name,
            account_type="user",
            api_id=api_id,
            api_hash=api_hash,
            phone_number=phone_number,
            session_name=session_name
        )
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        
        # Verbinde Account
        result = await account_manager.add_account(
            account_id=db_account.id,
            api_id=api_id,
            api_hash=api_hash,
            session_name=session_name,
            phone_number=phone_number,
            code=sms_code
        )
        
        if result.get("status") == "connected":
            purchase.status = "completed"
            purchase.account_id = db_account.id
            db.commit()
            
            return {
                "success": True,
                "account_id": db_account.id,
                "phone_number": phone_number,
                "cost": cost,
                "status": "completed",
                "message": "✅ Account erfolgreich erstellt und verbunden!"
            }
        else:
            return {
                "success": False,
                "account_id": db_account.id,
                "phone_number": phone_number,
                "status": result.get("status"),
                "message": result.get("message", "Account erstellt, aber Verbindung fehlgeschlagen")
            }
            
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Accounts: {str(e)}", exc_info=True)
        return {
            "success": False,
            "purchase_id": purchase.id,
            "phone_number": phone_number,
            "status": "error",
            "error": f"Account-Erstellung fehlgeschlagen: {str(e)}"
        }

@app.post("/api/accounts/auto-create", response_model=dict)
async def auto_create_accounts(
    request: AutoCreateAccountsRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Erstellt automatisch mehrere Telegram-Accounts basierend auf verfügbarem Guthaben.
    Prüft Guthaben, kauft Nummern, erstellt Accounts und speichert alles (ID, Nummer, Hash, API).
    """
    # Prüfe ob Feature verfügbar ist
    if not check_subscription(current_user, "auto_number_purchase"):
        raise HTTPException(
            status_code=403,
            detail="Automatischer Nummernkauf ist in deinem Paket nicht enthalten. Bitte upgraden."
        )
    
    # Lade API Key aus Umgebungsvariablen oder SystemSettings
    provider_api_key = None
    
    # Provider initialisieren
    if request.provider == "5sim":
        setting = db.query(SystemSettings).filter(SystemSettings.key == "fivesim_api_key").first()
        provider_api_key = setting.value if setting else os.getenv("FIVESIM_API_KEY")
        if not provider_api_key:
            raise HTTPException(status_code=500, detail="5sim API Key nicht konfiguriert")
        provider = FiveSimProvider(provider_api_key)
    elif request.provider == "sms-activate":
        setting = db.query(SystemSettings).filter(SystemSettings.key == "sms_activate_api_key").first()
        provider_api_key = setting.value if setting else os.getenv("SMS_ACTIVATE_API_KEY")
        if not provider_api_key:
            raise HTTPException(status_code=500, detail="SMS-Activate API Key nicht konfiguriert")
        provider = SMSActivateProvider(provider_api_key)
    elif request.provider == "sms-manager":
        setting = db.query(SystemSettings).filter(SystemSettings.key == "sms_manager_api_key").first()
        provider_api_key = setting.value if setting else os.getenv("SMS_MANAGER_API_KEY")
        if not provider_api_key:
            raise HTTPException(status_code=500, detail="SMS-Manager API Key nicht konfiguriert")
        provider = SMSManagerProvider(provider_api_key)
    elif request.provider == "getsmscode":
        setting = db.query(SystemSettings).filter(SystemSettings.key == "getsmscode_api_key").first()
        provider_api_key = setting.value if setting else os.getenv("GETSMSCODE_API_KEY")
        if not provider_api_key:
            raise HTTPException(status_code=500, detail="GetSMSCode API Key nicht konfiguriert")
        provider = GetSMSCodeProvider(provider_api_key)
    elif request.provider == "onlinesim":
        setting = db.query(SystemSettings).filter(SystemSettings.key == "onlinesim_api_key").first()
        provider_api_key = setting.value if setting else os.getenv("ONLINESIM_API_KEY")
        if not provider_api_key:
            raise HTTPException(status_code=500, detail="OnlineSim API Key nicht konfiguriert")
        provider = OnlineSimProvider(provider_api_key)
    else:
        raise HTTPException(status_code=400, detail=f"Unbekannter Provider: {request.provider}")
    
    # Prüfe Guthaben
    balance_result = await provider.get_balance()
    if not balance_result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=f"Fehler beim Abrufen des Guthabens: {balance_result.get('error', 'Unbekannter Fehler')}"
        )
    
    balance = balance_result.get("balance", 0)
    currency = balance_result.get("currency", "USD")
    
    if request.min_balance and balance < request.min_balance:
        raise HTTPException(
            status_code=400,
            detail=f"Nicht genug Guthaben. Verfügbar: {balance} {currency}, Mindest: {request.min_balance} {currency}"
        )
    
    # Lade API Credentials
    api_id = os.getenv('TELEGRAM_API_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH')
    
    if not api_id or not api_hash:
        raise HTTPException(
            status_code=500,
            detail="TELEGRAM_API_ID und TELEGRAM_API_HASH müssen in Umgebungsvariablen gesetzt sein"
        )
    
    # Prüfe Account-Limit
    account_count = db.query(Account).filter(Account.user_id == current_user.id).count()
    max_allowed = current_user.subscription.max_accounts if current_user.subscription else 1
    
    # Berechne wie viele Accounts erstellt werden können
    accounts_to_create = min(
        request.max_accounts,
        max_allowed - account_count
    )
    
    if accounts_to_create <= 0:
        raise HTTPException(
            status_code=403,
            detail=f"Account-Limit erreicht. Maximal {max_allowed} Accounts erlaubt."
        )
    
    results = {
        "success": True,
        "requested": request.max_accounts,
        "created": 0,
        "failed": 0,
        "accounts": [],
        "errors": [],
        "balance_before": balance,
        "balance_after": None
    }
    
    # Erstelle Accounts
    for i in range(accounts_to_create):
        try:
            # Prüfe Account-Limit vor jedem Kauf
            current_count = db.query(Account).filter(Account.user_id == current_user.id).count()
            if current_count >= max_allowed:
                results["errors"].append(f"Account-Limit erreicht nach {i} Accounts")
                break
            
            # Warte zwischen Käufen, um Rate-Limiting zu vermeiden
            if i > 0:
                await asyncio.sleep(3)  # 3 Sekunden zwischen Käufen
            
            # Kaufe Nummer
            buy_result = await provider.buy_number(
                country=request.country,
                service=request.service,
                operator=None
            )
            
            if not buy_result.get("success"):
                results["failed"] += 1
                error_msg = buy_result.get('error', 'Unbekannter Fehler')
                is_retryable = buy_result.get('retryable', False)
                
                # Verbesserte Fehlermeldung
                if "TRY_AGAIN_LATER" in error_msg.upper():
                    error_msg = f"Rate-Limit erreicht. Bitte später erneut versuchen. (Original: {error_msg})"
                elif "NO_NUMBERS" in error_msg.upper():
                    error_msg = f"Keine Nummern verfügbar für {request.country}. (Original: {error_msg})"
                elif "NO_BALANCE" in error_msg.upper():
                    error_msg = f"Nicht genug Guthaben bei OnlineSim.io. (Original: {error_msg})"
                
                results["errors"].append(f"Kauf {i+1} fehlgeschlagen: {error_msg}")
                
                # Wenn retry-fähig, warte länger vor nächstem Versuch
                if is_retryable and i < accounts_to_create - 1:
                    await asyncio.sleep(10)  # Warte 10 Sekunden vor nächstem Kauf
                
                continue
            
            phone_number = buy_result.get("phone_number")
            purchase_id = str(buy_result.get("purchase_id"))
            
            # Speichere Kauf in Datenbank
            purchase = PhoneNumberPurchase(
                user_id=current_user.id,
                provider=request.provider,
                phone_number=phone_number,
                country=request.country,
                service=request.service,
                purchase_id=purchase_id,
                cost=buy_result.get("cost"),
                status="pending",
                expires_at=buy_result.get("expires_at")
            )
            db.add(purchase)
            db.commit()
            db.refresh(purchase)
            
            # Warte auf SMS-Code (mit Timeout)
            sms_code = None
            max_wait = 300  # 5 Minuten
            wait_time = 0
            while wait_time < max_wait:
                await asyncio.sleep(10)  # Warte 10 Sekunden
                wait_time += 10
                
                code_result = await provider.get_sms_code(purchase_id)
                if code_result.get("success") and code_result.get("sms_code"):
                    sms_code = code_result.get("sms_code")
                    purchase.sms_code = sms_code
                    purchase.status = "active"
                    db.commit()
                    break
            
            if not sms_code:
                results["failed"] += 1
                results["errors"].append(f"Account {i+1} ({phone_number}): SMS-Code nicht erhalten")
                purchase.status = "timeout"
                db.commit()
                continue
            
            # Erstelle Account-Name
            account_name = f"Auto_{phone_number.replace('+', '').replace(' ', '')}"
            
            # Erstelle Session-Name
            session_name = f"sessions/auto_{phone_number.replace('+', '').replace(' ', '').replace('-', '')}"
            
            # Erstelle Account in Datenbank
            db_account = Account(
                user_id=current_user.id,
                name=account_name,
                account_type="user",
                api_id=api_id,
                api_hash=api_hash,
                phone_number=phone_number,
                session_name=session_name
            )
            db.add(db_account)
            db.commit()
            db.refresh(db_account)
            
            # Verbinde Account mit Telethon
            proxy_config = None
            if db_account.proxy_id:
                proxy = db.query(Proxy).filter(Proxy.id == db_account.proxy_id).first()
                if proxy:
                    proxy_config = {
                        "proxy_type": proxy.proxy_type,
                        "host": proxy.host,
                        "port": proxy.port,
                        "username": proxy.username,
                        "password": proxy.password,
                        "secret": proxy.secret
                    }
            
            # Verbinde Account mit SMS-Code
            result = await account_manager.add_account(
                account_id=db_account.id,
                api_id=api_id,
                api_hash=api_hash,
                session_name=session_name,
                phone_number=phone_number,
                code=sms_code,
                proxy_config=proxy_config
            )
            
            # Verknüpfe Purchase mit Account
            purchase.account_id = db_account.id
            purchase.status = "used"
            purchase.used_at = datetime.utcnow()
            db.commit()
            
            if result.get("status") == "connected":
                # Hole Account-Info für Rückgabe
                account_info = result.get("info", {})
                results["created"] += 1
                results["accounts"].append({
                    "account_id": db_account.id,
                    "name": account_name,
                    "phone_number": phone_number,
                    "api_id": api_id,
                    "api_hash": api_hash,
                    "session_name": session_name,
                    "status": "connected",
                    "user_id": account_info.get("id"),
                    "username": account_info.get("username"),
                    "first_name": account_info.get("first_name"),
                    "last_name": account_info.get("last_name")
                })
            else:
                results["failed"] += 1
                results["errors"].append(f"Account {i+1} ({phone_number}): Verbindung fehlgeschlagen - {result.get('error', 'Unbekannter Fehler')}")
            
            # Kurze Pause zwischen Accounts
            await asyncio.sleep(2)
            
        except Exception as e:
            results["failed"] += 1
            error_msg = str(e)
            results["errors"].append(f"Account {i+1}: {error_msg}")
            logger.error(f"Fehler beim automatischen Erstellen von Account {i+1}: {error_msg}", exc_info=True)
            continue
    
    # Prüfe finales Guthaben
    final_balance_result = await provider.get_balance()
    if final_balance_result.get("success"):
        results["balance_after"] = final_balance_result.get("balance", 0)
    
    return results

# Subscription/Paket Endpoints
@app.get("/api/subscriptions/plans", response_model=List[dict])
async def get_subscription_plans():
    """Gibt verfügbare Pakete zurück"""
    return [
        {
            "plan_type": "free_trial",
            "name": "🎁 Kostenloser Test",
            "price": 0,
            "duration_days": 7,
            "max_accounts": 2,
            "max_groups": 5,
            "max_messages_per_day": 10,
            "features": {
                "auto_number_purchase": False
            },
            "description": "7 Tage kostenlos testen"
        },
        {
            "plan_type": "basic",
            "name": "📦 Basis",
            "price": 99.00,
            "currency": "EUR",
            "duration_days": 30,
            "max_accounts": 5,
            "max_groups": 20,
            "max_messages_per_day": 100,
            "features": {
                "auto_number_purchase": False
            },
            "description": "Für Einsteiger"
        },
        {
            "plan_type": "pro",
            "name": "⭐ Pro",
            "price": 249.00,
            "currency": "EUR",
            "duration_days": 30,
            "max_accounts": 20,
            "max_groups": 100,
            "max_messages_per_day": 1000,
            "features": {
                "auto_number_purchase": True
            },
            "description": "Für Profis"
        },
        {
            "plan_type": "enterprise",
            "name": "🚀 Enterprise",
            "price": 499.00,
            "currency": "EUR",
            "duration_days": 30,
            "max_accounts": 100,
            "max_groups": 500,
            "max_messages_per_day": 10000,
            "features": {
                "auto_number_purchase": True
            },
            "description": "Für Unternehmen"
        }
    ]

@app.post("/api/subscriptions/purchase", response_model=dict)
async def purchase_subscription(
    request: PurchaseSubscriptionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Kauft ein Abonnement-Paket
    
    TODO: Stripe/PayPal Integration implementieren
    """
    # Prüfe ob Paket existiert
    plans = await get_subscription_plans()
    plan = next((p for p in plans if p["plan_type"] == request.plan_type), None)
    
    if not plan:
        raise HTTPException(status_code=400, detail="Ungültiges Paket")
    
    if request.plan_type == "free_trial":
        raise HTTPException(status_code=400, detail="Free Trial kann nicht gekauft werden")
    
    # TODO: Zahlung verarbeiten (Stripe/PayPal)
    # Hier würde die Zahlung verarbeitet werden
    # Für jetzt: Simuliere erfolgreiche Zahlung
    
    if request.payment_method == "stripe" and request.payment_token:
        # TODO: Stripe Payment verarbeiten
        # stripe.PaymentIntent.create(...)
        payment_success = True  # Simuliert
    elif request.payment_method == "paypal" and request.payment_token:
        # TODO: PayPal Payment verarbeiten
        payment_success = True  # Simuliert
    else:
        # Für Entwicklung: Zahlung ohne Token akzeptieren
        payment_success = True
    
    if not payment_success:
        raise HTTPException(status_code=400, detail="Zahlung fehlgeschlagen")
    
    # Erstelle oder aktualisiere Abonnement
    existing_subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id
    ).first()
    
    if existing_subscription:
        # Aktualisiere bestehendes Abonnement
        existing_subscription.plan_type = request.plan_type
        existing_subscription.status = "active"
        existing_subscription.started_at = datetime.utcnow()
        existing_subscription.expires_at = datetime.utcnow() + timedelta(days=plan["duration_days"])
        existing_subscription.max_accounts = plan["max_accounts"]
        existing_subscription.max_groups = plan["max_groups"]
        existing_subscription.max_messages_per_day = plan["max_messages_per_day"]
        existing_subscription.features = json.dumps(plan["features"])
        db.commit()
        db.refresh(existing_subscription)
        
        return {
            "success": True,
            "message": "Abonnement aktualisiert",
            "subscription": {
                "plan_type": existing_subscription.plan_type,
                "expires_at": existing_subscription.expires_at.isoformat() if existing_subscription.expires_at else None,
                "max_accounts": existing_subscription.max_accounts,
                "max_groups": existing_subscription.max_groups,
                "max_messages_per_day": existing_subscription.max_messages_per_day
            }
        }
    else:
        # Erstelle neues Abonnement
        new_subscription = Subscription(
            user_id=current_user.id,
            plan_type=request.plan_type,
            status="active",
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=plan["duration_days"]),
            max_accounts=plan["max_accounts"],
            max_groups=plan["max_groups"],
            max_messages_per_day=plan["max_messages_per_day"],
            features=json.dumps(plan["features"])
        )
        db.add(new_subscription)
        db.commit()
        db.refresh(new_subscription)
        
        return {
            "success": True,
            "message": "Abonnement erfolgreich gekauft",
            "subscription": {
                "plan_type": new_subscription.plan_type,
                "expires_at": new_subscription.expires_at.isoformat() if new_subscription.expires_at else None,
                "max_accounts": new_subscription.max_accounts,
                "max_groups": new_subscription.max_groups,
                "max_messages_per_day": new_subscription.max_messages_per_day
            }
        }

@app.post("/api/groups/search-by-name", response_model=List[dict])
async def search_groups_by_name(
    request: GroupSearchRequest,
    db: Session = Depends(get_db)
):
    """Sucht Gruppen nach Namen oder Username und fügt sie hinzu"""
    account = db.query(Account).filter(Account.id == request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.account_type != "user":
        raise HTTPException(status_code=400, detail="Nur User-Accounts können Gruppen suchen")
    
    # Lade Dialoge
    dialogs = await account_manager.get_dialogs(request.account_id)
    
    results = []
    added_groups = []
    
    for group_name in request.group_names:
        group_name_clean = group_name.strip()
        if not group_name_clean:
            continue
        
        # Entferne @ falls vorhanden
        search_name = group_name_clean.lstrip('@')
        
        # Suche in Dialogen
        found = False
        for dialog in dialogs:
            # Prüfe Name oder Username
            if (dialog.get("name", "").lower() == search_name.lower() or
                dialog.get("username", "").lower() == search_name.lower()):
                
                # Prüfe ob Gruppe bereits existiert
                existing = db.query(Group).filter(
                    Group.chat_id == str(dialog["id"])
                ).first()
                
                if existing:
                    results.append({
                        "name": group_name_clean,
                        "status": "exists",
                        "group_id": existing.id,
                        "group_name": existing.name
                    })
                else:
                    # Erstelle neue Gruppe
                    db_group = Group(
                        name=dialog.get("name", group_name_clean),
                        chat_id=str(dialog["id"]),
                        chat_type=dialog.get("type", "group"),
                        username=dialog.get("username")
                    )
                    db.add(db_group)
                    db.commit()
                    db.refresh(db_group)
                    
                    results.append({
                        "name": group_name_clean,
                        "status": "added",
                        "group_id": db_group.id,
                        "group_name": db_group.name
                    })
                    added_groups.append(db_group)
                
                found = True
                break
        
        if not found:
            results.append({
                "name": group_name_clean,
                "status": "not_found",
                "error": "Gruppe nicht in Dialogen gefunden"
            })
    
    return results

@app.post("/api/groups/bulk", response_model=List[dict])
async def bulk_create_groups(bulk: BulkGroupCreate, db: Session = Depends(get_db)):
    """Erstellt mehrere Gruppen auf einmal durch Namen"""
    request = GroupSearchRequest(account_id=bulk.account_id, group_names=bulk.group_names)
    return await search_groups_by_name(request, db)

# Scheduled Message Endpoints
@app.post("/api/scheduled-messages", response_model=dict)
async def create_scheduled_message(
    msg: ScheduledMessageCreate,
    db: Session = Depends(get_db)
):
    """Erstellt eine geplante Nachricht (Multi-Gruppen Support)"""
    # Validierung
    account = db.query(Account).filter(Account.id == msg.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if not msg.group_ids:
        raise HTTPException(status_code=400, detail="Mindestens eine Gruppe muss ausgewählt werden")
    
    # Validiere alle Gruppen
    groups = db.query(Group).filter(Group.id.in_(msg.group_ids)).all()
    if len(groups) != len(msg.group_ids):
        raise HTTPException(status_code=404, detail="Eine oder mehrere Gruppen nicht gefunden")
    
    if msg.scheduled_time < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Scheduled time muss in der Zukunft liegen")
    
    scheduled_msg = ScheduledMessage(
        account_id=msg.account_id,
        group_ids=json.dumps(msg.group_ids),  # Als JSON speichern
        message=msg.message,
        scheduled_time=msg.scheduled_time,
        delay=msg.delay,
        batch_size=msg.batch_size,
        batch_delay=msg.batch_delay,
        group_delay=msg.group_delay,
        repeat_count=msg.repeat_count
    )
    
    db.add(scheduled_msg)
    db.commit()
    db.refresh(scheduled_msg)
    
    # Plane die Nachricht
    if scheduler_service:
        await scheduler_service.schedule_message(scheduled_msg)
    else:
        raise HTTPException(status_code=503, detail="Scheduler Service nicht verfügbar")
    
    return {
        "id": scheduled_msg.id,
        "account_id": scheduled_msg.account_id,
        "group_ids": msg.group_ids,
        "message": scheduled_msg.message,
        "scheduled_time": scheduled_msg.scheduled_time.isoformat(),
        "status": scheduled_msg.status,
        "repeat_count": scheduled_msg.repeat_count
    }

@app.get("/api/scheduled-messages", response_model=List[dict])
async def list_scheduled_messages(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listet geplante Nachrichten"""
    query = db.query(ScheduledMessage)
    
    if status:
        query = query.filter(ScheduledMessage.status == status)
    
    messages = query.order_by(ScheduledMessage.scheduled_time.desc()).all()
    
    result = []
    for m in messages:
        try:
            group_ids = json.loads(m.group_ids) if m.group_ids else []
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Ungültiges JSON in group_ids für Nachricht {m.id}: {e}")
            group_ids = []
        
        result.append({
            "id": m.id,
            "account_id": m.account_id,
            "group_ids": group_ids,
            "message": m.message,
            "scheduled_time": m.scheduled_time.isoformat(),
            "status": m.status,
            "repeat_count": m.repeat_count,
            "sent_count": m.sent_count,
            "failed_count": m.failed_count,
            "created_at": m.created_at.isoformat() if m.created_at else None,
            "started_at": m.started_at.isoformat() if m.started_at else None,
            "completed_at": m.completed_at.isoformat() if m.completed_at else None,
            "error_message": m.error_message
        })
    return result

@app.get("/api/scheduled-messages/{message_id}", response_model=dict)
async def get_scheduled_message(message_id: int, db: Session = Depends(get_db)):
    """Gibt Details einer geplanten Nachricht zurück"""
    msg = db.query(ScheduledMessage).filter(ScheduledMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Nachricht nicht gefunden")
    
    try:
        group_ids = json.loads(msg.group_ids) if msg.group_ids else []
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Ungültiges JSON in group_ids für Nachricht {message_id}: {e}")
        group_ids = []
    
    return {
        "id": msg.id,
        "account_id": msg.account_id,
        "group_ids": group_ids,
        "message": msg.message,
        "scheduled_time": msg.scheduled_time.isoformat(),
        "status": msg.status,
        "delay": msg.delay,
        "batch_size": msg.batch_size,
        "batch_delay": msg.batch_delay,
        "repeat_count": msg.repeat_count,
        "sent_count": msg.sent_count,
        "failed_count": msg.failed_count,
        "created_at": msg.created_at.isoformat() if msg.created_at else None,
        "started_at": msg.started_at.isoformat() if msg.started_at else None,
        "completed_at": msg.completed_at.isoformat() if msg.completed_at else None,
        "error_message": msg.error_message
    }

@app.put("/api/scheduled-messages/{message_id}", response_model=dict)
async def update_scheduled_message(
    message_id: int,
    update: ScheduledMessageUpdate,
    db: Session = Depends(get_db)
):
    """Aktualisiert eine geplante Nachricht"""
    msg = db.query(ScheduledMessage).filter(ScheduledMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Nachricht nicht gefunden")
    
    if msg.status != "pending":
        raise HTTPException(status_code=400, detail="Nur pending Nachrichten können bearbeitet werden")
    
    # Alten Job entfernen
    if scheduler_service:
        scheduler_service.cancel_message(message_id)
    else:
        raise HTTPException(status_code=503, detail="Scheduler Service nicht verfügbar")
    
    # Felder aktualisieren
    if update.message is not None:
        msg.message = update.message
    if update.scheduled_time is not None:
        if update.scheduled_time < datetime.utcnow():
            raise HTTPException(status_code=400, detail="Scheduled time muss in der Zukunft liegen")
        msg.scheduled_time = update.scheduled_time
    if update.delay is not None:
        msg.delay = update.delay
    if update.batch_size is not None:
        msg.batch_size = update.batch_size
    if update.batch_delay is not None:
        msg.batch_delay = update.batch_delay
    if update.repeat_count is not None:
        msg.repeat_count = update.repeat_count
    
    db.commit()
    db.refresh(msg)
    
    # Neuen Job erstellen
    await scheduler_service.schedule_message(msg)
    
    return {
        "id": msg.id,
        "message": msg.message,
        "scheduled_time": msg.scheduled_time.isoformat(),
        "status": msg.status
    }

@app.delete("/api/scheduled-messages/{message_id}")
async def cancel_scheduled_message(message_id: int, db: Session = Depends(get_db)):
    """Bricht eine geplante Nachricht ab"""
    msg = db.query(ScheduledMessage).filter(ScheduledMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Nachricht nicht gefunden")
    
    if scheduler_service:
        scheduler_service.cancel_message(message_id)
    else:
        raise HTTPException(status_code=503, detail="Scheduler Service nicht verfügbar")
    
    return {"success": True}

@app.post("/api/send-test", response_model=dict)
async def send_test_message(
    account_id: int = Query(..., ge=1, description="Account ID muss >= 1 sein"),
    group_id: int = Query(..., ge=1, description="Group ID muss >= 1 sein"),
    message: str = Query(..., min_length=1, max_length=4096, description="Nachricht (1-4096 Zeichen)"),
    template_id: Optional[int] = Query(None, ge=1),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Sendet eine Testnachricht (sofort)"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    # Prüfe ob Account dem User gehört
    if account.user_id and account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Zugriff verweigert: Account gehört nicht zu diesem Benutzer")
    
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Gruppe nicht gefunden")
    
    # Prüfe ob Gruppe dem User gehört
    if group.user_id and group.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Zugriff verweigert: Gruppe gehört nicht zu diesem Benutzer")
    
    result = await account_manager.send_message(
        account_id=account_id,
        entity=group.chat_id,
        message=message,
        delay=0
    )
    
    # Speichere in DB
    save_sent_message(
        db,
        account_id=account_id,
        group_id=group_id,
        group_chat_id=group.chat_id,
        group_name=group.name,
        message=message,
        template_id=template_id,
        success=result.get("success", False),
        error_message=result.get("error"),
        telegram_message_id=result.get("telegram_message_id")
    )
    
    return result

# User Scraping Endpoints
@app.post("/api/scrape/group-members", response_model=dict)
async def scrape_group_members(
    request: ScrapeGroupMembersRequest,
    db: Session = Depends(get_db)
):
    """
    Scrapt Mitglieder aus einer Gruppe
    
    ⚠️ WARNUNG: User-Scraping kann gegen Telegram Nutzungsbedingungen verstoßen!
    """
    account = db.query(Account).filter(Account.id == request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.account_type != "user":
        raise HTTPException(status_code=400, detail="Nur User-Accounts können scrapen")
    
    # Bestimme group_entity
    group_entity = None
    if request.group_entity:
        group_entity = request.group_entity
    elif request.group_id:
        # Lade Gruppe aus Datenbank
        group = db.query(Group).filter(Group.id == request.group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Gruppe nicht gefunden")
        group_entity = group.chat_id
    else:
        raise HTTPException(status_code=400, detail="Bitte group_id oder group_entity angeben")
    
    # Scrape Mitglieder
    members = await account_manager.scrape_group_members(
        account_id=request.account_id,
        group_entity=group_entity,
        limit=request.limit
    )
    
    # Speichere in Datenbank
    saved_count = 0
    for member in members:
        # Prüfe ob User bereits existiert
        existing = db.query(ScrapedUser).filter(
            ScrapedUser.user_id == member["user_id"]
        ).first()
        
        if not existing:
            scraped_user = ScrapedUser(
                user_id=member["user_id"],
                username=member.get("username"),
                first_name=member.get("first_name"),
                last_name=member.get("last_name"),
                phone=member.get("phone"),
                source_group_id=group.chat_id,
                source_group_name=group.name
            )
            db.add(scraped_user)
            saved_count += 1
    
    db.commit()
    
    return {
        "success": True,
        "scraped": len(members),
        "saved": saved_count,
        "members": members[:100]  # Nur erste 100 zurückgeben
    }

@app.get("/api/scraped-users", response_model=List[dict])
async def list_scraped_users(
    source_group_id: Optional[str] = None,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """Listet gescrapte User"""
    query = db.query(ScrapedUser).filter(ScrapedUser.is_active == True)
    
    if source_group_id:
        query = query.filter(ScrapedUser.source_group_id == source_group_id)
    
    users = query.order_by(ScrapedUser.scraped_at.desc()).limit(limit).all()
    
    return [
        {
            "id": u.id,
            "user_id": u.user_id,
            "username": u.username,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "phone": u.phone,
            "source_group_name": u.source_group_name,
            "scraped_at": u.scraped_at.isoformat() if u.scraped_at else None
        }
        for u in users
    ]

@app.post("/api/invite/users", response_model=dict)
async def invite_users_to_group(
    request: InviteUsersRequest,
    db: Session = Depends(get_db)
):
    """
    Lädt User zu einer Gruppe ein
    
    Args:
        - user_ids: Liste von User-IDs oder Usernames (optional)
        - usernames: Liste von Usernamen (optional, wird bevorzugt wenn gesetzt)
        - invite_method: "admin" (direkte Einladung) oder "invite_link" (Link erstellen und senden)
    
    ⚠️ WARNUNG: Masseneinladungen können gegen Telegram Nutzungsbedingungen verstoßen!
    """
    account = db.query(Account).filter(Account.id == request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.account_type != "user":
        raise HTTPException(status_code=400, detail="Nur User-Accounts können einladen")
    
    # Bestimme group_entity
    group_entity = None
    if request.group_entity:
        group_entity = request.group_entity
    elif request.group_id:
        group = db.query(Group).filter(Group.id == request.group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Gruppe nicht gefunden")
        group_entity = group.chat_id
    else:
        raise HTTPException(status_code=400, detail="Bitte group_id oder group_entity angeben")
    
    # Verarbeite Usernamen-Liste
    user_ids = []
    if request.usernames:
        # Bereinige Usernamen (entferne @, Leerzeichen)
        for username in request.usernames:
            username = username.strip()
            if username:
                # Entferne @ falls vorhanden
                if username.startswith("@"):
                    username = username[1:]
                # Füge @ hinzu für Telegram
                user_ids.append(f"@{username}")
    elif request.user_ids:
        user_ids = request.user_ids
    else:
        raise HTTPException(status_code=400, detail="Bitte user_ids oder usernames angeben")
    
    if not user_ids:
        raise HTTPException(status_code=400, detail="Keine gültigen User-IDs oder Usernamen gefunden")
    
    # Validiere invite_method
    if request.invite_method not in ["admin", "invite_link"]:
        raise HTTPException(status_code=400, detail="invite_method muss 'admin' oder 'invite_link' sein")
    
    result = await account_manager.invite_users_to_group(
        account_id=request.account_id,
        group_entity=group_entity,
        user_ids=user_ids,
        delay=request.delay,
        invite_method=request.invite_method
    )
    
    return result

@app.post("/api/invite/from-scraped", response_model=dict)
async def invite_from_scraped_users(
    request: InviteFromScrapedRequest,
    db: Session = Depends(get_db)
):
    """
    Lädt gescrapte User zu einer Gruppe ein
    """
    account = db.query(Account).filter(Account.id == request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    group = db.query(Group).filter(Group.id == request.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Gruppe nicht gefunden")
    
    # Lade gescrapte User
    scraped_users = db.query(ScrapedUser).filter(
        ScrapedUser.id.in_(request.scraped_user_ids)
    ).all()
    
    if not scraped_users:
        raise HTTPException(status_code=404, detail="Keine gescrapten User gefunden")
    
    # Extrahiere User-IDs
    user_ids = []
    for user in scraped_users:
        if user.username:
            user_ids.append(f"@{user.username}")
        elif user.user_id:
            user_ids.append(user.user_id)
    
    result = await account_manager.invite_users_to_group(
        account_id=request.account_id,
        group_entity=group.chat_id,
        user_ids=user_ids,
        delay=request.delay
    )
    
    return result

@app.post("/api/accounts/add-to-groups", response_model=dict)
async def add_account_to_groups_endpoint(
    request: AddAccountToGroupsRequest,
    db: Session = Depends(get_db)
):
    """
    Fügt einen Account zu mehreren Gruppen hinzu
    
    Args:
        request: AddAccountToGroupsRequest mit account_id und group_ids
        
    Returns:
        Ergebnis-Dict mit Statistiken
    """
    account = db.query(Account).filter(Account.id == request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.account_type != "user":
        raise HTTPException(status_code=400, detail="Nur User-Accounts können Gruppen beitreten")
    
    # Lade Gruppen aus Datenbank
    groups = db.query(Group).filter(Group.id.in_(request.group_ids)).all()
    if not groups:
        raise HTTPException(status_code=404, detail="Keine Gruppen gefunden")
    
    # Extrahiere Chat-IDs
    group_entities = [group.chat_id for group in groups]
    
    # Füge Account zu Gruppen hinzu
    result = await account_manager.add_account_to_groups(
        account_id=request.account_id,
        group_entities=group_entities,
        delay=request.delay
    )
    
    # Aktualisiere Gruppendetails in Datenbank
    for group in groups:
        group.last_checked = datetime.utcnow()
    
    db.commit()
    
    return result

# Message Forwarding Endpoints
@app.post("/api/messages/get-group-messages", response_model=List[dict])
async def get_group_messages(
    request: GetGroupMessagesRequest,
    db: Session = Depends(get_db)
):
    """Ruft Nachrichten aus einer Gruppe ab"""
    account = db.query(Account).filter(Account.id == request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.account_type != "user":
        raise HTTPException(status_code=400, detail="Nur User-Accounts können Nachrichten abrufen")
    
    # Prüfe ob group_id oder manual_group_entity gesetzt ist
    group_entity = None
    if request.group_id:
        group = db.query(Group).filter(Group.id == request.group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Gruppe nicht gefunden")
        group_entity = group.chat_id
    elif hasattr(request, 'manual_group_entity') and request.manual_group_entity:
        group_entity = request.manual_group_entity
    else:
        raise HTTPException(status_code=400, detail="Bitte Gruppe auswählen oder manuell eingeben")
    
    result = await account_manager.get_group_messages(
        account_id=request.account_id,
        group_entity=group_entity,
        limit=request.limit,
        auto_join=True  # Automatisch beitreten, wenn nicht Mitglied
    )
    
    # Prüfe ob Fehler aufgetreten ist
    if result.get("error"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error")
        )
    
    return result.get("messages", [])

@app.post("/api/messages/forward-by-id", response_model=dict)
async def forward_message_by_id(
    request: ForwardMessageByIdRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Leitet eine einzelne Nachricht per Message-ID weiter
    
    Args:
        request: ForwardMessageByIdRequest mit Message-ID und Ziel-Gruppen
    """
    account = db.query(Account).filter(Account.id == request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Account gehört nicht zum aktuellen Benutzer")
    
    if account.account_type != "user":
        raise HTTPException(status_code=400, detail="Nur User-Accounts können weiterleiten")
    
    # Prüfe ob group_id oder source_group_entity gesetzt ist
    source_group_entity = None
    if request.source_group_entity:
        source_group_entity = request.source_group_entity
    elif request.source_group_id:
        source_group = db.query(Group).filter(Group.id == request.source_group_id).first()
        if not source_group:
            raise HTTPException(status_code=404, detail="Quell-Gruppe nicht gefunden")
        source_group_entity = source_group.chat_id
    else:
        raise HTTPException(status_code=400, detail="Bitte Quell-Gruppe angeben (ID oder manuell)")
    
    # Lade Ziel-Gruppen
    target_groups = db.query(Group).filter(Group.id.in_(request.target_group_ids)).all()
    if len(target_groups) != len(request.target_group_ids):
        raise HTTPException(status_code=404, detail="Eine oder mehrere Ziel-Gruppen nicht gefunden")
    
    target_chat_ids = [g.chat_id for g in target_groups]
    
    # Konvertiere message_id zu int (kann sehr groß sein, daher als String empfangen)
    try:
        message_id_int = int(request.message_id)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Ungültige Message-ID: {request.message_id}")
    
    result = await account_manager.forward_message_by_id(
        account_id=request.account_id,
        source_group=source_group_entity,
        message_id=message_id_int,
        target_groups=target_chat_ids,
        delay=request.delay
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Fehler beim Weiterleiten")
        )
    
    return result

@app.post("/api/messages/forward", response_model=dict)
async def forward_messages(
    request: ForwardMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Leitet Nachrichten per Message-ID weiter
    
    ⚠️ WARNUNG: Massenweiterleitungen können gegen Telegram Nutzungsbedingungen verstoßen!
    """
    account = db.query(Account).filter(Account.id == request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.account_type != "user":
        raise HTTPException(status_code=400, detail="Nur User-Accounts können weiterleiten")
    
    source_group = db.query(Group).filter(Group.id == request.source_group_id).first()
    if not source_group:
        raise HTTPException(status_code=404, detail="Quell-Gruppe nicht gefunden")
    
    # Lade Ziel-Gruppen
    target_groups = db.query(Group).filter(Group.id.in_(request.target_group_ids)).all()
    if len(target_groups) != len(request.target_group_ids):
        raise HTTPException(status_code=404, detail="Eine oder mehrere Ziel-Gruppen nicht gefunden")
    
    target_chat_ids = [g.chat_id for g in target_groups]
    
    result = await account_manager.forward_message(
        account_id=request.account_id,
        source_group=source_group.chat_id,
        message_ids=request.message_ids,
        target_groups=target_chat_ids,
        delay=request.delay
    )
    
    return result

# Account Warming Endpoints
@app.post("/api/warming/config", response_model=dict)
async def create_warming_config(
    config: WarmingConfigCreate,
    db: Session = Depends(get_db)
):
    """Erstellt oder aktualisiert Warming-Konfiguration für einen Account"""
    account = db.query(Account).filter(Account.id == config.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.account_type != "user":
        raise HTTPException(status_code=400, detail="Nur User-Accounts können gewärmt werden")
    
    # Prüfe ob bereits existiert
    existing = db.query(AccountWarming).filter(AccountWarming.account_id == config.account_id).first()
    
    if existing:
        # Update
        existing.read_messages_per_day = config.read_messages_per_day
        existing.scroll_dialogs_per_day = config.scroll_dialogs_per_day
        existing.reactions_per_day = config.reactions_per_day
        existing.small_messages_per_day = config.small_messages_per_day
        existing.start_time = config.start_time
        existing.end_time = config.end_time
        existing.min_delay = config.min_delay
        existing.max_delay = config.max_delay
        existing.max_warming_days = config.max_warming_days
        existing.updated_at = datetime.utcnow()
        warming = existing
    else:
        # Create
        warming = AccountWarming(
            account_id=config.account_id,
            read_messages_per_day=config.read_messages_per_day,
            scroll_dialogs_per_day=config.scroll_dialogs_per_day,
            reactions_per_day=config.reactions_per_day,
            small_messages_per_day=config.small_messages_per_day,
            start_time=config.start_time,
            end_time=config.end_time,
            min_delay=config.min_delay,
            max_delay=config.max_delay,
            max_warming_days=config.max_warming_days
        )
        db.add(warming)
    
    db.commit()
    db.refresh(warming)
    
    return {
        "id": warming.id,
        "account_id": warming.account_id,
        "is_active": warming.is_active,
        "read_messages_per_day": warming.read_messages_per_day,
        "scroll_dialogs_per_day": warming.scroll_dialogs_per_day,
        "reactions_per_day": warming.reactions_per_day,
        "small_messages_per_day": warming.small_messages_per_day,
        "start_time": warming.start_time,
        "end_time": warming.end_time,
        "min_delay": warming.min_delay,
        "max_delay": warming.max_delay,
        "max_warming_days": warming.max_warming_days,
        "warming_days": warming.warming_days,
        "total_actions": warming.total_actions,
        "last_action_at": warming.last_action_at.isoformat() if warming.last_action_at else None,
        "created_at": warming.created_at.isoformat() if warming.created_at else None
    }

@app.get("/api/warming/config/{account_id}", response_model=dict)
async def get_warming_config(account_id: int, db: Session = Depends(get_db)):
    """Gibt Warming-Konfiguration für einen Account zurück"""
    warming = db.query(AccountWarming).filter(AccountWarming.account_id == account_id).first()
    if not warming:
        raise HTTPException(status_code=404, detail="Warming-Konfiguration nicht gefunden")
    
    return {
        "id": warming.id,
        "account_id": warming.account_id,
        "is_active": warming.is_active,
        "read_messages_per_day": warming.read_messages_per_day,
        "scroll_dialogs_per_day": warming.scroll_dialogs_per_day,
        "reactions_per_day": warming.reactions_per_day,
        "small_messages_per_day": warming.small_messages_per_day,
        "start_time": warming.start_time,
        "end_time": warming.end_time,
        "min_delay": warming.min_delay,
        "max_delay": warming.max_delay,
        "max_warming_days": warming.max_warming_days,
        "warming_days": warming.warming_days,
        "total_actions": warming.total_actions,
        "last_action_at": warming.last_action_at.isoformat() if warming.last_action_at else None,
        "created_at": warming.created_at.isoformat() if warming.created_at else None
    }

@app.put("/api/warming/config/{account_id}", response_model=dict)
async def update_warming_config(
    account_id: int,
    config: WarmingConfigUpdate,
    db: Session = Depends(get_db)
):
    """Aktualisiert Warming-Konfiguration"""
    warming = db.query(AccountWarming).filter(AccountWarming.account_id == account_id).first()
    if not warming:
        raise HTTPException(status_code=404, detail="Warming-Konfiguration nicht gefunden")
    
    if config.is_active is not None:
        warming.is_active = config.is_active
        if config.is_active:
            if warming_service:
                await warming_service.start_warming(warming.id)
            else:
                raise HTTPException(status_code=503, detail="Warming Service nicht verfügbar")
        else:
            if warming_service:
                await warming_service.stop_warming(warming.id)
            else:
                raise HTTPException(status_code=503, detail="Warming Service nicht verfügbar")
    
    if config.read_messages_per_day is not None:
        warming.read_messages_per_day = config.read_messages_per_day
    if config.scroll_dialogs_per_day is not None:
        warming.scroll_dialogs_per_day = config.scroll_dialogs_per_day
    if config.reactions_per_day is not None:
        warming.reactions_per_day = config.reactions_per_day
    if config.small_messages_per_day is not None:
        warming.small_messages_per_day = config.small_messages_per_day
    if config.start_time is not None:
        warming.start_time = config.start_time
    if config.end_time is not None:
        warming.end_time = config.end_time
    if config.min_delay is not None:
        warming.min_delay = config.min_delay
    if config.max_delay is not None:
        warming.max_delay = config.max_delay
    if config.max_warming_days is not None:
        warming.max_warming_days = config.max_warming_days
    
    warming.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(warming)
    
    return {
        "id": warming.id,
        "account_id": warming.account_id,
        "is_active": warming.is_active,
        "read_messages_per_day": warming.read_messages_per_day,
        "scroll_dialogs_per_day": warming.scroll_dialogs_per_day,
        "reactions_per_day": warming.reactions_per_day,
        "small_messages_per_day": warming.small_messages_per_day,
        "start_time": warming.start_time,
        "end_time": warming.end_time,
        "min_delay": warming.min_delay,
        "max_delay": warming.max_delay,
        "max_warming_days": warming.max_warming_days,
        "warming_days": warming.warming_days,
        "total_actions": warming.total_actions,
        "last_action_at": warming.last_action_at.isoformat() if warming.last_action_at else None
    }

@app.get("/api/warming/activities/{account_id}", response_model=List[dict])
async def get_warming_activities(
    account_id: int,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Gibt Warming-Aktivitäten für einen Account zurück"""
    warming = db.query(AccountWarming).filter(AccountWarming.account_id == account_id).first()
    if not warming:
        return []
    
    activities = db.query(WarmingActivity).filter(
        WarmingActivity.warming_id == warming.id
    ).order_by(WarmingActivity.executed_at.desc()).limit(limit).all()
    
    return [
        {
            "id": a.id,
            "activity_type": a.activity_type,
            "target_chat_name": a.target_chat_name,
            "message_id": a.message_id,
            "success": a.success,
            "error_message": a.error_message,
            "executed_at": a.executed_at.isoformat() if a.executed_at else None
        }
        for a in activities
    ]

@app.get("/api/warming/stats", response_model=List[dict])
async def get_all_warming_stats(db: Session = Depends(get_db)):
    """Gibt Statistiken aller Warming-Konfigurationen zurück"""
    warmings = db.query(AccountWarming).all()
    
    result = []
    for warming in warmings:
        account = db.query(Account).filter(Account.id == warming.account_id).first()
        if account:
            result.append({
                "account_id": warming.account_id,
                "account_name": account.name,
                "is_active": warming.is_active,
                "warming_days": warming.warming_days,
                "max_warming_days": warming.max_warming_days,
                "total_actions": warming.total_actions,
                "last_action_at": warming.last_action_at.isoformat() if warming.last_action_at else None,
                "progress": min(warming.warming_days / warming.max_warming_days, 1.0) if warming.max_warming_days > 0 else 0
            })
    
    return result

# Message Templates Endpoints
@app.post("/api/message-templates", response_model=dict)
async def create_message_template(
    template: MessageTemplateCreate,
    db: Session = Depends(get_db)
):
    """Erstellt eine Nachrichtenvorlage"""
    db_template = MessageTemplate(
        name=template.name,
        message=template.message,
        category=template.category,
        tags=json.dumps(template.tags) if template.tags else None
    )
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    return {
        "id": db_template.id,
        "name": db_template.name,
        "message": db_template.message,
        "category": db_template.category,
        "tags": json.loads(db_template.tags) if db_template.tags else [],
        "usage_count": db_template.usage_count,
        "is_active": db_template.is_active,
        "created_at": db_template.created_at.isoformat() if db_template.created_at else None
    }

@app.get("/api/message-templates", response_model=List[dict])
async def list_message_templates(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Listet Nachrichtenvorlagen"""
    query = db.query(MessageTemplate)
    
    if category:
        query = query.filter(MessageTemplate.category == category)
    if is_active is not None:
        query = query.filter(MessageTemplate.is_active == is_active)
    
    templates = query.order_by(MessageTemplate.usage_count.desc(), MessageTemplate.created_at.desc()).all()
    
    return [
        {
            "id": t.id,
            "name": t.name,
            "message": t.message,
            "category": t.category,
            "tags": json.loads(t.tags) if t.tags else [],
            "usage_count": t.usage_count,
            "is_active": t.is_active,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None
        }
        for t in templates
    ]

@app.get("/api/message-templates/{template_id}", response_model=dict)
async def get_message_template(template_id: int, db: Session = Depends(get_db)):
    """Gibt eine Nachrichtenvorlage zurück"""
    template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Vorlage nicht gefunden")
    
    return {
        "id": template.id,
        "name": template.name,
        "message": template.message,
        "category": template.category,
        "tags": json.loads(template.tags) if template.tags else [],
        "usage_count": template.usage_count,
        "is_active": template.is_active,
        "created_at": template.created_at.isoformat() if template.created_at else None,
        "updated_at": template.updated_at.isoformat() if template.updated_at else None
    }

@app.put("/api/message-templates/{template_id}", response_model=dict)
async def update_message_template(
    template_id: int,
    template: MessageTemplateUpdate,
    db: Session = Depends(get_db)
):
    """Aktualisiert eine Nachrichtenvorlage"""
    db_template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Vorlage nicht gefunden")
    
    if template.name is not None:
        db_template.name = template.name
    if template.message is not None:
        db_template.message = template.message
    if template.category is not None:
        db_template.category = template.category
    if template.tags is not None:
        db_template.tags = json.dumps(template.tags)
    if template.is_active is not None:
        db_template.is_active = template.is_active
    
    db_template.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_template)
    
    return {
        "id": db_template.id,
        "name": db_template.name,
        "message": db_template.message,
        "category": db_template.category,
        "tags": json.loads(db_template.tags) if db_template.tags else [],
        "usage_count": db_template.usage_count,
        "is_active": db_template.is_active
    }

@app.delete("/api/message-templates/{template_id}")
async def delete_message_template(template_id: int, db: Session = Depends(get_db)):
    """Löscht eine Nachrichtenvorlage"""
    template = db.query(MessageTemplate).filter(MessageTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Vorlage nicht gefunden")
    
    db.delete(template)
    db.commit()
    
    return {"success": True}

@app.post("/api/message-templates/from-message", response_model=dict)
async def create_template_from_message(
    request: CreateTemplateFromMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Erstellt eine Nachrichtenvorlage aus einer Nachricht per Message ID
    
    Unterstützt Premium Emotes und alle Nachrichtentypen (Text, Media, etc.)
    """
    account = db.query(Account).filter(Account.id == request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.account_type != "user":
        raise HTTPException(status_code=400, detail="Nur User-Accounts können Nachrichten laden")
    
    # Lade Nachricht
    try:
        # Konvertiere message_id zu int
        message_id = int(request.message_id)
        
        # Lade Nachricht über account_manager
        # Verwende die gleiche Logik wie forward_message_by_id
        if request.account_id not in account_manager.clients:
            raise HTTPException(status_code=400, detail="Account nicht verbunden")
        
        client = account_manager.clients[request.account_id]
        
        # Lade Source Entity
        try:
            source_entity = await client.get_entity(request.source_group)
        except Exception as e:
            # Versuche als Chat-ID zu konvertieren
            try:
                chat_id_int = int(request.source_group)
                source_entity = await client.get_entity(chat_id_int)
            except:
                raise HTTPException(status_code=404, detail=f"Quell-Gruppe nicht gefunden: {request.source_group}")
        
        # Lade Nachricht
        try:
            result = await client.get_messages(source_entity, ids=message_id)
            
            # Prüfe ob es eine Liste ist
            if isinstance(result, list):
                if len(result) > 0:
                    message = result[0]
                else:
                    raise HTTPException(status_code=404, detail=f"Nachricht mit ID {message_id} nicht gefunden")
            else:
                message = result
            
            if not message:
                # Versuche über iter_messages
                found = False
                async for msg in client.iter_messages(source_entity, limit=10000):
                    if msg.id == message_id:
                        message = msg
                        found = True
                        break
                
                if not found:
                    raise HTTPException(status_code=404, detail=f"Nachricht mit ID {message_id} nicht gefunden")
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Fehler beim Laden der Nachricht: {str(e)}")
        
        # Extrahiere Nachrichtentext
        # Unterstützt Premium Emotes (werden als Unicode-Zeichen gespeichert)
        message_text = ""
        
        # Telethon Message-Objekte haben verschiedene Attribute für Text
        # Wir versuchen alle möglichen Quellen, um Premium Emotes zu erhalten
        
        # 1. Versuche raw_text (enthält alle Zeichen inkl. Premium Emotes)
        if hasattr(message, 'raw_text') and message.raw_text:
            message_text = message.raw_text
        # 2. Versuche message (Standard-Text)
        elif hasattr(message, 'message') and message.message:
            message_text = message.message
        # 3. Versuche text (Alternative)
        elif hasattr(message, 'text') and message.text:
            message_text = message.text
        # 4. Versuche Text aus Entities zu extrahieren (für komplexe Nachrichten)
        elif hasattr(message, 'entities') and message.entities and hasattr(message, 'message'):
            # Verwende message, da entities nur Formatierungen enthalten
            message_text = message.message or ""
        
        # Falls keine Text-Nachricht, erstelle Beschreibung
        if not message_text or message_text.strip() == "":
            # Erstelle Beschreibung basierend auf Nachrichtentyp
            if hasattr(message, 'media') and message.media:
                media_type = message.media.__class__.__name__
                # Versuche zusätzliche Info zu extrahieren
                if hasattr(message.media, 'photo'):
                    message_text = "[Foto]"
                elif hasattr(message.media, 'document'):
                    if hasattr(message.media.document, 'mime_type'):
                        if 'image' in message.media.document.mime_type:
                            message_text = "[Bild]"
                        elif 'video' in message.media.document.mime_type:
                            message_text = "[Video]"
                        else:
                            message_text = f"[Datei: {message.media.document.mime_type}]"
                    else:
                        message_text = "[Datei]"
                else:
                    message_text = f"[Media: {media_type}]"
            else:
                message_text = "[Nachricht ohne Text]"
        
        # Stelle sicher, dass Premium Emotes erhalten bleiben
        # raw_text sollte bereits alle Unicode-Zeichen enthalten
        # Falls nicht, verwende message (sollte auch Premium Emotes enthalten)
        
        # Erstelle Vorlage
        db_template = MessageTemplate(
            name=request.template_name,
            message=message_text,  # Enthält Premium Emotes als Unicode
            category=request.category,
            tags=json.dumps(request.tags) if request.tags else None
        )
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        
        return {
            "success": True,
            "id": db_template.id,
            "name": db_template.name,
            "message": db_template.message,
            "category": db_template.category,
            "tags": json.loads(db_template.tags) if db_template.tags else [],
            "usage_count": db_template.usage_count,
            "is_active": db_template.is_active,
            "created_at": db_template.created_at.isoformat() if db_template.created_at else None,
            "message_preview": message_text[:200] + "..." if len(message_text) > 200 else message_text
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Erstellen der Vorlage aus Nachricht: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Fehler beim Erstellen der Vorlage: {str(e)}")

# Sent Messages History Endpoints
@app.get("/api/sent-messages", response_model=List[dict])
async def list_sent_messages(
    account_id: Optional[int] = None,
    group_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Listet gesendete Nachrichten"""
    query = db.query(SentMessage)
    
    if account_id:
        query = query.filter(SentMessage.account_id == account_id)
    if group_id:
        query = query.filter(SentMessage.group_id == group_id)
    
    messages = query.order_by(SentMessage.sent_at.desc()).limit(limit).all()
    
    return [
        {
            "id": m.id,
            "account_id": m.account_id,
            "group_id": m.group_id,
            "group_name": m.group_name,
            "message": m.message,
            "template_id": m.message_template_id,
            "success": m.success,
            "error_message": m.error_message,
            "sent_at": m.sent_at.isoformat() if m.sent_at else None,
            "telegram_message_id": m.telegram_message_id
        }
        for m in messages
    ]

@app.get("/api/accounts/{account_id}/statistics", response_model=dict)
async def get_account_statistics_endpoint(account_id: int, db: Session = Depends(get_db)):
    """Gibt Statistiken für einen Account zurück"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    stats = get_account_statistics(db, account_id)
    
    return {
        "account_id": account_id,
        "account_name": account.name,
        **stats
    }

# Proxy Management Endpoints
@app.post("/api/proxies", response_model=dict)
async def create_proxy(proxy: ProxyCreate, db: Session = Depends(get_db)):
    """Erstellt einen neuen Proxy"""
    # Verschlüssele sensible Daten
    encrypted_password = encrypt_string(proxy.password) if proxy.password else None
    encrypted_secret = encrypt_string(proxy.secret) if proxy.secret else None
    
    db_proxy = Proxy(
        name=proxy.name,
        proxy_type=proxy.proxy_type,
        host=proxy.host,
        port=proxy.port,
        username=proxy.username,
        password=encrypted_password,
        secret=encrypted_secret,
        country=proxy.country,
        notes=proxy.notes
    )
    db.add(db_proxy)
    db.commit()
    db.refresh(db_proxy)
    
    return {
        "id": db_proxy.id,
        "name": db_proxy.name,
        "proxy_type": db_proxy.proxy_type,
        "host": db_proxy.host,
        "port": db_proxy.port,
        "username": db_proxy.username,
        "country": db_proxy.country,
        "is_active": db_proxy.is_active,
        "is_verified": db_proxy.is_verified,
        "usage_count": db_proxy.usage_count,
        "created_at": db_proxy.created_at.isoformat() if db_proxy.created_at else None
    }

@app.get("/api/proxies", response_model=List[dict])
async def list_proxies(
    is_active: Optional[bool] = None,
    proxy_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Listet alle Proxies"""
    query = db.query(Proxy)
    
    if is_active is not None:
        query = query.filter(Proxy.is_active == is_active)
    if proxy_type:
        query = query.filter(Proxy.proxy_type == proxy_type)
    
    proxies = query.order_by(Proxy.usage_count.desc(), Proxy.created_at.desc()).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "proxy_type": p.proxy_type,
            "host": p.host,
            "port": p.port,
            "username": p.username,
            "country": p.country,
            "is_active": p.is_active,
            "is_verified": p.is_verified,
            "usage_count": p.usage_count,
            "last_used": p.last_used.isoformat() if p.last_used else None,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in proxies
    ]

@app.get("/api/proxies/{proxy_id}", response_model=dict)
async def get_proxy(proxy_id: int, db: Session = Depends(get_db)):
    """Gibt einen Proxy zurück"""
    proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy nicht gefunden")
    
    # Proxy-Passwörter und Secrets niemals in API-Responses zurückgeben
    return {
        "id": proxy.id,
        "name": proxy.name,
        "proxy_type": proxy.proxy_type,
        "host": proxy.host,
        "port": proxy.port,
        "username": proxy.username,
        # password und secret werden aus Sicherheitsgründen nicht zurückgegeben
        "country": proxy.country,
        "is_active": proxy.is_active,
        "is_verified": proxy.is_verified,
        "usage_count": proxy.usage_count,
        "last_used": proxy.last_used.isoformat() if proxy.last_used else None,
        "created_at": proxy.created_at.isoformat() if proxy.created_at else None,
        "notes": proxy.notes
    }

@app.put("/api/proxies/{proxy_id}", response_model=dict)
async def update_proxy(
    proxy_id: int,
    proxy: ProxyUpdate,
    db: Session = Depends(get_db)
):
    """Aktualisiert einen Proxy"""
    db_proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
    if not db_proxy:
        raise HTTPException(status_code=404, detail="Proxy nicht gefunden")
    
    if proxy.name is not None:
        db_proxy.name = proxy.name
    if proxy.proxy_type is not None:
        db_proxy.proxy_type = proxy.proxy_type
    if proxy.host is not None:
        db_proxy.host = proxy.host
    if proxy.port is not None:
        db_proxy.port = proxy.port
    if proxy.username is not None:
        db_proxy.username = proxy.username
    if proxy.password is not None:
        db_proxy.password = encrypt_string(proxy.password) if proxy.password else None
    if proxy.secret is not None:
        db_proxy.secret = encrypt_string(proxy.secret) if proxy.secret else None
    if proxy.country is not None:
        db_proxy.country = proxy.country
    if proxy.is_active is not None:
        db_proxy.is_active = proxy.is_active
    if proxy.is_verified is not None:
        db_proxy.is_verified = proxy.is_verified
    if proxy.notes is not None:
        db_proxy.notes = proxy.notes
    
    db.commit()
    db.refresh(db_proxy)
    
    return {
        "id": db_proxy.id,
        "name": db_proxy.name,
        "proxy_type": db_proxy.proxy_type,
        "host": db_proxy.host,
        "port": db_proxy.port,
        "is_active": db_proxy.is_active,
        "is_verified": db_proxy.is_verified
    }

@app.delete("/api/proxies/{proxy_id}")
async def delete_proxy(proxy_id: int, db: Session = Depends(get_db)):
    """Löscht einen Proxy"""
    proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy nicht gefunden")
    
    # Prüfe ob Proxy noch verwendet wird
    accounts_using = db.query(Account).filter(Account.proxy_id == proxy_id).count()
    if accounts_using > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Proxy wird noch von {accounts_using} Account(s) verwendet"
        )
    
    db.delete(proxy)
    db.commit()
    
    return {"success": True}

@app.post("/api/proxies/bulk", response_model=dict)
async def bulk_create_proxies(bulk: BulkProxyCreate, db: Session = Depends(get_db)):
    """Erstellt mehrere Proxies auf einmal"""
    results = {
        "total": len(bulk.proxies),
        "success": 0,
        "failed": 0,
        "errors": []
    }
    
    for proxy_data in bulk.proxies:
        try:
            if not proxy_data.get("name") or not proxy_data.get("host") or not proxy_data.get("port"):
                results["failed"] += 1
                results["errors"].append({
                    "proxy": proxy_data.get("name", "Unbekannt"),
                    "error": "Name, Host und Port erforderlich"
                })
                continue
            
            # Verschlüssele sensible Daten
            encrypted_password = encrypt_string(proxy_data.get("password")) if proxy_data.get("password") else None
            encrypted_secret = encrypt_string(proxy_data.get("secret")) if proxy_data.get("secret") else None
            
            db_proxy = Proxy(
                name=proxy_data["name"],
                proxy_type=proxy_data.get("proxy_type", "socks5"),
                host=proxy_data["host"],
                port=int(proxy_data["port"]),
                username=proxy_data.get("username"),
                password=encrypted_password,
                secret=encrypted_secret,
                country=proxy_data.get("country"),
                notes=proxy_data.get("notes")
            )
            db.add(db_proxy)
            db.commit()
            db.refresh(db_proxy)
            
            results["success"] += 1
        
        except Exception as e:
            db.rollback()
            logger.error(f"Fehler beim Erstellen von Proxy '{proxy_data.get('name', 'Unbekannt')}': {str(e)}", exc_info=True)
            results["failed"] += 1
            results["errors"].append({
                "proxy": proxy_data.get("name", "Unbekannt"),
                "error": "Fehler beim Erstellen des Proxys"
            })
    
    return results

@app.post("/api/proxies/{proxy_id}/test", response_model=dict)
async def test_proxy(proxy_id: int, db: Session = Depends(get_db)):
    """Testet einen Proxy (vereinfachter Test)"""
    proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
    if not proxy:
        raise HTTPException(status_code=404, detail="Proxy nicht gefunden")
    
    # Einfacher Test: Versuche Verbindung (könnte erweitert werden)
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((proxy.host, proxy.port))
        sock.close()
        
        if result == 0:
            proxy.is_verified = True
            db.commit()
            return {"success": True, "message": "Proxy erreichbar"}
        else:
            return {"success": False, "message": "Proxy nicht erreichbar"}
    except Exception as e:
        logger.error(f"Fehler beim Testen des Proxys {proxy_id}: {str(e)}", exc_info=True)
        return {"success": False, "error": "Proxy-Test fehlgeschlagen"}

@app.put("/api/accounts/{account_id}/proxy", response_model=dict)
async def assign_proxy_to_account(
    account_id: int,
    proxy_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Weist einem Account einen Proxy zu oder entfernt ihn"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.account_type != "user":
        raise HTTPException(status_code=400, detail="Nur User-Accounts können Proxies verwenden")
    
    if proxy_id:
        proxy = db.query(Proxy).filter(Proxy.id == proxy_id).first()
        if not proxy:
            raise HTTPException(status_code=404, detail="Proxy nicht gefunden")
        account.proxy_id = proxy_id
    else:
        account.proxy_id = None
    
    db.commit()
    db.refresh(account)
    
    return {
        "account_id": account_id,
        "proxy_id": account.proxy_id,
        "message": "Proxy zugewiesen" if proxy_id else "Proxy entfernt"
    }

@app.post("/api/accounts/{account_id}/create-bot", response_model=dict)
async def create_bot_via_account(
    account_id: int,
    request: CreateBotViaAccountRequest,
    db: Session = Depends(get_db)
):
    """
    Erstellt einen neuen Bot über einen User-Account via BotFather
    
    Args:
        account_id: ID des User-Accounts, der den Bot erstellen soll
        request: Bot-Name und Username
    """
    # Prüfe ob Account existiert und User-Account ist
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.account_type != "user":
        raise HTTPException(status_code=400, detail="Nur User-Accounts können Bots erstellen")
    
    # Prüfe ob Account verbunden ist
    account_info = await account_manager.get_account_info(account_id)
    if not account_info:
        raise HTTPException(status_code=400, detail="Account nicht verbunden. Bitte zuerst verbinden.")
    
    # Validiere und bereinige Bot-Username
    bot_username = request.bot_username.lower()
    # Entferne ungültige Zeichen (nur a-z, 0-9, _ erlaubt)
    bot_username = ''.join(c for c in bot_username if c.isalnum() or c == '_')
    # Stelle sicher, dass Username auf "_bot" endet (nicht nur "bot")
    if not bot_username.endswith("_bot"):
        # Entferne "bot" oder "_bot" falls bereits vorhanden
        bot_username = bot_username.rstrip("_bot").rstrip("bot")
        bot_username = bot_username + "_bot"
    # Stelle sicher, dass Username zwischen 5 und 32 Zeichen lang ist
    if len(bot_username) < 5:
        padding_needed = 5 - len(bot_username)
        bot_username = bot_username[:-4] + "0" * padding_needed + "_bot"
    elif len(bot_username) > 32:
        max_base_length = 28  # 32 - 4 ("_bot")
        bot_username = bot_username[:max_base_length] + "_bot"
    
    # Erstelle Bot über BotFather
    result = await account_manager.create_bot_via_botfather(
        account_id=account_id,
        bot_name=request.bot_name,
        bot_username=bot_username
    )
    
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Fehler beim Erstellen des Bots")
        )
    
    bot_token = result.get("bot_token")
    if not bot_token:
        raise HTTPException(status_code=400, detail="Bot-Token nicht erhalten")
    
    # Erstelle Bot-Account in Datenbank
    bot_account = Account(
        name=request.bot_name,
        account_type="bot",
        bot_token=bot_token
    )
    db.add(bot_account)
    db.commit()
    db.refresh(bot_account)
    
    # Verbinde Bot
    bot_result = await bot_manager.add_bot(
        bot_id=bot_account.id,
        bot_token=bot_token
    )
    
    return {
        "success": True,
        "account_id": bot_account.id,
        "bot_token": bot_token,
        "bot_name": request.bot_name,
        "bot_username": request.bot_username,
        "bot_info": bot_result.get("info"),
        "message": "Bot erfolgreich erstellt und verbunden"
    }

@app.post("/api/accounts/{account_id}/bulk-create-bots", response_model=dict)
async def bulk_create_bots_via_account(
    account_id: int,
    request: BulkCreateBotsViaAccountRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Erstellt mehrere Bots über einen User-Account via BotFather mit automatisch generierten Namen
    
    Args:
        account_id: ID des User-Accounts, der die Bots erstellen soll
        request: Anzahl, Name-Präfix, Username-Präfix, Delay
    
    Returns:
        Dict mit Statistiken und erstellten Bots
    """
    from telethon.errors import FloodWaitError
    
    # Prüfe ob Account existiert und User-Account ist
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    # Prüfe ob Account dem aktuellen User gehört
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Account gehört nicht zum aktuellen Benutzer")
    
    if account.account_type != "user":
        raise HTTPException(status_code=400, detail="Nur User-Accounts können Bots erstellen")
    
    # Prüfe ob Account verbunden ist
    account_info = await account_manager.get_account_info(account_id)
    if not account_info:
        raise HTTPException(status_code=400, detail="Account nicht verbunden. Bitte zuerst verbinden.")
    
    # Prüfe Account-Limit
    account_count = db.query(Account).filter(Account.user_id == current_user.id).count()
    if not check_account_limit(current_user, account_count + request.count):
        raise HTTPException(
            status_code=403,
            detail=f"Account-Limit würde überschritten. Maximal {current_user.subscription.max_accounts if current_user.subscription else 1} Accounts erlaubt."
        )
    
    results = {
        "total": request.count,
        "success": 0,
        "failed": 0,
        "bots": [],
        "errors": []
    }
    
    for i in range(1, request.count + 1):
        # Generiere automatische Namen
        bot_name = f"{request.name_prefix} {i}"
        
        # Generiere Bot-Username gemäß Telegram-Richtlinien:
        # - Muss auf "_bot" enden
        # - Nur a-z, 0-9, _ erlaubt
        # - 5-32 Zeichen lang
        # - Eindeutig (mit fortlaufender Nummer)
        
        # Bereinige Username-Präfix: nur Kleinbuchstaben, Zahlen, Unterstriche
        clean_prefix = ''.join(c for c in request.username_prefix.lower() if c.isalnum() or c == '_')
        if not clean_prefix:
            clean_prefix = "bot"
        
        # Erstelle Username: prefix_i (mit fortlaufender Nummer statt Timestamp)
        # Format: prefix_i_bot
        username_base = f"{clean_prefix}_{i}"
        
        # Stelle sicher, dass Username auf "_bot" endet (nicht nur "bot")
        if not username_base.endswith("_bot"):
            # Entferne "bot" oder "_bot" falls bereits vorhanden
            username_base = username_base.rstrip("_bot").rstrip("bot")
            # Füge "_bot" hinzu
            bot_username = username_base + "_bot"
        else:
            bot_username = username_base
        
        # Kürze auf max 32 Zeichen (Telegram Limit)
        if len(bot_username) > 32:
            # Kürze den Base-Teil, behalte "_bot" Endung
            max_base_length = 28  # 32 - 4 ("_bot")
            bot_username = bot_username[:max_base_length] + "_bot"
        
        # Stelle sicher, dass Username mindestens 5 Zeichen hat
        if len(bot_username) < 5:
            # Füge Ziffern hinzu falls zu kurz
            padding = "0" * (5 - len(bot_username))
            bot_username = bot_username[:-4] + padding + "_bot"  # Füge vor "_bot" ein
        
        # Finale Validierung: nur a-z, 0-9, _
        bot_username = ''.join(c for c in bot_username if c.isalnum() or c == '_')
        # Stelle sicher, dass Username auf "_bot" endet (nicht nur "bot")
        if not bot_username.endswith("_bot"):
            # Entferne "bot" oder "_bot" falls bereits vorhanden
            bot_username = bot_username.rstrip("_bot").rstrip("bot")
            bot_username = bot_username + "_bot"
        
        try:
            # Erstelle Bot über BotFather
            result = await account_manager.create_bot_via_botfather(
                account_id=account_id,
                bot_name=bot_name,
                bot_username=bot_username
            )
            
            if result.get("success") and result.get("bot_token"):
                bot_token = result.get("bot_token")
                
                # Erstelle Bot-Account in Datenbank
                bot_account = Account(
                    user_id=current_user.id,
                    name=bot_name,
                    account_type="bot",
                    bot_token=bot_token
                )
                db.add(bot_account)
                db.commit()
                db.refresh(bot_account)
                
                # Verbinde Bot
                bot_result = await bot_manager.add_bot(
                    bot_id=bot_account.id,
                    bot_token=bot_token
                )
                
                if bot_result.get("status") == "connected":
                    results["success"] += 1
                    results["bots"].append({
                        "id": bot_account.id,
                        "name": bot_name,
                        "username": bot_username,
                        "token": bot_token[:30] + "..." if len(bot_token) > 30 else bot_token,
                        "info": bot_result.get("info")
                    })
                else:
                    results["failed"] += 1
                    results["errors"].append({
                        "bot": bot_name,
                        "error": f"Verbindung fehlgeschlagen: {bot_result.get('error')}"
                    })
            else:
                error_msg = result.get("error", "Unbekannter Fehler")
                results["failed"] += 1
                results["errors"].append({
                    "bot": bot_name,
                    "error": error_msg
                })
            
            # Rate Limiting: Warte zwischen Bot-Erstellungen
            if i < request.count:
                await asyncio.sleep(request.delay_between_bots)
        
        except FloodWaitError as e:
            results["failed"] += 1
            results["errors"].append({
                "bot": bot_name,
                "error": f"FloodWait: {e.seconds} Sekunden warten",
                "wait_seconds": e.seconds
            })
            await asyncio.sleep(e.seconds)
        
        except Exception as e:
            logger.error(f"Fehler beim Erstellen von Bot '{bot_name}': {str(e)}", exc_info=True)
            results["failed"] += 1
            results["errors"].append({
                "bot": bot_name,
                "error": str(e)
            })
            await asyncio.sleep(request.delay_between_bots)
    
    return {
        "success": results["success"] > 0,
        "total": results["total"],
        "created": results["success"],
        "failed": results["failed"],
        "bots": results["bots"],
        "errors": results["errors"],
        "message": f"{results['success']} von {results['total']} Bots erfolgreich erstellt"
    }

@app.post("/api/groups/{group_id}/update-chat-id", response_model=dict)
async def update_group_chat_id(
    group_id: int,
    account_id: int = Query(..., description="Account-ID zum Suchen der Gruppe"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Aktualisiert die Chat-ID einer Gruppe, indem die Dialoge des Accounts durchsucht werden
    
    Args:
        group_id: ID der Gruppe in der Datenbank
        account_id: Account-ID zum Suchen der Gruppe in Dialogen
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Account gehört nicht zum aktuellen Benutzer")
    
    if account.account_type != "user":
        raise HTTPException(status_code=400, detail="Nur User-Accounts können Gruppen aktualisieren")
    
    # Prüfe ob Account verbunden ist
    account_info = await account_manager.get_account_info(account_id)
    if not account_info:
        raise HTTPException(status_code=400, detail="Account nicht verbunden. Bitte zuerst verbinden.")
    
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Gruppe nicht gefunden")
    
    # Suche Gruppe in Dialogen
    found_dialog = await account_manager.find_group_in_dialogs(
        account_id=account_id,
        group_name=group.name,
        group_chat_id=group.chat_id
    )
    
    if not found_dialog:
        raise HTTPException(
            status_code=404,
            detail=f"Gruppe '{group.name}' nicht in den Dialogen des Accounts gefunden. Möglicherweise ist der Account nicht in der Gruppe."
        )
    
    # Aktualisiere Chat-ID
    old_chat_id = group.chat_id
    new_chat_id = str(found_dialog.get("id"))
    
    if old_chat_id != new_chat_id:
        group.chat_id = new_chat_id
        if found_dialog.get("username"):
            group.username = found_dialog.get("username")
        if found_dialog.get("type"):
            group.chat_type = found_dialog.get("type")
        group.last_checked = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "Chat-ID erfolgreich aktualisiert",
            "old_chat_id": old_chat_id,
            "new_chat_id": new_chat_id,
            "group_id": group.id,
            "group_name": group.name
        }
    else:
        return {
            "success": True,
            "message": "Chat-ID ist bereits aktuell",
            "chat_id": old_chat_id,
            "group_id": group.id,
            "group_name": group.name
        }

@app.post("/api/groups/check-exists", response_model=dict)
async def check_group_exists_endpoint(
    request: CheckGroupRequest,
    db: Session = Depends(get_db)
):
    """
    Prüft ob eine Gruppe existiert und gibt Informationen zurück
    """
    account = db.query(Account).filter(Account.id == request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.account_type != "user":
        raise HTTPException(status_code=400, detail="Nur User-Accounts können Gruppen prüfen")
    
    result = await account_manager.check_group_exists(
        account_id=request.account_id,
        group_entity=request.group_entity
    )
    
    return result

@app.post("/api/groups/check-bot-can-be-added", response_model=dict)
async def check_bot_can_be_added_endpoint(
    request: CheckBotCanBeAddedRequest,
    db: Session = Depends(get_db)
):
    """
    Prüft ob ein Bot zu einer Gruppe hinzugefügt werden kann
    
    Prüft:
    - Ob Gruppe existiert
    - Ob Account Admin ist
    - Ob Bot existiert
    - Ob Bot bereits in Gruppe ist
    - Ob Bot hinzugefügt werden kann
    """
    account = db.query(Account).filter(Account.id == request.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account nicht gefunden")
    
    if account.account_type != "user":
        raise HTTPException(status_code=400, detail="Nur User-Accounts können Bots prüfen")
    
    result = await account_manager.check_bot_can_be_added(
        account_id=request.account_id,
        group_entity=request.group_entity,
        bot_username=request.bot_username,
        bot_id=request.bot_id
    )
    
    return result

# ============================================
# ADMIN ENDPOINTS
# ============================================

# Admin Models
class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

class SystemSettingUpdate(BaseModel):
    value: str
    description: Optional[str] = None

class SystemSettingCreate(BaseModel):
    key: str
    value: str
    value_type: str = "string"
    description: Optional[str] = None
    category: str = "general"

# Admin: Benutzerverwaltung
@app.get("/api/admin/users", response_model=List[dict])
async def admin_list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Listet alle Benutzer (nur Admin)"""
    users = db.query(User).offset(skip).limit(limit).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "username": u.username,
            "is_active": u.is_active,
            "is_admin": u.is_admin,
            "created_at": u.created_at.isoformat() if u.created_at else None,
            "last_login": u.last_login.isoformat() if u.last_login else None,
            "subscription": {
                "plan_type": u.subscription.plan_type if u.subscription else None,
                "status": u.subscription.status if u.subscription else None,
                "expires_at": u.subscription.expires_at.isoformat() if u.subscription and u.subscription.expires_at else None
            } if u.subscription else None,
            "account_count": u.accounts.count(),
            "group_count": u.groups.count()
        }
        for u in users
    ]

@app.get("/api/admin/users/{user_id}", response_model=dict)
async def admin_get_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Gibt Details eines Benutzers zurück (nur Admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "is_active": user.is_active,
        "is_admin": user.is_admin,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "subscription": {
            "plan_type": user.subscription.plan_type if user.subscription else None,
            "status": user.subscription.status if user.subscription else None,
            "expires_at": user.subscription.expires_at.isoformat() if user.subscription and user.subscription.expires_at else None,
            "max_accounts": user.subscription.max_accounts if user.subscription else None,
            "max_groups": user.subscription.max_groups if user.subscription else None,
            "max_messages_per_day": user.subscription.max_messages_per_day if user.subscription else None
        } if user.subscription else None,
        "account_count": user.accounts.count(),
        "group_count": user.groups.count()
    }

@app.put("/api/admin/users/{user_id}", response_model=dict)
async def admin_update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Aktualisiert einen Benutzer (nur Admin)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    
    # Verhindere dass Admin sich selbst deaktiviert
    if user_id == current_user.id and user_update.is_admin == False:
        raise HTTPException(status_code=400, detail="Du kannst dir nicht selbst Admin-Rechte entziehen")
    
    if user_update.email is not None:
        # Prüfe ob Email bereits existiert
        existing = db.query(User).filter(User.email == user_update.email, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email bereits vergeben")
        user.email = user_update.email
    
    if user_update.username is not None:
        # Prüfe ob Username bereits existiert
        existing = db.query(User).filter(User.username == user_update.username, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username bereits vergeben")
        user.username = user_update.username
    
    if user_update.password is not None:
        user.password_hash = get_password_hash(user_update.password)
    
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    
    if user_update.is_admin is not None:
        user.is_admin = user_update.is_admin
    
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_active": user.is_active,
            "is_admin": user.is_admin
        }
    }

@app.delete("/api/admin/users/{user_id}", response_model=dict)
async def admin_delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Löscht einen Benutzer (nur Admin)"""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Du kannst dich nicht selbst löschen")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Benutzer nicht gefunden")
    
    db.delete(user)
    db.commit()
    
    return {"success": True, "message": "Benutzer gelöscht"}

# Admin: System-Einstellungen
@app.get("/api/admin/settings", response_model=List[dict])
async def admin_list_settings(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Listet alle System-Einstellungen (nur Admin)"""
    query = db.query(SystemSettings)
    if category:
        query = query.filter(SystemSettings.category == category)
    
    settings = query.order_by(SystemSettings.category, SystemSettings.key).all()
    return [
        {
            "id": s.id,
            "key": s.key,
            "value": s.value,
            "value_type": s.value_type,
            "description": s.description,
            "category": s.category,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            "updated_by": s.updated_by
        }
        for s in settings
    ]

@app.get("/api/admin/settings/{key}", response_model=dict)
async def admin_get_setting(
    key: str,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Gibt eine System-Einstellung zurück (nur Admin)"""
    setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Einstellung nicht gefunden")
    
    return {
        "id": setting.id,
        "key": setting.key,
        "value": setting.value,
        "value_type": setting.value_type,
        "description": setting.description,
        "category": setting.category,
        "updated_at": setting.updated_at.isoformat() if setting.updated_at else None,
        "updated_by": setting.updated_by
    }

@app.post("/api/admin/settings", response_model=dict)
async def admin_create_setting(
    setting: SystemSettingCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Erstellt eine neue System-Einstellung (nur Admin)"""
    existing = db.query(SystemSettings).filter(SystemSettings.key == setting.key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Einstellung mit diesem Key existiert bereits")
    
    new_setting = SystemSettings(
        key=setting.key,
        value=setting.value,
        value_type=setting.value_type,
        description=setting.description,
        category=setting.category,
        updated_by=current_user.id
    )
    db.add(new_setting)
    db.commit()
    db.refresh(new_setting)
    
    return {
        "success": True,
        "setting": {
            "id": new_setting.id,
            "key": new_setting.key,
            "value": new_setting.value,
            "value_type": new_setting.value_type,
            "description": new_setting.description,
            "category": new_setting.category
        }
    }

@app.put("/api/admin/settings/{key}", response_model=dict)
async def admin_update_setting(
    key: str,
    setting_update: SystemSettingUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Aktualisiert eine System-Einstellung (nur Admin)"""
    setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Einstellung nicht gefunden")
    
    setting.value = setting_update.value
    if setting_update.description is not None:
        setting.description = setting_update.description
    setting.updated_by = current_user.id
    setting.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(setting)
    
    return {
        "success": True,
        "setting": {
            "id": setting.id,
            "key": setting.key,
            "value": setting.value,
            "value_type": setting.value_type,
            "description": setting.description,
            "category": setting.category,
            "updated_at": setting.updated_at.isoformat() if setting.updated_at else None
        }
    }

@app.delete("/api/admin/settings/{key}", response_model=dict)
async def admin_delete_setting(
    key: str,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Löscht eine System-Einstellung (nur Admin)"""
    setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Einstellung nicht gefunden")
    
    db.delete(setting)
    db.commit()
    
    return {"success": True, "message": "Einstellung gelöscht"}

# Admin: API-Einstellungen (Telegram API, Provider APIs, etc.)
@app.get("/api/admin/api-settings", response_model=dict)
async def admin_get_api_settings(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Gibt alle API-Einstellungen zurück (nur Admin)"""
    # Lade aus SystemSettings oder Umgebungsvariablen
    api_settings = {}
    
    # Telegram API
    telegram_api_id = db.query(SystemSettings).filter(SystemSettings.key == "telegram_api_id").first()
    telegram_api_hash = db.query(SystemSettings).filter(SystemSettings.key == "telegram_api_hash").first()
    
    api_settings["telegram"] = {
        "api_id": telegram_api_id.value if telegram_api_id else os.getenv("TELEGRAM_API_ID", ""),
        "api_hash": telegram_api_hash.value if telegram_api_hash else os.getenv("TELEGRAM_API_HASH", ""),
        "source": "database" if telegram_api_id else "environment"
    }
    
    # 5sim API
    fivesim_key = db.query(SystemSettings).filter(SystemSettings.key == "fivesim_api_key").first()
    api_settings["5sim"] = {
        "api_key": fivesim_key.value if fivesim_key else os.getenv("FIVESIM_API_KEY", ""),
        "source": "database" if fivesim_key else "environment"
    }
    
    # SMS-Activate API
    sms_activate_key = db.query(SystemSettings).filter(SystemSettings.key == "sms_activate_api_key").first()
    api_settings["sms_activate"] = {
        "api_key": sms_activate_key.value if sms_activate_key else os.getenv("SMS_ACTIVATE_API_KEY", ""),
        "source": "database" if sms_activate_key else "environment"
    }
    
    # SMS-Manager API
    sms_manager_key = db.query(SystemSettings).filter(SystemSettings.key == "sms_manager_api_key").first()
    api_settings["sms_manager"] = {
        "api_key": sms_manager_key.value if sms_manager_key else os.getenv("SMS_MANAGER_API_KEY", ""),
        "source": "database" if sms_manager_key else "environment"
    }
    
    # GetSMSCode API
    getsmscode_key = db.query(SystemSettings).filter(SystemSettings.key == "getsmscode_api_key").first()
    api_settings["getsmscode"] = {
        "api_key": getsmscode_key.value if getsmscode_key else os.getenv("GETSMSCODE_API_KEY", ""),
        "source": "database" if getsmscode_key else "environment"
    }
    
    # OnlineSim API
    onlinesim_key = db.query(SystemSettings).filter(SystemSettings.key == "onlinesim_api_key").first()
    api_settings["onlinesim"] = {
        "api_key": onlinesim_key.value if onlinesim_key else os.getenv("ONLINESIM_API_KEY", ""),
        "source": "database" if onlinesim_key else "environment"
    }
    
    return api_settings

@app.put("/api/admin/api-settings", response_model=dict)
async def admin_update_api_settings(
    settings: dict,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Aktualisiert API-Einstellungen (nur Admin)"""
    results = {"updated": [], "errors": []}
    
    # Telegram API
    if "telegram" in settings:
        telegram = settings["telegram"]
        if "api_id" in telegram:
            setting = db.query(SystemSettings).filter(SystemSettings.key == "telegram_api_id").first()
            if setting:
                setting.value = str(telegram["api_id"])
                setting.updated_by = current_user.id
                setting.updated_at = datetime.utcnow()
            else:
                setting = SystemSettings(
                    key="telegram_api_id",
                    value=str(telegram["api_id"]),
                    value_type="string",
                    description="Telegram API ID",
                    category="api",
                    updated_by=current_user.id
                )
                db.add(setting)
            results["updated"].append("telegram_api_id")
        
        if "api_hash" in telegram:
            setting = db.query(SystemSettings).filter(SystemSettings.key == "telegram_api_hash").first()
            if setting:
                setting.value = telegram["api_hash"]
                setting.updated_by = current_user.id
                setting.updated_at = datetime.utcnow()
            else:
                setting = SystemSettings(
                    key="telegram_api_hash",
                    value=telegram["api_hash"],
                    value_type="string",
                    description="Telegram API Hash",
                    category="api",
                    updated_by=current_user.id
                )
                db.add(setting)
            results["updated"].append("telegram_api_hash")
    
    # 5sim API
    if "5sim" in settings and "api_key" in settings["5sim"]:
        setting = db.query(SystemSettings).filter(SystemSettings.key == "fivesim_api_key").first()
        if setting:
            setting.value = settings["5sim"]["api_key"]
            setting.updated_by = current_user.id
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSettings(
                key="fivesim_api_key",
                value=settings["5sim"]["api_key"],
                value_type="string",
                description="5sim.net API Key",
                category="api",
                updated_by=current_user.id
            )
            db.add(setting)
        results["updated"].append("fivesim_api_key")
    
    # SMS-Activate API
    if "sms_activate" in settings and "api_key" in settings["sms_activate"]:
        setting = db.query(SystemSettings).filter(SystemSettings.key == "sms_activate_api_key").first()
        if setting:
            setting.value = settings["sms_activate"]["api_key"]
            setting.updated_by = current_user.id
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSettings(
                key="sms_activate_api_key",
                value=settings["sms_activate"]["api_key"],
                value_type="string",
                description="SMS-Activate API Key",
                category="api",
                updated_by=current_user.id
            )
            db.add(setting)
        results["updated"].append("sms_activate_api_key")
    
    # SMS-Manager API
    if "sms_manager" in settings and "api_key" in settings["sms_manager"]:
        setting = db.query(SystemSettings).filter(SystemSettings.key == "sms_manager_api_key").first()
        if setting:
            setting.value = settings["sms_manager"]["api_key"]
            setting.updated_by = current_user.id
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSettings(
                key="sms_manager_api_key",
                value=settings["sms_manager"]["api_key"],
                value_type="string",
                description="SMS-Manager.com API Key",
                category="api",
                updated_by=current_user.id
            )
            db.add(setting)
        results["updated"].append("sms_manager_api_key")
    
    # GetSMSCode API
    if "getsmscode" in settings and "api_key" in settings["getsmscode"]:
        setting = db.query(SystemSettings).filter(SystemSettings.key == "getsmscode_api_key").first()
        if setting:
            setting.value = settings["getsmscode"]["api_key"]
            setting.updated_by = current_user.id
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSettings(
                key="getsmscode_api_key",
                value=settings["getsmscode"]["api_key"],
                value_type="string",
                description="GetSMSCode.com API Key (Format: username:token)",
                category="api",
                updated_by=current_user.id
            )
            db.add(setting)
        results["updated"].append("getsmscode_api_key")
    
    # OnlineSim API
    if "onlinesim" in settings and "api_key" in settings["onlinesim"]:
        setting = db.query(SystemSettings).filter(SystemSettings.key == "onlinesim_api_key").first()
        if setting:
            setting.value = settings["onlinesim"]["api_key"]
            setting.updated_by = current_user.id
            setting.updated_at = datetime.utcnow()
        else:
            setting = SystemSettings(
                key="onlinesim_api_key",
                value=settings["onlinesim"]["api_key"],
                value_type="string",
                description="OnlineSim.io API Key",
                category="api",
                updated_by=current_user.id
            )
            db.add(setting)
        results["updated"].append("onlinesim_api_key")
    
    db.commit()
    
    return {"success": True, **results}

# Admin: Statistiken
@app.get("/api/admin/stats", response_model=dict)
async def admin_get_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Gibt System-Statistiken zurück (nur Admin)"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.is_admin == True).count()
    total_accounts = db.query(Account).count()
    active_accounts = db.query(Account).filter(Account.is_active == True).count()
    total_groups = db.query(Group).count()
    total_proxies = db.query(Proxy).count()
    active_proxies = db.query(Proxy).filter(Proxy.is_active == True).count()
    total_scheduled = db.query(ScheduledMessage).count()
    pending_scheduled = db.query(ScheduledMessage).filter(ScheduledMessage.status == "pending").count()
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "admins": admin_users
        },
        "accounts": {
            "total": total_accounts,
            "active": active_accounts
        },
        "groups": {
            "total": total_groups
        },
        "proxies": {
            "total": total_proxies,
            "active": active_proxies
        },
        "scheduled_messages": {
            "total": total_scheduled,
            "pending": pending_scheduled
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

