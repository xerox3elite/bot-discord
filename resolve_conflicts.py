#!/usr/bin/env python3
"""
🔧 Arsenal Conflict Resolver
Résout automatiquement les conflits de commandes détectés par l'analyzer
"""

import os
import re
import json
from pathlib import Path

def analyze_conflicts():
    """Analyse les conflits détectés et propose des solutions"""
    
    conflicts_data = {
        "/automod": ["arsenal_automod_v5_fixed", "arsenal_command_groups_final"],
        "/config": ["arsenal_config_system", "config_modular"],  
        "/help_search": ["complete_commands_system", "help"],
        "/help": ["help", "help_system"],
        "/commands": ["complete_commands_system", "help_system"],
        "/register": ["hunt_royal_auth", "hunt_royal_system"],
        "/profile": ["hunt_royal_system", "hunt_royal_system"],
        "/timeout": ["sanction", "sanctions_system"],
        "/warn": ["sanction", "sanctions_system"],
        "/casier": ["sanction", "sanctions_system"]
    }
    
    print("🔍 ANALYSE DES CONFLITS")
    print("=" * 50)
    
    for command, sources in conflicts_data.items():
        print(f"\n⚠️ Conflit: {command}")
        print(f"   Sources: {' vs '.join(sources)}")
        
        # Proposer solution
        if "sanction" in sources and "sanctions_system" in sources:
            print("   💡 Solution: Désactiver l'ancien sanction.py")
        elif "arsenal_config_system" in sources:
            print("   💡 Solution: L'ancien arsenal_config_system doit être supprimé")
        elif command in ["/help", "/commands"]:
            print("   💡 Solution: Garder un seul système d'aide principal")
        elif "hunt_royal" in str(sources):
            print("   💡 Solution: Vérifier les doublons Hunt Royal")

def check_inactive_files():
    """Vérifie les fichiers inactifs qui peuvent être nettoyés"""
    
    inactive_files = [
        "arsenal_bugreport_system",
        "arsenal_command_groups_final", 
        "arsenal_config_system",
        "arsenal_profile_updater",
        "help",
        "help_system",
        "help_system_advanced", 
        "help_system_v2_complete",
        "help_ultimate",
        "reglement_system",
        "sanction"
    ]
    
    print("\n🚫 FICHIERS INACTIFS À ANALYSER")
    print("=" * 50)
    
    for file in inactive_files:
        filepath = f"commands/{file}.py"
        if os.path.exists(filepath):
            print(f"✅ Existe: {filepath}")
            # Vérifier s'il est importé dans main.py
            with open("main.py", "r", encoding="utf-8") as f:
                content = f.read()
                if file in content:
                    print(f"   🔗 Référencé dans main.py")
                else:
                    print(f"   ❌ Non référencé - peut être supprimé")
        else:
            print(f"❌ N'existe pas: {filepath}")

if __name__ == "__main__":
    analyze_conflicts()
    check_inactive_files()
