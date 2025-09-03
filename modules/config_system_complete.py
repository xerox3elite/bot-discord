"""
Arsenal Config System Complete V4.5.2
Système de configuration unifié avec toutes les permissions
"""

import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import json
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class ConfigDatabase:
    """Base de données configuration complète"""
    
    def __init__(self, db_path: str = "arsenal_config_complete.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS guild_settings (
                    guild_id INTEGER PRIMARY KEY,
                    economy_enabled INTEGER DEFAULT 1,
                    economy_daily_amount INTEGER DEFAULT 100,
                    economy_channels TEXT,
                    level_enabled INTEGER DEFAULT 1,
                    level_xp_message INTEGER DEFAULT 15,
                    level_xp_voice INTEGER DEFAULT 5,
                    level_bonus INTEGER DEFAULT 50,
                    level_roles TEXT,
                    automod_enabled INTEGER DEFAULT 1,
                    automod_delete_bad_words INTEGER DEFAULT 1,
                    automod_timeout_duration INTEGER DEFAULT 300,
                    automod_custom_words TEXT,
                    tickets_enabled INTEGER DEFAULT 1,
                    tickets_category_id INTEGER,
                    tickets_log_channel INTEGER,
                    sanctions_enabled INTEGER DEFAULT 1,
                    sanctions_log_channel INTEGER,
                    welcome_enabled INTEGER DEFAULT 0,
                    welcome_channel INTEGER,
                    welcome_message TEXT,
                    logs_enabled INTEGER DEFAULT 1,
                    logs_channel INTEGER,
                    prefix TEXT DEFAULT "!",
                    language TEXT DEFAULT "fr",
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info("✅ Base de données Config Complete initialisée")
            
        except Exception as e:
            logger.error(f"Erreur init config database: {e}")
    
    def get_guild_settings(self, guild_id: int) -> Dict[str, Any]:
        """Récupère les paramètres du serveur"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM guild_settings WHERE guild_id = ?", (guild_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return dict(result)
            else:
                self.create_guild_settings(guild_id)
                return self.get_guild_settings(guild_id)
                
        except Exception as e:
            logger.error(f"Erreur get_guild_settings: {e}")
            return {}
    
    def create_guild_settings(self, guild_id: int):
        """Crée les paramètres par défaut"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("INSERT OR IGNORE INTO guild_settings (guild_id) VALUES (?)", (guild_id,))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur create_guild_settings: {e}")
    
    def update_setting(self, guild_id: int, setting: str, value: Any):
        """Met à jour un paramètre"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Sécurité SQL injection
            allowed_settings = [
                'economy_enabled', 'economy_daily_amount', 'economy_channels',
                'level_enabled', 'level_xp_message', 'level_xp_voice', 'level_bonus', 'level_roles',
                'automod_enabled', 'automod_delete_bad_words', 'automod_timeout_duration', 'automod_custom_words',
                'tickets_enabled', 'tickets_category_id', 'tickets_log_channel',
                'sanctions_enabled', 'sanctions_log_channel',
                'welcome_enabled', 'welcome_channel', 'welcome_message',
                'logs_enabled', 'logs_channel', 'prefix', 'language'
            ]
            
            if setting in allowed_settings:
                cursor.execute(f"""
                    UPDATE guild_settings 
                    SET {setting} = ?, updated_at = CURRENT_TIMESTAMP 
                    WHERE guild_id = ?
                """, (value, guild_id))
                
                conn.commit()
                conn.close()
                return True
            else:
                logger.warning(f"Paramètre non autorisé: {setting}")
                conn.close()
                return False
                
        except Exception as e:
            logger.error(f"Erreur update_setting: {e}")
            return False

class ConfigView(discord.ui.View):
    """Interface de configuration interactive"""
    
    def __init__(self, guild_id: int, db: ConfigDatabase):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.db = db
    
    @discord.ui.select(
        placeholder="🔧 Choisir une catégorie de configuration...",
        options=[
            discord.SelectOption(label="💰 Économie", value="economy", description="Paramètres économiques"),
            discord.SelectOption(label="📈 Niveaux", value="levels", description="Système de niveaux"),
            discord.SelectOption(label="🛡️ AutoMod", value="automod", description="Modération automatique"),
            discord.SelectOption(label="🎫 Tickets", value="tickets", description="Système de tickets"),
            discord.SelectOption(label="⚖️ Sanctions", value="sanctions", description="Système de sanctions"),
            discord.SelectOption(label="👋 Welcome", value="welcome", description="Messages de bienvenue"),
            discord.SelectOption(label="📝 Logs", value="logs", description="Logs du serveur")
        ]
    )
    async def config_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        category = select.values[0]
        settings = self.db.get_guild_settings(self.guild_id)
        
        embed = discord.Embed(title=f"🔧 Configuration - {select.options[[opt.value for opt in select.options].index(category)].label}")
        
        if category == "economy":
            embed.add_field(name="💰 Économie activée", value="✅ Oui" if settings.get('economy_enabled') else "❌ Non", inline=True)
            embed.add_field(name="💵 Montant daily", value=f"{settings.get('economy_daily_amount', 100)} coins", inline=True)
            embed.add_field(name="📍 Salons économie", value=settings.get('economy_channels') or "Tous", inline=False)
        
        elif category == "levels":
            embed.add_field(name="📈 Niveaux activés", value="✅ Oui" if settings.get('level_enabled') else "❌ Non", inline=True)
            embed.add_field(name="💬 XP par message", value=f"{settings.get('level_xp_message', 15)} XP", inline=True)
            embed.add_field(name="🎤 XP vocal/min", value=f"{settings.get('level_xp_voice', 5)} XP", inline=True)
            embed.add_field(name="🎁 Bonus level up", value=f"{settings.get('level_bonus', 50)} coins", inline=True)
        
        elif category == "automod":
            embed.add_field(name="🛡️ AutoMod activé", value="✅ Oui" if settings.get('automod_enabled') else "❌ Non", inline=True)
            embed.add_field(name="🗑️ Supprimer mots interdits", value="✅ Oui" if settings.get('automod_delete_bad_words') else "❌ Non", inline=True)
            embed.add_field(name="⏰ Timeout (sec)", value=f"{settings.get('automod_timeout_duration', 300)}s", inline=True)
        
        elif category == "tickets":
            embed.add_field(name="🎫 Tickets activés", value="✅ Oui" if settings.get('tickets_enabled') else "❌ Non", inline=True)
            cat_id = settings.get('tickets_category_id')
            embed.add_field(name="📂 Catégorie", value=f"<#{cat_id}>" if cat_id else "Non définie", inline=True)
            log_id = settings.get('tickets_log_channel')
            embed.add_field(name="📋 Salon logs", value=f"<#{log_id}>" if log_id else "Non défini", inline=True)
        
        elif category == "sanctions":
            embed.add_field(name="⚖️ Sanctions activées", value="✅ Oui" if settings.get('sanctions_enabled') else "❌ Non", inline=True)
            log_id = settings.get('sanctions_log_channel')
            embed.add_field(name="📋 Salon logs", value=f"<#{log_id}>" if log_id else "Non défini", inline=True)
        
        elif category == "welcome":
            embed.add_field(name="👋 Welcome activé", value="✅ Oui" if settings.get('welcome_enabled') else "❌ Non", inline=True)
            chan_id = settings.get('welcome_channel')
            embed.add_field(name="📍 Salon welcome", value=f"<#{chan_id}>" if chan_id else "Non défini", inline=True)
            embed.add_field(name="💬 Message", value=settings.get('welcome_message') or "Message par défaut", inline=False)
        
        elif category == "logs":
            embed.add_field(name="📝 Logs activés", value="✅ Oui" if settings.get('logs_enabled') else "❌ Non", inline=True)
            log_id = settings.get('logs_channel')
            embed.add_field(name="📍 Salon logs", value=f"<#{log_id}>" if log_id else "Non défini", inline=True)
        
        embed.set_footer(text="Utilisez /config set <paramètre> <valeur> pour modifier")
        await interaction.response.edit_message(embed=embed, view=self)

class ConfigCog(commands.Cog):
    """Cog configuration complète"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = ConfigDatabase()
    
    def check_permissions(self, interaction: discord.Interaction) -> bool:
        """Vérifie les permissions admin"""
        return interaction.user.guild_permissions.administrator or interaction.user.id == interaction.guild.owner_id
    
    @app_commands.command(name="config", description="🔧 Configuration complète du serveur")
    async def config_main(self, interaction: discord.Interaction):
        """Menu principal de configuration"""
        if not self.check_permissions(interaction):
            embed = discord.Embed(
                title="❌ Permissions insuffisantes",
                description="Vous devez être administrateur pour utiliser cette commande.",
                color=0xFF0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔧 Configuration Arsenal",
            description="Sélectionnez une catégorie pour configurer votre serveur.",
            color=0x3498DB
        )
        embed.add_field(name="💰 Économie", value="Gérer l'économie du serveur", inline=True)
        embed.add_field(name="📈 Niveaux", value="Système de niveaux et XP", inline=True)  
        embed.add_field(name="🛡️ AutoMod", value="Modération automatique", inline=True)
        embed.add_field(name="🎫 Tickets", value="Système de support", inline=True)
        embed.add_field(name="⚖️ Sanctions", value="Gestion des sanctions", inline=True)
        embed.add_field(name="👋 Welcome", value="Messages de bienvenue", inline=True)
        
        view = ConfigView(interaction.guild.id, self.db)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="config-set", description="🔧 Modifier un paramètre")
    @app_commands.describe(
        setting="Nom du paramètre à modifier",
        value="Nouvelle valeur"
    )
    async def config_set(self, interaction: discord.Interaction, setting: str, value: str):
        """Modifie un paramètre de configuration"""
        if not self.check_permissions(interaction):
            await interaction.response.send_message("❌ Permissions insuffisantes", ephemeral=True)
            return
        
        # Conversion des valeurs
        converted_value = value
        
        # Booleans
        if value.lower() in ['true', 'on', '1', 'oui', 'yes']:
            converted_value = 1
        elif value.lower() in ['false', 'off', '0', 'non', 'no']:
            converted_value = 0
        # Nombres
        elif value.isdigit():
            converted_value = int(value)
        # Channel mentions
        elif value.startswith('<#') and value.endswith('>'):
            try:
                converted_value = int(value[2:-1])
            except:
                pass
        
        success = self.db.update_setting(interaction.guild.id, setting, converted_value)
        
        if success:
            embed = discord.Embed(
                title="✅ Paramètre mis à jour",
                description=f"**{setting}** = `{value}`",
                color=0x00FF00
            )
        else:
            embed = discord.Embed(
                title="❌ Erreur",
                description="Paramètre introuvable ou valeur invalide.",
                color=0xFF0000
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    """Setup function"""
    await bot.add_cog(ConfigCog(bot))
    logger.info("✅ Arsenal Config System Complete V4.5.2 chargé")

async def teardown(bot: commands.Bot):
    """Teardown function"""
    logger.info("🔄 Arsenal Config System Complete déchargé")
