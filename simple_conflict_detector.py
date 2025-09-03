#!/usr/bin/env python3
"""
Simple Conflict Detector - Sans emojis pour PowerShell
"""

import os
import re
from pathlib import Path

def find_commands_in_file(filepath):
    """Trouve toutes les commandes app_commands dans un fichier"""
    commands = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # Chercher les @app_commands.command(name="...")
            pattern = r'@app_commands\.command\(name="([^"]+)"'
            matches = re.findall(pattern, content)
            commands.extend(matches)
    except Exception as e:
        print(f"Erreur lecture {filepath}: {e}")
    return commands

def analyze_conflicts():
    """Analyse les conflits de commandes"""
    commands_map = {}
    
    # Scanner tous les fichiers Python dans commands/
    commands_dir = Path("commands")
    if not commands_dir.exists():
        print("Dossier commands/ non trouve")
        return
        
    for py_file in commands_dir.glob("*.py"):
        if py_file.name.endswith('.disabled'):
            continue
            
        commands = find_commands_in_file(py_file)
        file_stem = py_file.stem
        
        for cmd in commands:
            if cmd not in commands_map:
                commands_map[cmd] = []
            commands_map[cmd].append(file_stem)
    
    # Trouver les conflits
    conflicts = {}
    for cmd, sources in commands_map.items():
        if len(sources) > 1:
            conflicts[cmd] = sources
    
    print("=== ANALYSE CONFLITS ARSENAL ===")
    print(f"Total commandes: {sum(len(cmds) for cmds in commands_map.values())}")
    print(f"Conflits detectes: {len(conflicts)}")
    
    if conflicts:
        print("\nCONFLITS:")
        for cmd, sources in conflicts.items():
            print(f"  /{cmd}: {' vs '.join(sources)}")
    else:
        print("\nAucun conflit detecte!")

if __name__ == "__main__":
    analyze_conflicts()
