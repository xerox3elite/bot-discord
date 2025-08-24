#!/usr/bin/env python3
"""
Arsenal V4 WebPanel - Test Local
Test rapide de l'interface avancée
"""

import os
import sys
import subprocess
import time

def test_local_interface():
    print("🚀 Arsenal V4 WebPanel - Test Local")
    print("=" * 50)
    
    # Vérifier la structure des fichiers
    required_files = [
        'backend/app.py',
        'frontend/index.html',
        'frontend/js/arsenal-api.js',
        'frontend/js/arsenal-ui.js',
        'frontend/css/arsenal-theme.css'
    ]
    
    print("\n📁 Vérification des fichiers:")
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MANQUANT")
    
    # Vérifier la base de données
    if os.path.exists('backend/arsenal_v4.db'):
        print("  ✅ backend/arsenal_v4.db")
        # Taille de la DB
        size = os.path.getsize('backend/arsenal_v4.db')
        print(f"     Taille: {size} bytes")
    else:
        print("  ❌ backend/arsenal_v4.db - MANQUANT")
    
    print("\n🔧 Lancement du serveur Flask...")
    
    try:
        # Changer vers le répertoire backend
        os.chdir('backend')
        
        # Définir les variables d'environnement pour le test
        env = os.environ.copy()
        env['FLASK_DEBUG'] = '1'
        env['DISCORD_CLIENT_ID'] = 'TEST_CLIENT_ID'
        
        # Lancer le serveur
        print("   Démarrage sur http://localhost:5000")
        print("   Appuyez sur Ctrl+C pour arrêter")
        print("=" * 50)
        
        subprocess.run([sys.executable, 'app.py'], env=env)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Serveur arrêté par l'utilisateur")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
    
    print("\n✅ Test terminé")

if __name__ == "__main__":
    test_local_interface()

