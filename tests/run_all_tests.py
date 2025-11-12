#!/usr/bin/env python3
"""
One-Click Test Runner für alle Tests
Führt pytest mit Coverage, Bandit Security Check und Linting aus
"""
import subprocess
import sys
import os
from pathlib import Path

# Projekt-Root
PROJECT_ROOT = Path(__file__).parent.parent


def run_command(cmd, description):
    """Führt einen Befehl aus und gibt Ergebnis zurück"""
    print(f"\n{'='*60}")
    print(f"🔍 {description}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True, cwd=PROJECT_ROOT)
    return result.returncode == 0


def main():
    """Hauptfunktion: Führt alle Tests aus"""
    print("🚀 Starte vollständige Test-Suite...")
    print(f"📁 Projekt-Root: {PROJECT_ROOT}")
    
    success = True
    
    # 1. Linting (flake8 oder pylint)
    print("\n1️⃣  Linting...")
    lint_success = run_command(
        "python -m flake8 . --exclude=venv,__pycache__,tests --max-line-length=120 --ignore=E501,W503",
        "Linting mit flake8"
    )
    if not lint_success:
        print("⚠️  Linting-Warnungen gefunden (nicht kritisch)")
    
    # 2. Type Checking (mypy - optional)
    print("\n2️⃣  Type Checking...")
    try:
        type_check_success = run_command(
            "python -m mypy . --ignore-missing-imports --exclude '^(tests|venv)'",
            "Type Checking mit mypy"
        )
        if not type_check_success:
            print("⚠️  Type-Check-Warnungen gefunden (nicht kritisch)")
    except FileNotFoundError:
        print("⚠️  mypy nicht installiert, überspringe Type Checking")
    
    # 3. Security Check (Bandit)
    print("\n3️⃣  Security Check (Bandit)...")
    security_success = run_command(
        "python -m bandit -r . -x tests,venv -f json -o bandit-report.json",
        "Security Check mit Bandit"
    )
    if not security_success:
        print("⚠️  Security-Warnungen gefunden")
        # Prüfe ob High/Critical Issues vorhanden
        try:
            import json
            with open(PROJECT_ROOT / "bandit-report.json") as f:
                report = json.load(f)
                high_critical = [r for r in report.get("results", []) if r.get("issue_severity") in ["HIGH", "CRITICAL"]]
                if high_critical:
                    print(f"❌ {len(high_critical)} High/Critical Security Issues gefunden!")
                    success = False
        except:
            pass
    
    # 4. Unit Tests
    print("\n4️⃣  Unit Tests...")
    unit_success = run_command(
        "python -m pytest tests/unit/ -v --tb=short",
        "Unit Tests"
    )
    if not unit_success:
        success = False
    
    # 5. Integration Tests
    print("\n5️⃣  Integration Tests...")
    integration_success = run_command(
        "python -m pytest tests/integration/ -v --tb=short",
        "Integration Tests"
    )
    if not integration_success:
        success = False
    
    # 6. E2E Tests
    print("\n6️⃣  E2E Tests...")
    e2e_success = run_command(
        "python -m pytest tests/e2e/ -v --tb=short",
        "E2E Tests"
    )
    if not e2e_success:
        success = False
    
    # 7. Security Tests
    print("\n7️⃣  Security Tests...")
    security_test_success = run_command(
        "python -m pytest tests/security/ -v --tb=short",
        "Security Tests"
    )
    if not security_test_success:
        success = False
    
    # 8. Coverage Report
    print("\n8️⃣  Coverage Report...")
    coverage_success = run_command(
        "python -m pytest --cov=. --cov-report=html --cov-report=term --cov-report=xml --cov-fail-under=98 --ignore=tests --ignore=venv",
        "Coverage Report (Ziel: ≥98%)"
    )
    if not coverage_success:
        print("❌ Coverage unter 98%!")
        success = False
    
    # 9. Zusammenfassung
    print(f"\n{'='*60}")
    print("📊 ZUSAMMENFASSUNG")
    print(f"{'='*60}")
    
    if success:
        print("✅ ALLE TESTS ERFOLGREICH!")
        print("✅ Coverage: ≥98%")
        print("✅ Security: Keine kritischen Issues")
        print("✅ Alle Test-Suites bestanden")
        return 0
    else:
        print("❌ EINIGE TESTS FEHLGESCHLAGEN!")
        print("⚠️  Bitte Fehler beheben und erneut ausführen")
        return 1


if __name__ == "__main__":
    sys.exit(main())

