#!/usr/bin/env python3
"""
Test-Skript um zu prüfen, ob Daten in der Datenbank gespeichert werden
"""

import os
from database import init_db, get_session, User, Account, Group
from datetime import datetime

# Datenbank initialisieren
print("🔍 Initialisiere Datenbank...")
db_engine = init_db()
db = get_session(db_engine)

try:
    # Prüfe aktuelle Anzahl
    user_count_before = db.query(User).count()
    account_count_before = db.query(Account).count()
    group_count_before = db.query(Group).count()
    
    print(f"\n📊 Aktuelle Datenbank-Statistik:")
    print(f"  Users: {user_count_before}")
    print(f"  Accounts: {account_count_before}")
    print(f"  Groups: {group_count_before}")
    
    # Versuche Test-Daten zu speichern
    print("\n💾 Versuche Test-Daten zu speichern...")
    
    # Test-Gruppe erstellen
    test_group = Group(
        name="Test-Gruppe",
        chat_id="test_chat_123",
        chat_type="group",
        user_id=None
    )
    db.add(test_group)
    db.commit()
    db.refresh(test_group)
    
    print(f"✅ Test-Gruppe erstellt: ID={test_group.id}, Name={test_group.name}")
    
    # Prüfe ob gespeichert wurde
    group_count_after = db.query(Group).count()
    saved_group = db.query(Group).filter(Group.id == test_group.id).first()
    
    print(f"\n📊 Nach dem Speichern:")
    print(f"  Groups: {group_count_after} (vorher: {group_count_before})")
    
    if saved_group:
        print(f"✅ Gruppe wurde erfolgreich gespeichert!")
        print(f"   ID: {saved_group.id}")
        print(f"   Name: {saved_group.name}")
        print(f"   Chat ID: {saved_group.chat_id}")
    else:
        print("❌ Gruppe wurde NICHT gespeichert!")
    
    # Test-Gruppe wieder löschen
    print("\n🗑️  Lösche Test-Gruppe...")
    db.delete(test_group)
    db.commit()
    
    print("✅ Test-Gruppe gelöscht")
    
    # Prüfe ob Transaction funktioniert
    print("\n🔄 Teste Transaction...")
    test_group2 = Group(
        name="Test-Gruppe-2",
        chat_id="test_chat_456",
        chat_type="group",
        user_id=None
    )
    db.add(test_group2)
    db.flush()  # Flush ohne Commit
    
    # Prüfe ob nach Flush sichtbar
    group_after_flush = db.query(Group).filter(Group.id == test_group2.id).first()
    if group_after_flush:
        print("✅ Nach db.flush() ist Gruppe in Session sichtbar")
    else:
        print("❌ Nach db.flush() ist Gruppe NICHT in Session sichtbar")
    
    # Commit
    db.commit()
    db.refresh(test_group2)
    
    # Prüfe ob nach Commit sichtbar
    group_after_commit = db.query(Group).filter(Group.id == test_group2.id).first()
    if group_after_commit:
        print("✅ Nach db.commit() ist Gruppe gespeichert")
    else:
        print("❌ Nach db.commit() ist Gruppe NICHT gespeichert")
    
    # Lösche Test-Gruppe
    db.delete(test_group2)
    db.commit()
    
    print("\n✅ Test abgeschlossen!")
    
except Exception as e:
    print(f"\n❌ Fehler beim Test: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

