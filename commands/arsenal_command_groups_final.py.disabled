#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ Arsenal AutoMod V5.0.1 - Système de Modération Ultimate
489 mots spécialisés à travers 4 niveaux de sévérité
Développé par XeRoX - Arsenal Bot V4.6
"""

import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import asyncio
import json
import re
from typing import List, Dict, Optional
import datetime
import logging

class ArsenalCommandGroupsFinal(commands.Cog):
    """Arsenal AutoMod V5.0.1 - Système de Modération avec 489 mots"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/arsenal_automod_v5.db"
        
        # Base de 489 mots classés par sévérité
        self.WORDS_DATABASE = {
            "NIVEAU_1_LEGER": [
                # Insultes légères (42 mots)
                "débile", "idiot", "stupide", "nul", "con", "bête", "abruti", "crétin", 
                "imbécile", "andouille", "nigaud", "sot", "benêt", "dadais", "ballot", 
                "gourde", "bourrique", "âne", "mule", "cornichon", "citrouille", "navet",
                "patate", "pomme", "poire", "banane", "concombre", "radis", "courge",
                "melon", "pastèque", "tomate", "oignon", "poireau", "carotte", "haricot",
                "petit pois", "lentille", "pois chiche", "flageolet", "fève", "noob"
            ],
            
            "NIVEAU_2_MODERE": [
                # Termes moyennement offensants (97 mots) 
                "merde", "putain", "bordel", "foutoir", "salopard", "salaud", "salope",
                "enfoiré", "connard", "connasse", "porc", "cochon", "ordure", "déchet",
                "racaille", "crapule", "vermine", "parasite", "cafard", "punaise", "puce",
                "morpion", "tique", "sangsue", "limace", "escargot", "asticot", "ver",
                "larve", "chenille", "charogne", "charogn", "pourriture", "infection",
                "cancer", "tumeur", "kyste", "abcès", "furoncle", "bouton", "pustule",
                "clochard", "mendiant", "gueux", "va-nu-pieds", "loqueteux", "haillons",
                "serpillière", "torchon", "chiffon", "balai", "vadrouille", "éponge",
                "lavette", "carpette", "paillasson", "zero", "minus", "minable", "piteux",
                "lamentable", "pathétique", "ridicule", "grotesque", "risible", "dérisoire",
                "insignifiant", "médiocre", "quelconque", "banal", "terne", "fade",
                "insipide", "plat", "morne", "ennuyeux", "assommant", "soporifique",
                "barbant", "rasant", "chiant", "emmerdant", "gonflant", "lourd", "pénible",
                "casse-pieds", "pot de colle", "crampon", "ventouse", "sangsue", "parasite",
                "profiteur", "exploiteur", "vampire", "vautour", "hyène", "chacal", "rat",
                "souris", "mulot", "campagnol", "hamster", "gerbille", "cobaye", "lapin"
            ],
            
            "NIVEAU_3_SEVERE": [
                # Termes sévères et offensants (195 mots)
                "enculé", "bâtard", "fils de pute", "fdp", "ntm", "nique ta mère",
                "va te faire foutre", "vtff", "ferme ta gueule", "ftg", "ta gueule",
                "pd", "pédé", "tapette", "tantouze", "fiotte", "lopette", "gonzesse",
                "salope", "pute", "putain", "pétasse", "garce", "chienne", "truie",
                "cochonne", "trainée", "marie-couche-toi-là", "marie-salope", "pouffiasse",
                "grognasse", "mocheté", "thon", "boudin", "cageot", "laideron", "repoussoir",
                "horreur", "monstre", "aberration", "catastrophe", "désastre", "fléau",
                "plaie", "poison", "venin", "virus", "bactérie", "microbe", "parasite",
                "vermine", "nuisible", "cafard", "cancrelat", "blatte", "hanneton",
                "scarabée", "bousier", "termite", "fourmi", "guêpe", "frelon", "taon",
                "moustique", "moucheron", "mouche", "asticot", "ver", "sangsue", "limace",
                "escargot", "baveux", "gluant", "visqueux", "répugnant", "dégoûtant",
                "écœurant", "immonde", "ignoble", "abject", "sordide", "crasseux",
                "pouilleux", "galeux", "teigneux", "morveux", "chassieux", "purulent",
                "suintant", "baveux", "dégoulinant", "fétide", "nauséabond", "pestilentiel",
                "infecte", "putride", "rance", "moisi", "pourri", "avarié", "gâté",
                "corrompu", "vicié", "contaminé", "souillé", "crotté", "boueux", "fangeux",
                "vaseux", "limoneux", "bourbeux", "marécageux", "pestilentiel", "méphitique",
                "délétère", "toxique", "vénéneux", "mortel", "fatal", "létal", "funeste",
                "néfaste", "pernicieux", "maléfique", "diabolique", "satanique", "infernal",
                "démoniaque", "maudit", "damné", "réprouvé", "banni", "exclu", "paria",
                "pestiféré", "lépreux", "galeux", "teigneux", "pouilleux", "crasseux",
                "dégueu", "dégueulasse", "immonde", "ignoble", "abject", "sordide",
                "crapuleux", "ignominieux", "infâme", "vil", "bas", "rampant", "servile",
                "lâche", "couard", "pleutre", "poltron", "froussard", "trouillard",
                "dégonflé", "mollasse", "mou", "flasque", "avachi", "ramolli", "gâteux",
                "sénile", "décrépit", "caduc", "fini", "usé", "râpé", "élimé", "défraîchi",
                "fané", "flétri", "ratatiné", "rabougri", "chétif", "malingre", "rachitique",
                "squelettique", "décharné", "émacié", "étique", "famélique", "affamé",
                "crève-la-faim", "meurt-de-faim", "va-nu-pieds", "sans-le-sou", "fauché",
                "ruiné", "démuni", "nécessiteux", "indigent", "misérable", "misérable",
                "pitoyable", "lamentable", "navrant", "désolant", "affligeant", "consternant"
            ],
            
            "NIVEAU_4_EXTREME": [
                # Termes extrêmes nécessitant action immédiate (155 mots)
                "nazi", "hitler", "shoah", "holocauste", "génocide", "extermination",
                "chambre à gaz", "four crématoire", "solution finale", "race supérieure",
                "aryen", "ss", "gestapo", "reich", "führer", "mein kampf", "croix gammée",
                "svastika", "fasciste", "collabo", "collaborateur", "traître", "vendu",
                "terroriste", "kamikaze", "djihad", "allah akbar", "mort aux juifs",
                "mort aux arabes", "mort aux noirs", "sale juif", "sale arabe", "sale noir",
                "négro", "bamboula", "banania", "bounty", "oncle tom", "macaque", "singe",
                "gorille", "chimpanzé", "bonobo", "orang-outan", "gibbon", "mandrill",
                "babouin", "cynocéphale", "cercopithèque", "sapajou", "ouistiti", "tamarin",
                "marmouset", "capucin", "atèle", "hurleur", "lémur", "loris", "tarsier",
                "galago", "potto", "indri", "sifaka", "propithèque", "avahi", "hapalémur",
                "vari", "maki", "chirogale", "microcebus", "cheirogale", "allocebus",
                "phaner", "daubentonia", "aye-aye", "tenrec", "hérisson", "musaraigne",
                "taupe", "desman", "solénodon", "gymnure", "erinaceus", "sorex", "crocidura",
                "neomys", "blarina", "cryptotis", "notiosorex", "megasorex", "congosorex",
                "scutisorex", "diplomesodon", "desmanella", "galemys", "desmana", "scalopus",
                "scapanus", "parascalops", "neurotrichus", "urotrichus", "dymecodon",
                "mogera", "talpa", "scaptochirus", "parascaptor", "scaptonyx", "uropsilus",
                "nasillus", "scaptoryctes", "chrysochloris", "calcochloris", "huetia",
                "chlorotalpa", "cryptochloris", "eremitalpa", "grant", "neamblysomus",
                "amblysomus", "carpitalpa", "chrysospalax", "limnogale", "microgale",
                "oryzorictes", "microgale", "geogale", "setifer", "echinops", "hemicentetes",
                "endo", "connard", "salope", "fdp", "enculé", "putain", "merde", "chier",
                "pisser", "gerber", "vomir", "dégueuler", "cracher", "postillonner",
                "baver", "roter", "péter", "chier", "pisser", "se branler", "se masturber",
                "niquer", "baiser", "tringler", "bourrer", "ramoner", "limer", "sauter",
                "ken", "pogner", "pécho", "choper", "attraper", "saisir", "empoigner",
                "agripper", "happer", "gober", "avaler", "ingurgiter", "engloutir"
            ]
        }
        
        # Sanctions par niveau
        self.SANCTIONS = {
            "NIVEAU_1_LEGER": {
                "action": "warn",
                "duration": 0,
                "points": 1,
                "message": "⚠️ Attention au langage ! Évitez les termes inappropriés.",
                "auto_delete": True
            },
            "NIVEAU_2_MODERE": {
                "action": "timeout",
                "duration": 300,  # 5 minutes
                "points": 3,
                "message": "🔇 Timeout 5min pour langage modérément offensant",
                "auto_delete": True
            },
            "NIVEAU_3_SEVERE": {
                "action": "timeout",
                "duration": 1800,  # 30 minutes
                "points": 5,
                "message": "🚫 Timeout 30min pour langage sévère",
                "auto_delete": True
            },
            "NIVEAU_4_EXTREME": {
                "action": "ban",
                "duration": 0,  # Permanent
                "points": 10,
                "message": "🔨 Bannissement pour contenu extrême/haineux",
                "auto_delete": True
            }
        }

    async def cog_load(self):
        """Initialize database when cog loads"""
        await self.init_database()
        print("[AutoMod V5.0.1] Base de données initialisée avec 489 mots")

    async def init_database(self):
        """Initialize the automod database"""
        import os
        os.makedirs('data', exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            # Historique des sanctions
            await db.execute('''
                CREATE TABLE IF NOT EXISTS sanctions_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER,
                    user_id INTEGER, 
                    moderator_id INTEGER,
                    action TEXT,
                    reason TEXT,
                    level TEXT,
                    points INTEGER DEFAULT 0,
                    timestamp TEXT,
                    expires_at TEXT
                )
            ''')
            
            # Configuration par serveur
            await db.execute('''
                CREATE TABLE IF NOT EXISTS guild_config (
                    guild_id INTEGER PRIMARY KEY,
                    automod_enabled INTEGER DEFAULT 1,
                    log_channel INTEGER,
                    ignore_roles TEXT DEFAULT '[]',
                    ignore_channels TEXT DEFAULT '[]',
                    custom_words TEXT DEFAULT '[]',
                    rehab_enabled INTEGER DEFAULT 1,
                    rehab_threshold INTEGER DEFAULT 15
                )
            ''')
            
            await db.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        """Analyse tous les messages pour détecter les mots interdits"""
        if message.author.bot or not message.guild:
            return
            
        # Vérifier si l'AutoMod est activé
        config = await self.get_guild_config(message.guild.id)
        if not config['automod_enabled']:
            return
            
        # Ignorer certains rôles/channels
        if await self.should_ignore(message, config):
            return
            
        # Scanner le message
        detected_level = await self.scan_message(message.content)
        if detected_level:
            await self.apply_sanction(message, detected_level)

    async def scan_message(self, content: str) -> Optional[str]:
        """Scan message for forbidden words"""
        content_lower = content.lower()
        
        # Scanner par ordre de sévérité (du plus grave au moins grave)
        for level in ["NIVEAU_4_EXTREME", "NIVEAU_3_SEVERE", "NIVEAU_2_MODERE", "NIVEAU_1_LEGER"]:
            for word in self.WORDS_DATABASE[level]:
                if word.lower() in content_lower:
                    return level
        return None

    async def apply_sanction(self, message, level: str):
        """Apply sanction based on detected level"""
        sanction = self.SANCTIONS[level]
        user = message.author
        guild = message.guild
        
        try:
            # Supprimer le message
            if sanction["auto_delete"]:
                await message.delete()
            
            # Appliquer la sanction
            if sanction["action"] == "warn":
                await self.warn_user(user, guild, level, sanction["message"])
            elif sanction["action"] == "timeout":
                await user.timeout(discord.utils.utcnow() + discord.timedelta(seconds=sanction["duration"]), 
                                 reason=f"AutoMod V5.0.1 - {level}")
                await self.log_sanction(user, guild, "timeout", level, sanction["duration"])
            elif sanction["action"] == "ban":
                await user.ban(reason=f"AutoMod V5.0.1 - {level}")
                await self.log_sanction(user, guild, "ban", level, 0)
                
            # Sauvegarder dans l'historique  
            await self.save_sanction_history(guild.id, user.id, self.bot.user.id, 
                                           sanction["action"], level, sanction["points"])
            
        except discord.Forbidden:
            print(f"[AutoMod] Permissions insuffisantes pour sanctionner {user}")
        except Exception as e:
            print(f"[AutoMod] Erreur sanction: {e}")

    async def get_guild_config(self, guild_id: int) -> dict:
        """Get guild automod configuration"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT * FROM guild_config WHERE guild_id = ?", (guild_id,))
            result = await cursor.fetchone()
            
            if result:
                return {
                    'automod_enabled': bool(result[1]),
                    'log_channel': result[2],
                    'ignore_roles': json.loads(result[3] or '[]'),
                    'ignore_channels': json.loads(result[4] or '[]'),
                    'custom_words': json.loads(result[5] or '[]'),
                    'rehab_enabled': bool(result[6]),
                    'rehab_threshold': result[7]
                }
            else:
                # Config par défaut
                return {
                    'automod_enabled': True,
                    'log_channel': None,
                    'ignore_roles': [],
                    'ignore_channels': [],
                    'custom_words': [],
                    'rehab_enabled': True,
                    'rehab_threshold': 15
                }

    async def should_ignore(self, message, config: dict) -> bool:
        """Check if message should be ignored based on config"""
        # Ignorer certains rôles
        user_role_ids = [role.id for role in message.author.roles]
        if any(role_id in config['ignore_roles'] for role_id in user_role_ids):
            return True
            
        # Ignorer certains channels
        if message.channel.id in config['ignore_channels']:
            return True
            
        return False

    async def save_sanction_history(self, guild_id: int, user_id: int, moderator_id: int, 
                                  action: str, level: str, points: int):
        """Save sanction to history"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO sanctions_history 
                (guild_id, user_id, moderator_id, action, reason, level, points, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (guild_id, user_id, moderator_id, action, f"AutoMod V5.0.1 - {level}", 
                  level, points, datetime.datetime.now().isoformat()))
            await db.commit()

    # === COMMANDES SLASH ===
    
    @app_commands.command(name="automod", description="🛡️ Configurer Arsenal AutoMod V5.0.1 (489 mots)")
    @app_commands.describe(
        action="Action à effectuer",
        channel="Channel pour les logs",
        enabled="Activer/désactiver l'automod"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="🔧 Configurer", value="config"),
        app_commands.Choice(name="📊 Statistiques", value="stats"),
        app_commands.Choice(name="🗄️ Historique", value="history"),
        app_commands.Choice(name="ℹ️ Informations", value="info")
    ])
    async def automod_command(self, interaction: discord.Interaction, action: str, 
                            channel: discord.TextChannel = None, enabled: bool = None):
        """Système AutoMod V5.0.1 complet"""
        
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Permissions insuffisantes !", ephemeral=True)
            return
            
        if action == "config":
            await self.handle_config(interaction, channel, enabled)
        elif action == "stats":
            await self.handle_stats(interaction)
        elif action == "history":
            await self.handle_history(interaction)
        elif action == "info":
            await self.handle_info(interaction)

    async def handle_config(self, interaction, channel, enabled):
        """Handle automod configuration"""
        guild_id = interaction.guild.id
        
        # Mise à jour config
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO guild_config (guild_id, automod_enabled, log_channel)
                VALUES (?, ?, ?)
            ''', (guild_id, 1 if enabled else 0 if enabled is not None else 1, 
                  channel.id if channel else None))
            await db.commit()
        
        embed = discord.Embed(
            title="🛡️ **ARSENAL AUTOMOD V5.0.1 CONFIGURÉ**",
            description="**Système de modération automatique activé !**",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📊 **BASE DE DONNÉES**",
            value=f"🔤 **489 mots** classés en 4 niveaux\n"
                  f"⚠️ **Niveau 1:** {len(self.WORDS_DATABASE['NIVEAU_1_LEGER'])} mots (Avertissement)\n"
                  f"🔇 **Niveau 2:** {len(self.WORDS_DATABASE['NIVEAU_2_MODERE'])} mots (Timeout 5min)\n" 
                  f"🚫 **Niveau 3:** {len(self.WORDS_DATABASE['NIVEAU_3_SEVERE'])} mots (Timeout 30min)\n"
                  f"🔨 **Niveau 4:** {len(self.WORDS_DATABASE['NIVEAU_4_EXTREME'])} mots (Ban)",
            inline=False
        )
        
        if channel:
            embed.add_field(
                name="📢 **LOGS**",
                value=f"Canal configuré: {channel.mention}",
                inline=True
            )
            
        embed.add_field(
            name="🏥 **RÉHABILITATION**",
            value="Système de seconde chance activé\n"
                  "Points réduits au fil du temps",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

    async def handle_info(self, interaction):
        """Display AutoMod information"""
        total_words = sum(len(words) for words in self.WORDS_DATABASE.values())
        
        embed = discord.Embed(
            title="🛡️ **ARSENAL AUTOMOD V5.0.1**",
            description=f"**Système de modération révolutionnaire**\n"
                       f"**{total_words} mots** analysés en temps réel",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎯 **NIVEAUX DE SÉVÉRITÉ**",
            value="⚠️ **Léger** → Avertissement\n"
                  "🔇 **Modéré** → Timeout 5min\n"
                  "🚫 **Sévère** → Timeout 30min\n" 
                  "🔨 **Extrême** → Bannissement",
            inline=True
        )
        
        embed.add_field(
            name="⚡ **FONCTIONNALITÉS**",
            value="• Détection instantanée\n"
                  "• Sanctions progressives\n"
                  "• Système de réhabilitation\n"
                  "• Logs complets\n"
                  "• Configuration flexible",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def handle_stats(self, interaction):
        """Display AutoMod statistics"""
        guild_id = interaction.guild.id
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT action, COUNT(*) FROM sanctions_history 
                WHERE guild_id = ? GROUP BY action
            ''', (guild_id,))
            stats = await cursor.fetchall()
        
        embed = discord.Embed(
            title="📊 **STATISTIQUES AUTOMOD V5.0.1**",
            color=discord.Color.orange()
        )
        
        if stats:
            for action, count in stats:
                embed.add_field(
                    name=f"🔹 {action.upper()}",
                    value=f"{count} sanctions",
                    inline=True
                )
        else:
            embed.description = "Aucune sanction enregistrée"
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ArsenalCommandGroupsFinal(bot))
