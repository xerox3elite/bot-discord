#!/usr/bin/env python3
"""
🔧 Script de Correction Ephemeral pour Arsenal V5.0.1
Ajoute ephemeral=True aux commandes admin/mod qui n'en ont pas
"""

import re

def fix_ephemeral_commands():
    """Corrige les commandes sans ephemeral"""
    file_path = "commands/arsenal_command_groups_final.py"
    
    # Lire le fichier
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patterns à corriger (commandes qui doivent être privées)
    patterns_to_fix = [
        # Commandes kick, ban, clear (modération)
        (r'await member\.kick\(reason=reason\)\s+embed = discord\.Embed.*?await interaction\.response\.send_message\(embed=embed\)', 
         lambda m: m.group(0).replace('send_message(embed=embed)', 'send_message(embed=embed, ephemeral=True)')),
        
        # Commandes ban
        (r'await member\.ban\(reason=reason\)\s+embed = discord\.Embed.*?await interaction\.response\.send_message\(embed=embed\)', 
         lambda m: m.group(0).replace('send_message(embed=embed)', 'send_message(embed=embed, ephemeral=True)')),
         
        # Toutes les autres commandes sans ephemeral dans admin/mod groups
        (r'(\@(admin|mod|owner)_group\.command.*?def \w+.*?\n.*?await interaction\.response\.send_message\(embed=embed\))(?!\s*,\s*ephemeral)', 
         lambda m: m.group(0).replace('send_message(embed=embed)', 'send_message(embed=embed, ephemeral=True)')),
    ]
    
    # Appliquer les corrections
    modified = False
    for pattern, replacement in patterns_to_fix:
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            modified = True
    
    # Corrections spécifiques ligne par ligne
    lines = content.split('\n')
    corrections_made = 0
    
    for i, line in enumerate(lines):
        # Chercher les lignes send_message sans ephemeral dans les sections admin/mod
        if ('await interaction.response.send_message(embed=embed)' in line and 
            'ephemeral' not in line and
            i > 0 and any(keyword in '\n'.join(lines[max(0, i-20):i]) for keyword in ['@admin_group', '@mod_group', '@owner_group'])):
            
            lines[i] = line.replace('send_message(embed=embed)', 'send_message(embed=embed, ephemeral=True)')
            corrections_made += 1
            modified = True
    
    if modified:
        # Sauvegarder le fichier corrigé
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        
        print(f"✅ {corrections_made} corrections ephemeral appliquées")
        return True
    else:
        print("ℹ️ Aucune correction nécessaire")
        return False

def main():
    """Point d'entrée principal"""
    print("🔧 Correction Ephemeral Arsenal V5.0.1")
    print("=" * 40)
    
    success = fix_ephemeral_commands()
    
    if success:
        print("🎉 Corrections appliquées avec succès !")
        print("📋 Toutes les commandes admin/mod sont maintenant privées")
        print("🚫 Fini le spam dans les canaux publics !")
    else:
        print("✨ Fichier déjà optimal")

if __name__ == "__main__":
    main()
