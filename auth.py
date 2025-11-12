"""
Authentifizierung und Autorisierung
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import User, Subscription, get_session, init_db
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Lade Umgebungsvariablen aus .env
load_dotenv()

# Initialisiere DB-Engine für get_db Dependency
db_engine = init_db()

# JWT Konfiguration
import os
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY muss in Umgebungsvariablen gesetzt sein. "
        "Generiere einen sicheren Key mit: openssl rand -hex 32"
    )
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 Tage

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifiziert ein Passwort"""
    try:
        # bcrypt erwartet bytes
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        if isinstance(plain_password, str):
            plain_password = plain_password.encode('utf-8')
        return bcrypt.checkpw(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Erstellt einen Passwort-Hash"""
    if isinstance(password, str):
        password = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Erstellt ein JWT Token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_db():
    """Dependency für DB Session"""
    db = get_session(db_engine)
    try:
        yield db
    finally:
        db.close()

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Gibt den aktuellen Benutzer aus dem JWT Token zurück"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_raw = payload.get("sub")
        if user_id_raw is None:
            raise credentials_exception
        # Konvertiere zu int (kann String oder int sein)
        user_id: int = int(user_id_raw) if isinstance(user_id_raw, str) else user_id_raw
    except (JWTError, ValueError, TypeError) as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Gibt den aktuellen aktiven Benutzer zurück"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Prüft ob Benutzer Admin ist"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin-Zugriff erforderlich")
    return current_user


def check_subscription(user: User, feature: Optional[str] = None) -> bool:
    """Prüft ob Benutzer ein aktives Abonnement hat"""
    if not user.subscription:
        return False
    if not user.subscription.is_active():
        return False
    if feature:
        return user.subscription.has_feature(feature)
    return True


def check_account_limit(user: User, current_count: int) -> bool:
    """Prüft ob Benutzer noch Accounts erstellen kann"""
    if not user.subscription or not user.subscription.is_active():
        return current_count < 2  # Free Trial: 2 Accounts
    return current_count < user.subscription.max_accounts


def check_group_limit(user: User, current_count: int) -> bool:
    """Prüft ob Benutzer noch Gruppen erstellen kann"""
    if not user.subscription or not user.subscription.is_active():
        return current_count < 5  # Free Trial: 5 Gruppen
    return current_count < user.subscription.max_groups

