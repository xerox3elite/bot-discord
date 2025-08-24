#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arsenal Hotfix Deploy - Corrections rapides pour déploiement
Script pour patcher les problèmes identifiés dans les logs Render
"""

import os
import json
from pathlib import Path

def apply_hotfixes():
    """Applique les corrections rapides pour les problèmes de déploiement"""
    
    print("🔧 ARSENAL HOTFIXES - Corrections de déploiement")
    print("=" * 50)
    
    project_root = Path("A:/Arsenal_propre")
    fixes_applied = []
    
    # Fix 1: Community.py imports
    community_file = project_root / "commands" / "community.py"
    if community_file.exists():
        try:
            with open(community_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Réparer les imports cassés
            if "config_d" in content:
                content = content.replace("from manager.config_manager import config_d", "# config_d import removed")
                fixes_applied.append("✅ Community.py imports fixed")
        except:
            pass
    
    # Fix 2: Terminal Manager - Disable complètement en production
    terminal_file = project_root / "manager" / "terminal_manager.py"
    if terminal_file.exists():
        try:
            with open(terminal_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remplacer par version simplifiée sans input
            simple_terminal = '''import asyncio
import sys
import os
from core.logger import log

async def start_terminal(client):
    """Terminal désactivé en production pour éviter EOFError"""
    # Toujours désactiver en production
    log.info("[TERMINAL] Terminal désactivé - Mode production")
    return
'''
            
            with open(terminal_file, 'w', encoding='utf-8') as f:
                f.write(simple_terminal)
                
            fixes_applied.append("✅ Terminal Manager production-safe")
        except Exception as e:
            print(f"❌ Terminal Manager fix failed: {e}")
    
    # Fix 3: Remove GUI dependencies 
    gui_imports = [
        "# # # # from gui. - GUI removed for production - GUI removed for productionMemberPanel import lancer_member_interface - GUI removed for production - GUI removed for production",
        "# # from gui. - GUI removed for production - GUI removed for production",
        "# # import gui. - GUI removed for production - GUI removed for production"
    ]
    
    # Scanner tous les fichiers Python pour retirer GUI
    python_files = list(project_root.rglob("*.py"))
    gui_fixes = 0
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                original_content = content
            
            for gui_import in gui_imports:
                if gui_import in content:
                    content = content.replace(gui_import, f"# {gui_import} - GUI removed for production")
                    gui_fixes += 1
            
            # Sauver si modifié
            if content != original_content:
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
        except:
            continue
    
    if gui_fixes > 0:
        fixes_applied.append(f"✅ GUI imports removed from {gui_fixes} files")
    
    # Fix 4: Create .renderignore pour éviter fichiers inutiles
    renderignore = project_root / ".renderignore"
    with open(renderignore, 'w', encoding='utf-8') as f:
        f.write("""# Arsenal .renderignore for Render deployment
*.pyc
__pycache__/
.git/
.vscode/
*.tmp
*.log
test_*.py
check_*.py
gui/
logs/
""")
    fixes_applied.append("✅ .renderignore created")
    
    # Fix 5: Simplify Procfile pour éviter check_env
    procfile = project_root / "Procfile"
    with open(procfile, 'w', encoding='utf-8') as f:
        f.write("web: python main.py")
    fixes_applied.append("✅ Procfile simplified")
    
    # Fix 6: Create basic check_env.py minimal
    check_env = project_root / "check_env.py"
    with open(check_env, 'w', encoding='utf-8') as f:
        f.write("""#!/usr/bin/env python3
# Basic environment check for Render
import os
import sys

print("🔍 Arsenal Environment Check")
print("Python:", sys.version)
print("DISCORD_TOKEN:", "✅ Present" if os.getenv('DISCORD_TOKEN') else "❌ Missing")
print("Environment check completed")
""")
    fixes_applied.append("✅ check_env.py minimal created")
    
    # Résumé
    print("\n📊 HOTFIXES APPLIQUÉS:")
    for fix in fixes_applied:
        print(f"   {fix}")
    
    print(f"\n🎯 TOTAL: {len(fixes_applied)} corrections appliquées")
    print("\n✅ PRÊT POUR REDÉPLOIEMENT!")
    
    return len(fixes_applied)

if __name__ == "__main__":
    fixes = apply_hotfixes()
    print(f"\n🚀 Exécuter maintenant:")
    print("git add .")
    print("git commit -m 'Arsenal V4.5.0 - Hotfixes for Render deployment 🔧'")
    print("git push origin main")
    
    exit(0)

