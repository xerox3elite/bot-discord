#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test final avant déploiement Render
Vérifie que tous les composants sont opérationnels
"""

import sys
import os
import traceback

def test_imports():
    """Test tous les imports requis"""
    print("🔍 Test des imports...")
    
    required_modules = [
        'flask', 'flask_cors', 'requests', 'psutil', 
        'sqlite3', 'secrets', 'datetime', 'json'
    ]
    
    local_modules = [
        'oauth_config', 'casino_system', 'sqlite_database'
    ]
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            return False
    
    # Test des modules locaux
    sys.path.append('backend')
    for module in local_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            return False
    
    return True

def test_database():
    """Test de la base de données"""
    print("🗄️ Test de la base de données...")
    
    try:
        sys.path.append('backend')
        from sqlite_database import ArsenalDatabase
        
        db = ArsenalDatabase()
        print("  ✅ Connexion DB OK")
        
        # Test d'une requête simple
        stats = db.get_stats()
        print("  ✅ Requête test OK")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Erreur DB: {e}")
        return False

def test_server_startup():
    """Test du démarrage du serveur Flask"""
    print("🌐 Test du serveur Flask...")
    
    try:
        sys.path.append('backend')
        from advanced_server import app
        
        # Test de création de l'app
        if app:
            print("  ✅ App Flask créée")
            
            # Test avec le test client
            with app.test_client() as client:
                response = client.get('/api')
                if response.status_code == 200:
                    print("  ✅ API répond")
                else:
                    print(f"  ⚠️ API status: {response.status_code}")
            
            return True
        else:
            print("  ❌ App Flask non créée")
            return False
            
    except Exception as e:
        print(f"  ❌ Erreur serveur: {e}")
        return False

def test_files():
    """Vérifier que tous les fichiers nécessaires existent"""
    print("📁 Test des fichiers...")
    
    required_files = [
        'requirements.txt',
        'Procfile',
        'start.sh',
        'backend/advanced_server.py',
        'backend/oauth_config.py',
        'backend/casino_system.py',
        'backend/sqlite_database.py',
        'advanced_interface.html',
        'login.html'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} manquant")
            return False
    
    return True

def main():
    """Test principal"""
    print("🚀 TEST FINAL AVANT DÉPLOIEMENT RENDER")
    print("=" * 50)
    
    tests = [
        ("Fichiers requis", test_files),
        ("Imports Python", test_imports), 
        ("Base de données", test_database),
        ("Serveur Flask", test_server_startup)
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name} - RÉUSSI\n")
            else:
                print(f"❌ {test_name} - ÉCHEC\n")
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} - ERREUR: {e}\n")
            traceback.print_exc()
            all_passed = False
    
    print("=" * 50)
    if all_passed:
        print("🎉 TOUS LES TESTS RÉUSSIS !")
        print("🚀 PRÊT POUR LE DÉPLOIEMENT SUR RENDER !")
        print("\nPour déployer :")
        print("1. Pusher le code sur GitHub")
        print("2. Connecter Render à votre repo")
        print("3. Configurer les variables d'environnement")
        print("4. Déployer !")
    else:
        print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("❌ CORRIGER LES ERREURS AVANT DÉPLOIEMENT")
    
    return all_passed

if __name__ == "__main__":
    sys.exit(0 if main() else 1)

