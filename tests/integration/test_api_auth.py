"""
Integration Tests für Authentication API Endpoints
Kritikalität: 🔴 KRITISCH - 100% Coverage erforderlich
"""
import pytest
from fastapi import status
from database import User


class TestRegister:
    """Tests für POST /api/auth/register"""
    
    def test_register_success(self, client, db_session):
        """Test: User wird erfolgreich registriert"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "securepass123"
            }
        )
        
        # API gibt 200 OK zurück (nicht 201 Created)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data.get("success") is True
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "user_id" in data  # API verwendet user_id, nicht id
        assert "access_token" in data
        assert "password" not in data  # Passwort nicht in Response
    
    def test_register_duplicate_email(self, client, db_session, test_user):
        """Test: Fehler bei doppelter Email"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": test_user.email,  # Bereits existierend
                "username": "differentuser",
                "password": "securepass123"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_duplicate_username(self, client, db_session, test_user):
        """Test: Fehler bei doppeltem Username"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "different@example.com",
                "username": test_user.username,  # Bereits existierend
                "password": "securepass123"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_register_invalid_email(self, client):
        """Test: Fehler bei ungültiger Email"""
        response = client.post(
            "/api/auth/register",
            json={
                "email": "invalid-email",
                "username": "testuser",
                "password": "securepass123"
            }
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """Tests für POST /api/auth/login"""
    
    def test_login_success(self, client, test_user):
        """Test: Login erfolgreich"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpass123"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0
    
    def test_login_wrong_password(self, client, test_user):
        """Test: Fehler bei falschem Passwort"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_nonexistent_user(self, client):
        """Test: Fehler bei nicht existierendem User"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "anypassword"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_inactive_user(self, client, db_session):
        """Test: Fehler bei inaktivem User"""
        from auth import get_password_hash
        import uuid
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            email=f"inactive_{unique_id}@example.com",
            username=f"inactive_{unique_id}",
            password_hash=get_password_hash("pass123"),
            is_active=False
        )
        db_session.add(user)
        db_session.commit()
        
        response = client.post(
            "/api/auth/login",
            data={
                "username": user.email,
                "password": "pass123"
            }
        )
        
        # API gibt 400 Bad Request für inaktive User (nicht 401)
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]


class TestGetMe:
    """Tests für GET /api/auth/me"""
    
    def test_get_me_success(self, authenticated_client, test_user):
        """Test: User-Info wird zurückgegeben"""
        response = authenticated_client.get("/api/auth/me")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # API kann user_id oder id zurückgeben
        user_id = data.get("user_id") or data.get("id")
        assert user_id == test_user.id
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert "password" not in data
    
    def test_get_me_unauthorized(self, client):
        """Test: Fehler ohne Token"""
        response = client.get("/api/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_me_invalid_token(self, client):
        """Test: Fehler bei ungültigem Token"""
        client.headers = {"Authorization": "Bearer invalid_token_12345"}
        response = client.get("/api/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_me_expired_token(self, client, test_user):
        """Test: Fehler bei abgelaufenem Token"""
        from datetime import timedelta
        from auth import create_access_token
        
        # Erstelle abgelaufenes Token
        expired_token = create_access_token(
            {"sub": str(test_user.id)},
            expires_delta=timedelta(seconds=-1)
        )
        
        client.headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSecurity:
    """Security Tests für Auth Endpoints"""
    
    def test_token_not_in_logs(self, client, test_user, caplog):
        """Test: Token wird nicht in Logs ausgegeben"""
        import logging
        logging.basicConfig(level=logging.INFO)
        
        response = client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpass123"
            }
        )
        
        token = response.json().get("access_token", "")
        log_output = caplog.text
        
        # Token sollte nicht in Logs erscheinen
        assert token not in log_output or len(token) == 0
    
    def test_password_not_in_response(self, client, test_user):
        """Test: Passwort wird nicht in Response zurückgegeben"""
        response = client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpass123"
            }
        )
        
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data

