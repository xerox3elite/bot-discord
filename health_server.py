#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arsenal Health Server - Serveur Flask minimal pour Render Web Service
Permet à Arsenal de fonctionner comme Web Service avec health check
"""

from flask import Flask, jsonify
import threading
import json
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    """Page d'accueil Arsenal"""
    return jsonify({
        "bot": "Arsenal V4.5.0",
        "status": "online",
        "description": "Bot Discord Arsenal avec 150+ commandes",
        "features": [
            "ArsenalCoin Economy System",
            "29 Modules Configuration", 
            "Hunt Royal Integration",
            "Update Notification System",
            "XP/Level System"
        ],
        "timestamp": datetime.now().isoformat(),
        "version": "4.5.0"
    })

@app.route('/health')
def health():
    """Health check pour Render"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Arsenal Bot Discord"
    })

@app.route('/status')
def bot_status():
    """Status du bot Discord"""
    try:
        # Lire le fichier de status du bot
        if os.path.exists('bot_status.json'):
            with open('bot_status.json', 'r', encoding='utf-8') as f:
                status_data = json.load(f)
        else:
            status_data = {
                "online": False,
                "status": "initializing"
            }
        
        return jsonify(status_data)
    except:
        return jsonify({
            "online": False,
            "status": "error",
            "message": "Status file not accessible"
        })

def start_health_server():
    """Démarre le serveur Flask pour health checks"""
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == '__main__':
    # Si exécuté directement, démarrer seulement le serveur Flask
    start_health_server()
