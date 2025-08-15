import discord
from discord.ext import commands, tasks
import asyncio, os, sys, json, datetime, threading
from dotenv import load_dotenv

print(f"[DEBUG] Python path: {sys.path}")
print(f"[DEBUG] Working directory: {os.getcwd()}")
print(f"[DEBUG] Files in current dir: {os.listdir('.')[:10]}")

# Core config & logs
try:
    from core.logger import log
    print("[OK] [DEBUG] core.logger importé")
except Exception as e:
    print(f"[ERROR] [DEBUG] Erreur import core.logger: {e}")
    # Fallback logger
    import logging
    log = logging.getLogger(__name__)

try:
    from manager.config_manager import config_data, load_config, save_config
    print("[OK] [DEBUG] manager.config_manager importé")
except Exception as e:
    print(f"[ERROR] [DEBUG] Erreur import manager.config_manager: {e}")
    # Fallback config

# Import du système de statut
try:
    from core.status_loop import ArsenalStatusLoop
    print("[OK] [DEBUG] core.status_loop importé")
except Exception as e:
    print(f"[ERROR] [DEBUG] Erreur import core.status_loop: {e}")
    config_data = {}
    def load_config(): return {}
    def save_config(data): pass

def update_bot_status():
    """Met à jour le fichier de statut du bot pour l'API"""
    try:
        if hasattr(client, 'user') and client.user and client.is_ready():
            uptime_seconds = (datetime.datetime.now(datetime.UTC) - client.startup_time).total_seconds()
            hours = int(uptime_seconds // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            uptime = f"{hours}h {minutes}m"
            
            status_data = {
                "online": True,
                "uptime": uptime,
                "latency": round(client.latency * 1000) if client.latency else 0,
                "servers_connected": len(client.guilds),
                "users_connected": sum(guild.member_count or 0 for guild in client.guilds),
                "status": "operational",
                "last_restart": client.startup_time.strftime("%H:%M:%S"),
                "last_update": datetime.datetime.now(datetime.UTC).isoformat()
            }
        else:
            status_data = {
                "online": False,
                "uptime": "0h 0m",
                "latency": 0,
                "servers_connected": 0,
                "users_connected": 0,
                "status": "offline",
                "last_restart": "Jamais",
                "last_update": datetime.datetime.now(datetime.UTC).isoformat()
            }
        
        with open('bot_status.json', 'w') as f:
            json.dump(status_data, f, indent=2)
        
    except Exception as e:
        print(f"[ERROR] Erreur update_bot_status: {e}")

# Système de rechargement de modules (NOUVEAU)
try:
    from core.module_reloader import ReloaderCommands, reload_group
    RELOADER_AVAILABLE = True
    print("[OK] Système de rechargement de modules chargé")
except Exception as e:
    RELOADER_AVAILABLE = False
    print(f"[WARNING] Système de rechargement non disponible: {e}")

# Modules Hunt Royal et Suggestions (NOUVEAU)
try:
    from modules.hunt_royal_system import HuntRoyalCommands
    from modules.suggestions_system import SuggestionsCommands
    HUNT_ROYAL_AVAILABLE = True
    SUGGESTIONS_AVAILABLE = True
    print("[OK] Modules Hunt Royal et Suggestions chargés")
except Exception as e:
    HUNT_ROYAL_AVAILABLE = False
    SUGGESTIONS_AVAILABLE = False
    print(f"[WARNING] Modules Hunt Royal/Suggestions non disponibles: {e}")

# Managers système & extension
from manager.voice_manager import restore_voice_channels
from manager.terminal_manager import start_terminal
from manager.memory_manager import memoire

# Setup audio
from commands.music import setup_audio

# Arsenal Status System (NOUVEAU)
from manager.status_manager import initialize_status_system

# Modules de commandes
import commands.creator_tools as creator
# import commands.community as community  # Maintenant géré par le Cog CommunityCommands
import commands.admin as admin
import commands.moderateur as moderateur
import commands.sanction as sanction
import commands.music as music

# WebPanel Integration Commands (NOUVEAU)
try:
    from commands.webpanel_integration import WebPanelCommands
    WEBPANEL_COMMANDS_AVAILABLE = True
    print("[OK] WebPanel Integration Commands chargé")
except Exception as e:
    WEBPANEL_COMMANDS_AVAILABLE = False

# Bot Migration System (RÉVOLUTIONNAIRE)
try:
    from commands.bot_migration_system import BotMigrationSystem
    BOT_MIGRATION_AVAILABLE = True
    print("🚀 [OK] Bot Migration System chargé - Système révolutionnaire!")
except Exception as e:
    BOT_MIGRATION_AVAILABLE = False
    print(f"❌ [ERREUR] Bot Migration System: {e}")
    print(f"[ERROR] Erreur import WebPanel Commands: {e}")

# Advanced Bot Features (NOUVEAU)
try:
    from commands.advanced_features import AdvancedBotFeatures
    ADVANCED_FEATURES_AVAILABLE = True
    print("[OK] Advanced Bot Features chargé")
except Exception as e:
    ADVANCED_FEATURES_AVAILABLE = False
    print(f"[ERROR] Erreur import Advanced Features: {e}")

# Hunt Royal Auth System (NOUVEAU)
try:
    import commands.hunt_royal_auth as hunt_auth
    HUNT_AUTH_AVAILABLE = True
    print("[OK] Hunt Royal Auth System chargé")
except Exception as e:
    HUNT_AUTH_AVAILABLE = False
    print(f"[WARNING] Hunt Royal Auth non disponible: {e}")

# Hunt Royal Profiles System (NOUVEAU)
try:
    import commands.hunt_royal_profiles as hunt_profiles
    HUNT_PROFILES_AVAILABLE = True
    print("[OK] Hunt Royal Profiles System chargé")
except Exception as e:
    HUNT_PROFILES_AVAILABLE = False
    print(f"[WARNING] Hunt Royal Profiles non disponible: {e}")

# Hunt Royal Integration System (NOUVEAU V4)
try:
    import commands.hunt_royal_integration as hunt_integration
    HUNT_INTEGRATION_AVAILABLE = True
    print("[OK] Hunt Royal Integration System chargé")
except Exception as e:
    HUNT_INTEGRATION_AVAILABLE = False
    print(f"[WARNING] Hunt Royal Integration non disponible: {e}")

# Server Management System (NOUVEAU V4.3)
try:
    import commands.server_management_system as server_management
    SERVER_MANAGEMENT_AVAILABLE = True
    print("[OK] Server Management System chargé")
except Exception as e:
    SERVER_MANAGEMENT_AVAILABLE = False
    print(f"[WARNING] Server Management System non disponible: {e}")

# Gaming API System (NOUVEAU V4.3)
try:
    import commands.gaming_api_system as gaming_api
    GAMING_API_AVAILABLE = True
    print("[OK] Gaming API System chargé")
except Exception as e:
    GAMING_API_AVAILABLE = False
    print(f"[WARNING] Gaming API System non disponible: {e}")

# Social Fun System (NOUVEAU V4.3)
try:
    import commands.social_fun_system as social_fun
    SOCIAL_FUN_AVAILABLE = True
    print("[OK] Social Fun System chargé")
except Exception as e:
    SOCIAL_FUN_AVAILABLE = False
    print(f"[WARNING] Social Fun System non disponible: {e}")

# Enhanced Music System (NOUVEAU V4.3)
try:
    import commands.music_enhanced_system as music_enhanced
    MUSIC_ENHANCED_AVAILABLE = True
    print("[OK] Enhanced Music System chargé")
except Exception as e:
    MUSIC_ENHANCED_AVAILABLE = False
    print(f"[WARNING] Enhanced Music System non disponible: {e}")

# Crypto System Integration (NOUVEAU V4.2)
try:
    from modules.crypto_bot_integration import setup_crypto
    CRYPTO_INTEGRATION_AVAILABLE = True
    print("[OK] Crypto System Integration chargé")
except Exception as e:
    CRYPTO_INTEGRATION_AVAILABLE = False
    print(f"[WARNING] Crypto System Integration non disponible: {e}")

# SQLite Database Manager (NOUVEAU V4.5)
try:
    from modules.sqlite_database import database_manager
    SQLITE_DATABASE_AVAILABLE = True
    print("[OK] SQLite Database Manager chargé")
except Exception as e:
    SQLITE_DATABASE_AVAILABLE = False
    print(f"⚠️ Module sqlite_database non trouvé: {e}")

# Panneau Creator GUI (Tkinter)
# # from gui. - GUI removed for production - GUI removed for productionArsenalCreatorStudio import lancer_creator_interface

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CREATOR_ID = int(os.getenv("CREATOR_ID", 431359112039890945))
PREFIX = os.getenv("PREFIX", "!")

# Vérification du token Discord
print("[INFO] Vérification des variables d'environnement...")
print(f"TOKEN présent: {'[OK] Oui' if TOKEN else '[ERROR] NON'}")
print(f"CREATOR_ID: {CREATOR_ID}")
print(f"PREFIX: {PREFIX}")

if not TOKEN:
    print("[ERROR] CRITIQUE: DISCORD_TOKEN manquant dans les variables d'environnement!")
    print("[INFO] Ajoutez DISCORD_TOKEN sur Render avec votre token de bot Discord")
    sys.exit(1)

intents = discord.Intents.all()

# Tâche de mise à jour du statut bot
@tasks.loop(seconds=30)
async def update_bot_status_task():
    """Met à jour le fichier de statut toutes les 30 secondes"""
    update_bot_status()

class ArsenalBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_system = None
        
    async def setup_hook(self):
        # Initialise le système de statut Arsenal
        self.status_system = initialize_status_system(self)
        print("🔄 [STATUS] Système de statut Arsenal initialisé")
        self.loop.create_task(restore_voice_channels(self))
        self.loop.create_task(start_terminal(self))
        # Démarre les systèmes de statut Arsenal
        await self.status_system.start_status_rotation()
        await self.status_system.start_keepalive()
        setup_audio(self)
        
        # Charger le système de rechargement de modules
        if RELOADER_AVAILABLE:
            try:
                await self.add_cog(ReloaderCommands(self))
                log.info("[OK] Système de rechargement de modules chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement reloader: {e}")
        
        # Charger Hunt Royal et Suggestions
        if HUNT_ROYAL_AVAILABLE:
            try:
                await self.add_cog(HuntRoyalCommands(self))
                log.info("[OK] Module Hunt Royal chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Hunt Royal: {e}")
        
        if SUGGESTIONS_AVAILABLE:
            try:
                await self.add_cog(SuggestionsCommands(self))
                log.info("[OK] Module Suggestions chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Suggestions: {e}")
        
        # Charger Hunt Royal Integration
        if HUNT_INTEGRATION_AVAILABLE:
            try:
                await self.add_cog(hunt_integration.HuntRoyalIntegration(self))
                log.info("[OK] Module Hunt Royal Integration chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Hunt Royal Integration: {e}")
        
        # Charger Crypto System Integration
        if CRYPTO_INTEGRATION_AVAILABLE:
            try:
                self.crypto_integration = setup_crypto_integration(self)
                log.info("[OK] Module Crypto System Integration chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Crypto System Integration: {e}")
        
        # Charger WebPanel Integration Commands
        if WEBPANEL_COMMANDS_AVAILABLE:
            try:
                await self.add_cog(WebPanelCommands(self))
                log.info("[OK] Module WebPanel Integration Commands chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement WebPanel Commands: {e}")
        
        # Charger Advanced Bot Features
        if ADVANCED_FEATURES_AVAILABLE:
            try:
                await self.add_cog(AdvancedBotFeatures(self))
                log.info("[OK] Module Advanced Bot Features chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Advanced Features: {e}")
        
        # Charger Server Management System
        if SERVER_MANAGEMENT_AVAILABLE:
            try:
                await self.add_cog(server_management.ServerManagementSystem(self))
                log.info("[OK] Module Server Management System chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Server Management: {e}")
        
        # Charger Gaming API System
        if GAMING_API_AVAILABLE:
            try:
                await self.add_cog(gaming_api.GamingAPISystem(self))
                log.info("[OK] Module Gaming API System chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Gaming API: {e}")
        
        # Charger Social Fun System
        if SOCIAL_FUN_AVAILABLE:
            try:
                await self.add_cog(social_fun.SocialFunSystem(self))
                log.info("[OK] Module Social Fun System chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Social Fun: {e}")
        
        # Charger Enhanced Music System
        if MUSIC_ENHANCED_AVAILABLE:
            try:
                await self.add_cog(music_enhanced.EnhancedMusicSystem(self))
                log.info("[OK] Module Enhanced Music System chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Enhanced Music: {e}")
        
        # Charger Arsenal Economy System (NOUVEAU V4.5) avec Configuration Moderne
        if ARSENAL_ECONOMY_AVAILABLE:
            try:
                await self.add_cog(ArsenalEconomySystem(self))
                await self.add_cog(ArsenalShopAdmin(self))
                # NOUVEAU: Configuration moderne avec MODALS au lieu de menus superficiels
                from commands.config_modal_system import ArsenalConfigSystemModal
                await self.add_cog(ArsenalConfigSystemModal(self))
                await self.add_cog(ArsenalUpdateNotifier(self))
                log.info("[OK] Arsenal Economy, Shop, Config Modal Moderne & Update Notifier System chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Arsenal Economy: {e}")
                
            # Bot Migration System - Révolutionnaire
            if BOT_MIGRATION_AVAILABLE:
                try:
                    await self.add_cog(BotMigrationSystem(self))
                    log.info("🚀 [OK] Bot Migration System - Système révolutionnaire de récupération de configs d'autres bots!")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement Bot Migration System: {e}")
            else:
                log.warning("[WARNING] Bot Migration System non disponible")
                
            # Migration Help System
            try:
                from commands.migration_help import MigrationHelp
                await self.add_cog(MigrationHelp(self))
                log.info("📚 [OK] Migration Help System - Guide interactif de migration!")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Migration Help: {e}")
                
            # Arsenal Features System - Affichage complet des fonctionnalités
            try:
                from commands.arsenal_features import ArsenalBotFeatures
                await self.add_cog(ArsenalBotFeatures(self))
                log.info("🌟 [OK] Arsenal Features System - Toutes les fonctionnalités Discord natives!")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Arsenal Features: {e}")
                
            # Arsenal Profile Updater - Mise à jour auto du profil
            try:
                from commands.arsenal_profile_updater import ArsenalProfileUpdater
                await self.add_cog(ArsenalProfileUpdater(self))
                log.info("🎯 [OK] Arsenal Profile Updater - Profil Discord auto-optimisé!")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Profile Updater: {e}")
                
            # Arsenal Context Menus - Menus contextuels (clic droit)
            try:
                from commands.arsenal_context_menus import ArsenalContextMenus
                await self.add_cog(ArsenalContextMenus(self))
                log.info("🖱️ [OK] Arsenal Context Menus - Menus contextuels natifs Discord!")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Context Menus: {e}")

client = ArsenalBot(command_prefix=PREFIX, intents=intents)
client.startup_time = datetime.datetime.now(datetime.timezone.utc)
client.command_usage = {}

@client.event
async def on_ready():
    log.info(f"[START] Arsenal Studio lancé comme {client.user.name}")
    
    # Définir le statut streaming par défaut AVANT tout
    try:
        activity = discord.Streaming(
            name="Arsenal V4.5.1 | /help", 
            url="https://twitch.tv/xerox3elite"
        )
        await client.change_presence(activity=activity)
        log.info("💜 [STATUS] Statut streaming défini par défaut")
    except Exception as e:
        log.error(f"❌ [STATUS] Erreur définition statut: {e}")
    
    try:
        await client.tree.sync()
        log.info(f"[SYNC] Commandes Slash synchronisées.")
        
        # Le système de statut Arsenal démarre automatiquement via setup_hook()
        if hasattr(client, 'status_system') and client.status_system:
            log.info("[STATUS] Système de statut Arsenal actif")
        
        # Démarre la mise à jour du statut du bot
        try:
            update_bot_status_task.start()
        except:
            pass  # Task déjà démarrée
            
    except Exception as e:
        log.error(f"[SYNC ERROR] {e}")

# Imports modules
client.tree.add_command(moderateur.moderator_group)
client.tree.add_command(admin.admin_group)
client.tree.add_command(creator.creator_group)
client.tree.add_command(sanction.sanction_group)
client.tree.add_command(creator.creator_tools_group)

# Individuelles - Les commandes community sont maintenant gérées par le Cog CommunityCommands

# Hunt Royal Auth Commands (NOUVEAU)
if HUNT_AUTH_AVAILABLE:
    client.tree.add_command(hunt_auth.register_hunt_royal)
    client.tree.add_command(hunt_auth.get_my_token)
    client.tree.add_command(hunt_auth.hunt_royal_stats)

# Hunt Royal Profile Commands (NOUVEAU)
if HUNT_PROFILES_AVAILABLE:
    client.tree.add_command(hunt_profiles.link_hunt_royal)
    client.tree.add_command(hunt_profiles.profile_hunt_royal)
    client.tree.add_command(hunt_profiles.unlink_hunt_royal)

# Reload System Commands (NOUVEAU)
if RELOADER_AVAILABLE:
    client.tree.add_command(reload_group)

# Arsenal Economy System (NOUVEAU V4.5)
try:
    from commands.arsenal_economy_system import ArsenalEconomySystem
    from commands.arsenal_shop_admin import ArsenalShopAdmin
    from commands.arsenal_config_system import ArsenalConfigSystem
    from commands.arsenal_config_complete import ArsenalCompleteConfig
    from commands.arsenal_update_notifier import ArsenalUpdateNotifier
    ARSENAL_ECONOMY_AVAILABLE = True
    print("[OK] Arsenal Economy, Config, Arsenal Complete & Update Notifier System chargé")
except Exception as e:
    ARSENAL_ECONOMY_AVAILABLE = False
    print(f"[WARNING] Arsenal Economy System non disponible: {e}")

# Creator GUI Panel
def lancer_gui():
    try:
        lancer_creator_interface(client)
    except Exception as e:
        log.warning(f"[GUI ERROR] {e}")

# Lancement
if __name__ == "__main__":
    import threading
    
    # Démarrer serveur Flask health check en parallèle
    try:
        from health_server import start_health_server
        flask_thread = threading.Thread(target=start_health_server, daemon=True)
        flask_thread.start()
        log.info("[HEALTH] Serveur Flask démarré pour Render health checks")
    except Exception as e:
        log.warning(f"[HEALTH] Impossible de démarrer serveur Flask: {e}")
    
    # Démarrer GUI si disponible
    try:
        threading.Thread(target=lancer_gui, daemon=True).start()
    except:
        log.info("[GUI] Interface GUI désactivée en production")
    
    # Démarrer bot Discord
    try:
        client.run(TOKEN)
    except Exception as e:
        log.error(f"[RUN ERROR] {e}")
