# 🔥 Arsenal V4 - Compteur Ultra-Complet de Commandes
import os
import re
import ast
import inspect
from typing import List, Dict

class ArsenalCommandCounter:
    """Compteur ultra-précis de toutes les commandes Arsenal"""
    
    def __init__(self):
        self.commands_found = {}
        self.total_commands = 0
    
    def count_all_commands(self):
        """Compte TOUTES les commandes dans Arsenal"""
        print("🔥 ARSENAL ULTRA-COMMAND COUNTER V1.0")
        print("=" * 60)
        print("🎯 Mission: Compter CHAQUE commande Arsenal")
        print("=" * 60)
        
        commands_dir = "commands"
        
        for filename in os.listdir(commands_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                filepath = os.path.join(commands_dir, filename)
                commands_in_file = self._analyze_file(filepath)
                
                if commands_in_file:
                    self.commands_found[filename] = commands_in_file
                    print(f"📁 {filename:<35} - {len(commands_in_file):>3} commandes")
                    for cmd in commands_in_file[:5]:  # Afficher les 5 premières
                        print(f"   ├─ {cmd}")
                    if len(commands_in_file) > 5:
                        print(f"   └─ ... et {len(commands_in_file) - 5} autres")
                else:
                    print(f"🟡 {filename:<35} - {0:>3} commandes")
        
        self.total_commands = sum(len(cmds) for cmds in self.commands_found.values())
        
        print("\n" + "=" * 60)
        print(f"📊 RÉSULTATS FINAUX:")
        print(f"📁 Fichiers analysés: {len([f for f in os.listdir(commands_dir) if f.endswith('.py')])}")
        print(f"📁 Fichiers avec commandes: {len(self.commands_found)}")
        print(f"⚡ TOTAL COMMANDES ARSENAL: {self.total_commands}")
        print("=" * 60)
        
        # Top 10 des fichiers avec le plus de commandes
        top_files = sorted(self.commands_found.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        print("\n🏆 TOP 10 FICHIERS AVEC LE PLUS DE COMMANDES:")
        for i, (filename, cmds) in enumerate(top_files, 1):
            print(f"{i:>2}. {filename:<30} - {len(cmds):>3} commandes")
        
        return self.total_commands
    
    def _analyze_file(self, filepath: str) -> List[str]:
        """Analyse un fichier pour trouver toutes les commandes"""
        commands = []
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Méthode 1: Recherche par regex des décorateurs @app_commands.command
            app_command_pattern = r'@app_commands\.command\s*\(\s*name\s*=\s*["\']([^"\']+)["\']'
            for match in re.finditer(app_command_pattern, content):
                commands.append(f"/{match.group(1)}")
            
            # Méthode 2: Recherche par regex des décorateurs @commands.command
            command_pattern = r'@commands\.command\s*\(\s*name\s*=\s*["\']([^"\']+)["\']'
            for match in re.finditer(command_pattern, content):
                commands.append(f"!{match.group(1)}")
            
            # Méthode 3: Recherche des @app_commands.command sans name= (utilise le nom de fonction)
            simple_app_pattern = r'@app_commands\.command.*?\n\s*async def\s+(\w+)\s*\('
            for match in re.finditer(simple_app_pattern, content, re.MULTILINE | re.DOTALL):
                cmd_name = match.group(1)
                if cmd_name != 'command':  # Éviter les faux positifs
                    commands.append(f"/{cmd_name}")
            
            # Méthode 4: Recherche des @commands.command sans name=
            simple_command_pattern = r'@commands\.command.*?\n\s*async def\s+(\w+)\s*\('
            for match in re.finditer(simple_command_pattern, content, re.MULTILINE | re.DOTALL):
                cmd_name = match.group(1)
                if cmd_name != 'command':
                    commands.append(f"!{cmd_name}")
            
            # Méthode 5: Recherche des commandes dans les groupes de commandes
            group_pattern = r'@(\w+)\.command\s*\(\s*name\s*=\s*["\']([^"\']+)["\']'
            for match in re.finditer(group_pattern, content):
                group_name = match.group(1)
                cmd_name = match.group(2)
                commands.append(f"/{group_name} {cmd_name}")
            
            # Méthode 6: Recherche des sous-commandes
            subcommand_pattern = r'@app_commands\.describe.*?\n\s*async def\s+(\w+)\s*\('
            for match in re.finditer(subcommand_pattern, content, re.MULTILINE | re.DOTALL):
                cmd_name = match.group(1)
                if cmd_name not in [cmd.split('/')[-1].split()[0] for cmd in commands]:
                    commands.append(f"/{cmd_name} (sub)")
            
            # Méthode 7: Analyse AST pour plus de précision
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Vérifier les décorateurs
                        for decorator in node.decorator_list:
                            if isinstance(decorator, ast.Attribute):
                                if (isinstance(decorator.value, ast.Name) and 
                                    decorator.value.id in ['app_commands', 'commands'] and
                                    decorator.attr == 'command'):
                                    commands.append(f"/{node.name} (ast)")
                            elif isinstance(decorator, ast.Call):
                                if (isinstance(decorator.func, ast.Attribute) and
                                    isinstance(decorator.func.value, ast.Name) and
                                    decorator.func.value.id in ['app_commands', 'commands'] and
                                    decorator.func.attr == 'command'):
                                    # Chercher le paramètre name
                                    cmd_name = node.name
                                    for keyword in decorator.keywords:
                                        if keyword.arg == 'name' and isinstance(keyword.value, ast.Str):
                                            cmd_name = keyword.value.s
                                    commands.append(f"/{cmd_name} (ast)")
            except:
                pass  # Si l'AST échoue, on continue avec les regex
            
            # Supprimer les doublons et nettoyer
            commands = list(set(commands))
            commands.sort()
            
        except Exception as e:
            print(f"❌ Erreur analyse {filepath}: {e}")
        
        return commands

if __name__ == "__main__":
    counter = ArsenalCommandCounter()
    total = counter.count_all_commands()
    print(f"\n🎉 ARSENAL POSSÈDE {total} COMMANDES AU TOTAL ! 🎉")
