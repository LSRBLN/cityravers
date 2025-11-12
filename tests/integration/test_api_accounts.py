"""
Integration Tests für Accounts API Endpoints
Kritikalität: 🔴 KRITISCH - 100% Coverage erforderlich
"""
import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock
from database import Account


class TestCreateAccount:
    """Tests für POST /api/accounts"""
    
    def test_create_user_account_success(self, authenticated_client, db_session, test_user, test_subscription):
        """Test: User-Account wird erfolgreich erstellt"""
        with patch('api.account_manager') as mock_manager:
            mock_manager.add_account = AsyncMock(return_value={
                "status": "connected",
                "account_id": 1,
                "info": {"username": "test_account"}
            })
            
            response = authenticated_client.post(
                "/api/accounts",
                json={
                    "name": "My Account",
                    "account_type": "user",
                    "api_id": "12345",
                    "api_hash": "abcdef123456",
                    "phone_number": "+1234567890"
                }
            )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "My Account"
        assert data["account_type"] == "user"
        assert "id" in data
    
    def test_create_bot_account_success(self, authenticated_client, db_session, test_user, test_subscription):
        """Test: Bot-Account wird erfolgreich erstellt"""
        with patch('api.bot_manager') as mock_manager:
            mock_manager.add_bot = AsyncMock(return_value={
                "status": "connected",
                "bot_id": 1,
                "info": {"username": "test_bot"}
            })
            
            response = authenticated_client.post(
                "/api/accounts",
                json={
                    "name": "My Bot",
                    "account_type": "bot",
                    "bot_token": "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
                }
            )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["account_type"] == "bot"
    
    def test_create_account_limit_reached(self, authenticated_client, db_session, test_user):
        """Test: Fehler bei erreichtem Account-Limit"""
        # Erstelle bereits max_accounts Accounts
        for i in range(2):  # Free Trial: 2 Accounts
            account = Account(
                user_id=test_user.id,
                name=f"Account {i}",
                account_type="user",
                api_id="12345",
                api_hash="abcdef"
            )
            db_session.add(account)
        db_session.commit()
        
        response = authenticated_client.post(
            "/api/accounts",
            json={
                "name": "Extra Account",
                "account_type": "user",
                "api_id": "12345",
                "api_hash": "abcdef"
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "limit" in response.json()["detail"].lower()
    
    def test_create_account_unauthorized(self, client):
        """Test: Fehler ohne Authentifizierung"""
        response = client.post(
            "/api/accounts",
            json={
                "name": "Test Account",
                "account_type": "user"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestAccountLogin:
    """Tests für POST /api/accounts/{account_id}/login"""
    
    def test_request_code_success(self, authenticated_client, test_account):
        """Test: Code-Anfrage erfolgreich"""
        with patch('api.account_manager') as mock_manager:
            mock_manager.add_account = AsyncMock(return_value={
                "status": "code_required",
                "account_id": test_account.id
            })
            
            response = authenticated_client.post(
                f"/api/accounts/{test_account.id}/request-code",
                json={"phone_number": "+1234567890"}
            )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "code_required"
    
    def test_login_with_code_success(self, authenticated_client, test_account):
        """Test: Login mit Code erfolgreich"""
        with patch('api.account_manager') as mock_manager:
            mock_manager.add_account = AsyncMock(return_value={
                "status": "connected",
                "account_id": test_account.id,
                "info": {"username": "test_account"}
            })
            
            response = authenticated_client.post(
                f"/api/accounts/{test_account.id}/login",
                json={
                    "code": "12345",
                    "phone_number": "+1234567890"
                }
            )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "connected"
    
    def test_login_2fa_required(self, authenticated_client, test_account):
        """Test: 2FA Passwort erforderlich"""
        with patch('api.account_manager') as mock_manager:
            mock_manager.add_account = AsyncMock(return_value={
                "status": "password_required",
                "account_id": test_account.id
            })
            
            response = authenticated_client.post(
                f"/api/accounts/{test_account.id}/login",
                json={
                    "code": "12345",
                    "phone_number": "+1234567890"
                }
            )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "password_required"


class TestGetAccounts:
    """Tests für GET /api/accounts"""
    
    def test_get_accounts_success(self, authenticated_client, test_account):
        """Test: Accounts werden gelistet"""
        response = authenticated_client.get("/api/accounts")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(acc["id"] == test_account.id for acc in data)
    
    def test_get_accounts_only_own(self, authenticated_client, db_session, test_user):
        """Test: Nur eigene Accounts werden zurückgegeben"""
        # Erstelle Account für anderen User
        from database import User
        other_user = User(
            email="other@example.com",
            username="otheruser",
            password_hash="hash",
            is_active=True
        )
        db_session.add(other_user)
        db_session.commit()
        
        other_account = Account(
            user_id=other_user.id,
            name="Other Account",
            account_type="user",
            api_id="12345",
            api_hash="abcdef"
        )
        db_session.add(other_account)
        db_session.commit()
        
        response = authenticated_client.get("/api/accounts")
        data = response.json()
        
        # Anderer Account sollte nicht in Liste sein
        assert not any(acc["id"] == other_account.id for acc in data)


class TestDeleteAccount:
    """Tests für DELETE /api/accounts/{account_id}"""
    
    def test_delete_account_success(self, authenticated_client, test_account):
        """Test: Account wird gelöscht"""
        with patch('api.account_manager') as mock_manager:
            mock_manager.remove_account = AsyncMock()
            
            response = authenticated_client.delete(f"/api/accounts/{test_account.id}")
        
        assert response.status_code == status.HTTP_200_OK
    
    def test_delete_account_not_found(self, authenticated_client):
        """Test: Fehler bei nicht existierendem Account"""
        response = authenticated_client.delete("/api/accounts/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_account_unauthorized(self, client, test_account):
        """Test: Fehler ohne Authentifizierung"""
        response = client.delete(f"/api/accounts/{test_account.id}")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSecurity:
    """Security Tests für Accounts Endpoints"""
    
    def test_api_credentials_not_in_response(self, authenticated_client, test_account):
        """Test: API Credentials werden nicht in Response zurückgegeben"""
        response = authenticated_client.get(f"/api/accounts/{test_account.id}")
        
        data = response.json()
        assert "api_hash" not in data or data.get("api_hash") is None
        # api_id kann in Response sein (weniger sensibel)
    
    def test_bot_token_not_in_response(self, authenticated_client, test_bot_account):
        """Test: Bot-Token wird nicht in Response zurückgegeben"""
        response = authenticated_client.get(f"/api/accounts/{test_bot_account.id}")
        
        data = response.json()
        assert "bot_token" not in data or data.get("bot_token") is None

