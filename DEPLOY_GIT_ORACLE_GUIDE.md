# 🚀 Arsenal V4.5.2 Ultimate - Guide de Déploiement Git + Oracle

## 📋 Étapes de Déploiement

### 1️⃣ Préparation Git

```bash
# Vérifier l'état du repository
git status

# Ajouter tous les fichiers
git add .

# Commit avec message descriptif
git commit -m "🚀 Arsenal V4.5.2 Ultimate - Ready for Oracle deployment

✅ Features implemented:
- Advanced Ticket System (584 lines)
- Unified Config System (300+ lines) 
- Custom Commands System (500+ lines)
- Command Analyzer & Code Cleaner
- 43 cogs loaded, 525 active commands
- Conflicts reduced from 55 to 13

🔧 Optimizations:
- Removed 20 dead files
- Fixed duplicate decorators
- Renamed conflicting commands
- Clean codebase ready for production"

# Push vers le repository
git push origin main
```

### 2️⃣ Déploiement Oracle Cloud

```bash
# Connexion SSH à Oracle
ssh -i ~/.ssh/oracle-key ubuntu@your-oracle-ip

# Clone/Pull du repository
git clone https://github.com/xerox3elite/bot-discord.git arsenal-bot
# OU si déjà cloné:
cd arsenal-bot && git pull origin main

# Installation Python et dépendances
sudo apt update
sudo apt install python3 python3-pip python3-venv -y

# Création environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt
```

### 3️⃣ Configuration Variables d'Environnement

```bash
# Créer le fichier .env
nano .env

# Ajouter:
DISCORD_TOKEN=your_discord_token_here
CREATOR_ID=431359112039890945
PREFIX=!

# Ou utiliser les variables système Oracle
export DISCORD_TOKEN="your_token"
export CREATOR_ID="431359112039890945"
export PREFIX="!"
```

### 4️⃣ Démarrage du Bot

```bash
# Test manuel
python3 main.py

# Ou utiliser le script de déploiement
chmod +x deploy_oracle.sh
./deploy_oracle.sh
```

### 5️⃣ Configuration Service Systemd (Optionnel)

```bash
# Créer le service
sudo nano /etc/systemd/system/arsenal-bot.service

# Contenu:
[Unit]
Description=Arsenal Discord Bot V4.5.2 Ultimate
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/arsenal-bot
Environment=PATH=/home/ubuntu/arsenal-bot/venv/bin
ExecStart=/home/ubuntu/arsenal-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Activer le service
sudo systemctl daemon-reload
sudo systemctl enable arsenal-bot
sudo systemctl start arsenal-bot

# Vérifier le statut
sudo systemctl status arsenal-bot
```

## 📊 État du Bot Après Déploiement

### ✅ Systèmes Actifs (43 cogs):
- **Advanced Ticket System**: Tickets avec catégories et modals
- **Arsenal Config Unified**: Configuration centralisée /config  
- **Custom Commands**: 15 commandes personnalisées par serveur
- **Hunt Royal Integration**: Système Hunt Royal complet
- **Economy System**: ArsenalCoin et système de niveaux
- **Moderation Tools**: AutoMod V5 avec sanctions
- **Voice Management**: Hub vocal et music système
- **Analytics**: Monitoring et statistiques avancées
- **Profile Ultimate 2000%**: Profil bot révolutionnaire

### 📈 Statistiques:
- **525 commandes actives** (vs 222 initialement)
- **43 cogs chargés** (vs 28 initialement)
- **358 commandes inactives** (vs 1238 initialement)
- **13 conflits restants** (vs 55 initialement)
- **Code optimisé**: 20 fichiers morts supprimés

## 🔧 Monitoring et Maintenance

### Logs:
```bash
# Logs du service
sudo journalctl -u arsenal-bot -f

# Logs du bot
tail -f logs/bot.log
```

### Mise à jour:
```bash
cd arsenal-bot
git pull origin main
sudo systemctl restart arsenal-bot
```

### Health Check:
```bash
python3 healthcheck.py
```

## 🚨 Dépannage

### Bot ne démarre pas:
1. Vérifier les variables d'environnement
2. Vérifier les permissions Discord
3. Vérifier les logs: `sudo journalctl -u arsenal-bot`

### Commandes en conflit:
- Les 13 conflits restants sont documentés
- Utiliser `/helpv2` au lieu de `/help`
- Utiliser `/huntcalc` au lieu de `/calculator`

### Performance:
- RAM recommandée: 1GB+
- CPU: 1 vCore minimum
- Stockage: 2GB minimum

---
**Arsenal V4.5.2 Ultimate** - Le bot Discord le plus avancé 🚀
