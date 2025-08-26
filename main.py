import discord
from discord.ext import commands, tasks
import asyncio, os, sys, json, datetime, threading, traceback
from dotenv import load_dotenv

print(f"[DEBUG] Python path: {sys.path}")
print(f"[DEBUG] Working directory: {os.getcwd()}")
print(f"[DEBUG] Files in current dir: {os.listdir('.')[:10]}")

# Gestionnaire d'erreurs global pour éviter les crashes
async def handle_error(error, context="Unknown"):
    """Gestionnaire d'erreurs global"""
    try:
        error_msg = f"❌ [ERROR] {context}: {str(error)}"
        print(error_msg)
        traceback.print_exc()
        
        # Écrire dans les logs si possible
        try:
            with open("logs/error.log", "a", encoding="utf-8") as f:
                f.write(f"{datetime.datetime.now()}: {error_msg}\n{traceback.format_exc()}\n\n")
        except:
            pass
            
    except Exception as e:
        print(f"❌ [CRITICAL] Erreur dans le gestionnaire d'erreurs: {e}")

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
    """Met à jour le fichier de statut du bot pour l'API - Version sécurisée"""
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
                "users_total": sum(guild.member_count for guild in client.guilds if guild.member_count),
                "last_update": datetime.datetime.now(datetime.UTC).isoformat(),
                "bot_name": str(client.user) if client.user else "Arsenal Bot",
                "commands_loaded": len(client.cogs) if hasattr(client, 'cogs') else 0
            }
            
            # Sauvegarde sécurisée
            try:
                os.makedirs("data", exist_ok=True)
                with open("data/bot_status.json", "w", encoding="utf-8") as f:
                    json.dump(status_data, f, indent=2, ensure_ascii=False)
            except Exception as write_error:
                print(f"⚠️ [STATUS] Erreur écriture fichier: {write_error}")
        else:
            # Bot pas prêt
            offline_status = {
                "online": False,
                "uptime": "0h 0m",
                "latency": 0,
                "servers_connected": 0,
                "users_total": 0,
                "last_update": datetime.datetime.now(datetime.UTC).isoformat(),
                "bot_name": "Arsenal Bot",
                "commands_loaded": 0
            }
            
            try:
                os.makedirs("data", exist_ok=True)
                with open("data/bot_status.json", "w", encoding="utf-8") as f:
                    json.dump(offline_status, f, indent=2, ensure_ascii=False)
            except Exception as write_error:
                print(f"⚠️ [STATUS] Erreur écriture offline: {write_error}")
                
    except Exception as e:
        print(f"❌ [STATUS] Erreur générale update_bot_status: {e}")
        # En cas d'erreur, on crée un statut d'urgence
        try:
            emergency_status = {
                "online": False,
                "error": str(e),
                "last_update": datetime.datetime.now(datetime.UTC).isoformat()
            }
            os.makedirs("data", exist_ok=True)
            with open("data/bot_status.json", "w", encoding="utf-8") as f:
                json.dump(emergency_status, f, indent=2)
        except:
            pass  # Si même ça échoue, on abandonne silencieusement

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

# Setup audio - utilise le système avancé maintenant
try:
    from commands.music_system_advanced import setup_audio
except ImportError:
    print("[WARNING] Module audio avancé non disponible, utilisation du fallback")
    def setup_audio():
        pass

# Arsenal Status System (NOUVEAU)
from manager.status_manager import initialize_status_system

# Modules de commandes
# import commands.community as community  # Maintenant géré par le Cog CommunityCommands
# import commands.admin as admin  # DÉSACTIVÉ - Remplacé par ArsenalCommandGroupsFinal
import commands.moderateur as moderateur
import commands.sanction as sanction

# Import music avancé pour éviter l'erreur
try:
    import commands.music_system_advanced as music
    print("[OK] Music System Advanced chargé")
except ImportError:
    print("[WARNING] Music System non disponible")
    music = None

# WebPanel Integration Commands (NOUVEAU)
try:
    from commands.webpanel_integration import WebPanelCommands
    WEBPANEL_COMMANDS_AVAILABLE = True
    print("[OK] WebPanel Integration Commands chargé")
except Exception as e:
    WEBPANEL_COMMANDS_AVAILABLE = False

# Bot Migration System
try:
    from commands.bot_migration_system import BotMigrationSystem
    BOT_MIGRATION_AVAILABLE = True
    print("🚀 [OK] Bot Migration System chargé")
except Exception as e:
    BOT_MIGRATION_AVAILABLE = False
    print(f"❌ [ERREUR] Bot Migration System: {e}")
    print(f"[ERROR] Erreur import WebPanel Commands: {e}")

# Advanced Bot Features
try:
    from commands.advanced_features import AdvancedBotFeatures
    ADVANCED_FEATURES_AVAILABLE = True
    print("[OK] Advanced Bot Features chargé")
except Exception as e:
    ADVANCED_FEATURES_AVAILABLE = False
    print(f"[ERROR] Erreur import Advanced Features: {e}")

# Arsenal Features System
try:
    from commands.arsenal_features import ArsenalBotFeatures
    ARSENAL_FEATURES_AVAILABLE = True
    print("🚀 [OK] Arsenal Features System chargé")
except Exception as e:
    ARSENAL_FEATURES_AVAILABLE = False
    print(f"❌ [ERREUR] Arsenal Features System: {e}")

# Arsenal Config Revolution (V2.0)
try:
    from commands.config_revolution import ArsenalConfigRevolution
    ARSENAL_CONFIG_REVOLUTION_AVAILABLE = True
    print("🚀 [OK] Arsenal Config Revolution chargé")
except Exception as e:
    ARSENAL_CONFIG_REVOLUTION_AVAILABLE = False
    print(f"❌ [ERREUR] Arsenal Config Revolution: {e}")

# L'ancien module "Arsenal Config Ultimate" est maintenant unifié dans /config
ARSENAL_CONFIG_ULTIMATE_AVAILABLE = False

# Arsenal Profile Ultimate
try:
    from commands.arsenal_profile_ultimate import ArsenalProfileUltimate  
    ARSENAL_PROFILE_ULTIMATE_AVAILABLE = True
    print("💎 [OK] Arsenal Profile Ultimate chargé")
except Exception as e:
    ARSENAL_PROFILE_ULTIMATE_AVAILABLE = False
    print(f"❌ [ERREUR] Arsenal Profile Ultimate: {e}")

# Discord Badges System
try:
    from core.discord_badges import DiscordBadges
    DISCORD_BADGES_AVAILABLE = True
    print("🏆 [OK] Discord Badges System chargé")
except Exception as e:
    DISCORD_BADGES_AVAILABLE = False
    print(f"❌ [ERREUR] Discord Badges System: {e}")

# Arsenal Diagnostic System
try:
    from commands.arsenal_diagnostic import ArsenalDiagnostic
    ARSENAL_DIAGNOSTIC_AVAILABLE = True
    print("🔧 [OK] Arsenal Diagnostic System chargé")
except Exception as e:
    ARSENAL_DIAGNOSTIC_AVAILABLE = False
    print(f"❌ [ERREUR] Arsenal Diagnostic System: {e}")

# Hunt Royal Auth System
try:
    import commands.hunt_royal_auth as hunt_auth
    HUNT_AUTH_AVAILABLE = True
    print("[OK] Hunt Royal Auth System chargé")
except Exception as e:
    HUNT_AUTH_AVAILABLE = False
    print(f"[WARNING] Hunt Royal Auth non disponible: {e}")

# Hunt Royal Profiles System
try:
    import commands.hunt_royal_profiles as hunt_profiles
    HUNT_PROFILES_AVAILABLE = True
    print("[OK] Hunt Royal Profiles System chargé")
except Exception as e:
    HUNT_PROFILES_AVAILABLE = False
    print(f"[WARNING] Hunt Royal Profiles non disponible: {e}")

# Hunt Royal Integration System
try:
    import commands.hunt_royal_integration as hunt_integration
    HUNT_INTEGRATION_AVAILABLE = True
    print("[OK] Hunt Royal Integration System chargé")
except Exception as e:
    HUNT_INTEGRATION_AVAILABLE = False
    print(f"[WARNING] Hunt Royal Integration non disponible: {e}")

# Server Management System
try:
    import commands.server_management_system as server_management
    SERVER_MANAGEMENT_AVAILABLE = True
    print("[OK] Server Management System chargé")
except Exception as e:
    SERVER_MANAGEMENT_AVAILABLE = False
    print(f"[WARNING] Server Management System non disponible: {e}")

# Gaming API System
try:
    import commands.gaming_api_system as gaming_api
    GAMING_API_AVAILABLE = True
    print("[OK] Gaming API System chargé")
except Exception as e:
    GAMING_API_AVAILABLE = False
    print(f"[WARNING] Gaming API System non disponible: {e}")

# Absence Ticket System
try:
    from commands.absence_tickets import AbsenceTicketSystem
    from commands.absence_config import setup_absence_config_db
    ABSENCE_SYSTEM_AVAILABLE = True
    print("🎫 [OK] Absence Ticket System chargé")
except Exception as e:
    ABSENCE_SYSTEM_AVAILABLE = False
    print(f"❌ [ERREUR] Absence Ticket System: {e}")

# Social Fun System
try:
    import commands.social_fun_system as social_fun
    SOCIAL_FUN_AVAILABLE = True
    print("[OK] Social Fun System chargé")
except Exception as e:
    SOCIAL_FUN_AVAILABLE = False
    print(f"[WARNING] Social Fun System non disponible: {e}")

# Enhanced Music System
try:
    import commands.music_enhanced_system as music_enhanced
    MUSIC_ENHANCED_AVAILABLE = True
    print("[OK] Enhanced Music System chargé")
except Exception as e:
    MUSIC_ENHANCED_AVAILABLE = False
    print(f"[WARNING] Enhanced Music System non disponible: {e}")

# Crypto System Integration
try:
    from modules.crypto_bot_integration import setup
    CRYPTO_INTEGRATION_AVAILABLE = True
    print("[OK] Crypto System Integration chargé")
except Exception as e:
    CRYPTO_INTEGRATION_AVAILABLE = False
    print(f"[WARNING] Crypto System Integration non disponible: {e}")

# SQLite Database Manager
try:
    from modules.sqlite_database import database_manager
    SQLITE_DATABASE_AVAILABLE = True
    print("[OK] SQLite Database Manager chargé")
except Exception as e:
    SQLITE_DATABASE_AVAILABLE = False
    print(f"⚠️ Module sqlite_database non trouvé: {e}")

# Sanctions System
try:
    from commands.sanctions_system import SanctionsSystem
    SANCTIONS_SYSTEM_AVAILABLE = True
    print("⚖️ [OK] Sanctions System chargé")
except Exception as e:
    SANCTIONS_SYSTEM_AVAILABLE = False
    print(f"❌ [ERREUR] Sanctions System: {e}")

# Complete Commands System
try:
    from commands.complete_commands_system import CompleteCommandsSystem
    COMPLETE_COMMANDS_SYSTEM_AVAILABLE = True
    print("📋 [OK] Complete Commands System chargé")
except Exception as e:
    COMPLETE_COMMANDS_SYSTEM_AVAILABLE = False
    print(f"❌ [ERREUR] Complete Commands System: {e}")

# Communication System
try:
    from commands.communication_system import CommunicationSystem
    COMMUNICATION_SYSTEM_AVAILABLE = True
    print("📢 [OK] Communication System chargé")
except Exception as e:
    COMMUNICATION_SYSTEM_AVAILABLE = False
    print(f"❌ [ERREUR] Communication System: {e}")

# Help System V2
try:
    from commands.help_system_v2 import HelpSystemV2
    HELP_SYSTEM_V2_AVAILABLE = True
    print("📚 [OK] Help System V2 chargé")
except Exception as e:
    HELP_SYSTEM_V2_AVAILABLE = False
    print(f"❌ [ERREUR] Help System V2: {e}")
    # Log plus détaillé pour debug
    import traceback
    print(f"[DEBUG] Help System V2 Traceback: {traceback.format_exc()}")

# Configuration
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

# Tâche de mise à jour du statut bot - Optimisée pour stabilité
@tasks.loop(minutes=2)  # Réduire à 2 minutes au lieu de 30 secondes
async def update_bot_status_task():
    """Met à jour le fichier de statut - Version stable"""
    try:
        update_bot_status()
    except Exception as e:
        print(f"⚠️ [STATUS] Erreur mise à jour statut: {e}")

class ArsenalBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_system = None
        
    async def setup_hook(self):
        # Initialiser et démarrer le nouveau système de statut
        self.status_system = initialize_status_system(self)
        self.loop.create_task(self.status_system.start_status_rotation())
        self.loop.create_task(self.status_system.start_keepalive())

        self.loop.create_task(restore_voice_channels(self))
        self.loop.create_task(start_terminal(self))
        setup_audio(self)
        
        # Charger le système de rechargement de modules
        if RELOADER_AVAILABLE:
            try:
                await self.add_cog(ReloaderCommands(self))
                log.info("[OK] Cog 'ReloaderCommands' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'ReloaderCommands': {e}")
        
        # Charger Hunt Royal et Suggestions
        if HUNT_ROYAL_AVAILABLE:
            try:
                await self.add_cog(HuntRoyalCommands(self))
                log.info("[OK] Cog 'HuntRoyalCommands' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'HuntRoyalCommands': {e}")
        
        if SUGGESTIONS_AVAILABLE:
            try:
                await self.add_cog(SuggestionsCommands(self))
                log.info("[OK] Cog 'SuggestionsCommands' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'SuggestionsCommands': {e}")
        
        # Charger Hunt Royal Integration
        if HUNT_INTEGRATION_AVAILABLE:
            try:
                await self.add_cog(hunt_integration.HuntRoyalIntegration(self))
                log.info("[OK] Cog 'HuntRoyalIntegration' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'HuntRoyalIntegration': {e}")
        
        # Charger Crypto System Integration
        if CRYPTO_INTEGRATION_AVAILABLE:
            try:
                self.crypto_integration = setup(self)
                log.info("[OK] Intégration 'Crypto System' chargée")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement intégration 'Crypto System': {e}")
        
        # Charger WebPanel Integration Commands
        if WEBPANEL_COMMANDS_AVAILABLE:
            try:
                await self.add_cog(WebPanelCommands(self))
                log.info("[OK] Cog 'WebPanelCommands' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'WebPanelCommands': {e}")
        
        # Charger Advanced Bot Features
        if ADVANCED_FEATURES_AVAILABLE:
            try:
                await self.add_cog(AdvancedBotFeatures(self))
                log.info("[OK] Cog 'AdvancedBotFeatures' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'AdvancedBotFeatures': {e}")
        
        # Charger Server Management System
        if SERVER_MANAGEMENT_AVAILABLE:
            try:
                await self.add_cog(server_management.ServerManagementSystem(self))
                log.info("[OK] Cog 'ServerManagementSystem' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'ServerManagementSystem': {e}")
        
        # Charger Gaming API System
        if GAMING_API_AVAILABLE:
            try:
                await self.add_cog(gaming_api.GamingAPISystem(self))
                log.info("[OK] Cog 'GamingAPISystem' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'GamingAPISystem': {e}")
        
        # Charger Social Fun System
        if SOCIAL_FUN_AVAILABLE:
            try:
                await self.add_cog(social_fun.SocialFunSystem(self))
                log.info("[OK] Cog 'SocialFunSystem' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'SocialFunSystem': {e}")
        
        # Charger Arsenal Config Revolution
        if ARSENAL_CONFIG_REVOLUTION_AVAILABLE:
            try:
                await self.add_cog(ArsenalConfigRevolution(self))
                log.info("[OK] Cog 'ArsenalConfigRevolution' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'ArsenalConfigRevolution': {e}")
        
        # Charger Enhanced Music System
        if MUSIC_ENHANCED_AVAILABLE:
            try:
                await self.add_cog(music_enhanced.EnhancedMusicSystem(self))
                log.info("[OK] Cog 'EnhancedMusicSystem' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'EnhancedMusicSystem': {e}")
        
        # Charger Arsenal Economy System
        if ARSENAL_ECONOMY_AVAILABLE:
            try:
                await self.add_cog(ArsenalEconomyUnified(self))
                await self.add_cog(ArsenalShopAdmin(self))
                await self.add_cog(ArsenalUpdateNotifier(self))
                log.info("[OK] Cogs 'ArsenalEconomyUnified', 'ArsenalShopAdmin', 'ArsenalUpdateNotifier' chargés")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cogs 'Arsenal Economy': {e}")
                
        # Arsenal AutoMod V5.0.1
        try:
            from commands.arsenal_automod_v5_fixed import ArsenalCommandGroupsFinalFixed
            await self.add_cog(ArsenalCommandGroupsFinalFixed(self))
            log.info("🛡️ [OK] Cog 'ArsenalAutoMod V5.0.1' chargé")
        except Exception as e:
            log.error(f"[ERROR] Erreur chargement cog 'ArsenalAutoMod V5.0.1': {e}")
            
        # Arsenal Bug Reporter
        try:
            from commands.arsenal_bug_reporter import ArsenalBugReporter
            await self.add_cog(ArsenalBugReporter(self))
            log.info("🐛 [OK] Cog 'ArsenalBugReporter' chargé")
        except Exception as e:
            log.error(f"[ERROR] Erreur chargement cog 'ArsenalBugReporter': {e}")
            
        # Arsenal Test Suite
        try:
            from commands.arsenal_test_suite import ArsenalTestSuite
            await self.add_cog(ArsenalTestSuite(self))
            log.info("🧪 [OK] Cog 'ArsenalTestSuite' chargé")
        except Exception as e:
            log.error(f"[ERROR] Erreur chargement cog 'ArsenalTestSuite': {e}")
                
            # Bot Migration System
            if BOT_MIGRATION_AVAILABLE:
                try:
                    await self.add_cog(BotMigrationSystem(self))
                    log.info("[OK] Cog 'BotMigrationSystem' chargé")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement cog 'BotMigrationSystem': {e}")
            else:
                log.warning("[WARNING] Cog 'BotMigrationSystem' non disponible")
                
            # Migration Help System
            try:
                from commands.migration_help import MigrationHelp
                await self.add_cog(MigrationHelp(self))
                log.info("[OK] Cog 'MigrationHelp' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'MigrationHelp': {e}")
                
            # Arsenal Features System
            try:
                from commands.arsenal_features import ArsenalBotFeatures
                await self.add_cog(ArsenalBotFeatures(self))
                log.info("[OK] Cog 'ArsenalBotFeatures' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'ArsenalBotFeatures': {e}")
                
            # Arsenal Config Ultimate
            try:
                from commands.arsenal_config_ultimate import ArsenalConfigUltimate
                await self.add_cog(ArsenalConfigUltimate(self))
                log.info("[OK] Cog 'ArsenalConfigUltimate' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'ArsenalConfigUltimate': {e}")
            
            # Règlement Intelligent
            try:
                from commands.reglement import ReglementSystem
                await self.add_cog(ReglementSystem(self))
                log.info("[OK] Cog 'ReglementSystem' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'ReglementSystem': {e}")
                
            # Hub Vocal
            try:
                from commands.hub_vocal import HubVocal
                await self.add_cog(HubVocal(self))
                log.info("[OK] Cog 'HubVocal' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'HubVocal': {e}")
                
            # Arsenal Profile Ultimate 2000%
            try:
                from commands.arsenal_profile_ultimate_2000 import ArsenalProfileUltimate2000
                await self.add_cog(ArsenalProfileUltimate2000(self))
                log.info("[OK] Cog 'ArsenalProfileUltimate2000' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'ArsenalProfileUltimate2000': {e}")
                
            # L'ancien module "Arsenal Config 2000%" est maintenant unifié dans /config
            log.info("ℹ️ [INFO] 'Arsenal Config 2000%' est maintenant unifié dans /config")
                
            # Discord Badges System
            if DISCORD_BADGES_AVAILABLE:
                try:
                    await self.add_cog(DiscordBadges(self))
                    log.info("[OK] Cog 'DiscordBadges' chargé")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement cog 'DiscordBadges': {e}")
                    
            # Arsenal Diagnostic System
            if ARSENAL_DIAGNOSTIC_AVAILABLE:
                try:
                    await self.add_cog(ArsenalDiagnostic(self))
                    log.info("[OK] Cog 'ArsenalDiagnostic' chargé")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement cog 'ArsenalDiagnostic': {e}")
                
            # Arsenal Context Menus
            try:
                from commands.arsenal_context_menus import ArsenalContextMenus
                await self.add_cog(ArsenalContextMenus(self))
                log.info("[OK] Cog 'ArsenalContextMenus' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'ArsenalContextMenus': {e}")
                
            # Discord Integration Forcer
            try:
                from commands.discord_integration_forcer import DiscordIntegrationForcer
                await self.add_cog(DiscordIntegrationForcer(self))
                log.info("[OK] Cog 'DiscordIntegrationForcer' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'DiscordIntegrationForcer': {e}")
                
            # Absence Ticket System
            if ABSENCE_SYSTEM_AVAILABLE:
                try:
                    await setup_absence_config_db()
                    await self.add_cog(AbsenceTicketSystem(self))
                    log.info("[OK] Cog 'AbsenceTicketSystem' chargé")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement cog 'AbsenceTicketSystem': {e}")
                    
            # Sanctions System
            if SANCTIONS_SYSTEM_AVAILABLE:
                try:
                    await self.add_cog(SanctionsSystem(self))
                    log.info("[OK] Cog 'SanctionsSystem' chargé")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement cog 'SanctionsSystem': {e}")

            # Casier System
            try:
                from commands.casier_system import CasierSystem
                await self.add_cog(CasierSystem(self))
                log.info("[OK] Cog 'CasierSystem' chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement cog 'CasierSystem': {e}")
            # Complete Commands System
            if COMPLETE_COMMANDS_SYSTEM_AVAILABLE:
                try:
                    await self.add_cog(CompleteCommandsSystem(self))
                    log.info("[OK] Cog 'CompleteCommandsSystem' chargé")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement cog 'CompleteCommandsSystem': {e}")
                    
            # Communication System
            if COMMUNICATION_SYSTEM_AVAILABLE:
                try:
                    await self.add_cog(CommunicationSystem(self))
                    log.info("[OK] Cog 'CommunicationSystem' chargé")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement cog 'CommunicationSystem': {e}")
                    import traceback
                    log.error(f"[DEBUG] Communication System Traceback: {traceback.format_exc()}")
                    
            # Help System V2
            if HELP_SYSTEM_V2_AVAILABLE:
                try:
                    await self.add_cog(HelpSystemV2(self))
                    log.info("[OK] Cog 'HelpSystemV2' chargé")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement cog 'HelpSystemV2': {e}")
                    import traceback
                    log.error(f"[DEBUG] Help System V2 Detailed Error: {traceback.format_exc()}")

client = ArsenalBot(command_prefix=PREFIX, intents=intents)
client.creator_id = CREATOR_ID
client.startup_time = datetime.datetime.now(datetime.timezone.utc)
client.command_usage = {}

@client.event
async def on_ready():
    log.info(f"[START] Arsenal Studio lancé comme {client.user.name}")
    log.info(f"[DEBUG] Bot ID: {client.user.id}")
    log.info(f"[DEBUG] Nombre de serveurs: {len(client.guilds)}")
    log.info(f"[DEBUG] Nombre d'utilisateurs visibles: {len(client.users)}")
    
    # Log des serveurs (limité aux 5 premiers pour éviter spam)
    for guild in list(client.guilds)[:5]:
        log.info(f"[GUILD] {guild.name} ({guild.id}) - {guild.member_count} membres")
    
    if len(client.guilds) > 5:
        log.info(f"[GUILD] ... et {len(client.guilds) - 5} autres serveurs")
    
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

@client.event
async def on_error(event, *args, **kwargs):
    """Gestionnaire d'erreurs global pour éviter les crashes"""
    import traceback
    error_info = traceback.format_exc()
    await handle_error(f"Event {event} failed", f"Événement Discord: {event}")
    print(f"❌ [EVENT ERROR] {event}: {error_info}")

@client.event  
async def on_command_error(ctx, error):
    """Gestionnaire d'erreurs pour les commandes"""
    await handle_error(error, f"Commande: {ctx.command}")
    
    # Envoyer une réponse utilisateur conviviale
    try:
        if isinstance(error, commands.CommandNotFound):
            return  # Ignorer les commandes introuvables
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Vous n'avez pas les permissions nécessaires.")
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send("❌ Le bot n'a pas les permissions nécessaires.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏰ Commande en cooldown. Réessayez dans {error.retry_after:.1f}s.")
        else:
            await ctx.send(f"❌ Une erreur est survenue: {str(error)[:100]}")
    except:
        pass  # Ne pas crasher si l'envoi du message échoue

# Imports modules
client.tree.add_command(moderateur.moderator_group)
# client.tree.add_command(admin.admin_group)  # DÉSACTIVÉ - Remplacé par ArsenalCommandGroupsFinal
client.tree.add_command(sanction.sanction_group)

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

# Arsenal Economy System UNIFIÉ (NOUVEAU V4.6)
try:
    from commands.arsenal_economy_unified import ArsenalEconomyUnified
    from commands.arsenal_shop_admin import ArsenalShopAdmin
    from commands.arsenal_config_system import ArsenalConfigSystem
    from commands.arsenal_config_complete import ArsenalCompleteConfig
    from commands.arsenal_update_notifier import ArsenalUpdateNotifier
    ARSENAL_ECONOMY_AVAILABLE = True
    print("[OK] Arsenal Economy UNIFIÉ, Config, Arsenal Complete & Update Notifier System chargé")
except Exception as e:
    ARSENAL_ECONOMY_AVAILABLE = False
    print(f"[WARNING] Arsenal Economy System non disponible: {e}")

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
    
    # Démarrer bot Discord
    try:
        client.run(TOKEN)
    except Exception as e:
        log.error(f"[RUN ERROR] {e}")

