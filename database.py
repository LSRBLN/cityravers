"""
Datenbank-Modell für Accounts, Gruppen und geplante Nachrichten
"""

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timedelta
import bcrypt

Base = declarative_base()


class Account(Base):
    """Telegram Account (User oder Bot)"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Besitzer des Accounts
    name = Column(String, unique=True, index=True, nullable=False)
    account_type = Column(String, default="user")  # 'user' oder 'bot'
    api_id = Column(String)  # Nur für User-Accounts
    api_hash = Column(String)  # Nur für User-Accounts
    bot_token = Column(String)  # Nur für Bot-Accounts
    phone_number = Column(String)  # Nur für User-Accounts
    session_name = Column(String, unique=True)  # Nur für User-Accounts
    session_file_path = Column(String)  # Pfad zur hochgeladenen Session-Datei
    tdata_path = Column(String)  # Pfad zum tdata-Ordner
    proxy_id = Column(Integer, ForeignKey("proxies.id"))  # Zugewiesener Proxy
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    
    # Relationships
    scheduled_messages = relationship("ScheduledMessage", back_populates="account", cascade="all, delete-orphan")
    proxy = relationship("Proxy", foreign_keys=[proxy_id])


class Group(Base):
    """Telegram Gruppe/Chat"""
    __tablename__ = "groups"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Besitzer der Gruppe
    name = Column(String, nullable=False)
    chat_id = Column(String, nullable=False, unique=True, index=True)
    chat_type = Column(String)  # 'group', 'channel', 'private'
    username = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Neue Felder für Gruppendetails
    member_count = Column(Integer, default=0)  # Anzahl der Mitglieder
    is_public = Column(Boolean, default=True)  # Öffentlich oder privat
    bot_invite_allowed = Column(Boolean, default=True)  # Können Bots eingeladen werden
    description = Column(Text)  # Gruppenbeschreibung
    invite_link = Column(String)  # Einladungslink (falls vorhanden)
    last_checked = Column(DateTime)  # Wann zuletzt geprüft wurde
    
    # Relationships entfernt - verwenden jetzt group_ids (JSON) statt Foreign Key


class ScheduledMessage(Base):
    """Geplante Nachricht"""
    __tablename__ = "scheduled_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    group_ids = Column(Text, nullable=False)  # JSON-Array von Group-IDs für Multi-Gruppen
    message = Column(Text, nullable=False)
    scheduled_time = Column(DateTime, nullable=False, index=True)
    delay = Column(Float, default=1.0)  # Sekunden zwischen Nachrichten
    batch_size = Column(Integer, default=10)
    batch_delay = Column(Float, default=5.0)
    group_delay = Column(Float, default=2.0)  # Sekunden zwischen verschiedenen Gruppen
    repeat_count = Column(Integer, default=1)  # Wie oft soll die Nachricht gesendet werden
    status = Column(String, default="pending")  # pending, running, completed, failed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    error_message = Column(Text)
    
    # Relationships
    account = relationship("Account", back_populates="scheduled_messages")
    # group_ids als JSON gespeichert, keine Foreign Key Relationship mehr


class ScrapedUser(Base):
    """Gescrapte Telegram User"""
    __tablename__ = "scraped_users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)  # Telegram User ID
    username = Column(String, index=True)
    first_name = Column(String)
    last_name = Column(String)
    phone = Column(String)
    source_group_id = Column(String)  # Aus welcher Gruppe gescrapt
    source_group_name = Column(String)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Metadaten
    notes = Column(Text)  # Notizen zum User


class AccountWarming(Base):
    """Account-Warming Konfiguration"""
    __tablename__ = "account_warming"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, unique=True)
    is_active = Column(Boolean, default=False)
    
    # Aktivitäts-Limits (pro Tag)
    read_messages_per_day = Column(Integer, default=20)  # Nachrichten lesen
    scroll_dialogs_per_day = Column(Integer, default=10)  # Durch Dialoge scrollen
    reactions_per_day = Column(Integer, default=5)  # Reaktionen
    small_messages_per_day = Column(Integer, default=3)  # Kleine Nachrichten
    
    # Zeitplanung
    start_time = Column(String, default="09:00")  # Startzeit (HH:MM)
    end_time = Column(String, default="22:00")  # Endzeit (HH:MM)
    min_delay = Column(Float, default=30.0)  # Mindest-Delay zwischen Aktionen (Sekunden)
    max_delay = Column(Float, default=300.0)  # Maximal-Delay zwischen Aktionen (Sekunden)
    
    # Warming-Phase (Tage seit Start)
    warming_days = Column(Integer, default=0)  # Wie viele Tage läuft das Warming bereits
    max_warming_days = Column(Integer, default=14)  # Maximale Warming-Dauer
    
    # Statistiken
    total_actions = Column(Integer, default=0)
    last_action_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("Account")


class WarmingActivity(Base):
    """Warming-Aktivitäten Log"""
    __tablename__ = "warming_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    warming_id = Column(Integer, ForeignKey("account_warming.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    activity_type = Column(String, nullable=False)  # 'read', 'scroll', 'reaction', 'message'
    target_chat_id = Column(String)
    target_chat_name = Column(String)
    message_id = Column(Integer)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    executed_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    warming = relationship("AccountWarming")


class MessageTemplate(Base):
    """Nachrichtenvorlagen für spätere Verwendung"""
    __tablename__ = "message_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    message = Column(Text, nullable=False)
    category = Column(String)  # z.B. 'marketing', 'info', 'announcement'
    tags = Column(Text)  # JSON-Array von Tags
    usage_count = Column(Integer, default=0)  # Wie oft verwendet
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class SentMessage(Base):
    """Historie gesendeter Nachrichten"""
    __tablename__ = "sent_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"))
    group_chat_id = Column(String)  # Backup falls Gruppe gelöscht
    group_name = Column(String)  # Backup falls Gruppe gelöscht
    message = Column(Text, nullable=False)
    message_template_id = Column(Integer, ForeignKey("message_templates.id"))  # Optional: Verweis auf Vorlage
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    telegram_message_id = Column(String)  # Telegram Message ID falls verfügbar
    
    # Relationships
    account = relationship("Account")
    group = relationship("Group")
    template = relationship("MessageTemplate")


class AccountStatistic(Base):
    """Statistiken für Accounts"""
    __tablename__ = "account_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, unique=True, index=True)
    
    # Gesendete Nachrichten
    total_messages_sent = Column(Integer, default=0)
    total_messages_failed = Column(Integer, default=0)
    
    # Gruppen-Statistiken
    total_groups_used = Column(Integer, default=0)
    
    # Zeitstempel
    first_message_at = Column(DateTime)
    last_message_at = Column(DateTime)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    account = relationship("Account")


class Proxy(Base):
    """Proxy-Konfiguration"""
    __tablename__ = "proxies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    proxy_type = Column(String, nullable=False)  # 'socks5', 'http', 'https', 'mtproto'
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String)  # Optional
    password = Column(String)  # Optional
    secret = Column(String)  # Für MTProto
    
    # Metadaten
    country = Column(String)  # Optional: Land des Proxys
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Ob Proxy getestet wurde
    last_used = Column(DateTime)
    usage_count = Column(Integer, default=0)  # Wie oft verwendet
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)  # Notizen zum Proxy


class User(Base):
    """Benutzer-Account für das Tool"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)  # bcrypt Hash
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="user", uselist=False, cascade="all, delete-orphan")
    accounts = relationship("Account", backref="owner_user", lazy="dynamic")
    groups = relationship("Group", backref="owner_user", lazy="dynamic")
    
    def verify_password(self, password: str) -> bool:
        """Verifiziert ein Passwort"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Erstellt einen Passwort-Hash"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


class Subscription(Base):
    """Abonnement/Paket für Benutzer"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    plan_type = Column(String, nullable=False)  # 'free_trial', 'basic', 'pro', 'enterprise'
    status = Column(String, default="active")  # 'active', 'expired', 'cancelled'
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    max_accounts = Column(Integer, default=1)  # Maximale Anzahl Accounts
    max_groups = Column(Integer, default=5)  # Maximale Anzahl Gruppen
    max_messages_per_day = Column(Integer, default=10)  # Maximale Nachrichten pro Tag
    features = Column(Text)  # JSON-String mit Features (z.B. {"auto_number_purchase": true})
    
    # Relationships
    user = relationship("User", back_populates="subscription")
    
    def is_active(self) -> bool:
        """Prüft ob Abonnement aktiv ist"""
        if self.status != "active":
            return False
        if self.expires_at and self.expires_at < datetime.utcnow():
            return False
        return True
    
    def has_feature(self, feature: str) -> bool:
        """Prüft ob Feature verfügbar ist"""
        import json
        if not self.features:
            return False
        try:
            features = json.loads(self.features)
            return features.get(feature, False)
        except:
            return False


class SystemSettings(Base):
    """System-Einstellungen (nur für Admins)"""
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False, index=True)  # Einstellungsschlüssel
    value = Column(Text)  # Wert (kann JSON sein)
    value_type = Column(String, default="string")  # 'string', 'integer', 'boolean', 'json'
    description = Column(Text)  # Beschreibung der Einstellung
    category = Column(String, default="general")  # 'general', 'api', 'security', 'features'
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Wer hat es geändert


class PhoneNumberPurchase(Base):
    """Gekaufte Telefonnummern von 5sim.net oder ähnlichen Anbietern"""
    __tablename__ = "phone_number_purchases"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String, nullable=False)  # '5sim', 'sms-activate', etc.
    phone_number = Column(String, nullable=False)
    country = Column(String)  # ISO Country Code
    service = Column(String, default="telegram")  # Service für den die Nummer gekauft wurde
    purchase_id = Column(String)  # ID vom Provider
    cost = Column(Float)  # Kosten in der Provider-Währung
    status = Column(String, default="pending")  # 'pending', 'active', 'used', 'expired', 'cancelled'
    sms_code = Column(String)  # Empfangener SMS-Code
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)  # Verknüpfter Account
    purchased_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    used_at = Column(DateTime)
    
    # Relationships
    user = relationship("User")
    account = relationship("Account")


# Datenbank initialisieren
def init_db(db_path: str = None):
    """
    Initialisiert die Datenbank
    
    Unterstützt SQLite (Entwicklung) und PostgreSQL (Produktion)
    Umgebungsvariable DATABASE_URL für PostgreSQL:
    postgresql://user:password@localhost/dbname
    """
    import os
    
    # Prüfe ob PostgreSQL URL vorhanden
    db_url = os.getenv("DATABASE_URL")
    
    if db_url:
        # PostgreSQL verwenden
        engine = create_engine(db_url)
    else:
        # SQLite verwenden (Fallback für Entwicklung)
        if db_path is None:
            db_path = "telegram_bot.db"
        engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    
    Base.metadata.create_all(bind=engine)
    return engine


def get_session(engine):
    """Erstellt eine Datenbank-Session"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

