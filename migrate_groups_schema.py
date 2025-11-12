"""
Datenbank-Migration: Fügt fehlende Spalten zur groups-Tabelle hinzu
Behebt E006: Schema-Mismatch
"""
import sqlite3
import os
from pathlib import Path

def migrate_groups_table():
    """Fügt fehlende Spalten zur groups-Tabelle hinzu"""
    db_path = os.getenv("DATABASE_URL")
    
    if db_path and db_path.startswith("postgresql://"):
        # PostgreSQL - verwende SQLAlchemy
        from sqlalchemy import create_engine, text
        engine = create_engine(db_path)
        with engine.connect() as conn:
            # Prüfe ob Spalten existieren
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'groups'
            """))
            existing_columns = [row[0] for row in result]
            
            # Füge fehlende Spalten hinzu
            if 'user_id' not in existing_columns:
                conn.execute(text("ALTER TABLE groups ADD COLUMN user_id INTEGER"))
                conn.commit()
                print("✅ Spalte 'user_id' hinzugefügt")
            
            if 'member_count' not in existing_columns:
                conn.execute(text("ALTER TABLE groups ADD COLUMN member_count INTEGER DEFAULT 0"))
                conn.commit()
                print("✅ Spalte 'member_count' hinzugefügt")
            
            if 'is_public' not in existing_columns:
                conn.execute(text("ALTER TABLE groups ADD COLUMN is_public BOOLEAN DEFAULT TRUE"))
                conn.commit()
                print("✅ Spalte 'is_public' hinzugefügt")
            
            if 'bot_invite_allowed' not in existing_columns:
                conn.execute(text("ALTER TABLE groups ADD COLUMN bot_invite_allowed BOOLEAN DEFAULT TRUE"))
                conn.commit()
                print("✅ Spalte 'bot_invite_allowed' hinzugefügt")
            
            if 'description' not in existing_columns:
                conn.execute(text("ALTER TABLE groups ADD COLUMN description TEXT"))
                conn.commit()
                print("✅ Spalte 'description' hinzugefügt")
            
            if 'invite_link' not in existing_columns:
                conn.execute(text("ALTER TABLE groups ADD COLUMN invite_link VARCHAR"))
                conn.commit()
                print("✅ Spalte 'invite_link' hinzugefügt")
            
            if 'last_checked' not in existing_columns:
                conn.execute(text("ALTER TABLE groups ADD COLUMN last_checked TIMESTAMP"))
                conn.commit()
                print("✅ Spalte 'last_checked' hinzugefügt")
    else:
        # SQLite
        if db_path:
            # Extrahiere Pfad aus DATABASE_URL falls vorhanden
            db_path = db_path.replace("sqlite:///", "")
        else:
            db_path = "telegram_bot.db"
        
        if not os.path.exists(db_path):
            print(f"⚠️  Datenbank-Datei nicht gefunden: {db_path}")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Prüfe welche Spalten existieren
            cursor.execute("PRAGMA table_info(groups)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            # Füge fehlende Spalten hinzu
            if 'user_id' not in existing_columns:
                cursor.execute("ALTER TABLE groups ADD COLUMN user_id INTEGER")
                print("✅ Spalte 'user_id' hinzugefügt")
            
            if 'member_count' not in existing_columns:
                cursor.execute("ALTER TABLE groups ADD COLUMN member_count INTEGER DEFAULT 0")
                print("✅ Spalte 'member_count' hinzugefügt")
            
            if 'is_public' not in existing_columns:
                cursor.execute("ALTER TABLE groups ADD COLUMN is_public BOOLEAN DEFAULT 1")
                print("✅ Spalte 'is_public' hinzugefügt")
            
            if 'bot_invite_allowed' not in existing_columns:
                cursor.execute("ALTER TABLE groups ADD COLUMN bot_invite_allowed BOOLEAN DEFAULT 1")
                print("✅ Spalte 'bot_invite_allowed' hinzugefügt")
            
            if 'description' not in existing_columns:
                cursor.execute("ALTER TABLE groups ADD COLUMN description TEXT")
                print("✅ Spalte 'description' hinzugefügt")
            
            if 'invite_link' not in existing_columns:
                cursor.execute("ALTER TABLE groups ADD COLUMN invite_link VARCHAR")
                print("✅ Spalte 'invite_link' hinzugefügt")
            
            if 'last_checked' not in existing_columns:
                cursor.execute("ALTER TABLE groups ADD COLUMN last_checked DATETIME")
                print("✅ Spalte 'last_checked' hinzugefügt")
            
            conn.commit()
            print("\n✅ Migration erfolgreich abgeschlossen!")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Fehler bei Migration: {e}")
            raise
        finally:
            conn.close()

if __name__ == "__main__":
    print("🔄 Starte Datenbank-Migration für groups-Tabelle...\n")
    migrate_groups_table()

