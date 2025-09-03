#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 Arsenal V4.5.2 Ultimate - Deployment Ready Check
=================================================
Vérification finale avant déploiement sur Git + Oracle
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def main():
    """Vérification complète de l'état de déploiement"""
    print("🚀 ARSENAL V4.5.2 ULTIMATE - DEPLOYMENT READY CHECK")
    print("=" * 60)
    
    errors = []
    warnings = []
    
    # 1. Vérifier les fichiers essentiels
    print("\n📁 [CHECK] Fichiers essentiels...")
    essential_files = [
        "main.py",
        "requirements.txt",
        "deploy_oracle.sh",
        "DEPLOY_GIT_ORACLE_GUIDE.md"
    ]
    
    for file in essential_files:
        if Path(file).exists():
            print(f"✅ [OK] {file}")
        else:
            print(f"❌ [ERROR] {file} manquant")
            errors.append(f"Fichier manquant: {file}")
    
    # 2. Vérifier main.py
    print("\n🔍 [CHECK] Syntaxe main.py...")
    try:
        with open("main.py", 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, "main.py", 'exec')
        print("✅ [OK] Syntaxe main.py valide")
        
        # Vérifier que les systèmes sont chargés
        if "ArsenalConfigSystemUnified" in code:
            print("✅ [OK] Système de config unifié détecté")
        
        if "AdvancedTicketSystem" in code:
            print("✅ [OK] Système de tickets avancé détecté")
            
        if "ArsenalCustomCommands" in code:
            print("✅ [OK] Système de commandes personnalisées détecté")
            
    except SyntaxError as e:
        print(f"❌ [ERROR] Erreur syntaxe main.py: {e}")
        errors.append(f"Erreur syntaxe: {e}")
    except Exception as e:
        print(f"⚠️ [WARNING] Problème lecture main.py: {e}")
        warnings.append(f"Problème main.py: {e}")
    
    # 3. Vérifier requirements.txt
    print("\n📦 [CHECK] Dépendances...")
    try:
        with open("requirements.txt", 'r') as f:
            deps = f.read()
            
        critical_deps = ['discord.py', 'aiosqlite']
        for dep in critical_deps:
            if dep in deps:
                print(f"✅ [OK] {dep} présent")
            else:
                print(f"❌ [ERROR] {dep} manquant")
                errors.append(f"Dépendance manquante: {dep}")
                
    except Exception as e:
        print(f"❌ [ERROR] Problème requirements.txt: {e}")
        errors.append(f"Erreur requirements: {e}")
    
    # 4. Vérifier la structure
    print("\n📂 [CHECK] Structure du projet...")
    required_dirs = ['commands', 'core', 'data', 'logs']
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            py_files = list(Path(dir_name).glob("*.py"))
            print(f"✅ [OK] {dir_name}/ ({len(py_files)} fichiers)")
        else:
            print(f"⚠️ [WARNING] {dir_name}/ manquant")
            warnings.append(f"Dossier manquant: {dir_name}")
    
    # 5. Vérifier Git
    print("\n🔀 [CHECK] État Git...")
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            uncommitted = result.stdout.strip()
            if uncommitted:
                lines = len(uncommitted.split('\n'))
                print(f"⚠️ [WARNING] {lines} fichiers non commités")
                warnings.append(f"{lines} fichiers non commités")
            else:
                print("✅ [OK] Repository Git propre")
        else:
            print("⚠️ [WARNING] Problème Git")
            
    except FileNotFoundError:
        print("⚠️ [WARNING] Git non disponible")
        warnings.append("Git non installé")
    
    # 6. Vérifier les variables d'environnement
    print("\n🔧 [CHECK] Variables d'environnement...")
    
    # Chercher .env
    if Path(".env").exists():
        print("✅ [OK] .env trouvé")
        try:
            with open(".env", 'r') as f:
                env_content = f.read()
                if "DISCORD_TOKEN" in env_content:
                    print("✅ [OK] DISCORD_TOKEN dans .env")
                else:
                    print("⚠️ [WARNING] DISCORD_TOKEN manquant dans .env")
                    warnings.append("DISCORD_TOKEN manquant dans .env")
        except Exception:
            pass
    else:
        print("⚠️ [WARNING] .env non trouvé")
        warnings.append("Fichier .env non trouvé")
        
        # Vérifier variables système
        if os.getenv("DISCORD_TOKEN"):
            print("✅ [OK] DISCORD_TOKEN dans variables système")
        else:
            print("❌ [ERROR] DISCORD_TOKEN non défini")
            errors.append("DISCORD_TOKEN non défini")
    
    # 7. Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE VÉRIFICATION")
    print("=" * 60)
    
    print(f"❌ Erreurs critiques: {len(errors)}")
    print(f"⚠️ Avertissements: {len(warnings)}")
    
    if errors:
        print("\n🚨 ERREURS CRITIQUES À CORRIGER:")
        for error in errors:
            print(f"  • {error}")
        print("\n❗ Corrigez ces erreurs avant de déployer !")
        return False
    else:
        print("\n🎉 [SUCCESS] Projet prêt pour le déploiement !")
        
        if warnings:
            print("\n⚠️ AVERTISSEMENTS (non critiques):")
            for warning in warnings:
                print(f"  • {warning}")
        
        print("\n📋 COMMANDES DE DÉPLOIEMENT:")
        print("1️⃣ Git:")
        print("   git add .")
        print('   git commit -m "🚀 Arsenal V4.5.2 Ultimate Ready"')
        print("   git push origin main")
        print("\n2️⃣ Oracle:")
        print("   ssh ubuntu@your-oracle-ip")
        print("   git pull origin main")
        print("   python3 main.py")
        print("\n🚀 Bon déploiement !")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
