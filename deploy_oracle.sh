#!/bin/bash

echo "🚀 Arsenal Bot - Oracle Cloud Setup"
echo "=================================="

# Update système
sudo apt update && sudo apt upgrade -y

# Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip git -y

# Créer utilisateur arsenal
sudo useradd -m -s /bin/bash arsenal
sudo usermod -aG sudo arsenal

# Créer dossier projet
sudo mkdir -p /opt/arsenal
sudo chown arsenal:arsenal /opt/arsenal

# Clone le repo
cd /opt/arsenal
git clone https://github.com/xerox3elite/bot-discord.git .

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Permissions
sudo chown -R arsenal:arsenal /opt/arsenal

echo "✅ Installation terminée !"
echo "📝 Prochaine étape : Configuration .env"
