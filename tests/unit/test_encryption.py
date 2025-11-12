"""
Unit Tests für Encryption Utils (encryption_utils.py)
Kritikalität: 🔴 HOCH - 100% Coverage erforderlich
"""
import pytest
import os
from unittest.mock import patch
from encryption_utils import (
    encrypt_string,
    decrypt_string,
    get_encryption_key,
    get_fernet
)


class TestEncryptionKey:
    """Tests für Encryption Key Management"""
    
    def test_get_encryption_key_from_env(self):
        """Test: Key wird aus ENCRYPTION_KEY geladen"""
        with patch.dict(os.environ, {"ENCRYPTION_KEY": "test_key_123456789012345678901234567890"}):
            key = get_encryption_key()
            assert key is not None
            assert isinstance(key, bytes)
    
    def test_get_encryption_key_fallback_to_jwt(self):
        """Test: Fallback zu JWT_SECRET_KEY wenn ENCRYPTION_KEY fehlt"""
        with patch.dict(os.environ, {
            "JWT_SECRET_KEY": "test_jwt_secret_12345678901234567890",
            "ENCRYPTION_KEY": ""
        }, clear=False):
            key = get_encryption_key()
            assert key is not None
            assert isinstance(key, bytes)
    
    def test_get_encryption_key_error_no_keys(self):
        """Test: Fehler wenn keine Keys gesetzt sind"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(RuntimeError):
                get_encryption_key()


class TestEncryptDecrypt:
    """Tests für encrypt_string() und decrypt_string()"""
    
    def test_encrypt_string(self):
        """Test: String wird verschlüsselt"""
        plaintext = "test_secret_password"
        encrypted = encrypt_string(plaintext)
        
        assert encrypted is not None
        assert encrypted != plaintext
        assert isinstance(encrypted, str)
        assert len(encrypted) > 0
    
    def test_decrypt_string(self):
        """Test: String wird entschlüsselt"""
        plaintext = "test_secret_password"
        encrypted = encrypt_string(plaintext)
        decrypted = decrypt_string(encrypted)
        
        assert decrypted == plaintext
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test: Roundtrip Verschlüsselung/Entschlüsselung"""
        test_strings = [
            "simple",
            "with spaces",
            "with-special-chars!@#$%",
            "unicode: 测试 🚀",
            "very long string " * 100,
            "1234567890",
            ""
        ]
        
        for plaintext in test_strings:
            encrypted = encrypt_string(plaintext)
            decrypted = decrypt_string(encrypted)
            assert decrypted == plaintext, f"Roundtrip failed for: {plaintext[:50]}"
    
    def test_encrypt_empty_string(self):
        """Test: Leerer String wird behandelt"""
        encrypted = encrypt_string("")
        assert encrypted == ""
    
    def test_decrypt_empty_string(self):
        """Test: Leerer String wird entschlüsselt"""
        decrypted = decrypt_string("")
        assert decrypted == ""
    
    def test_decrypt_invalid_string(self):
        """Test: Ungültiger verschlüsselter String wird behandelt"""
        # Versuche einen zufälligen String zu entschlüsseln
        decrypted = decrypt_string("invalid_encrypted_string_12345")
        # Sollte leerer String zurückgegeben werden bei Fehler
        assert decrypted == ""
    
    def test_encrypt_different_strings_different_output(self):
        """Test: Unterschiedliche Strings erzeugen unterschiedliche Outputs"""
        str1 = "test1"
        str2 = "test2"
        
        enc1 = encrypt_string(str1)
        enc2 = encrypt_string(str2)
        
        assert enc1 != enc2
    
    def test_encrypt_same_string_different_output(self):
        """Test: Gleicher String erzeugt unterschiedliche Outputs (durch IV)"""
        plaintext = "test_secret"
        
        enc1 = encrypt_string(plaintext)
        enc2 = encrypt_string(plaintext)
        
        # Fernet verwendet zufälliges IV, daher unterschiedliche Outputs
        assert enc1 != enc2
        # Aber beide sollten entschlüsselbar sein
        assert decrypt_string(enc1) == plaintext
        assert decrypt_string(enc2) == plaintext


class TestFernetInstance:
    """Tests für get_fernet()"""
    
    def test_get_fernet_returns_instance(self):
        """Test: get_fernet() gibt Fernet-Instanz zurück"""
        fernet = get_fernet()
        assert fernet is not None
    
    def test_get_fernet_singleton(self):
        """Test: get_fernet() gibt immer dieselbe Instanz zurück"""
        fernet1 = get_fernet()
        fernet2 = get_fernet()
        
        assert fernet1 is fernet2


class TestSecurity:
    """Security Tests für Encryption"""
    
    def test_encryption_key_not_hardcoded(self):
        """Test: Key ist nicht hardcoded"""
        # Prüfe dass Key aus Umgebungsvariablen kommt
        with patch.dict(os.environ, {"ENCRYPTION_KEY": "test_key"}):
            key = get_encryption_key()
            assert key == b"test_key"
    
    def test_encrypted_data_not_plaintext(self):
        """Test: Verschlüsselte Daten enthalten keinen Plaintext"""
        plaintext = "secret_password_123"
        encrypted = encrypt_string(plaintext)
        
        # Verschlüsselter String sollte den Plaintext nicht enthalten
        assert plaintext not in encrypted
        assert "secret" not in encrypted.lower()
        assert "password" not in encrypted.lower()
    
    def test_encryption_proxy_password(self):
        """Test: Proxy-Passwörter werden korrekt verschlüsselt"""
        password = "my_proxy_password_123"
        encrypted = encrypt_string(password)
        decrypted = decrypt_string(encrypted)
        
        assert decrypted == password
        assert encrypted != password

