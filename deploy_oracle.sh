#!/bin/bash
echo "🚀 ARSENAL BOT - DÉPLOIEMENT ORACLE CLOUD"
echo "============================================="

# Configuration Oracle Cloud
INSTANCE_IP="your-oracle-instance-ip"
SSH_KEY="~/.ssh/oracle-key"
REMOTE_PATH="/home/ubuntu/arsenal-bot"

echo "📦 Préparation des fichiers de déploiement..."

# Créer requirements.txt optimisé pour production
echo "discord.py>=2.3.0
aiohttp>=3.8.0
asyncio
sqlite3
python-dotenv
psutil
colorama" > requirements.txt

echo "🔧 Création du fichier de service systemd..."
cat > arsenal-bot.service << 'EOF'
[Unit]
Description=Arsenal Discord Bot V4
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
EOF

echo "📋 Création du script de démarrage..."
cat > start_bot.sh << 'EOF'
#!/bin/bash
cd /home/ubuntu/arsenal-bot
source venv/bin/activate
export PYTHONPATH=/home/ubuntu/arsenal-bot:$PYTHONPATH
python main.py
EOF
chmod +x start_bot.sh

echo "🔄 Création du script de mise à jour..."
cat > update_bot.sh << 'EOF'
#!/bin/bash
echo "🔄 Mise à jour Arsenal Bot..."
cd /home/ubuntu/arsenal-bot
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo systemctl restart arsenal-bot
echo "✅ Bot mis à jour et redémarré !"
EOF
chmod +x update_bot.sh

echo "📡 Synchronisation avec Oracle Cloud..."
echo "rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.log' . ubuntu@$INSTANCE_IP:$REMOTE_PATH/"

echo "🏗️ Script de configuration serveur..."
cat > setup_server.sh << 'EOF'
#!/bin/bash
echo "🏗️ Configuration du serveur Oracle Cloud..."

# Mise à jour système
sudo apt update && sudo apt upgrade -y

# Installation Python 3.10
sudo apt install -y python3.10 python3.10-venv python3-pip git

# Création environnement virtuel
cd /home/ubuntu/arsenal-bot
python3.10 -m venv venv
source venv/bin/activate

# Installation dépendances
pip install --upgrade pip
pip install -r requirements.txt

# Configuration service systemd
sudo cp arsenal-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable arsenal-bot

# Configuration firewall
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Création des répertoires de logs
mkdir -p logs
chmod 755 logs

echo "✅ Serveur configuré ! Utilisez 'sudo systemctl start arsenal-bot' pour démarrer"
EOF
chmod +x setup_server.sh

echo ""
echo "🎯 ÉTAPES DE DÉPLOIEMENT :"
echo "1. Modifier INSTANCE_IP dans ce script avec votre IP Oracle"
echo "2. Copier vos fichiers : rsync -avz --exclude='.git' . ubuntu@IP:/home/ubuntu/arsenal-bot/"
echo "3. Se connecter : ssh -i ~/.ssh/oracle-key ubuntu@IP"
echo "4. Exécuter : chmod +x setup_server.sh && ./setup_server.sh"
echo "5. Configurer .env avec vos tokens"
echo "6. Démarrer : sudo systemctl start arsenal-bot"
echo "7. Vérifier : sudo systemctl status arsenal-bot"
echo ""
echo "🔄 Pour les mises à jour : ./update_bot.sh"
echo "📊 Logs en temps réel : sudo journalctl -u arsenal-bot -f"
echo ""
echo "✅ Scripts de déploiement prêts !"
