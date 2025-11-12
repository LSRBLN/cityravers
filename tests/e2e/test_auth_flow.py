"""
End-to-End Tests für Authentication Flow
Kritikalität: 🔴 KRITISCH
"""
import pytest
from fastapi import status


class TestCompleteAuthFlow:
    """Vollständiger Authentication Flow"""
    
    def test_register_login_get_me_flow(self, client, db_session):
        """Test: Vollständiger Flow: Registrierung → Login → Get Me"""
        # 1. Registrierung
        register_response = client.post(
            "/api/auth/register",
            json={
                "email": "e2e@example.com",
                "username": "e2euser",
                "password": "e2epass123"
            }
        )
        assert register_response.status_code == status.HTTP_201_CREATED
        user_id = register_response.json()["id"]
        
        # 2. Login
        login_response = client.post(
            "/api/auth/login",
            data={
                "username": "e2e@example.com",
                "password": "e2epass123"
            }
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        
        # 3. Get Me mit Token
        client.headers = {"Authorization": f"Bearer {token}"}
        me_response = client.get("/api/auth/me")
        assert me_response.status_code == status.HTTP_200_OK
        assert me_response.json()["id"] == user_id
        assert me_response.json()["email"] == "e2e@example.com"
    
    def test_login_wrong_password_then_correct(self, client, test_user):
        """Test: Falsches Passwort, dann korrektes"""
        # 1. Falsches Passwort
        wrong_response = client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpass"
            }
        )
        assert wrong_response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # 2. Korrektes Passwort
        correct_response = client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpass123"
            }
        )
        assert correct_response.status_code == status.HTTP_200_OK
        assert "access_token" in correct_response.json()


class TestAccountFlow:
    """End-to-End Account Management Flow"""
    
    def test_create_account_list_delete_flow(self, authenticated_client, db_session, test_user, test_subscription):
        """Test: Account erstellen → Listen → Löschen"""
        from unittest.mock import patch, AsyncMock
        
        # 1. Account erstellen
        with patch('api.account_manager') as mock_manager:
            mock_manager.add_account = AsyncMock(return_value={
                "status": "connected",
                "account_id": 1,
                "info": {"username": "test_account"}
            })
            
            create_response = authenticated_client.post(
                "/api/accounts",
                json={
                    "name": "E2E Account",
                    "account_type": "user",
                    "api_id": "12345",
                    "api_hash": "abcdef123456"
                }
            )
        
        assert create_response.status_code == status.HTTP_201_CREATED
        account_id = create_response.json()["id"]
        
        # 2. Accounts listen
        list_response = authenticated_client.get("/api/accounts")
        assert list_response.status_code == status.HTTP_200_OK
        accounts = list_response.json()
        assert any(acc["id"] == account_id for acc in accounts)
        
        # 3. Account löschen
        with patch('api.account_manager') as mock_manager:
            mock_manager.remove_account = AsyncMock()
            
            delete_response = authenticated_client.delete(f"/api/accounts/{account_id}")
        
        assert delete_response.status_code == status.HTTP_200_OK
        
        # 4. Prüfe dass Account gelöscht ist
        get_response = authenticated_client.get(f"/api/accounts/{account_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

