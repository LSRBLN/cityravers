"""
Unit Tests für Database Models (database.py)
Kritikalität: 🔴 HOCH - 100% Coverage erforderlich
"""
import pytest
from datetime import datetime, timedelta
from database import (
    User, Account, Group, ScheduledMessage, Subscription,
    Proxy, AccountWarming, ScrapedUser, MessageTemplate,
    SentMessage, AccountStatistic
)


class TestUserModel:
    """Tests für User Model"""
    
    def test_user_creation(self, db_session):
        """Test: User wird erstellt"""
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
    
    def test_user_password_verification(self, db_session):
        """Test: User.verify_password() funktioniert"""
        password = "testpass123"
        user = User(
            email="test@example.com",
            username="testuser",
            password_hash=User.hash_password(password),
            is_active=True
        )
        db_session.add(user)
        db_session.commit()
        
        assert user.verify_password(password) is True
        assert user.verify_password("wrongpass") is False
    
    def test_user_unique_email(self, db_session):
        """Test: Email muss eindeutig sein"""
        user1 = User(
            email="test@example.com",
            username="user1",
            password_hash="hash1",
            is_active=True
        )
        db_session.add(user1)
        db_session.commit()
        
        user2 = User(
            email="test@example.com",  # Gleiche Email
            username="user2",
            password_hash="hash2",
            is_active=True
        )
        db_session.add(user2)
        
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


class TestAccountModel:
    """Tests für Account Model"""
    
    def test_account_creation(self, db_session, test_user):
        """Test: Account wird erstellt"""
        account = Account(
            user_id=test_user.id,
            name="Test Account",
            account_type="user",
            api_id="12345",
            api_hash="abcdef",
            is_active=True
        )
        db_session.add(account)
        db_session.commit()
        
        assert account.id is not None
        assert account.user_id == test_user.id
        assert account.account_type == "user"
    
    def test_bot_account_creation(self, db_session, test_user):
        """Test: Bot-Account wird erstellt"""
        account = Account(
            user_id=test_user.id,
            name="Test Bot",
            account_type="bot",
            bot_token="123456789:ABCdef",
            is_active=True
        )
        db_session.add(account)
        db_session.commit()
        
        assert account.account_type == "bot"
        assert account.bot_token is not None
    
    def test_account_user_relationship(self, db_session, test_user):
        """Test: Account-User Relationship funktioniert"""
        account = Account(
            user_id=test_user.id,
            name="Test Account",
            account_type="user",
            api_id="12345",
            api_hash="abcdef"
        )
        db_session.add(account)
        db_session.commit()
        
        assert account.owner_user.id == test_user.id


class TestGroupModel:
    """Tests für Group Model"""
    
    def test_group_creation(self, db_session, test_user):
        """Test: Gruppe wird erstellt"""
        group = Group(
            user_id=test_user.id,
            name="Test Group",
            chat_id="-1001234567890",
            chat_type="group",
            is_active=True
        )
        db_session.add(group)
        db_session.commit()
        
        assert group.id is not None
        assert group.chat_id == "-1001234567890"
        assert group.chat_type == "group"
    
    def test_group_unique_chat_id(self, db_session, test_user):
        """Test: Chat-ID muss eindeutig sein"""
        group1 = Group(
            user_id=test_user.id,
            name="Group 1",
            chat_id="-1001234567890"
        )
        db_session.add(group1)
        db_session.commit()
        
        group2 = Group(
            user_id=test_user.id,
            name="Group 2",
            chat_id="-1001234567890"  # Gleiche Chat-ID
        )
        db_session.add(group2)
        
        with pytest.raises(Exception):  # IntegrityError
            db_session.commit()


class TestScheduledMessageModel:
    """Tests für ScheduledMessage Model"""
    
    def test_scheduled_message_creation(self, db_session, test_account, test_group):
        """Test: Geplante Nachricht wird erstellt"""
        import json
        message = ScheduledMessage(
            account_id=test_account.id,
            group_ids=json.dumps([test_group.id]),
            message="Test Message",
            scheduled_time=datetime.utcnow() + timedelta(hours=1),
            status="pending"
        )
        db_session.add(message)
        db_session.commit()
        
        assert message.id is not None
        assert message.status == "pending"
        assert message.account_id == test_account.id
    
    def test_scheduled_message_account_relationship(self, db_session, test_account, test_group):
        """Test: ScheduledMessage-Account Relationship"""
        import json
        message = ScheduledMessage(
            account_id=test_account.id,
            group_ids=json.dumps([test_group.id]),
            message="Test",
            scheduled_time=datetime.utcnow() + timedelta(hours=1)
        )
        db_session.add(message)
        db_session.commit()
        
        assert message.account.id == test_account.id


class TestSubscriptionModel:
    """Tests für Subscription Model"""
    
    def test_subscription_creation(self, db_session, test_user):
        """Test: Abonnement wird erstellt"""
        subscription = Subscription(
            user_id=test_user.id,
            plan_type="pro",
            status="active",
            expires_at=datetime.utcnow() + timedelta(days=30),
            max_accounts=10,
            max_groups=50
        )
        db_session.add(subscription)
        db_session.commit()
        
        assert subscription.id is not None
        assert subscription.plan_type == "pro"
    
    def test_subscription_is_active(self, db_session, test_user):
        """Test: subscription.is_active() prüft Status und Ablauf"""
        # Aktives Abonnement
        sub1 = Subscription(
            user_id=test_user.id,
            plan_type="pro",
            status="active",
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        assert sub1.is_active() is True
        
        # Abgelaufenes Abonnement
        sub2 = Subscription(
            user_id=test_user.id,
            plan_type="pro",
            status="active",
            expires_at=datetime.utcnow() - timedelta(days=1)
        )
        assert sub2.is_active() is False
        
        # Gekündigtes Abonnement
        sub3 = Subscription(
            user_id=test_user.id,
            plan_type="pro",
            status="cancelled",
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        assert sub3.is_active() is False
    
    def test_subscription_has_feature(self, db_session, test_user):
        """Test: subscription.has_feature() prüft Features"""
        import json
        subscription = Subscription(
            user_id=test_user.id,
            plan_type="pro",
            status="active",
            features=json.dumps({"auto_number_purchase": True, "api_access": False})
        )
        
        assert subscription.has_feature("auto_number_purchase") is True
        assert subscription.has_feature("api_access") is False
        assert subscription.has_feature("nonexistent") is False


class TestProxyModel:
    """Tests für Proxy Model"""
    
    def test_proxy_creation(self, db_session):
        """Test: Proxy wird erstellt"""
        proxy = Proxy(
            name="Test Proxy",
            proxy_type="socks5",
            host="127.0.0.1",
            port=1080,
            is_active=True
        )
        db_session.add(proxy)
        db_session.commit()
        
        assert proxy.id is not None
        assert proxy.proxy_type == "socks5"
        assert proxy.host == "127.0.0.1"


class TestCascadeDeletes:
    """Tests für Cascade Delete Relationships"""
    
    def test_account_deletion_cascades_scheduled_messages(self, db_session, test_account, test_group):
        """Test: Account-Löschung löscht geplante Nachrichten"""
        import json
        message = ScheduledMessage(
            account_id=test_account.id,
            group_ids=json.dumps([test_group.id]),
            message="Test",
            scheduled_time=datetime.utcnow() + timedelta(hours=1)
        )
        db_session.add(message)
        db_session.commit()
        message_id = message.id
        
        # Lösche Account
        db_session.delete(test_account)
        db_session.commit()
        
        # Nachricht sollte auch gelöscht sein
        deleted_message = db_session.query(ScheduledMessage).filter(
            ScheduledMessage.id == message_id
        ).first()
        assert deleted_message is None

