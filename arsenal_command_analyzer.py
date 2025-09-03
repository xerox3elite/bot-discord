"""
ARSENAL COMMAND ANALYZER - ANALYSEUR DE COMMANDES COMPLET
Analyse toutes les commandes théoriques vs réellement chargées
Par xerox3elite - Arsenal V4.5.1 ULTIMATE
"""

import os
import re
import ast
import json
from typing import Dict, List, Set
from pathlib import Path

class ArsenalCommandAnalyzer:
    """Analyseur complet des commandes Arsenal"""
    
    def __init__(self, arsenal_path: str = "a:/Arsenal_propre"):
        self.arsenal_path = Path(arsenal_path)
        self.commands_path = self.arsenal_path / "commands"
        self.main_file = self.arsenal_path / "main.py"
        
        # Stockage des résultats
        self.theoretical_commands = {}
        self.loaded_cogs = set()
        self.command_conflicts = []
        self.inactive_commands = []
        self.active_commands = []
        
    def analyze_theoretical_commands(self):
        """Analyse toutes les commandes théoriques dans les fichiers"""
        print("🔍 [ANALYSIS] Analyse des commandes théoriques...")
        
        if not self.commands_path.exists():
            print(f"❌ [ERROR] Dossier commands non trouvé: {self.commands_path}")
            return
        
        # Parcourir tous les fichiers Python
        for file_path in self.commands_path.glob("*.py"):
            if file_path.name.startswith("__"):
                continue
                
            try:
                self._analyze_file(file_path)
            except Exception as e:
                print(f"❌ [ERROR] Erreur analyse {file_path.name}: {e}")
        
        print(f"✅ [SUCCESS] {len(self.theoretical_commands)} commandes théoriques trouvées")
    
    def _analyze_file(self, file_path: Path):
        """Analyse un fichier Python pour les commandes"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_name = file_path.stem
            file_commands = []
            
            # Rechercher les décorateurs de commandes
            app_command_pattern = r'@app_commands\.command\(name="([^"]+)"[^)]*description="([^"]*)"[^)]*\)'
            command_pattern = r'@commands\.command\(name="([^"]+)"[^)]*\)'
            group_pattern = r'(\w+)_group = app_commands\.Group\(name="([^"]+)"'
            
            # App commands
            for match in re.finditer(app_command_pattern, content, re.MULTILINE):
                command_name = match.group(1)
                description = match.group(2)
                file_commands.append({
                    'name': command_name,
                    'type': 'app_command',
                    'description': description,
                    'file': file_name
                })
            
            # Commands traditionnels
            for match in re.finditer(command_pattern, content, re.MULTILINE):
                command_name = match.group(1)
                file_commands.append({
                    'name': command_name,
                    'type': 'traditional_command',
                    'description': 'N/A',
                    'file': file_name
                })
            
            # Groupes de commandes
            groups_found = []
            for match in re.finditer(group_pattern, content, re.MULTILINE):
                group_var = match.group(1)
                group_name = match.group(2)
                groups_found.append((group_var, group_name))
            
            # Sous-commandes des groupes
            for group_var, group_name in groups_found:
                subcommand_pattern = f'@{group_var}\.command\(name="([^"]+)"[^)]*description="([^"]*)"[^)]*\)'
                for match in re.finditer(subcommand_pattern, content, re.MULTILINE):
                    subcommand_name = match.group(1)
                    description = match.group(2)
                    file_commands.append({
                        'name': f"{group_name} {subcommand_name}",
                        'type': 'group_command',
                        'description': description,
                        'file': file_name,
                        'group': group_name
                    })
            
            if file_commands:
                self.theoretical_commands[file_name] = file_commands
                print(f"📁 {file_name}: {len(file_commands)} commandes")
                
        except Exception as e:
            print(f"❌ [ERROR] Erreur lecture {file_path}: {e}")
    
    def analyze_loaded_cogs(self):
        """Analyse les cogs chargés dans main.py"""
        print("🔍 [ANALYSIS] Analyse des cogs chargés...")
        
        if not self.main_file.exists():
            print(f"❌ [ERROR] main.py non trouvé: {self.main_file}")
            return
        
        try:
            with open(self.main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Rechercher les add_cog
            add_cog_pattern = r'await self\.add_cog\((\w+)\(self\)\)'
            import_pattern = r'from commands\.(\w+) import (\w+)'
            
            imports_mapping = {}
            
            # Mapper les imports
            for match in re.finditer(import_pattern, content, re.MULTILINE):
                file_name = match.group(1)
                class_name = match.group(2)
                imports_mapping[class_name] = file_name
            
            # Trouver les cogs chargés
            for match in re.finditer(add_cog_pattern, content, re.MULTILINE):
                class_name = match.group(1)
                file_name = imports_mapping.get(class_name, 'unknown')
                self.loaded_cogs.add(file_name)
            
            # Vérifier les cogs commentés ou dans des try/except
            commented_pattern = r'#.*await self\.add_cog\((\w+)\(self\)\)'
            for match in re.finditer(commented_pattern, content, re.MULTILINE):
                class_name = match.group(1)
                file_name = imports_mapping.get(class_name, 'unknown')
                if file_name in self.loaded_cogs:
                    self.loaded_cogs.remove(file_name)
                print(f"⚠️ [DISABLED] Cog commenté: {file_name} ({class_name})")
            
            print(f"✅ [SUCCESS] {len(self.loaded_cogs)} cogs chargés identifiés")
            
        except Exception as e:
            print(f"❌ [ERROR] Erreur analyse main.py: {e}")
    
    def cross_reference_commands(self):
        """Croise les données pour identifier les commandes actives vs inactives"""
        print("🔍 [ANALYSIS] Croisement des données...")
        
        for file_name, commands in self.theoretical_commands.items():
            if file_name in self.loaded_cogs:
                for cmd in commands:
                    cmd['status'] = 'active'
                    self.active_commands.extend(commands)
            else:
                for cmd in commands:
                    cmd['status'] = 'inactive'
                    self.inactive_commands.extend(commands)
        
        # Détecter les conflits de noms
        command_names = {}
        for file_name, commands in self.theoretical_commands.items():
            for cmd in commands:
                cmd_name = cmd['name']
                if cmd_name in command_names:
                    self.command_conflicts.append({
                        'command': cmd_name,
                        'files': [command_names[cmd_name], file_name]
                    })
                else:
                    command_names[cmd_name] = file_name
        
        print(f"✅ [SUCCESS] {len(self.active_commands)} commandes actives")
        print(f"⚠️ [WARNING] {len(self.inactive_commands)} commandes inactives")
        print(f"🔥 [CONFLICT] {len(self.command_conflicts)} conflits détectés")
    
    def generate_report(self) -> Dict:
        """Génère un rapport complet"""
        print("📊 [REPORT] Génération du rapport...")
        
        report = {
            'timestamp': '2025-09-03 16:35:00',
            'analysis_summary': {
                'total_files': len(self.theoretical_commands),
                'total_commands': sum(len(cmds) for cmds in self.theoretical_commands.values()),
                'active_commands': len(self.active_commands),
                'inactive_commands': len(self.inactive_commands),
                'loaded_cogs': len(self.loaded_cogs),
                'command_conflicts': len(self.command_conflicts)
            },
            'loaded_cogs': list(self.loaded_cogs),
            'theoretical_commands': self.theoretical_commands,
            'active_commands': self.active_commands,
            'inactive_commands': self.inactive_commands,
            'command_conflicts': self.command_conflicts,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Génère des recommandations basées sur l'analyse"""
        recommendations = []
        
        if self.command_conflicts:
            recommendations.append(f"⚠️ Résoudre {len(self.command_conflicts)} conflits de noms de commandes")
        
        if self.inactive_commands:
            recommendations.append(f"🔧 Activer {len(self.inactive_commands)} commandes inactives ou nettoyer le code")
        
        # Fichiers avec beaucoup de commandes non chargées
        inactive_files = {}
        for cmd in self.inactive_commands:
            file_name = cmd['file']
            inactive_files[file_name] = inactive_files.get(file_name, 0) + 1
        
        for file_name, count in inactive_files.items():
            if count > 5:
                recommendations.append(f"🗂️ Fichier {file_name}: {count} commandes non chargées")
        
        return recommendations
    
    def print_detailed_report(self):
        """Affiche un rapport détaillé dans la console"""
        print("\n" + "="*80)
        print("📊 ARSENAL COMMAND ANALYSIS REPORT")
        print("="*80)
        
        report = self.generate_report()
        summary = report['analysis_summary']
        
        print(f"\n📋 RÉSUMÉ GÉNÉRAL:")
        print(f"   📁 Fichiers analysés: {summary['total_files']}")
        print(f"   🎯 Commandes totales: {summary['total_commands']}")
        print(f"   ✅ Commandes actives: {summary['active_commands']}")
        print(f"   ❌ Commandes inactives: {summary['inactive_commands']}")
        print(f"   🔧 Cogs chargés: {summary['loaded_cogs']}")
        print(f"   ⚠️ Conflits détectés: {summary['command_conflicts']}")
        
        print(f"\n🔧 COGS CHARGÉS ({len(self.loaded_cogs)}):")
        for cog in sorted(self.loaded_cogs):
            if cog in self.theoretical_commands:
                cmd_count = len(self.theoretical_commands[cog])
                print(f"   ✅ {cog}: {cmd_count} commandes")
            else:
                print(f"   ⚠️ {cog}: Aucune commande détectée")
        
        if self.command_conflicts:
            print(f"\n🔥 CONFLITS DE COMMANDES ({len(self.command_conflicts)}):")
            for conflict in self.command_conflicts:
                print(f"   ⚠️ /{conflict['command']}: {', '.join(conflict['files'])}")
        
        print(f"\n❌ FICHIERS NON CHARGÉS:")
        inactive_files = set(self.theoretical_commands.keys()) - self.loaded_cogs
        for file_name in sorted(inactive_files):
            cmd_count = len(self.theoretical_commands[file_name])
            print(f"   🚫 {file_name}: {cmd_count} commandes inactives")
        
        print(f"\n💡 RECOMMANDATIONS:")
        for rec in report['recommendations']:
            print(f"   {rec}")
        
        print("\n" + "="*80)
    
    def save_report(self, filename: str = "arsenal_command_analysis.json"):
        """Sauvegarde le rapport en JSON"""
        report = self.generate_report()
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"💾 [SAVED] Rapport sauvegardé: {filename}")
        except Exception as e:
            print(f"❌ [ERROR] Erreur sauvegarde: {e}")
    
    def run_complete_analysis(self):
        """Lance l'analyse complète"""
        print("🚀 [START] Arsenal Command Analysis")
        print("-" * 50)
        
        self.analyze_theoretical_commands()
        self.analyze_loaded_cogs()
        self.cross_reference_commands()
        
        self.print_detailed_report()
        self.save_report()
        
        print(f"\n🎯 [COMPLETE] Analyse terminée!")

if __name__ == "__main__":
    analyzer = ArsenalCommandAnalyzer()
    analyzer.run_complete_analysis()
