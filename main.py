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

# Arsenal Features System (RÉVOLUTIONNAIRE - 40 fonctionnalités)
try:
    from commands.arsenal_features import ArsenalBotFeatures
    ARSENAL_FEATURES_AVAILABLE = True
    print("🚀 [OK] Arsenal Features System chargé - 40 fonctionnalités Discord!")
except Exception as e:
    ARSENAL_FEATURES_AVAILABLE = False
    print(f"❌ [ERREUR] Arsenal Features System: {e}")

# Arsenal Config Ultimate (RÉVOLUTIONNAIRE V2.0)
try:
    from commands.config_revolution import ArsenalConfigRevolution
    ARSENAL_CONFIG_REVOLUTION_AVAILABLE = True
    print("🚀 [OK] Arsenal Config Revolution chargé - Configuration révolutionnaire V2.0!")
except Exception as e:
    ARSENAL_CONFIG_REVOLUTION_AVAILABLE = False
    print(f"❌ [ERREUR] Arsenal Config Revolution: {e}")

# Arsenal Config Ultimate (UNIFIÉ DANS /config)
# try:
#     from commands.arsenal_config_ultimate import ArsenalConfigUltimate
#     ARSENAL_CONFIG_ULTIMATE_AVAILABLE = True
#     print("🔥 [OK] Arsenal Config Ultimate chargé - Configuration révolutionnaire!")
# except Exception as e:
ARSENAL_CONFIG_ULTIMATE_AVAILABLE = False
print("ℹ️ [INFO] Arsenal Config Ultimate unifié dans /config")

# Arsenal Profile Ultimate (RÉVOLUTIONNAIRE - Profil bot le plus impressionnant)
try:
    from commands.arsenal_profile_ultimate import ArsenalProfileUltimate  
    ARSENAL_PROFILE_ULTIMATE_AVAILABLE = True
    print("💎 [OK] Arsenal Profile Ultimate chargé - Profil révolutionnaire!")
except Exception as e:
    ARSENAL_PROFILE_ULTIMATE_AVAILABLE = False
    print(f"❌ [ERREUR] Arsenal Profile Ultimate: {e}")

# Discord Badges System (NOUVEAU - Pour afficher les capacités à droite du nom)
try:
    from core.discord_badges import DiscordBadges
    DISCORD_BADGES_AVAILABLE = True
    print("🏆 [OK] Discord Badges System chargé - Badges natifs Discord!")
except Exception as e:
    DISCORD_BADGES_AVAILABLE = False
    print(f"❌ [ERREUR] Discord Badges System: {e}")

# Arsenal Diagnostic System (NOUVEAU - Vérification complète du bot)
try:
    from commands.arsenal_diagnostic import ArsenalDiagnostic
    ARSENAL_DIAGNOSTIC_AVAILABLE = True
    print("🔧 [OK] Arsenal Diagnostic System chargé - Vérification complète!")
except Exception as e:
    ARSENAL_DIAGNOSTIC_AVAILABLE = False
    print(f"❌ [ERREUR] Arsenal Diagnostic System: {e}")

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

# Absence Ticket System (NOUVEAU V4.5.2)
try:
    from commands.absence_tickets import AbsenceTicketSystem
    from commands.absence_config import setup_absence_config_db
    ABSENCE_SYSTEM_AVAILABLE = True
    print("🎫 [OK] Absence Ticket System chargé - Gestion tickets d'absence!")
except Exception as e:
    ABSENCE_SYSTEM_AVAILABLE = False
    print(f"❌ [ERREUR] Absence Ticket System: {e}")

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
    from modules.crypto_bot_integration import setup
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

# Sanctions System (NOUVEAU V4.5.2)
try:
    from commands.sanctions_system import SanctionsSystem
    SANCTIONS_SYSTEM_AVAILABLE = True
    print("⚖️ [OK] Sanctions System chargé - Casier permanent & AutoMod!")
except Exception as e:
    SANCTIONS_SYSTEM_AVAILABLE = False
    print(f"❌ [ERREUR] Sanctions System: {e}")

# Complete Commands System - Liste TOUTES les commandes (NOUVEAU V4.5.2)
try:
    from commands.complete_commands_system import CompleteCommandsSystem
    COMPLETE_COMMANDS_SYSTEM_AVAILABLE = True
    print("📋 [OK] Complete Commands System chargé - Liste toutes les commandes!")
except Exception as e:
    COMPLETE_COMMANDS_SYSTEM_AVAILABLE = False
    print(f"❌ [ERREUR] Complete Commands System: {e}")

# Communication System - Say et Traduction (NOUVEAU V4.5.2)
try:
    from commands.communication_system import CommunicationSystem
    COMMUNICATION_SYSTEM_AVAILABLE = True
    print("📢 [OK] Communication System chargé - Say & Traduction IA!")
except Exception as e:
    COMMUNICATION_SYSTEM_AVAILABLE = False
    print(f"❌ [ERREUR] Communication System: {e}")

# Help System V2 (NOUVEAU V4.5.2)
try:
    from commands.help_system_v2 import HelpSystemV2
    HELP_SYSTEM_V2_AVAILABLE = True
    print("📚 [OK] Help System V2 chargé - Interface révolutionnaire!")
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
        # DÉSACTIVÉ - Système de statut Arsenal (remplacé par Profile Ultimate 2000%)
        # self.status_system = initialize_status_system(self)
        # print("🔄 [STATUS] Système de statut Arsenal initialisé")
        self.loop.create_task(restore_voice_channels(self))
        self.loop.create_task(start_terminal(self))
        # DÉSACTIVÉ - Démarrage systèmes de statut Arsenal (conflit avec Profile 2000%)
        # await self.status_system.start_status_rotation()
        # await self.status_system.start_keepalive()
        print("🔄 [STATUS] Systèmes de statut gérés par Arsenal Profile Ultimate 2000%")
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
                self.crypto_integration = setup(self)
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
        
        # Charger Arsenal Config Revolution (SYSTÈME RÉVOLUTIONNAIRE V2.0)
        if ARSENAL_CONFIG_REVOLUTION_AVAILABLE:
            try:
                await self.add_cog(ArsenalConfigRevolution(self))
                log.info("🚀 [OK] Arsenal Config Revolution chargé - Configuration révolutionnaire V2.0!")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Arsenal Config Revolution: {e}")
        
        # Charger Enhanced Music System
        if MUSIC_ENHANCED_AVAILABLE:
            try:
                await self.add_cog(music_enhanced.EnhancedMusicSystem(self))
                log.info("[OK] Module Enhanced Music System chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Enhanced Music: {e}")
        
        # Charger Arsenal Economy System UNIFIÉ (NOUVEAU V4.6) avec Configuration Moderne
        if ARSENAL_ECONOMY_AVAILABLE:
            try:
                await self.add_cog(ArsenalEconomyUnified(self))
                await self.add_cog(ArsenalShopAdmin(self))
                # Config unifié maintenant dans commands/config.py
                # from commands.config_modal_system import ArsenalConfigSystemModal
                # await self.add_cog(ArsenalConfigSystemModal(self))
                await self.add_cog(ArsenalUpdateNotifier(self))
                log.info("[OK] Arsenal Economy UNIFIÉ, Shop & Update Notifier System chargé")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Arsenal Economy UNIFIÉ: {e}")
                
        # Arsenal AutoMod V5.0.1 CORRIGÉ - Exactement 489 mots (NOUVEAU)
        try:
            from commands.arsenal_automod_v5_fixed import ArsenalCommandGroupsFinalFixed
            await self.add_cog(ArsenalCommandGroupsFinalFixed(self))
            log.info("🛡️ [OK] Arsenal AutoMod V5.0.1 CORRIGÉ - Exactement 489 mots chargé!")
        except Exception as e:
            log.error(f"[ERROR] Erreur chargement Arsenal AutoMod V5.0.1 CORRIGÉ: {e}")
            
        # Arsenal Bug Reporter - Système de signalement (NOUVEAU)
        try:
            from commands.arsenal_bug_reporter import ArsenalBugReporter
            await self.add_cog(ArsenalBugReporter(self))
            log.info("🐛 [OK] Arsenal Bug Reporter - Système de signalement chargé!")
        except Exception as e:
            log.error(f"[ERROR] Erreur chargement Arsenal Bug Reporter: {e}")
            
        # Arsenal Test Suite - Tests automatiques (NOUVEAU)
        try:
            from commands.arsenal_test_suite import ArsenalTestSuite
            await self.add_cog(ArsenalTestSuite(self))
            log.info("🧪 [OK] Arsenal Test Suite - Tests automatiques chargé!")
        except Exception as e:
            log.error(f"[ERROR] Erreur chargement Arsenal Test Suite: {e}")
                
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
                
            # Arsenal Config Ultimate - Configuration révolutionnaire
            try:
                from commands.arsenal_config_ultimate import ArsenalConfigUltimate
                await self.add_cog(ArsenalConfigUltimate(self))
                log.info("🔥 [OK] Arsenal Config Ultimate - Configuration la plus avancée Discord!")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Arsenal Config Ultimate: {e}")
            
            # Règlement Intelligent - Système ultra-complet avec interface moderne
            try:
                from commands.reglement import ReglementSystem
                await self.add_cog(ReglementSystem(self))
                log.info("📜 [OK] Règlement Intelligent - Interface ultra-complète avec toutes les fonctionnalités !")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Règlement: {e}")
                
            # Hub Vocal - Salons temporaires avec panel de contrôle
            try:
                from commands.hub_vocal import HubVocal
                await self.add_cog(HubVocal(self))
                log.info("🎤 [OK] Hub Vocal - Système complet de salons temporaires avec contrôle !")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Hub Vocal: {e}")
                
            # DÉSACTIVÉ - Arsenal Profile Ultimate (ancien, remplacé par 2000%)
            # try:
            #     from commands.arsenal_profile_ultimate import ArsenalProfileUltimate
            #     await self.add_cog(ArsenalProfileUltimate(self))
            #     log.info("💎 [OK] Arsenal Profile Ultimate - Profil bot révolutionnaire!")
            # except Exception as e:
            #     log.error(f"[ERROR] Erreur chargement Arsenal Profile Ultimate: {e}")
                
            # Arsenal Profile Ultimate 2000% - Profil révolutionnaire COMPLET (SEUL ACTIF)
            try:
                from commands.arsenal_profile_ultimate_2000 import ArsenalProfileUltimate2000
                await self.add_cog(ArsenalProfileUltimate2000(self))
                log.info("🔥 [OK] Arsenal Profile Ultimate 2000% - STREAMING + 2000% personnalisation!")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Arsenal Profile Ultimate 2000%: {e}")
                
            # Arsenal Config 2000% (UNIFIÉ DANS /config)
            # try:
            #     from commands.arsenal_config_2000 import ArsenalConfig2000System
            #     await self.add_cog(ArsenalConfig2000System(self))
            #     log.info("🚀 [OK] Arsenal Config 2000% - Configuration la plus avancée Discord!")
            # except Exception as e:
            log.info("ℹ️ [INFO] Arsenal Config 2000% unifié dans /config")
                
            # Discord Badges System - Pour afficher les capacités à droite du nom
            if DISCORD_BADGES_AVAILABLE:
                try:
                    await self.add_cog(DiscordBadges(self))
                    log.info("🏆 [OK] Discord Badges System - Badges natifs Discord activés!")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement Discord Badges System: {e}")
                    
            # Arsenal Diagnostic System - Vérification complète du bot
            if ARSENAL_DIAGNOSTIC_AVAILABLE:
                try:
                    await self.add_cog(ArsenalDiagnostic(self))
                    log.info("🔧 [OK] Arsenal Diagnostic System - Vérification complète activée!")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement Arsenal Diagnostic System: {e}")
                
            # DÉSACTIVÉ - Arsenal Profile Updater (conflit avec Profile Ultimate 2000%)
            # try:
            #     from commands.arsenal_profile_updater import ArsenalProfileUpdater
            #     await self.add_cog(ArsenalProfileUpdater(self))
            #     log.info("🎯 [OK] Arsenal Profile Updater - Profil Discord auto-optimisé!")
            # except Exception as e:
            #     log.error(f"[ERROR] Erreur chargement Profile Updater: {e}")
                
            # Arsenal Context Menus - Menus contextuels (clic droit)
            try:
                from commands.arsenal_context_menus import ArsenalContextMenus
                await self.add_cog(ArsenalContextMenus(self))
                log.info("🖱️ [OK] Arsenal Context Menus - Menus contextuels natifs Discord!")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Context Menus: {e}")
                
            # Discord Integration Forcer - Force Discord à reconnaître TOUTES nos prises en charge
            try:
                from commands.discord_integration_forcer import DiscordIntegrationForcer
                await self.add_cog(DiscordIntegrationForcer(self))
                log.info("💎 [OK] Discord Integration Forcer - TOUTES les prises en charge forcées!")
            except Exception as e:
                log.error(f"[ERROR] Erreur chargement Discord Integration Forcer: {e}")
                
            # Absence Ticket System - Gestion des tickets d'absence
            if ABSENCE_SYSTEM_AVAILABLE:
                try:
                    # Initialiser la base de données
                    await setup_absence_config_db()
                    await self.add_cog(AbsenceTicketSystem(self))
                    log.info("🎫 [OK] Absence Ticket System - Tickets d'absence avec auto-expiry!")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement Absence Ticket System: {e}")
                    
            # Sanctions System - Casier judiciaire permanent
            if SANCTIONS_SYSTEM_AVAILABLE:
                try:
                    await self.add_cog(SanctionsSystem(self))
                    log.info("⚖️ [OK] Sanctions System - Casier permanent & Modération avancée!")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement Sanctions System: {e}")
                    
            # Complete Commands System - Liste toutes les commandes
            if COMPLETE_COMMANDS_SYSTEM_AVAILABLE:
                try:
                    await self.add_cog(CompleteCommandsSystem(self))
                    log.info("📋 [OK] Complete Commands System - Liste complète des commandes!")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement Complete Commands System: {e}")
                    
            # Communication System - Say & Traduction avancée
            if COMMUNICATION_SYSTEM_AVAILABLE:
                try:
                    await self.add_cog(CommunicationSystem(self))
                    log.info("📢 [OK] Communication System - Say & Traduction IA chargés!")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement Communication System: {e}")
                    import traceback
                    log.error(f"[DEBUG] Communication System Traceback: {traceback.format_exc()}")
                    
            # Help System V2 - Interface d'aide révolutionnaire
            if HELP_SYSTEM_V2_AVAILABLE:
                try:
                    await self.add_cog(HelpSystemV2(self))
                    log.info("📚 [OK] Help System V2 - Interface moderne chargée!")
                except Exception as e:
                    log.error(f"[ERROR] Erreur chargement Help System V2: {e}")
                    import traceback
                    log.error(f"[DEBUG] Help System V2 Detailed Error: {traceback.format_exc()}")

client = ArsenalBot(command_prefix=PREFIX, intents=intents)
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
    
    # Définir le statut streaming par défaut AVANT tout
    try:
        activity = discord.Streaming(
            name="🚀 Arsenal V4.5.2 ULTIMATE | /help", 
            url="https://twitch.tv/xerox3elite"
        )
        await client.change_presence(activity=activity)
        log.info("💜 [STATUS] Statut streaming défini par défaut")
    except Exception as e:
        log.error(f"❌ [STATUS] Erreur définition statut: {e}")
        import traceback
        log.error(f"[DEBUG] Status Error Traceback: {traceback.format_exc()}")
    
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

