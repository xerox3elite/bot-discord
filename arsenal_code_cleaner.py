"""
ARSENAL CODE CLEANER - NETTOYEUR DE CODE ET RÉSOLVEUR DE CONFLITS
Nettoie le code mort et résout les conflits de commandes
Par xerox3elite - Arsenal V4.5.1 ULTIMATE
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

class ArsenalCodeCleaner:
    """Nettoyeur de code Arsenal ultra-avancé"""
    
    def __init__(self, arsenal_path: str = "a:/Arsenal_propre"):
        self.arsenal_path = Path(arsenal_path)
        self.commands_path = self.arsenal_path / "commands"
        self.backup_path = self.arsenal_path / f"backup_cleanup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Fichiers à supprimer (code mort identifié)
        self.files_to_remove = [
            # Fichiers de sauvegarde et anciens
            "help_OLD_BACKUP.py",
            "help_system_advanced_OLD_BACKUP.py", 
            "help_ultimate_OLD_BACKUP.py",
            
            # Doublons identifiés
            "arsenal_economy_system.py",  # Remplacé par arsenal_economy_unified
            "economy_system.py",  # Conflit avec système unifié
            "level.py",  # Remplacé par level_system
            "sanction.py",  # Remplacé par sanctions_system
            
            # Systèmes non utilisés
            "crypto_commands.py",
            "crypto_economy_advanced.py",
            "games_system.py",  # Remplacé par gaming_api_system
            "tempchannels_advanced.py",
            "tempvoice_commands.py",
            "utilities_system.py",
            
            # Hunt Royal doublons
            "hunt_royal_system.py",  # Conflit majeur avec hunt_royal_auth/profiles
            
            # Anciens systèmes
            "arsenal_config_complete.py",  # Remplacé par config_system_unified
            "config.py",  # Ancien système config
            
            # Modération doublons
            "automod.py",  # Remplacé par arsenal_automod_v5_fixed
            "moderation_advanced.py",
            
            # Autres doublons
            "reglement_simple.py",  # Conflit avec reglement.py
            "music_system_advanced.py",  # Conflit avec music_enhanced_system
        ]
        
        # Conflits à résoudre par renommage
        self.conflicts_to_resolve = {
            # Renommer les commandes en conflit dans certains fichiers
            "community.py": {
                "old_commands": ["bugreport", "top_messages", "version"],
                "new_commands": ["community_bugreport", "community_top_messages", "community_version"]
            }
        }
    
    def create_backup(self):
        """Crée une sauvegarde complète avant nettoyage"""
        print(f"💾 [BACKUP] Création sauvegarde: {self.backup_path}")
        
        try:
            os.makedirs(self.backup_path, exist_ok=True)
            
            # Copier tout le dossier commands
            backup_commands = self.backup_path / "commands"
            shutil.copytree(self.commands_path, backup_commands)
            
            # Copier main.py
            shutil.copy2(self.arsenal_path / "main.py", self.backup_path / "main.py")
            
            print(f"✅ [BACKUP] Sauvegarde créée: {len(os.listdir(backup_commands))} fichiers")
            return True
            
        except Exception as e:
            print(f"❌ [BACKUP] Erreur: {e}")
            return False
    
    def remove_dead_files(self):
        """Supprime les fichiers de code mort"""
        print("🗑️ [CLEANUP] Suppression code mort...")
        
        removed_count = 0
        for filename in self.files_to_remove:
            file_path = self.commands_path / filename
            
            if file_path.exists():
                try:
                    os.remove(file_path)
                    print(f"   ✅ Supprimé: {filename}")
                    removed_count += 1
                except Exception as e:
                    print(f"   ❌ Erreur suppression {filename}: {e}")
            else:
                print(f"   ⚠️ Déjà absent: {filename}")
        
        print(f"✅ [CLEANUP] {removed_count} fichiers supprimés")
    
    def resolve_command_conflicts(self):
        """Résout les conflits de noms de commandes"""
        print("🔧 [CONFLICTS] Résolution conflits de commandes...")
        
        for filename, conflict_data in self.conflicts_to_resolve.items():
            file_path = self.commands_path / filename
            
            if not file_path.exists():
                print(f"   ⚠️ Fichier non trouvé: {filename}")
                continue
            
            try:
                # Lire le fichier
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Remplacer les commandes conflictuelles
                old_commands = conflict_data['old_commands']
                new_commands = conflict_data['new_commands']
                
                modified = False
                for i, old_cmd in enumerate(old_commands):
                    new_cmd = new_commands[i]
                    
                    # Remplacer dans les décorateurs
                    old_pattern = f'@app_commands.command(name="{old_cmd}"'
                    new_pattern = f'@app_commands.command(name="{new_cmd}"'
                    
                    if old_pattern in content:
                        content = content.replace(old_pattern, new_pattern)
                        modified = True
                        print(f"   🔄 {filename}: /{old_cmd} → /{new_cmd}")
                
                # Sauvegarder si modifié
                if modified:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"   ✅ {filename} mis à jour")
                
            except Exception as e:
                print(f"   ❌ Erreur {filename}: {e}")
    
    def update_main_py(self):
        """Met à jour main.py pour supprimer les imports de fichiers supprimés"""
        print("🔧 [MAIN] Mise à jour main.py...")
        
        main_file = self.arsenal_path / "main.py"
        
        try:
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            modified = False
            
            # Supprimer les imports des fichiers supprimés
            for filename in self.files_to_remove:
                module_name = filename.replace('.py', '')
                
                # Patterns d'import à supprimer
                patterns = [
                    f"from commands.{module_name} import",
                    f"await self.add_cog({module_name}",
                    f"# {module_name}",
                ]
                
                for pattern in patterns:
                    lines = content.split('\n')
                    new_lines = []
                    
                    for line in lines:
                        if pattern.lower() not in line.lower():
                            new_lines.append(line)
                        else:
                            new_lines.append(f"# SUPPRIMÉ: {line.strip()}")
                            modified = True
                            print(f"   🗑️ Commenté import: {module_name}")
                    
                    content = '\n'.join(new_lines)
            
            # Sauvegarder si modifié
            if modified:
                with open(main_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("   ✅ main.py mis à jour")
            else:
                print("   ℹ️ main.py déjà à jour")
                
        except Exception as e:
            print(f"   ❌ Erreur main.py: {e}")
    
    def generate_cleanup_report(self):
        """Génère un rapport de nettoyage"""
        print("📊 [REPORT] Génération rapport de nettoyage...")
        
        remaining_files = [f.name for f in self.commands_path.glob("*.py") if f.name != "__init__.py"]
        
        report = {
            "cleanup_date": datetime.now().isoformat(),
            "backup_location": str(self.backup_path),
            "files_removed": self.files_to_remove,
            "files_remaining": remaining_files,
            "conflicts_resolved": list(self.conflicts_to_resolve.keys()),
            "summary": {
                "files_before": len(remaining_files) + len(self.files_to_remove),
                "files_removed": len(self.files_to_remove),
                "files_after": len(remaining_files),
                "space_saved_estimate": f"{len(self.files_to_remove) * 50} KB"
            }
        }
        
        # Sauvegarder rapport
        report_file = self.arsenal_path / "cleanup_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"💾 [REPORT] Rapport sauvegardé: {report_file}")
        
        return report
    
    def print_summary(self, report):
        """Affiche un résumé du nettoyage"""
        print("\n" + "="*70)
        print("🧹 ARSENAL CODE CLEANUP SUMMARY")
        print("="*70)
        
        summary = report['summary']
        
        print(f"\n📊 STATISTIQUES:")
        print(f"   📁 Fichiers avant: {summary['files_before']}")
        print(f"   🗑️ Fichiers supprimés: {summary['files_removed']}")
        print(f"   📁 Fichiers restants: {summary['files_after']}")
        print(f"   💾 Espace libéré (est.): {summary['space_saved_estimate']}")
        
        print(f"\n🗑️ FICHIERS SUPPRIMÉS ({len(report['files_removed'])}):")
        for filename in report['files_removed']:
            print(f"   ❌ {filename}")
        
        print(f"\n🔧 CONFLITS RÉSOLUS ({len(report['conflicts_resolved'])}):")
        for filename in report['conflicts_resolved']:
            print(f"   ✅ {filename}")
        
        print(f"\n💾 SAUVEGARDE:")
        print(f"   📂 {report['backup_location']}")
        
        print(f"\n✅ NETTOYAGE TERMINÉ!")
        print("="*70)
    
    def run_full_cleanup(self):
        """Lance le nettoyage complet"""
        print("🚀 [START] Arsenal Code Cleanup")
        print("-" * 50)
        
        # Étape 1: Sauvegarde
        if not self.create_backup():
            print("❌ [ABORT] Échec sauvegarde - nettoyage annulé")
            return False
        
        # Étape 2: Suppression code mort
        self.remove_dead_files()
        
        # Étape 3: Résolution conflits
        self.resolve_command_conflicts()
        
        # Étape 4: Mise à jour main.py
        self.update_main_py()
        
        # Étape 5: Rapport
        report = self.generate_cleanup_report()
        self.print_summary(report)
        
        return True

if __name__ == "__main__":
    cleaner = ArsenalCodeCleaner()
    
    # Demander confirmation
    print("🧹 ARSENAL CODE CLEANUP TOOL")
    print("="*50)
    print("⚠️  ATTENTION: Cet outil va:")
    print("   • Supprimer des fichiers de code mort")
    print("   • Résoudre les conflits de commandes") 
    print("   • Modifier main.py")
    print("   • Créer une sauvegarde complète")
    print("")
    
    response = input("Continuer le nettoyage ? [y/N]: ")
    
    if response.lower() in ['y', 'yes', 'o', 'oui']:
        success = cleaner.run_full_cleanup()
        if success:
            print("\n🎉 Nettoyage terminé avec succès !")
            print("Vous pouvez maintenant redémarrer le bot.")
        else:
            print("\n❌ Échec du nettoyage.")
    else:
        print("\n⚠️ Nettoyage annulé par l'utilisateur.")
