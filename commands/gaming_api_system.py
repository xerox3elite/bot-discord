# 🚀 Arsenal V4 - Gaming & API Integration System
"""
Système d'intégration Gaming pour Arsenal V4:
- Informations Fortnite (stats, boutique)
- Rocket League stats
- Call of Duty intégration
- Twitch stream status
- Hunt Royal chasseurs database
- Minecraft mods management
- Gaming leaderboards
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import aiohttp
import asyncio
from datetime import datetime
import os
from typing import Optional, Dict, List
import random

class GamingAPISystem(commands.Cog):
    """Système Gaming & API pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.hunters_data_file = "data/hunters_data.json"
        self.mods_data_file = "data/minecraft_mods.json"
        self.gaming_stats_file = "data/gaming_stats.json"
        self.init_gaming_data()

    def init_gaming_data(self):
        """Initialise les données gaming"""
        os.makedirs("data", exist_ok=True)
        
        # Hunters data par défaut
        if not os.path.exists(self.hunters_data_file):
            default_hunters = {
                "hunters": {
                    "Night Raider": {
                        "hp": 150,
                        "dmg": "Élevé",
                        "style": "Furtif",
                        "distance": "Moyenne",
                        "niveau": 45,
                        "awa": "oui",
                        "description": "Chasseur spécialisé dans les attaques nocturnes"
                    },
                    "Storm Archer": {
                        "hp": 120,
                        "dmg": "Moyen",
                        "style": "Distance",
                        "distance": "Longue",
                        "niveau": 38,
                        "awa": "oui",
                        "description": "Archer électrisant avec attaques à distance"
                    },
                    "Blood Warrior": {
                        "hp": 200,
                        "dmg": "Très élevé",
                        "style": "Combat rapproché",
                        "distance": "Courte",
                        "niveau": 52,
                        "awa": "oui",
                        "description": "Guerrier brutal spécialisé dans le corps à corps"
                    }
                }
            }
            with open(self.hunters_data_file, 'w', encoding='utf-8') as f:
                json.dump(default_hunters, f, indent=2, ensure_ascii=False)
        
        # Mods Minecraft par défaut
        if not os.path.exists(self.mods_data_file):
            default_mods = {
                "hardcore": [
                    {
                        "name": "Tough As Nails",
                        "versions": ["1.20.1", "1.19.4", "1.18.2"],
                        "downloads": "2M+",
                        "rating": "4.7/5",
                        "description": "Système de température et soif réaliste"
                    },
                    {
                        "name": "Blood Magic",
                        "versions": ["1.18.2", "1.16.5"],
                        "downloads": "2.5M+",
                        "rating": "4.6/5",
                        "description": "Magie sanguinaire avec rituels complexes"
                    }
                ],
                "tech": [
                    {
                        "name": "Applied Energistics 2",
                        "versions": ["1.20.1", "1.19.4", "1.18.2"],
                        "downloads": "5M+",
                        "rating": "4.9/5",
                        "description": "Système de stockage et automatisation avancé"
                    },
                    {
                        "name": "Create",
                        "versions": ["1.20.1", "1.18.2"],
                        "downloads": "6M+",
                        "rating": "5.0/5",
                        "description": "Mécanique et ingénierie créative"
                    }
                ]
            }
            with open(self.mods_data_file, 'w', encoding='utf-8') as f:
                json.dump(default_mods, f, indent=2, ensure_ascii=False)

    @app_commands.command(name="gaming", description="🎮 Menu principal Gaming Arsenal")
    async def gaming_menu(self, interaction: discord.Interaction):
        """Menu principal du système gaming"""
        embed = discord.Embed(
            title="🎮 Arsenal Gaming Hub",
            description="Toutes vos intégrations gaming en un seul endroit !",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🏹 Hunt Royal",
            value=(
                "`/hunter_info` - Info chasseur\n"
                "`/hunters_list` - Liste chasseurs\n"
                "`/hunter_build` - Build recommandé"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🟦 Minecraft",
            value=(
                "`/minecraft_mods` - Explorer mods\n"
                "`/mod_search` - Rechercher mod\n"
                "`/modpack_create` - Créer modpack"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🚀 Stats Gaming",
            value=(
                "`/fortnite_stats` - Stats Fortnite\n"
                "`/rl_stats` - Rocket League\n"
                "`/gaming_profile` - Profil gaming"
            ),
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="hunter_info", description="🏹 Informations détaillées sur un chasseur")
    @app_commands.describe(name="Nom du chasseur")
    async def hunter_info(self, interaction: discord.Interaction, name: str):
        """Affiche les informations d'un chasseur Hunt Royal"""
        
        try:
            with open(self.hunters_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            hunters = data.get("hunters", {})
            
            # Recherche case-insensitive
            hunter_info = None
            actual_name = None
            for hunter_name, info in hunters.items():
                if hunter_name.lower() == name.lower():
                    hunter_info = info
                    actual_name = hunter_name
                    break
            
            if not hunter_info:
                # Suggestions similaires
                suggestions = [h for h in hunters.keys() if name.lower() in h.lower()]
                if suggestions:
                    suggest_text = "\n".join([f"• {s}" for s in suggestions[:5]])
                    await interaction.response.send_message(
                        f"❌ Chasseur `{name}` introuvable.\n\n**Suggestions :**\n{suggest_text}",
                        ephemeral=True
                    )
                else:
                    await interaction.response.send_message(f"❌ Chasseur `{name}` introuvable.", ephemeral=True)
                return
            
            # Création embed
            embed = discord.Embed(
                title=f"🏹 {actual_name}",
                description=hunter_info.get("description", "Chasseur Hunt Royal"),
                color=discord.Color.gold()
            )
            
            embed.add_field(
                name="💖 Points de Vie",
                value=f"**{hunter_info['hp']} HP**",
                inline=True
            )
            
            embed.add_field(
                name="⚔️ Dégâts",
                value=f"**{hunter_info['dmg']}**",
                inline=True
            )
            
            embed.add_field(
                name="🎯 Style",
                value=f"**{hunter_info['style']}**",
                inline=True
            )
            
            embed.add_field(
                name="📏 Portée",
                value=f"**{hunter_info['distance']}**",
                inline=True
            )
            
            embed.add_field(
                name="🌟 Niveau",
                value=f"**{hunter_info['niveau']}**",
                inline=True
            )
            
            awakening = "✅ Disponible" if hunter_info.get('awa') == 'oui' else "❌ Indisponible"
            embed.add_field(
                name="🔥 Awakening",
                value=awakening,
                inline=True
            )
            
            embed.set_footer(text="Arsenal V4 • Hunt Royal Database")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur lors de la récupération des données: {e}", ephemeral=True)

    @app_commands.command(name="hunters_list", description="🏹 Liste de tous les chasseurs disponibles")
    async def hunters_list(self, interaction: discord.Interaction):
        """Affiche la liste complète des chasseurs avec menu dropdown"""
        
        try:
            with open(self.hunters_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            hunters = data.get("hunters", {})
            
            if not hunters:
                await interaction.response.send_message("❌ Aucun chasseur dans la base de données.", ephemeral=True)
                return
            
            view = HuntersDropdownView(hunters)
            
            embed = discord.Embed(
                title="🏹 Base de Données Hunt Royal",
                description=f"**{len(hunters)} chasseurs** disponibles\nSélectionnez un chasseur dans le menu ci-dessous :",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📊 Statistiques",
                value=f"**Total chasseurs:** {len(hunters)}\n**Avec Awakening:** {sum(1 for h in hunters.values() if h.get('awa') == 'oui')}\n**Styles uniques:** {len(set(h.get('style', 'Unknown') for h in hunters.values()))}",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed, view=view)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)

    @app_commands.command(name="minecraft_mods", description="🟦 Explorer les mods Minecraft par catégorie")
    @app_commands.describe(category="Catégorie de mods")
    async def minecraft_mods(self, interaction: discord.Interaction, 
                           category: Optional[str] = None):
        """Explore les mods Minecraft par catégorie"""
        
        try:
            with open(self.mods_data_file, 'r', encoding='utf-8') as f:
                mods_data = json.load(f)
            
            if not category:
                # Liste des catégories disponibles
                categories = list(mods_data.keys())
                embed = discord.Embed(
                    title="🟦 Minecraft Mods Database",
                    description="Choisissez une catégorie de mods à explorer :",
                    color=discord.Color.green()
                )
                
                for cat in categories:
                    mod_count = len(mods_data[cat])
                    embed.add_field(
                        name=f"📂 {cat.title()}",
                        value=f"{mod_count} mods disponibles",
                        inline=True
                    )
                
                embed.add_field(
                    name="💡 Usage",
                    value="Utilisez `/minecraft_mods category:[nom]` pour voir les mods d'une catégorie",
                    inline=False
                )
                
                await interaction.response.send_message(embed=embed)
                return
            
            # Afficher les mods de la catégorie
            if category.lower() not in mods_data:
                available = ", ".join(mods_data.keys())
                await interaction.response.send_message(f"❌ Catégorie inconnue.\n**Disponibles:** {available}", ephemeral=True)
                return
            
            mods = mods_data[category.lower()]
            
            embed = discord.Embed(
                title=f"🟦 Mods {category.title()}",
                description=f"{len(mods)} mods disponibles dans cette catégorie",
                color=discord.Color.green()
            )
            
            for mod in mods[:10]:  # Limite à 10 pour éviter la limite des embeds
                versions = ", ".join(mod["versions"][:3])  # Max 3 versions
                embed.add_field(
                    name=f"📦 {mod['name']}",
                    value=f"**Versions:** {versions}\n**Downloads:** {mod['downloads']}\n**Rating:** {mod['rating']}",
                    inline=False
                )
            
            if len(mods) > 10:
                embed.set_footer(text=f"Affichage des 10 premiers mods sur {len(mods)} total")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)

    @app_commands.command(name="fortnite_stats", description="🚀 Statistiques Fortnite d'un joueur")
    @app_commands.describe(username="Nom d'utilisateur Fortnite")
    async def fortnite_stats(self, interaction: discord.Interaction, username: str):
        """Affiche les stats Fortnite (simulation si pas d'API)"""
        
        await interaction.response.defer()
        
        # Simulation de stats (en attendant une vraie API)
        fake_stats = {
            "level": random.randint(50, 500),
            "wins_solo": random.randint(10, 200),
            "wins_duo": random.randint(15, 180),
            "wins_squad": random.randint(20, 250),
            "kills": random.randint(1000, 15000),
            "matches_played": random.randint(500, 3000),
            "win_rate": round(random.uniform(5.0, 25.0), 1)
        }
        
        embed = discord.Embed(
            title=f"🚀 Stats Fortnite - {username}",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="🏆 Victoires",
            value=f"**Solo:** {fake_stats['wins_solo']}\n**Duo:** {fake_stats['wins_duo']}\n**Squad:** {fake_stats['wins_squad']}",
            inline=True
        )
        
        embed.add_field(
            name="📊 Général",
            value=f"**Niveau:** {fake_stats['level']}\n**Kills:** {fake_stats['kills']:,}\n**Parties:** {fake_stats['matches_played']:,}",
            inline=True
        )
        
        embed.add_field(
            name="📈 Performance",
            value=f"**Win Rate:** {fake_stats['win_rate']}%\n**K/D Ratio:** {fake_stats['kills']/fake_stats['matches_played']:.2f}\n**Avg Kills/Game:** {fake_stats['kills']/fake_stats['matches_played']:.1f}",
            inline=True
        )
        
        embed.set_footer(text="Arsenal V4 Gaming • Stats simulées")
        
        await interaction.followup.send(embed=embed)

class HuntersDropdownView(discord.ui.View):
    """Vue avec dropdown pour sélectionner un chasseur"""
    
    def __init__(self, hunters_data):
        super().__init__(timeout=60)
        self.hunters_data = hunters_data
        
        # Diviser les chasseurs en groupes de 25 (limite Discord)
        hunter_names = list(hunters_data.keys())
        groups = [hunter_names[i:i+25] for i in range(0, len(hunter_names), 25)]
        
        for i, group in enumerate(groups):
            dropdown = HunterSelectDropdown(group, hunters_data, f"Groupe {i+1}")
            self.add_item(dropdown)

class HunterSelectDropdown(discord.ui.Select):
    """Dropdown pour sélectionner un chasseur"""
    
    def __init__(self, hunters_group, hunters_data, group_name):
        self.hunters_data = hunters_data
        
        options = [
            discord.SelectOption(
                label=name,
                description=f"Niveau {hunters_data[name].get('niveau', '?')} • {hunters_data[name].get('style', 'Unknown')}",
                emoji="🏹"
            )
            for name in hunters_group
        ]
        
        super().__init__(
            placeholder=f"Choisir un chasseur ({group_name})",
            options=options,
            min_values=1,
            max_values=1
        )
    
    async def callback(self, interaction: discord.Interaction):
        selected_hunter = self.values[0]
        hunter_info = self.hunters_data[selected_hunter]
        
        embed = discord.Embed(
            title=f"🏹 {selected_hunter}",
            description=hunter_info.get("description", "Chasseur Hunt Royal"),
            color=discord.Color.gold()
        )
        
        embed.add_field(name="💖 HP", value=hunter_info['hp'], inline=True)
        embed.add_field(name="⚔️ Dégâts", value=hunter_info['dmg'], inline=True)
        embed.add_field(name="🎯 Style", value=hunter_info['style'], inline=True)
        embed.add_field(name="📏 Distance", value=hunter_info['distance'], inline=True)
        embed.add_field(name="🌟 Niveau", value=hunter_info['niveau'], inline=True)
        
        awakening = "✅ Disponible" if hunter_info.get('awa') == 'oui' else "❌ Indisponible"
        embed.add_field(name="🔥 Awakening", value=awakening, inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(GamingAPISystem(bot))
    print("🎮 [Gaming API System] Module chargé avec succès!")
