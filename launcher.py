#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ARSENAL BOT LAUNCHER - Script de lancement ultra-stable pour Render
Gère les redémarrages automatiques et la stabilité du bot
Par xerox3elite - Arsenal V4.5.2 ULTIMATE
"""

import sys
import time
import subprocess
import os
from datetime import datetime

def log_message(message):
    """Log avec timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def start_bot():
    """Démarre le bot avec gestion d'erreurs"""
    log_message("🚀 Démarrage Arsenal Bot...")
    
    try:
        # Variables d'environnement pour stabilité
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'  # Sortie immédiate
        env['PYTHONIOENCODING'] = 'utf-8'  # Encoding UTF-8
        
        # Lancement du bot
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=env
        )
        
        log_message("✅ Bot démarré avec succès!")
        
        # Affichage en temps réel des logs
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line.rstrip())
        
        # Attendre la fin du processus
        process.wait()
        return process.returncode
        
    except Exception as e:
        log_message(f"❌ Erreur lors du démarrage: {e}")
        return 1

def main():
    """Fonction principale avec auto-restart"""
    log_message("🔧 Arsenal Bot Launcher V4.5.2 - Mode Render")
    
    max_restarts = 5  # Maximum 5 redémarrages
    restart_count = 0
    
    while restart_count < max_restarts:
        if restart_count > 0:
            log_message(f"🔄 Redémarrage #{restart_count}/{max_restarts}")
            time.sleep(10)  # Attendre 10 secondes avant redémarrage
        
        exit_code = start_bot()
        
        if exit_code == 0:
            log_message("✅ Bot arrêté proprement")
            break
        else:
            restart_count += 1
            log_message(f"⚠️ Bot crashé avec code {exit_code}")
            
            if restart_count < max_restarts:
                log_message(f"🔄 Redémarrage automatique dans 10 secondes...")
            else:
                log_message("❌ Nombre maximum de redémarrages atteint!")
                break
    
    log_message("🛑 Launcher terminé")
    return exit_code

if __name__ == "__main__":
    exit(main())

