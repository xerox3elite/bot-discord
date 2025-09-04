"""
🔧 Arsenal Utilities Basic - Commandes utilitaires essentielles
Commandes de base manquantes identifiées lors de l'audit complet
Auteur: Arsenal Studio
"""

import discord
from discord.ext import commands
from discord import app_commands
import time
import psutil
import platform
from datetime import datetime, timedelta
import random
from commands.arsenal_protection_middleware import require_registration

class ArsenalUtilitiesBasic(commands.Cog):
    """Commandes utilitaires de base pour Arsenal"""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
    
    @app_commands.command(name="ping", description="🏓 Affiche la latence du bot")
    @require_registration("basic")
    async def ping(self, interaction: discord.Interaction):
        """Commande ping avec latence détaillée"""
        
        start_time = time.time()
        
        embed = discord.Embed(
            title="🏓 Pong !",
            color=0x00ff00,
            timestamp=datetime.now()
        )
        
        # Latence WebSocket
        embed.add_field(
            name="🌐 Latence WebSocket",
            value=f"`{round(self.bot.latency * 1000)}ms`",
            inline=True
        )
        
        # Latence API (calculée)
        await interaction.response.send_message(embed=embed)
        api_latency = round((time.time() - start_time) * 1000)
        
        embed.add_field(
            name="⚡ Latence API",
            value=f"`{api_latency}ms`",
            inline=True
        )
        
        # Statut qualité
        if api_latency < 100:
            status = "🟢 Excellent"
        elif api_latency < 200:
            status = "🟡 Bon"
        else:
            status = "🔴 Lent"
            
        embed.add_field(
            name="📊 Qualité",
            value=status,
            inline=True
        )
        
        await interaction.edit_original_response(embed=embed)
    
    @app_commands.command(name="uptime", description="⏰ Temps de fonctionnement du bot")
    @require_registration("basic")
    async def uptime(self, interaction: discord.Interaction):
        """Affiche le temps de fonctionnement"""
        
        uptime_seconds = time.time() - self.start_time
        uptime_delta = timedelta(seconds=int(uptime_seconds))
        
        embed = discord.Embed(
            title="⏰ Temps de fonctionnement",
            color=0x00aaff,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🚀 Démarré depuis",
            value=f"`{uptime_delta}`",
            inline=False
        )
        
        embed.add_field(
            name="📊 Statistiques",
            value=f"```yaml\nServeurs: {len(self.bot.guilds)}\nUtilisateurs: {len(self.bot.users)}\nCommandes chargées: {len(self.bot.cogs)}```",
            inline=False
        )
        
        embed.set_footer(text="Arsenal V4.5.2 ULTIMATE")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="serverinfo", description="🏰 Informations détaillées du serveur")
    @require_registration("basic")
    async def serverinfo(self, interaction: discord.Interaction):
        """Informations complètes du serveur"""
        
        guild = interaction.guild
        
        embed = discord.Embed(
            title=f"🏰 {guild.name}",
            color=0x7289da,
            timestamp=datetime.now()
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        # Informations générales
        embed.add_field(
            name="👑 Propriétaire",
            value=f"{guild.owner.mention}",
            inline=True
        )
        
        embed.add_field(
            name="📅 Créé le",
            value=f"<t:{int(guild.created_at.timestamp())}:D>",
            inline=True
        )
        
        embed.add_field(
            name="🔗 ID",
            value=f"`{guild.id}`",
            inline=True
        )
        
        # Statistiques membres
        total_members = guild.member_count
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        bots = sum(1 for member in guild.members if member.bot)
        
        embed.add_field(
            name="👥 Membres",
            value=f"```yaml\nTotal: {total_members}\nEn ligne: {online_members}\nBots: {bots}\nHumains: {total_members - bots}```",
            inline=False
        )
        
        # Canaux
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        embed.add_field(
            name="📺 Canaux",
            value=f"```yaml\nTexte: {text_channels}\nVocal: {voice_channels}\nCatégories: {categories}```",
            inline=True
        )
        
        # Rôles et autres
        embed.add_field(
            name="🎭 Autres",
            value=f"```yaml\nRôles: {len(guild.roles)}\nEmojis: {len(guild.emojis)}\nBoosts: {guild.premium_subscription_count}```",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="userinfo", description="👤 Informations détaillées d'un utilisateur")
    @app_commands.describe(user="Utilisateur à analyser (optionnel, vous par défaut)")
    @require_registration("basic")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        """Informations complètes d'un utilisateur"""
        
        if user is None:
            user = interaction.user
        
        embed = discord.Embed(
            title=f"👤 {user.display_name}",
            color=user.color if user.color.value != 0 else 0x7289da,
            timestamp=datetime.now()
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        
        # Informations générales
        embed.add_field(
            name="🏷️ Nom d'utilisateur",
            value=f"`{user.name}`",
            inline=True
        )
        
        embed.add_field(
            name="🔗 ID",
            value=f"`{user.id}`",
            inline=True
        )
        
        embed.add_field(
            name="🤖 Bot",
            value="✅ Oui" if user.bot else "❌ Non",
            inline=True
        )
        
        # Dates importantes
        embed.add_field(
            name="📅 Compte créé",
            value=f"<t:{int(user.created_at.timestamp())}:D>\n<t:{int(user.created_at.timestamp())}:R>",
            inline=True
        )
        
        embed.add_field(
            name="📅 A rejoint",
            value=f"<t:{int(user.joined_at.timestamp())}:D>\n<t:{int(user.joined_at.timestamp())}:R>",
            inline=True
        )
        
        # Statut et activité
        status_emoji = {
            discord.Status.online: "🟢",
            discord.Status.idle: "🟡",
            discord.Status.dnd: "🔴",
            discord.Status.offline: "⚫"
        }
        
        embed.add_field(
            name="📊 Statut",
            value=f"{status_emoji.get(user.status, '❓')} {user.status.name.title()}",
            inline=True
        )
        
        # Rôles (limité à 5 + highest)
        roles = [role.mention for role in user.roles[1:]]  # Exclure @everyone
        if len(roles) > 5:
            role_text = f"{', '.join(roles[:5])}, ... (+{len(roles)-5})"
        else:
            role_text = ', '.join(roles) if roles else "Aucun"
        
        embed.add_field(
            name=f"🎭 Rôles ({len(roles)})",
            value=role_text,
            inline=False
        )
        
        # Permissions clés
        perms = user.guild_permissions
        key_perms = []
        if perms.administrator:
            key_perms.append("👑 Administrateur")
        if perms.manage_guild:
            key_perms.append("🏰 Gérer le serveur")
        if perms.manage_channels:
            key_perms.append("📺 Gérer les canaux")
        if perms.manage_roles:
            key_perms.append("🎭 Gérer les rôles")
        if perms.kick_members:
            key_perms.append("👮 Expulser")
        if perms.ban_members:
            key_perms.append("🔨 Bannir")
        
        if key_perms:
            embed.add_field(
                name="🛡️ Permissions clés",
                value='\n'.join(key_perms[:5]),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="coin-flip", description="🪙 Lance une pièce de monnaie")
    @require_registration("basic")
    async def coin_flip(self, interaction: discord.Interaction):
        """Lance une pièce"""
        
        result = random.choice(["Pile", "Face"])
        emoji = "🪙" if result == "Pile" else "🥇"
        
        embed = discord.Embed(
            title="🪙 Lancer de pièce",
            description=f"## {emoji} {result} !",
            color=0xffd700,
            timestamp=datetime.now()
        )
        
        embed.set_footer(text=f"Lancé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="dice-roll", description="🎲 Lance un ou plusieurs dés")
    @app_commands.describe(
        sides="Nombre de faces du dé (défaut: 6)",
        count="Nombre de dés à lancer (défaut: 1, max: 10)"
    )
    @require_registration("basic")
    async def dice_roll(self, interaction: discord.Interaction, sides: int = 6, count: int = 1):
        """Lance des dés"""
        
        if sides < 2 or sides > 100:
            await interaction.response.send_message("❌ Le dé doit avoir entre 2 et 100 faces !", ephemeral=True)
            return
        
        if count < 1 or count > 10:
            await interaction.response.send_message("❌ Vous pouvez lancer entre 1 et 10 dés !", ephemeral=True)
            return
        
        results = [random.randint(1, sides) for _ in range(count)]
        total = sum(results)
        
        embed = discord.Embed(
            title="🎲 Lancer de dés",
            color=0xff6b6b,
            timestamp=datetime.now()
        )
        
        if count == 1:
            embed.description = f"## 🎲 {results[0]}"
        else:
            dice_display = " + ".join(f"🎲{r}" for r in results)
            embed.description = f"### {dice_display}\n## 🔢 Total: {total}"
        
        embed.add_field(
            name="📊 Détails",
            value=f"```yaml\nDé(s): {count}d{sides}\nRésultat(s): {results}\nTotal: {total}```",
            inline=False
        )
        
        embed.set_footer(text=f"Lancé par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="random-joke", description="😂 Raconte une blague aléatoire")
    @require_registration("basic")
    async def random_joke(self, interaction: discord.Interaction):
        """Blague aléatoire"""
        
        jokes = [
            "Pourquoi les plongeurs plongent-ils toujours en arrière et jamais en avant ? Parce que sinon, ils tombent dans le bateau !",
            "Que dit un informaticien quand il se noie ? F1 ! F1 !",
            "Comment appelle-t-on un chat tombé dans un pot de peinture le jour de Noël ? Un chat-mallow !",
            "Pourquoi les poissons n'aiment pas jouer au tennis ? Parce qu'ils ont peur du filet !",
            "Que dit un escargot quand il croise une limace ? 'Regarde, un nudiste !'",
            "Comment appelle-t-on un boomerang qui ne revient pas ? Un bâton !",
            "Pourquoi les développeurs préfèrent-ils le thé ? Parce que le café les rend trop java !",
            "Que dit un bot Discord quand il bug ? 'Je crois que j'ai une erreur 404... de personnalité !'",
            "Pourquoi Arsenal bot est-il si intelligent ? Parce qu'il a été codé avec amour ! ❤️"
        ]
        
        joke = random.choice(jokes)
        
        embed = discord.Embed(
            title="😂 Blague du jour",
            description=joke,
            color=0xffeb3b,
            timestamp=datetime.now()
        )
        
        embed.set_footer(text="Arsenal Comedy Club 🎭")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="random-fact", description="🧠 Partage un fait aléatoire intéressant")
    @require_registration("basic")
    async def random_fact(self, interaction: discord.Interaction):
        """Fait aléatoire intéressant"""
        
        facts = [
            "🐙 Les pieuvres ont trois cœurs et du sang bleu !",
            "🍯 Le miel ne pourrit jamais. On a trouvé du miel vieux de 3000 ans encore comestible !",
            "🦈 Les requins existent depuis plus longtemps que les arbres !",
            "🌙 La Lune s'éloigne de la Terre de 3,8 cm chaque année.",
            "🧠 Votre cerveau utilise environ 20% de l'énergie de votre corps.",
            "🔥 La température de la foudre est 5 fois plus chaude que la surface du Soleil !",
            "🐌 Un escargot peut dormir pendant 3 ans !",
            "💎 Il pleut des diamants sur Saturne et Jupiter !",
            "🤖 Arsenal bot traite des milliers de commandes par jour avec une précision de 99.9% !"
        ]
        
        fact = random.choice(facts)
        
        embed = discord.Embed(
            title="🧠 Le saviez-vous ?",
            description=fact,
            color=0x2196f3,
            timestamp=datetime.now()
        )
        
        embed.set_footer(text="Arsenal Knowledge Base 📚")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Fonction d'installation du cog"""
    await bot.add_cog(ArsenalUtilitiesBasic(bot))
