#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arsenal Update Publisher - Script pour publier une nouvelle version
Utilise le système ArsenalUpdateNotifier pour diffuser les changements
"""

import asyncio
import discord
from discord.ext import commands
import json
import os
from datetime import datetime

class UpdatePublisher:
    def __init__(self):
        self.version_data = {
            "4.5.0": {
                "title": "Configuration Complète Original",
                "date": "14 Août 2025",
                "description": "**Arsenal V4.5.0 - Configuration Complète Original**\n\nSystème de configuration Arsenal 100% original avec 29 modules configurables !",
                "features": [
                    "🔧 Système de Configuration Arsenal Original (29 modules)",
                    "💰 ArsenalCoin Economy System complet avec boutique",
                    "🏪 Arsenal Shop System avec panel administrateur",
                    "⚙️ Interface utilisateur Arsenal 100% originale",
                    "📊 Sauvegarde JSON automatique des configurations",
                    "🛡️ Gestion d'erreurs avancée pour tous les modules",
                    "📋 Documentation technique complète intégrée",
                    "🎯 Support multi-serveurs avec config individuelle"
                ],
                "improvements": [
                    "Architecture modulaire optimisée pour performances",
                    "Interface utilisateur intuitive avec menus déroulants",
                    "Système de permissions granulaire par module",
                    "Tests automatisés complets intégrés",
                    "Logging professionnel pour debugging"
                ],
                "fixes": [
                    "Correction erreur TWITCH_ACCESS_TOKEN null",
                    "Fix imports manquants configuration complète", 
                    "Résolution problèmes permissions administrateur",
                    "Stabilité améliorée pour grands serveurs"
                ],
                "stats": {
                    "commands": "150+",
                    "modules": "29", 
                    "lines_code": "~20,000+",
                    "servers_supported": "Multi-serveurs"
                }
            },
            "4.4.2": {
                "title": "Hunt Royal Integration",
                "date": "20 Juillet 2025", 
                "description": "**Arsenal V4.4.2 - Hunt Royal Integration**\n\nIntégration complète du système Hunt Royal avec authentification et profils gaming !",
                "features": [
                    "🎮 Hunt Royal Auth System complet",
                    "👤 Hunt Royal Profiles avec liaison comptes",
                    "📊 Hunt Royal Stats en temps réel",
                    "🔐 Système d'authentification Hunt Royal sécurisé",
                    "🏆 Classements Hunt Royal intégrés"
                ],
                "improvements": [
                    "Optimisation base de données Hunt Royal",
                    "Cache système pour meilleures performances gaming",
                    "Interface Hunt Royal améliorée"
                ],
                "fixes": [
                    "Correction problèmes de connectivité Hunt Royal",
                    "Fix synchronisation profils gaming"
                ]
            }
        }

    def get_changelog_embed(self, version: str) -> discord.Embed:
        """Génère l'embed changelog pour une version"""
        if version not in self.version_data:
            return None
            
        data = self.version_data[version]
        
        embed = discord.Embed(
            title=f"🚀 Arsenal V{version} - {data['title']}",
            description=data["description"],
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        # Nouvelles fonctionnalités 
        if "features" in data and data["features"]:
            features_text = "\n".join([f"• {feature}" for feature in data["features"][:6]])
            embed.add_field(
                name="✨ Nouvelles Fonctionnalités",
                value=features_text,
                inline=False
            )
        
        # Améliorations
        if "improvements" in data and data["improvements"]:
            improvements_text = "\n".join([f"• {improvement}" for improvement in data["improvements"][:4]])
            embed.add_field(
                name="🔧 Améliorations",
                value=improvements_text,
                inline=True
            )
        
        # Corrections
        if "fixes" in data and data["fixes"]:
            fixes_text = "\n".join([f"• {fix}" for fix in data["fixes"][:4]])
            embed.add_field(
                name="🐛 Corrections",
                value=fixes_text,
                inline=True
            )
        
        # Statistiques
        if "stats" in data:
            stats = data["stats"]
            stats_text = f"""
• **{stats.get('commands', 'N/A')}** commandes disponibles
• **{stats.get('modules', 'N/A')}** modules configurables  
• **{stats.get('lines_code', 'N/A')}** lignes de code
• **{stats.get('servers_supported', 'N/A')}** pris en charge
            """
            embed.add_field(
                name="📊 Statistiques Version",
                value=stats_text,
                inline=False
            )
        
        embed.add_field(
            name="📋 Plus d'Informations",
            value="Utilisez `/changelog_latest` pour voir le changelog détaillé",
            inline=False
        )
        
        embed.set_footer(
            text=f"Arsenal V{version} • {data.get('date', 'Date inconnue')}"
        )
        
        return embed

    async def publish_update(self, bot, version: str):
        """Publie une mise à jour via le système de notifications"""
        if version not in self.version_data:
            print(f"❌ Version {version} non trouvée dans les données")
            return False
            
        data = self.version_data[version]
        
        # Récupérer le cog ArsenalUpdateNotifier
        update_notifier = bot.get_cog('ArsenalUpdateNotifier')
        if not update_notifier:
            print("❌ ArsenalUpdateNotifier cog non trouvé")
            return False
        
        # Préparer les données changelog
        changelog_data = {
            "description": data["description"],
            "features": data.get("features", []),
            "improvements": data.get("improvements", []),
            "fixes": data.get("fixes", []),
            "date": data.get("date", "Date inconnue")
        }
        
        # Diffuser la mise à jour
        try:
            await update_notifier.broadcast_update(version, changelog_data)
            print(f"✅ Mise à jour V{version} diffusée avec succès !")
            return True
        except Exception as e:
            print(f"❌ Erreur lors de la diffusion: {e}")
            return False

# Script d'exemple pour publier une version
async def main():
    """Script principal pour publier une version"""
    print("🚀 Arsenal Update Publisher")
    print("=" * 40)
    
    # Ici tu peux configurer le bot pour publier une version
    # Note: Ce script nécessite que le bot soit en ligne
    
    publisher = UpdatePublisher()
    
    # Afficher les versions disponibles
    print("📋 Versions disponibles:")
    for version, data in publisher.version_data.items():
        print(f"  • V{version} - {data['title']} ({data['date']})")
    
    print("\n💡 Pour publier une version:")
    print("1. Assure-toi que le bot Arsenal est en ligne")
    print("2. Utilise la commande /dev_broadcast_update <version> sur Discord")
    print("3. Ou modifie ce script pour automatiser la publication")

if __name__ == "__main__":
    asyncio.run(main())
