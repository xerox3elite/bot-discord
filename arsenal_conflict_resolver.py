#!/usr/bin/env python3
"""
🔧 Arsenal Conflict Resolver V1.0
=================================

Résout automatiquement les conflits de commandes et nettoie les fichiers inactifs.
Basé sur l'analyse de arsenal_command_analyzer.py

Fonctionnalités:
- Résolution automatique des conflits de noms
- Suppression des doublons dans les fichiers
- Nettoyage des imports inutilisés
- Renommage intelligent des commandes conflictuelles
- Sauvegarde automatique avant modifications
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
import re

class ArsenalConflictResolver:
    def __init__(self):
        self.backup_dir = Path("backup_conflict_resolver")
        self.log_file = "arsenal_conflict_resolver.log"
        self.conflicts_resolved = 0
        self.files_cleaned = 0
        
    def log(self, message):
        """Logger avec timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def backup_file(self, file_path):
        """Sauvegarde un fichier avant modification"""
        file_path = Path(file_path)
        if not file_path.exists():
            return False
            
        # Créer le dossier de backup
        self.backup_dir.mkdir(exist_ok=True)
        backup_path = self.backup_dir / f"{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_path.suffix}"
        
        try:
            shutil.copy2(file_path, backup_path)
            self.log(f"✅ Sauvegarde: {file_path} → {backup_path}")
            return True
        except Exception as e:
            self.log(f"❌ Erreur sauvegarde {file_path}: {e}")
            return False
    
    def resolve_hunt_royal_profiles_duplicates(self):
        """Résout les doublons dans hunt_royal_profiles.py"""
        file_path = Path("commands/hunt_royal_profiles.py")
        if not file_path.exists():
            return False
            
        self.log("🔧 Résolution des doublons Hunt Royal Profiles...")
        self.backup_file(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Supprimer les doublons de commandes (garder seulement la première occurrence)
        patterns_to_fix = [
            (r'@app_commands\.command\(name="link-hunt".*?\n.*?async def .*?\(.*?\):.*?\n(.*?\n)*?.*?await.*?\.response\.send_message.*?\n', 1),
            (r'@app_commands\.command\(name="unlink-hunt".*?\n.*?async def .*?\(.*?\):.*?\n(.*?\n)*?.*?await.*?\.response\.send_message.*?\n', 1),
            (r'@app_commands\.command\(name="profile-hunt".*?\n.*?async def .*?\(.*?\):.*?\n(.*?\n)*?.*?await.*?\.response\.send_message.*?\n', 1),
        ]
        
        original_content = content
        for pattern, keep_first in patterns_to_fix:
            matches = list(re.finditer(pattern, content, re.MULTILINE | re.DOTALL))
            if len(matches) > keep_first:
                self.log(f"   - Trouvé {len(matches)} occurrences, suppression des doublons...")
                # Supprimer toutes les occurrences sauf la première
                for match in reversed(matches[keep_first:]):
                    content = content[:match.start()] + content[match.end():]
                    self.conflicts_resolved += 1
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.log(f"✅ Doublons supprimés dans {file_path}")
            return True
        else:
            self.log(f"ℹ️ Aucun doublon trouvé dans {file_path}")
            return False
    
    def resolve_hunt_royal_system_duplicates(self):
        """Résout les doublons dans hunt_royal_system.py"""
        file_path = Path("commands/hunt_royal_system.py")
        if not file_path.exists():
            return False
            
        self.log("🔧 Résolution des doublons Hunt Royal System...")
        self.backup_file(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Chercher les sections dupliquées
        lines = content.split('\n')
        unique_lines = []
        seen_commands = set()
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Détecter les commandes dupliquées
            if '@app_commands.command' in line and 'name=' in line:
                # Extraire le nom de la commande
                match = re.search(r'name="([^"]+)"', line)
                if match:
                    command_name = match.group(1)
                    if command_name in seen_commands:
                        self.log(f"   - Suppression du doublon: /{command_name}")
                        # Ignorer cette commande et sa fonction
                        while i < len(lines) and not (lines[i].strip().startswith('@') or lines[i].strip().startswith('class ')):
                            i += 1
                        continue
                    else:
                        seen_commands.add(command_name)
            
            unique_lines.append(line)
            i += 1
        
        cleaned_content = '\n'.join(unique_lines)
        if cleaned_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            self.log(f"✅ Doublons supprimés dans {file_path}")
            self.conflicts_resolved += len(seen_commands) - len(set(seen_commands))
            return True
        else:
            self.log(f"ℹ️ Aucun doublon trouvé dans {file_path}")
            return False
    
    def rename_conflicting_commands(self):
        """Renomme les commandes en conflit pour éviter les doublons"""
        self.log("🔧 Renommage des commandes en conflit...")
        
        # Conflits principaux à résoudre
        renames = [
            # Ancien sanction -> sanction-legacy  
            ("commands/sanction.py", [
                (r'@app_commands\.command\(name="warn"', '@app_commands.command(name="warn-legacy"'),
                (r'@app_commands\.command\(name="timeout"', '@app_commands.command(name="timeout-legacy"'),
                (r'@app_commands\.command\(name="casier"', '@app_commands.command(name="casier-legacy"'),
            ]),
            
            # Help systems -> help-alt
            ("commands/help.py", [
                (r'@app_commands\.command\(name="help"', '@app_commands.command(name="help-alt"'),
                (r'@app_commands\.command\(name="commands"', '@app_commands.command(name="commands-alt"'),
            ]),
            
            ("commands/help_system.py", [
                (r'@app_commands\.command\(name="help"', '@app_commands.command(name="help-system"'),
                (r'@app_commands\.command\(name="commands"', '@app_commands.command(name="commands-system"'),
            ]),
        ]
        
        for file_path, replacements in renames:
            path = Path(file_path)
            if path.exists():
                self.backup_file(path)
                
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                for old_pattern, new_replacement in replacements:
                    content = re.sub(old_pattern, new_replacement, content)
                    if old_pattern != new_replacement:
                        self.conflicts_resolved += len(re.findall(old_pattern, original_content))
                
                if content != original_content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.log(f"✅ Commandes renommées dans {path}")
    
    def run_full_resolution(self):
        """Lance la résolution complète des conflits"""
        self.log("🚀 DÉMARRAGE - Arsenal Conflict Resolver")
        self.log("=" * 50)
        
        # 1. Résoudre les doublons Hunt Royal
        self.resolve_hunt_royal_profiles_duplicates()
        self.resolve_hunt_royal_system_duplicates()
        
        # 2. Renommer les commandes conflictuelles
        self.rename_conflicting_commands()
        
        # 3. Résumé
        self.log("=" * 50)
        self.log(f"📊 RÉSUMÉ:")
        self.log(f"   ✅ Conflits résolus: {self.conflicts_resolved}")
        self.log(f"   🧹 Fichiers nettoyés: {self.files_cleaned}")
        self.log(f"   💾 Sauvegardes dans: {self.backup_dir}")
        self.log("🎯 TERMINÉ - Résolution des conflits")

if __name__ == "__main__":
    resolver = ArsenalConflictResolver()
    resolver.run_full_resolution()
