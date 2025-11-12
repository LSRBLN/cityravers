"""
Aktualisiert Accounts mit Telefonnummern aus JSON-Dateien
"""
import os
import json
from pathlib import Path
from database import init_db, Account
from sqlalchemy.orm import sessionmaker

db_engine = init_db()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
db = SessionLocal()

# JSON-Dateien mit Telefonnummern
json_files = {
    "12897046237": "+12897046237",
    "12897086495": "+12897086495",
    "13434362430": "+13434362430",
    "13434372101": "+13434372101",
    "13434382684": "+13434382684"
}

print("📋 Aktualisiere Accounts mit Telefonnummern...\n")

for account_name, phone_number in json_files.items():
    account = db.query(Account).filter(Account.name == account_name).first()
    if account:
        account.phone_number = phone_number
        print(f"✅ Account '{account_name}': Telefonnummer gesetzt: {phone_number}")
    else:
        print(f"⚠️  Account '{account_name}' nicht gefunden")

db.commit()
print(f"\n✅ {len(json_files)} Account(s) aktualisiert")

db.close()

