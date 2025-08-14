# 🚀 Arsenal V4 - Advanced Social & Fun Commands
"""
Commandes sociales et de divertissement avancées pour Arsenal V4:
- Citations motivantes et quotes d'anime
- Blagues Chuck Norris
- Système de mémoire persistent
- Traducteur basique
- Profil utilisateur étendu
- Commandes interactives
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import random
import asyncio
from datetime import datetime
import os
from typing import Optional
import hashlib
import base64

class SocialFunSystem(commands.Cog):
    """Système de commandes sociales et divertissement"""
    
    def __init__(self, bot):
        self.bot = bot
        self.memory_file = "data/memory.json"
        self.user_profiles_file = "data/user_profiles.json"
        self.quotes_file = "data/quotes.json"
        self.init_social_data()
        
    def init_social_data(self):
        """Initialise les données sociales"""
        os.makedirs("data", exist_ok=True)
        
        # Mémoire du bot
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump({"volume": 0.5, "preferences": {}}, f, indent=2)
        
        # Citations par défaut
        if not os.path.exists(self.quotes_file):
            default_quotes = {
                "motivational": [
                    "Le succès n'est pas final, l'échec n'est pas fatal : c'est le courage de continuer qui compte.",
                    "Votre limitation c'est seulement votre imagination.",
                    "Les grandes choses n'arrivent jamais depuis la zone de confort.",
                    "Rêvez plus grand. Faites plus. Devenez plus.",
                    "Le succès commence par la volonté de réussir."
                ],
                "anime": [
                    "\"Si tu ne prends pas de risques, tu ne peux rien créer.\" - Monkey D. Luffy",
                    "\"Les gens deviennent plus forts quand ils ont quelque chose à protéger.\" - Naruto",
                    "\"Un héros doit toujours être prêt.\" - All Might",
                    "\"L'important n'est pas de savoir si tu peux le faire, mais si tu le feras.\" - Natsu Dragneel",
                    "\"Un vrai héros sauve tout le monde.\" - Deku"
                ],
                "chuck_norris": [
                    "Chuck Norris peut diviser par zéro.",
                    "Chuck Norris compte jusqu'à l'infini. Deux fois.",
                    "Chuck Norris peut éteindre une lampe en appuyant sur l'interrupteur... même si elle n'est pas branchée.",
                    "Chuck Norris peut battre le rock-paper-scissors avec juste du papier.",
                    "Chuck Norris peut compiler du code en un clignement d'œil."
                ]
            }
            with open(self.quotes_file, 'w', encoding='utf-8') as f:
                json.dump(default_quotes, f, indent=2, ensure_ascii=False)

    def load_memory(self):
        """Charge la mémoire du bot"""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"volume": 0.5, "preferences": {}}
    
    def save_memory(self, data):
        """Sauvegarde la mémoire du bot"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @app_commands.command(name="random_quote", description="✨ Affiche une citation motivante")
    @app_commands.describe(category="Catégorie de citation (motivational/anime)")
    async def random_quote(self, interaction: discord.Interaction, 
                          category: Optional[str] = "motivational"):
        """Affiche une citation aléatoire"""
        
        try:
            with open(self.quotes_file, 'r', encoding='utf-8') as f:
                quotes_data = json.load(f)
            
            if category.lower() not in quotes_data:
                available = ", ".join(quotes_data.keys())
                await interaction.response.send_message(
                    f"❌ Catégorie invalide.\n**Disponibles:** {available}", 
                    ephemeral=True
                )
                return
            
            quote = random.choice(quotes_data[category.lower()])
            
            # Couleur selon la catégorie
            colors = {
                "motivational": discord.Color.blue(),
                "anime": discord.Color.orange(),
                "chuck_norris": discord.Color.red()
            }
            
            embed = discord.Embed(
                title=f"✨ Citation {category.title()}",
                description=f"*{quote}*",
                color=colors.get(category.lower(), discord.Color.blue())
            )
            
            embed.set_footer(text=f"Arsenal V4 • Citations {category.title()}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)

    @app_commands.command(name="anime_quote", description="🍥 Citation inspirante d'anime")
    async def anime_quote(self, interaction: discord.Interaction):
        """Citation d'anime spécifique"""
        await self.random_quote(interaction, "anime")

    @app_commands.command(name="chuck_norris_joke", description="💪 Blague Chuck Norris")
    async def chuck_norris_joke(self, interaction: discord.Interaction):
        """Blague Chuck Norris"""
        await self.random_quote(interaction, "chuck_norris")

    @app_commands.command(name="mock_text", description="🤪 Transforme un texte en version sarcastique")
    @app_commands.describe(text="Texte à transformer")
    async def mock_text(self, interaction: discord.Interaction, text: str):
        """Transforme un texte en mocking SpongeBob"""
        
        if len(text) > 200:
            await interaction.response.send_message("❌ Texte trop long (max 200 caractères)", ephemeral=True)
            return
        
        # Alternance majuscule/minuscule
        mocked_text = ""
        uppercase = True
        
        for char in text:
            if char.isalpha():
                mocked_text += char.upper() if uppercase else char.lower()
                uppercase = not uppercase
            else:
                mocked_text += char
        
        embed = discord.Embed(
            title="🤪 SpongeBob Mocking",
            color=discord.Color.yellow()
        )
        
        embed.add_field(
            name="📝 Original",
            value=f"`{text}`",
            inline=False
        )
        
        embed.add_field(
            name="🤪 Mocked",
            value=f"`{mocked_text}`",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="magic_8ball", description="🎱 Pose une question à la boule magique")
    @app_commands.describe(question="Ta question")
    async def magic_8ball(self, interaction: discord.Interaction, question: str):
        """Magic 8-ball avec réponses"""
        
        responses = [
            "✅ Oui, absolument !",
            "❌ Non, définitivement pas.",
            "🤔 Peut-être...",
            "🔮 Les signes pointent vers oui.",
            "⚠️ Ne comptez pas là-dessus.",
            "🌟 C'est certain !",
            "❓ Demandez à nouveau plus tard.",
            "🎯 Mes sources disent non.",
            "🔥 Oui, sans aucun doute !",
            "💭 Concentrez-vous et demandez à nouveau.",
            "⭐ Très probable.",
            "🌊 La réponse est floue.",
            "💫 Oui, dans vos rêves !",
            "⚡ Les chances sont bonnes.",
            "🚫 Mieux vaut ne pas vous le dire maintenant."
        ]
        
        response = random.choice(responses)
        
        embed = discord.Embed(
            title="🎱 Magic 8-Ball Arsenal",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="❓ Question",
            value=f"*{question}*",
            inline=False
        )
        
        embed.add_field(
            name="🔮 Réponse",
            value=f"**{response}**",
            inline=False
        )
        
        embed.set_footer(text="🎱 La boule magique a parlé !")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="spin_wheel", description="🎡 Tourne une roue et choisis une option")
    @app_commands.describe(options="Options séparées par des virgules")
    async def spin_wheel(self, interaction: discord.Interaction, options: str):
        """Roue de fortune avec options personnalisées"""
        
        option_list = [opt.strip() for opt in options.split(",") if opt.strip()]
        
        if len(option_list) < 2:
            await interaction.response.send_message("❌ Il faut au moins 2 options séparées par des virgules", ephemeral=True)
            return
        
        if len(option_list) > 20:
            await interaction.response.send_message("❌ Maximum 20 options", ephemeral=True)
            return
        
        # Animation de la roue
        await interaction.response.send_message("🎡 La roue tourne...")
        
        await asyncio.sleep(1)
        chosen = random.choice(option_list)
        
        embed = discord.Embed(
            title="🎡 Roue de Fortune Arsenal",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name="🎯 Résultat",
            value=f"**{chosen}**",
            inline=False
        )
        
        embed.add_field(
            name="📋 Options",
            value=f"{', '.join(option_list)}",
            inline=False
        )
        
        embed.set_footer(text="🍀 Que la chance soit avec vous !")
        
        await interaction.edit_original_response(content=None, embed=embed)

    @app_commands.command(name="random_member", description="🎲 Choisit un membre aléatoire du serveur")
    @app_commands.describe(role="Rôle spécifique (optionnel)")
    async def random_member(self, interaction: discord.Interaction, 
                           role: Optional[discord.Role] = None):
        """Sélectionne un membre aléatoire"""
        
        if role:
            members = [m for m in role.members if not m.bot]
            source = f"avec le rôle **{role.name}**"
        else:
            members = [m for m in interaction.guild.members if not m.bot]
            source = "du serveur"
        
        if not members:
            await interaction.response.send_message(f"❌ Aucun membre trouvé {source}", ephemeral=True)
            return
        
        chosen = random.choice(members)
        
        embed = discord.Embed(
            title="🎲 Membre Aléatoire",
            color=discord.Color.random()
        )
        
        embed.add_field(
            name="🎯 Choisi",
            value=f"**{chosen.mention}**\n({chosen.display_name})",
            inline=False
        )
        
        embed.add_field(
            name="📊 Stats",
            value=f"**Membres disponibles:** {len(members)}\n**Source:** {source}",
            inline=False
        )
        
        if chosen.avatar:
            embed.set_thumbnail(url=chosen.avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="game_picker", description="🎮 Propose un jeu aléatoire")
    async def game_picker(self, interaction: discord.Interaction):
        """Suggère un jeu aléatoire"""
        
        games = [
            {"name": "Among Us", "emoji": "🚀", "players": "4-15", "genre": "Déduction"},
            {"name": "Minecraft", "emoji": "🟫", "players": "1-∞", "genre": "Sandbox"},
            {"name": "Valorant", "emoji": "🎯", "players": "10", "genre": "FPS"},
            {"name": "League of Legends", "emoji": "⚔️", "players": "10", "genre": "MOBA"},
            {"name": "Fall Guys", "emoji": "🏃", "players": "60", "genre": "Battle Royale"},
            {"name": "Rocket League", "emoji": "🚗", "players": "2-8", "genre": "Sport"},
            {"name": "Overwatch 2", "emoji": "🦾", "players": "12", "genre": "FPS"},
            {"name": "Fortnite", "emoji": "🏗️", "players": "100", "genre": "Battle Royale"},
            {"name": "Apex Legends", "emoji": "🔫", "players": "60", "genre": "Battle Royale"},
            {"name": "CS2", "emoji": "💣", "players": "10", "genre": "FPS"},
        ]
        
        chosen_game = random.choice(games)
        
        embed = discord.Embed(
            title="🎮 Suggestion de Jeu",
            description="Voici un jeu aléatoire pour vous !",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name=f"{chosen_game['emoji']} {chosen_game['name']}",
            value=f"**Genre:** {chosen_game['genre']}\n**Joueurs:** {chosen_game['players']}\n**Suggéré par:** Arsenal V4",
            inline=False
        )
        
        embed.add_field(
            name="🎲 Autres options",
            value="Re-lancez la commande pour une nouvelle suggestion !",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="translate_text", description="🌍 Traduction basique de texte")
    @app_commands.describe(text="Texte à traduire", target_lang="Langue cible")
    async def translate_text(self, interaction: discord.Interaction, 
                           text: str, target_lang: str = "en"):
        """Traducteur basique (simulation)"""
        
        # Dictionnaire de traductions basiques
        translations = {
            "bonjour": {"en": "Hello", "es": "Hola", "de": "Hallo", "it": "Ciao"},
            "merci": {"en": "Thank you", "es": "Gracias", "de": "Danke", "it": "Grazie"},
            "au revoir": {"en": "Goodbye", "es": "Adiós", "de": "Auf Wiedersehen", "it": "Arrivederci"},
            "oui": {"en": "Yes", "es": "Sí", "de": "Ja", "it": "Sì"},
            "non": {"en": "No", "es": "No", "de": "Nein", "it": "No"}
        }
        
        text_lower = text.lower()
        translated = translations.get(text_lower, {}).get(target_lang.lower())
        
        if not translated:
            translated = f"[Traduction indisponible pour '{text}' vers '{target_lang}']"
        
        embed = discord.Embed(
            title="🌍 Traduction Arsenal",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📝 Texte original",
            value=f"`{text}`",
            inline=False
        )
        
        embed.add_field(
            name=f"🔄 Traduit ({target_lang.upper()})",
            value=f"`{translated}`",
            inline=False
        )
        
        embed.set_footer(text="Traducteur basique • Fonctions limitées")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="user_profile", description="👤 Profil utilisateur Arsenal")
    @app_commands.describe(user="Utilisateur à consulter")
    async def user_profile(self, interaction: discord.Interaction, 
                          user: Optional[discord.Member] = None):
        """Affiche le profil utilisateur étendu"""
        
        target_user = user or interaction.user
        
        # Calculs statistiques
        join_date = target_user.joined_at
        account_age = (datetime.now(join_date.tzinfo) - target_user.created_at).days if target_user.created_at else 0
        server_time = (datetime.now(join_date.tzinfo) - join_date).days if join_date else 0
        
        embed = discord.Embed(
            title=f"👤 Profil de {target_user.display_name}",
            color=target_user.color if target_user.color != discord.Color.default() else discord.Color.blue()
        )
        
        if target_user.avatar:
            embed.set_thumbnail(url=target_user.avatar.url)
        
        embed.add_field(
            name="📋 Informations",
            value=f"**Pseudo:** {target_user.name}#{target_user.discriminator}\n**Surnom:** {target_user.display_name}\n**ID:** {target_user.id}",
            inline=False
        )
        
        embed.add_field(
            name="📅 Dates",
            value=f"**Compte créé:** <t:{int(target_user.created_at.timestamp())}:R>\n**Rejoint le serveur:** <t:{int(join_date.timestamp())}:R>" if join_date else "**Rejoint:** Inconnu",
            inline=True
        )
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"**Âge du compte:** {account_age} jours\n**Temps sur le serveur:** {server_time} jours\n**Rôles:** {len(target_user.roles)-1}",
            inline=True
        )
        
        # Rôles (limité à 10)
        if len(target_user.roles) > 1:
            roles = [role.mention for role in sorted(target_user.roles[1:], key=lambda r: r.position, reverse=True)][:10]
            embed.add_field(
                name="🏷️ Rôles",
                value=" ".join(roles) or "Aucun rôle",
                inline=False
            )
        
        # Status
        status_emojis = {
            discord.Status.online: "🟢",
            discord.Status.idle: "🟡", 
            discord.Status.dnd: "🔴",
            discord.Status.offline: "⚫"
        }
        
        embed.add_field(
            name="📡 Status",
            value=f"{status_emojis.get(target_user.status, '❓')} {target_user.status.name.title()}",
            inline=True
        )
        
        embed.set_footer(text=f"Arsenal V4 Profile • Demandé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(SocialFunSystem(bot))
    print("🎭 [Social Fun System] Module chargé avec succès!")
