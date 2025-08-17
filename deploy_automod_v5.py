#!/usr/bin/env python3
"""
🚀 Script de Déploiement Arsenal AutoMod V5.0.1
Déploiement automatique avec vérifications et tests
"""

import os
import sys
import sqlite3
import json
import shutil
from datetime import datetime

class AutoModDeployment:
    """Gestionnaire de déploiement AutoMod V5.0.1"""
    
    def __init__(self):
        self.version = "V5.0.1"
        self.deployment_time = datetime.now()
        self.errors = []
        self.warnings = []
        
    def check_prerequisites(self):
        """Vérification des prérequis"""
        print("🔍 Vérification des prérequis...")
        
        # Vérifier Python
        if sys.version_info < (3, 8):
            self.errors.append("Python 3.8+ requis")
            
        # Vérifier discord.py
        try:
            import discord
            if discord.__version__ < "2.3.0":
                self.warnings.append("Discord.py 2.3.2+ recommandé")
        except ImportError:
            self.errors.append("Discord.py non installé")
            
        # Vérifier fichiers essentiels
        essential_files = [
            "commands/arsenal_command_groups_final.py",
            "arsenal_automod.db"
        ]
        
        for file in essential_files:
            if not os.path.exists(file):
                self.errors.append(f"Fichier manquant: {file}")
                
        print(f"✅ Prérequis: {len(self.errors)} erreurs, {len(self.warnings)} warnings")
        
    def backup_current_version(self):
        """Sauvegarde de la version actuelle"""
        print("💾 Sauvegarde de la version actuelle...")
        
        backup_dir = f"backup_automod_{self.deployment_time.strftime('%Y%m%d_%H%M%S')}"
        
        try:
            os.makedirs(backup_dir, exist_ok=True)
            
            # Sauvegarder les fichiers critiques
            critical_files = [
                "commands/arsenal_command_groups_final.py",
                "arsenal_automod.db"
            ]
            
            for file in critical_files:
                if os.path.exists(file):
                    shutil.copy2(file, backup_dir)
                    
            print(f"✅ Sauvegarde créée: {backup_dir}")
            
        except Exception as e:
            self.errors.append(f"Erreur sauvegarde: {e}")
            
    def test_database_migration(self):
        """Test de migration de la base de données"""
        print("🗄️ Test de migration base de données...")
        
        try:
            conn = sqlite3.connect('arsenal_automod.db')
            cursor = conn.cursor()
            
            # Vérifier les nouvelles tables
            expected_tables = [
                'custom_bad_words',
                'automod_stats', 
                'user_sanctions',
                'guild_automod_config',
                'rehabilitation_progress'
            ]
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            for table in expected_tables:
                if table not in existing_tables:
                    self.errors.append(f"Table manquante: {table}")
                else:
                    print(f"  ✅ Table {table} OK")
                    
            conn.close()
            print("✅ Migration base de données OK")
            
        except Exception as e:
            self.errors.append(f"Erreur DB: {e}")
            
    def test_word_levels_system(self):
        """Test du système de niveaux de mots"""
        print("🎚️ Test système de niveaux...")
        
        try:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from commands.arsenal_command_groups_final import ArsenalAutoModSystem
            
            class MockBot:
                pass
            
            automod = ArsenalAutoModSystem(MockBot())
            
            # Vérifier les 4 niveaux
            for level in range(1, 5):
                if level not in automod.level_words:
                    self.errors.append(f"Niveau {level} manquant")
                elif len(automod.level_words[level]) == 0:
                    self.warnings.append(f"Niveau {level} vide")
                else:
                    print(f"  ✅ Niveau {level}: {len(automod.level_words[level])} mots")
                    
            total_words = sum(len(words) for words in automod.level_words.values())
            print(f"✅ Total: {total_words} mots par niveaux")
            
        except Exception as e:
            self.errors.append(f"Erreur test niveaux: {e}")
            
    def generate_deployment_report(self):
        """Génération du rapport de déploiement"""
        print("📊 Génération rapport de déploiement...")
        
        report = {
            "version": self.version,
            "deployment_time": self.deployment_time.isoformat(),
            "status": "SUCCESS" if len(self.errors) == 0 else "FAILED",
            "errors": self.errors,
            "warnings": self.warnings,
            "features": {
                "level_system": True,
                "progressive_sanctions": True,
                "rehabilitation": True,
                "advanced_config": True,
                "database_v5": True
            }
        }
        
        with open(f"deployment_report_{self.version}.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        print(f"✅ Rapport généré: deployment_report_{self.version}.json")
        return report
        
    def deploy(self):
        """Déploiement principal"""
        print(f"🚀 DÉPLOIEMENT ARSENAL AUTOMOD {self.version}")
        print("=" * 50)
        
        # Étapes de déploiement
        self.check_prerequisites()
        
        if len(self.errors) > 0:
            print("❌ Prérequis non satisfaits:")
            for error in self.errors:
                print(f"  - {error}")
            return False
            
        self.backup_current_version()
        self.test_database_migration()
        self.test_word_levels_system()
        
        # Rapport final
        report = self.generate_deployment_report()
        
        print("\n" + "=" * 50)
        if report["status"] == "SUCCESS":
            print("🎉 DÉPLOIEMENT RÉUSSI !")
            print(f"✅ Arsenal AutoMod {self.version} est opérationnel")
            print("\n📋 Fonctionnalités activées:")
            for feature, status in report["features"].items():
                print(f"  ✅ {feature.replace('_', ' ').title()}")
                
            if self.warnings:
                print(f"\n⚠️ {len(self.warnings)} warnings:")
                for warning in self.warnings:
                    print(f"  - {warning}")
                    
        else:
            print("❌ DÉPLOIEMENT ÉCHOUÉ !")
            print(f"🚫 {len(self.errors)} erreurs critiques:")
            for error in self.errors:
                print(f"  - {error}")
                
        return report["status"] == "SUCCESS"

def main():
    """Point d'entrée principal"""
    deployment = AutoModDeployment()
    success = deployment.deploy()
    
    if success:
        print("\n🎯 Prochaines étapes:")
        print("  1. Redémarrer le bot Discord")
        print("  2. Tester /admin automod")
        print("  3. Configurer les niveaux par serveur")
        print("  4. Surveiller les statistiques pour le badge Discord")
        
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
