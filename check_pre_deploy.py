#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arsenal Pre-Deploy Checklist
Script de vérification avant déploiement Render
"""

import os
import json
import importlib.util
from pathlib import Path
import asyncio

class PreDeployChecker:
    def __init__(self):
        self.project_root = Path("A:/Arsenal_propre")
        self.issues = []
        self.warnings = []
        self.passed_checks = []
    
    def log_pass(self, check_name: str, details: str = ""):
        """Log une vérification réussie"""
        self.passed_checks.append({"name": check_name, "details": details})
        status = "✅"
        print(f"{status} {check_name}")
        if details:
            print(f"   → {details}")
    
    def log_warning(self, check_name: str, details: str):
        """Log un avertissement"""
        self.warnings.append({"name": check_name, "details": details})
        status = "⚠️"
        print(f"{status} {check_name}")
        print(f"   → {details}")
    
    def log_issue(self, check_name: str, details: str):
        """Log un problème critique"""
        self.issues.append({"name": check_name, "details": details})
        status = "❌"
        print(f"{status} {check_name}")
        print(f"   → {details}")
    
    def check_essential_files(self):
        """Vérifier les fichiers essentiels"""
        print("\n📋 VÉRIFICATION FICHIERS ESSENTIELS")
        print("=" * 50)
        
        essential_files = {
            "main.py": "Point d'entrée bot",
            "Procfile": "Configuration Render",
            "requirements.txt": "Dépendances Python",
            "runtime.txt": "Version Python",
            ".env.example": "Template configuration"
        }
        
        for file, description in essential_files.items():
            file_path = self.project_root / file
            if file_path.exists():
                size = file_path.stat().st_size
                if size > 0:
                    self.log_pass(f"{file}", f"{description} ({size} bytes)")
                else:
                    self.log_warning(f"{file}", f"{description} - Fichier vide")
            else:
                self.log_issue(f"{file}", f"{description} - Fichier manquant")
    
    def check_dependencies(self):
        """Vérifier requirements.txt"""
        print("\n📦 VÉRIFICATION DÉPENDANCES")
        print("=" * 50)
        
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r', encoding='utf-8') as f:
                requirements = f.read().strip().split('\n')
            
            essential_deps = {
                'discord.py': 'Discord API',
                'python-dotenv': 'Variables environnement',
                'aiofiles': 'Fichiers asynchrones',
                'aiosqlite': 'Base de données',
                'requests': 'Requêtes HTTP'
            }
            
            found_deps = []
            for req in requirements:
                if req and not req.startswith('#'):
                    dep_name = req.split('>=')[0].split('==')[0].strip()
                    found_deps.append(dep_name)
            
            for dep, description in essential_deps.items():
                if any(dep in found for found in found_deps):
                    self.log_pass(f"Dépendance {dep}", description)
                else:
                    self.log_issue(f"Dépendance {dep}", f"{description} - Manquante")
            
            self.log_pass("Requirements.txt", f"{len(found_deps)} dépendances listées")
        else:
            self.log_issue("Requirements.txt", "Fichier manquant")
    
    def check_project_structure(self):
        """Vérifier structure du projet"""
        print("\n📁 VÉRIFICATION STRUCTURE PROJET")
        print("=" * 50)
        
        required_dirs = {
            "commands": "Commandes bot",
            "core": "Système principal",
            "data": "Base de données",
            "logs": "Fichiers logs"
        }
        
        for dir_name, description in required_dirs.items():
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                file_count = len(list(dir_path.glob("*.py")))
                self.log_pass(f"Dossier {dir_name}/", f"{description} ({file_count} fichiers .py)")
            else:
                self.log_warning(f"Dossier {dir_name}/", f"{description} - Manquant")
    
    def check_commands_files(self):
        """Vérifier fichiers de commandes"""
        print("\n⚡ VÉRIFICATION COMMANDES")
        print("=" * 50)
        
        commands_dir = self.project_root / "commands"
        if commands_dir.exists():
            py_files = list(commands_dir.glob("*.py"))
            
            essential_commands = [
                "arsenal_economy_system.py",
                "arsenal_config_complete.py", 
                "arsenal_update_notifier.py",
                "arsenal_shop_admin.py"
            ]
            
            for cmd_file in essential_commands:
                cmd_path = commands_dir / cmd_file
                if cmd_path.exists():
                    size = cmd_path.stat().st_size
                    self.log_pass(f"Commande {cmd_file}", f"{size} bytes")
                else:
                    self.log_issue(f"Commande {cmd_file}", "Fichier manquant")
            
            self.log_pass("Total commandes", f"{len(py_files)} fichiers Python")
        else:
            self.log_issue("Dossier commands/", "Dossier manquant")
    
    def check_config_files(self):
        """Vérifier fichiers de configuration"""
        print("\n⚙️ VÉRIFICATION CONFIGURATION")
        print("=" * 50)
        
        # Vérifier .env.example
        env_example = self.project_root / ".env.example"
        if env_example.exists():
            with open(env_example, 'r') as f:
                env_content = f.read()
                
            required_vars = ['DISCORD_TOKEN', 'CREATOR_ID', 'PREFIX']
            for var in required_vars:
                if var in env_content:
                    self.log_pass(f"Variable {var}", "Présente dans .env.example")
                else:
                    self.log_warning(f"Variable {var}", "Absente de .env.example")
        
        # Vérifier Procfile
        procfile = self.project_root / "Procfile"
        if procfile.exists():
            with open(procfile, 'r') as f:
                procfile_content = f.read().strip()
            
            if "python main.py" in procfile_content:
                self.log_pass("Procfile", f"Commande: {procfile_content}")
            else:
                self.log_warning("Procfile", f"Contenu inattendu: {procfile_content}")
    
    def check_documentation(self):
        """Vérifier documentation"""
        print("\n📚 VÉRIFICATION DOCUMENTATION")
        print("=" * 50)
        
        docs = [
            "RENDER_DEPLOYMENT_GUIDE.md",
            "CHANGELOG_ARSENAL_COMPLET.md",
            "GUIDE_UPDATE_NOTIFICATIONS.md",
            "NOTIFICATION_SYSTEM_COMPLETE.md"
        ]
        
        for doc in docs:
            doc_path = self.project_root / doc
            if doc_path.exists():
                size = doc_path.stat().st_size
                self.log_pass(f"Doc {doc}", f"{size} bytes")
            else:
                self.log_warning(f"Doc {doc}", "Documentation manquante")
    
    def check_database_structure(self):
        """Vérifier structure base de données"""
        print("\n💾 VÉRIFICATION BASE DE DONNÉES")
        print("=" * 50)
        
        data_dir = self.project_root / "data"
        if data_dir.exists():
            db_files = list(data_dir.glob("*.db")) + list(data_dir.glob("*.json"))
            
            if db_files:
                for db_file in db_files[:5]:  # Montrer les 5 premiers
                    size = db_file.stat().st_size
                    self.log_pass(f"DB {db_file.name}", f"{size} bytes")
                
                if len(db_files) > 5:
                    self.log_pass("Autres DB", f"{len(db_files)-5} fichiers supplémentaires")
            else:
                self.log_warning("Base de données", "Aucun fichier .db/.json trouvé")
        else:
            self.log_warning("Dossier data/", "Dossier manquant")
    
    def print_summary(self):
        """Afficher résumé final"""
        print("\n" + "="*60)
        print("📊 RÉSUMÉ VÉRIFICATION PRE-DEPLOY")
        print("="*60)
        
        total_checks = len(self.passed_checks) + len(self.warnings) + len(self.issues)
        
        print(f"✅ Vérifications réussies: {len(self.passed_checks)}")
        print(f"⚠️  Avertissements: {len(self.warnings)}")
        print(f"❌ Problèmes critiques: {len(self.issues)}")
        print(f"📊 Total vérifications: {total_checks}")
        
        if self.issues:
            print(f"\n🚨 PROBLÈMES CRITIQUES À RÉSOUDRE:")
            for issue in self.issues[:5]:
                print(f"   • {issue['name']}: {issue['details']}")
        
        if self.warnings:
            print(f"\n⚠️  AVERTISSEMENTS:")
            for warning in self.warnings[:3]:
                print(f"   • {warning['name']}: {warning['details']}")
        
        print(f"\n🎯 STATUT DÉPLOIEMENT:")
        if len(self.issues) == 0:
            if len(self.warnings) <= 2:
                print("🟢 PRÊT POUR PRODUCTION - Déploiement recommandé")
            else:
                print("🟡 PRÊT AVEC RÉSERVES - Corriger avertissements si possible")
        else:
            print("🔴 NON PRÊT - Corriger problèmes critiques avant deploy")
        
        return len(self.issues) == 0

def main():
    """Lance toutes les vérifications"""
    print("🚀 ARSENAL PRE-DEPLOY CHECKLIST")
    print("Vérification complète avant déploiement Render...")
    
    checker = PreDeployChecker()
    
    # Lancer toutes les vérifications
    checker.check_essential_files()
    checker.check_dependencies()
    checker.check_project_structure()
    checker.check_commands_files()
    checker.check_config_files()
    checker.check_documentation()
    checker.check_database_structure()
    
    # Résumé final
    ready_to_deploy = checker.print_summary()
    
    if ready_to_deploy:
        print(f"\n🚀 NEXT STEPS:")
        print("1. Commit et push vers GitHub:")
        print("   git add .")
        print("   git commit -m 'Arsenal V4.5.0 - Ready for Production 🚀'")
        print("   git push origin main")
        print("\n2. Configurer variables d'environnement sur Render")
        print("3. Lancer déploiement depuis dashboard Render")
    else:
        print(f"\n🔧 CORRECTIONS NÉCESSAIRES:")
        print("Résoudre les problèmes critiques avant déploiement")
    
    return ready_to_deploy

if __name__ == "__main__":
    ready = main()
    exit(0 if ready else 1)
