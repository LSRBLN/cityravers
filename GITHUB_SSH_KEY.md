# 🔑 GitHub SSH-Key für Deployment

## ✅ SSH-Key erstellt

**Key-Dateien:**
- **Privater Key:** `~/.ssh/id_ed25519_github_deploy`
- **Öffentlicher Key:** `~/.ssh/id_ed25519_github_deploy.pub`

**Key-Typ:** ED25519 (modern & sicher)

---

## 📋 Öffentlicher SSH-Key

```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOVsJku+qj+Oadfg8rCesJQFd1CipRwoo2Y/8oHgLzJ4 github-deploy-20251117
```

---

## 🚀 Key zu GitHub hinzufügen

### Schritt 1: Key kopieren

```bash
cat ~/.ssh/id_ed25519_github_deploy.pub | pbcopy
```

Oder manuell kopieren (siehe oben).

### Schritt 2: GitHub öffnen

1. **Gehe zu:** https://github.com/settings/keys
2. **"New SSH key"** klicken
3. **Title:** `GitHub Deploy Key` (oder beliebiger Name)
4. **Key:** Füge den öffentlichen Key ein (siehe oben)
5. **"Add SSH key"** klicken

### Schritt 3: Für Repository (Deploy Key)

Falls du einen Deploy Key für ein spezifisches Repository brauchst:

1. **Repository öffnen:** `phnxvision-pixel/tele`
2. **Settings** → **Deploy keys** → **"Add deploy key"**
3. **Title:** `Deploy Key`
4. **Key:** Füge den öffentlichen Key ein
5. **✅ "Allow write access"** (falls nötig für Deployments)
6. **"Add key"** klicken

---

## ✅ SSH-Verbindung testen

```bash
ssh -T git@github.com
```

**Erwartete Ausgabe:**
```
Hi phnxvision-pixel! You've successfully authenticated, but GitHub does not provide shell access.
```

---

## 🔧 SSH-Config

Die SSH-Config wurde automatisch erstellt:

**Datei:** `~/.ssh/config`

```ssh-config
# GitHub Deploy Key
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_github_deploy
  IdentitiesOnly yes
```

Diese Config stellt sicher, dass GitHub automatisch den richtigen Key verwendet.

---

## 🔄 Remote-URL auf SSH umstellen

**WICHTIG:** Dein Repository verwendet aktuell HTTPS. Um SSH zu verwenden:

```bash
cd /Users/rebelldesign/Documents/telegram-bot

# Aktuelle Remote-URL prüfen
git remote -v

# Auf SSH umstellen
git remote set-url origin git@github.com:phnxvision-pixel/tele.git

# Testen
git remote -v
```

**Nach dem Umstellen:**
- Keine Token mehr nötig
- Automatische Authentifizierung mit SSH-Key
- Sicherer für CI/CD Deployments

---

## 🐛 Troubleshooting

### Problem: "Permission denied (publickey)"

**Lösung:**
```bash
# Key zum SSH-Agent hinzufügen
ssh-add ~/.ssh/id_ed25519_github_deploy

# Testen
ssh -T git@github.com
```

### Problem: "Host key verification failed"

**Lösung:**
```bash
# GitHub's Host-Key hinzufügen
ssh-keyscan github.com >> ~/.ssh/known_hosts
```

### Problem: Falscher Key wird verwendet

**Lösung:**
```bash
# SSH-Agent leeren
ssh-add -D

# Nur den GitHub-Deploy-Key hinzufügen
ssh-add ~/.ssh/id_ed25519_github_deploy

# Testen
ssh -T git@github.com
```

---

## 🔒 Sicherheit

- ✅ **Privater Key:** Niemals teilen oder committen!
- ✅ **Berechtigungen:** `~/.ssh/id_ed25519_github_deploy` sollte `600` sein
- ✅ **Backup:** Privaten Key sicher aufbewahren
- ✅ **Rotation:** Keys regelmäßig rotieren (alle 6-12 Monate)

---

## 📞 Hilfe

- **GitHub SSH Docs:** https://docs.github.com/en/authentication/connecting-to-github-with-ssh
- **SSH-Key generieren:** https://docs.github.com/en/authentication/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent
- **Deploy Keys:** https://docs.github.com/en/authentication/connecting-to-github-with-ssh/managing-deploy-keys

---

## ✅ Checkliste

- [x] SSH-Key erstellt
- [x] SSH-Config konfiguriert
- [ ] Öffentlichen Key zu GitHub hinzugefügt
- [ ] SSH-Verbindung getestet (`ssh -T git@github.com`)
- [ ] Remote-URL auf SSH umgestellt (falls nötig)
- [ ] Git-Operationen funktionieren

---

## 🎯 Nächste Schritte

1. **Key zu GitHub hinzufügen** (siehe oben)
2. **SSH-Verbindung testen**
3. **Remote-URL auf SSH umstellen** (falls nötig)
4. **Fertig!** Du kannst jetzt mit SSH pushen/pullen

