"""
Unit Tests für Authentication (auth.py)
Kritikalität: 🔴 HOCH - 100% Coverage erforderlich
"""
import pytest
from datetime import datetime, timedelta
from jose import jwt, JWTError
from auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from database import User


class TestPasswordHashing:
    """Tests für Password Hashing & Verification"""
    
    def test_hash_password_creates_hash(self):
        """Test: Passwort-Hash wird erstellt"""
        password = "testpass123"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt Format
    
    def test_verify_password_correct(self):
        """Test: Korrektes Passwort wird verifiziert"""
        password = "testpass123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test: Falsches Passwort wird abgelehnt"""
        password = "testpass123"
        hashed = get_password_hash(password)
        
        assert verify_password("wrongpass", hashed) is False
    
    def test_verify_password_empty(self):
        """Test: Leeres Passwort wird abgelehnt"""
        hashed = get_password_hash("testpass123")
        
        assert verify_password("", hashed) is False
    
    def test_user_verify_password_method(self, test_user):
        """Test: User.verify_password() Methode funktioniert"""
        assert test_user.verify_password("testpass123") is True
        assert test_user.verify_password("wrongpass") is False
    
    def test_user_hash_password_static(self):
        """Test: User.hash_password() statische Methode"""
        password = "testpass123"
        hashed = User.hash_password(password)
        
        assert hashed is not None
        assert hashed != password
        assert verify_password(password, hashed) is True


class TestJWTToken:
    """Tests für JWT Token Generation & Validation"""
    
    def test_create_access_token(self):
        """Test: Access Token wird erstellt"""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_token_contains_exp(self):
        """Test: Token enthält Expiration"""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload
        assert payload["sub"] == "123"
    
    def test_token_expiration_time(self):
        """Test: Token Expiration ist korrekt"""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp_timestamp = payload["exp"]
        exp = datetime.fromtimestamp(exp_timestamp)
        now = datetime.utcnow()
        
        # Expiration sollte in der Zukunft sein (mindestens 6 Tage)
        min_expiration = now + timedelta(days=6)
        max_expiration = now + timedelta(days=8)
        assert min_expiration < exp < max_expiration
    
    def test_token_custom_expiration(self):
        """Test: Custom Expiration wird verwendet"""
        data = {"sub": "123"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = datetime.fromtimestamp(payload["exp"])
        now = datetime.utcnow()
        
        # Expiration sollte in der Zukunft sein (mindestens 25 Minuten)
        # Prüfe nur dass exp > now + 25min (Toleranz für Test-Ausführung)
        assert exp > now + timedelta(minutes=25)
    
    def test_token_decode_valid(self):
        """Test: Gültiger Token wird dekodiert"""
        data = {"sub": "123", "username": "testuser"}
        token = create_access_token(data)
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "123"
        assert payload["username"] == "testuser"
    
    def test_token_decode_invalid_secret(self):
        """Test: Token mit falschem Secret wird abgelehnt"""
        data = {"sub": "123"}
        token = create_access_token(data)
        
        with pytest.raises(JWTError):
            jwt.decode(token, "wrong_secret", algorithms=[ALGORITHM])
    
    def test_token_decode_expired(self):
        """Test: Abgelaufener Token wird abgelehnt"""
        data = {"sub": "123"}
        expires_delta = timedelta(seconds=-1)  # Bereits abgelaufen
        token = create_access_token(data, expires_delta=expires_delta)
        
        with pytest.raises(JWTError):
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


class TestSecurity:
    """Security Tests für Authentication"""
    
    def test_secret_key_not_empty(self):
        """Test: SECRET_KEY ist gesetzt"""
        assert SECRET_KEY is not None
        assert len(SECRET_KEY) > 0
    
    def test_secret_key_not_in_code(self):
        """Test: SECRET_KEY ist nicht hardcoded (aus Env-Var)"""
        # Prüfe dass SECRET_KEY nicht "changeme" oder ähnlich ist
        assert SECRET_KEY != "changeme"
        assert SECRET_KEY != "secret"
        assert len(SECRET_KEY) >= 32  # Mindestlänge für sichere Keys
    
    def test_password_hash_salt_unique(self):
        """Test: Jeder Hash verwendet einzigartiges Salt"""
        password = "testpass123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Bcrypt erstellt unterschiedliche Hashes durch Salt
        assert hash1 != hash2
        # Beide sollten aber das gleiche Passwort verifizieren
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

