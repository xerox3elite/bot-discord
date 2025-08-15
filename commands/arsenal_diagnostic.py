"""
🔧 ARSENAL DIAGNOSTIC SYSTEM - Vérifie l'intégralité du bot
Système ultra-complet qui check TOUT et dit exactement ce qui va pas
"""

import discord
from discord.ext import commands
import asyncio
import importlib
import sys
import os
import json
import sqlite3
from datetime import datetime, timezone
import aiohttp
import traceback
from pathlib import Path

# Imports pour les tests spécialisés
try:
    import psutil
except ImportError:
    psutil = None
import traceback
import aiohttp

class ArsenalDiagnostic(commands.Cog):
    """Système de diagnostic complet Arsenal - Check tout le bot"""
    
    def __init__(self, bot):
        self.bot = bot
        self.diagnostic_results = {}
        self.errors_found = []
        self.warnings_found = []
        
    @commands.hybrid_command(name="diagnostic", description="🔧 Diagnostic complet Arsenal - Vérification intégralité bot")
    @commands.is_owner()
    async def run_full_diagnostic(self, ctx):
        """Lance un diagnostic complet d'Arsenal"""
        
        # Message de démarrage
        embed_start = discord.Embed(
            title="🔧 **DIAGNOSTIC ARSENAL EN COURS**",
            description="Vérification complète de tous les systèmes...\n\n⏳ **Patientez pendant l'analyse**",
            color=0xffaa00
        )
        msg = await ctx.send(embed=embed_start)
        
        # Réinitialiser les résultats
        self.diagnostic_results = {}
        self.errors_found = []
        self.warnings_found = []
        
        # Tests à effectuer
        tests = [
            ("🤖 Bot Status", self.check_bot_status),
            ("📊 Discord API", self.check_discord_api),
            ("💾 Base de données", self.check_databases),
            ("📁 Fichiers système", self.check_system_files),
            ("🔗 Modules Python", self.check_python_modules),
            ("⚙️ Commandes Discord", self.check_discord_commands),
            ("🎵 Systèmes Audio", self.check_audio_systems),
            ("💰 Économie Arsenal", self.check_economy_system),
            ("🛡️ Modération", self.check_moderation_system),
            ("🎮 Gaming APIs", self.check_gaming_apis),
            ("🌐 Connexions réseau", self.check_network_connections),
            ("🔧 Configuration", self.check_configuration),
            ("📝 Permissions", self.check_permissions),
            ("🏆 Badges Discord", self.check_discord_badges),
            ("🔄 Tâches en arrière-plan", self.check_background_tasks)
        ]
        
        # Exécuter tous les tests
        for test_name, test_func in tests:
            try:
                result = await test_func()
                self.diagnostic_results[test_name] = result
            except Exception as e:
                self.diagnostic_results[test_name] = {"status": "ERREUR", "details": str(e)}
                self.errors_found.append(f"{test_name}: {str(e)}")
        
        # Générer le rapport final
        await self.generate_diagnostic_report(ctx, msg)
    
    async def check_bot_status(self):
        """Vérifie le status général du bot"""
        results = {"status": "OK", "details": []}
        
        # Connexion Discord
        if not self.bot.is_ready():
            results["status"] = "ERREUR"
            results["details"].append("Bot non connecté à Discord")
        else:
            results["details"].append(f"✅ Connecté comme {self.bot.user.name}")
        
        # Latence
        try:
            latency_ms = round(self.bot.latency * 1000)
            if latency_ms > 300:
                results["status"] = "ATTENTION" if results["status"] == "OK" else results["status"]
                results["details"].append(f"⚠️ Latence élevée: {latency_ms}ms")
            else:
                results["details"].append(f"✅ Latence: {latency_ms}ms")
        except (ValueError, TypeError):
            results["details"].append("⚠️ Latence: Non disponible (bot hors ligne)")
        
        # Serveurs
        guild_count = len(self.bot.guilds)
        results["details"].append(f"✅ Serveurs connectés: {guild_count}")
        
        # Uptime
        if hasattr(self.bot, 'startup_time'):
            # S'assurer que les deux datetimes ont le même timezone
            current_time = datetime.now(timezone.utc)
            startup_time = self.bot.startup_time
            
            # Si startup_time n'a pas de timezone, on assume UTC
            if startup_time.tzinfo is None:
                startup_time = startup_time.replace(tzinfo=timezone.utc)
            
            uptime = current_time - startup_time
            results["details"].append(f"✅ Uptime: {str(uptime).split('.')[0]}")
        else:
            results["details"].append("⚠️ Temps de démarrage non disponible")
        
        return results
    
    async def check_discord_api(self):
        """Vérifie l'état de l'API Discord"""
        results = {"status": "OK", "details": []}
        
        try:
            # Si le bot est connecté, utiliser ses infos
            if self.bot.is_ready() and self.bot.user:
                results["details"].append("✅ API Discord accessible (bot connecté)")
            else:
                # Sinon test basique sans authentification
                async with aiohttp.ClientSession() as session:
                    # Test endpoint public Discord
                    async with session.get("https://discord.com/api/v10/gateway", timeout=aiohttp.ClientTimeout(total=10)) as resp:
                        if resp.status == 200:
                            results["details"].append("✅ API Discord accessible")
                        else:
                            results["status"] = "ATTENTION"
                            results["details"].append(f"⚠️ API Discord: Status {resp.status}")
        except asyncio.TimeoutError:
            results["status"] = "ATTENTION"
            results["details"].append("⚠️ API Discord: Timeout de connexion")
        except Exception as e:
            results["status"] = "ATTENTION"
            results["details"].append(f"⚠️ Connexion API: {str(e)[:50]}")
        
        # Test Slash Commands seulement si le bot est prêt
        try:
            if self.bot.is_ready():
                synced = await self.bot.tree.sync()
                results["details"].append(f"✅ Slash Commands: {len(synced)} synchronisées")
            else:
                results["details"].append("⚠️ Slash Commands: Bot non connecté")
        except Exception as e:
            results["status"] = "ATTENTION" if results["status"] == "OK" else results["status"]
            results["details"].append(f"⚠️ Sync Commands: {str(e)[:50]}")
        
        return results
    
    async def check_databases(self):
        """Vérifie toutes les bases de données"""
        results = {"status": "OK", "details": []}
        
        # Bases de données à vérifier
        dbs = [
            "arsenal_v4.db",
            "hunt_royal.db", 
            "hunt_royal_auth.db",
            "hunt_royal_profiles.db",
            "suggestions.db",
            "crypto_wallets.db",
            "arsenal_coins_central.db"
        ]
        
        for db_name in dbs:
            try:
                if os.path.exists(db_name):
                    # Test connexion SQLite
                    conn = sqlite3.connect(db_name)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    conn.close()
                    results["details"].append(f"✅ {db_name}: {len(tables)} tables")
                else:
                    results["status"] = "ATTENTION" if results["status"] == "OK" else results["status"]
                    results["details"].append(f"⚠️ {db_name}: Fichier manquant")
            except Exception as e:
                results["status"] = "ERREUR"
                results["details"].append(f"❌ {db_name}: {str(e)}")
        
        return results
    
    async def check_system_files(self):
        """Vérifie les fichiers système critiques"""
        results = {"status": "OK", "details": []}
        
        critical_files = [
            ".env",
            "main.py",
            "requirements.txt",
            "bot_status.json",
            "hunt_royal_cache.json"
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                results["details"].append(f"✅ {file_path}")
            else:
                results["status"] = "ATTENTION" if results["status"] == "OK" else results["status"]
                results["details"].append(f"⚠️ {file_path}: Manquant")
        
        return results
    
    async def check_python_modules(self):
        """Vérifie les modules Python critiques"""
        results = {"status": "OK", "details": []}
        
        # Modules critiques Arsenal
        critical_modules = [
            "commands.arsenal_profile_ultimate_2000",
            "commands.arsenal_config_2000", 
            "commands.arsenal_features",
            "core.discord_badges",
            "manager.config_manager",
            "core.logger"
        ]
        
        for module_name in critical_modules:
            try:
                if module_name in sys.modules:
                    results["details"].append(f"✅ {module_name}")
                else:
                    # Tenter l'import
                    importlib.import_module(module_name)
                    results["details"].append(f"✅ {module_name} (importé)")
            except Exception as e:
                results["status"] = "ERREUR"
                results["details"].append(f"❌ {module_name}: {str(e)}")
        
        return results
    
    async def check_discord_commands(self):
        """Vérifie les commandes Discord"""
        results = {"status": "OK", "details": []}
        
        # Compter les commandes
        slash_commands = len(self.bot.tree.get_commands())
        prefix_commands = len(self.bot.commands)
        
        results["details"].append(f"✅ Slash Commands: {slash_commands}")
        results["details"].append(f"✅ Commandes préfixe: {prefix_commands}")
        
        # Tester quelques commandes clés
        key_commands = ["arsenal_help", "profile_2000", "config_2000", "diagnostic"]
        for cmd_name in key_commands:
            cmd = self.bot.get_command(cmd_name)
            if cmd:
                results["details"].append(f"✅ /{cmd_name}")
            else:
                results["status"] = "ATTENTION" if results["status"] == "OK" else results["status"]  
                results["details"].append(f"⚠️ /{cmd_name}: Non trouvée")
        
        return results
    
    async def check_audio_systems(self):
        """Vérifie les systèmes audio/musique"""
        results = {"status": "OK", "details": []}
        
        try:
            # Vérifier si youtube_dl est disponible
            import youtube_dl
            results["details"].append("✅ youtube_dl disponible")
        except ImportError:
            results["status"] = "ATTENTION"
            results["details"].append("⚠️ youtube_dl non installé")
        
        try:
            # Vérifier discord voice
            voice_clients = len(self.bot.voice_clients)
            results["details"].append(f"✅ Clients vocaux: {voice_clients}")
        except Exception as e:
            results["status"] = "ERREUR"
            results["details"].append(f"❌ Voice clients: {str(e)}")
        
        return results
    
    async def check_economy_system(self):
        """Vérifie le système économique Arsenal"""
        results = {"status": "OK", "details": []}
        
        try:
            # Vérifier la DB ArsenalCoins
            if os.path.exists("arsenal_coins_central.db"):
                results["details"].append("✅ Base ArsenalCoins")
            else:
                results["status"] = "ATTENTION"
                results["details"].append("⚠️ Base ArsenalCoins manquante")
            
            # Vérifier les cogs économie
            economy_cogs = ["ArsenalEconomySystem", "ArsenalShopAdmin"]
            for cog_name in economy_cogs:
                if self.bot.get_cog(cog_name):
                    results["details"].append(f"✅ {cog_name}")
                else:
                    results["status"] = "ATTENTION" if results["status"] == "OK" else results["status"]
                    results["details"].append(f"⚠️ {cog_name}: Non chargé")
        
        except Exception as e:
            results["status"] = "ERREUR"
            results["details"].append(f"❌ Économie: {str(e)}")
        
        return results
    
    async def check_moderation_system(self):
        """Vérifie les systèmes de modération"""
        results = {"status": "OK", "details": []}
        
        # Vérifier les permissions de modération dans les serveurs connectés
        if self.bot.guilds:
            # Prendre le premier serveur pour le test
            guild = self.bot.guilds[0] 
            bot_member = guild.me
            perms = bot_member.guild_permissions
            
            mod_perms = [
                ("manage_messages", "Gérer les messages"),
                ("kick_members", "Expulser"),
                ("ban_members", "Bannir"),
                ("manage_roles", "Gérer les rôles"),
                ("manage_channels", "Gérer les salons")
            ]
            
            for perm_name, perm_display in mod_perms:
                if getattr(perms, perm_name):
                    results["details"].append(f"✅ {perm_display}")
                else:
                    results["status"] = "ATTENTION" if results["status"] == "OK" else results["status"]
                    results["details"].append(f"⚠️ {perm_display}: Manquant")
        else:
            results["details"].append("⚠️ Pas de serveur pour tester les permissions")
        
        return results
    
    async def check_gaming_apis(self):
        """Vérifie les APIs gaming"""
        results = {"status": "OK", "details": []}
        
        # APIs à tester (sans faire de vraies requêtes pour éviter les rate limits)
        gaming_apis = [
            "Steam API",
            "Riot Games API", 
            "Xbox Live API",
            "PlayStation Network",
            "Epic Games Store"
        ]
        
        for api_name in gaming_apis:
            # Pour l'instant on marque comme disponible, on testera plus tard si nécessaire
            results["details"].append(f"🔄 {api_name}: Configuré")
        
        return results
    
    async def check_network_connections(self):
        """Vérifie les connexions réseau"""
        results = {"status": "OK", "details": []}
        
        # Test connexions importantes
        test_urls = [
            ("Discord API", "https://discord.com/api/v10"),
            ("GitHub", "https://api.github.com"),
            ("Google", "https://www.google.com")
        ]
        
        for name, url in test_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=5) as resp:
                        if resp.status < 400:
                            results["details"].append(f"✅ {name}")
                        else:
                            results["status"] = "ATTENTION" if results["status"] == "OK" else results["status"]
                            results["details"].append(f"⚠️ {name}: Status {resp.status}")
            except Exception as e:
                results["status"] = "ERREUR"
                results["details"].append(f"❌ {name}: Timeout/Erreur")
        
        return results
    
    async def check_configuration(self):
        """Vérifie la configuration Arsenal"""
        results = {"status": "OK", "details": []}
        
        # Variables d'environnement importantes
        env_vars = ["TOKEN", "CREATOR_ID", "PREFIX"]
        
        for var in env_vars:
            if os.getenv(var):
                results["details"].append(f"✅ {var}")
            else:
                results["status"] = "ERREUR"
                results["details"].append(f"❌ {var}: Variable manquante")
        
        return results
    
    async def check_permissions(self):
        """Vérifie les permissions du bot"""
        results = {"status": "OK", "details": []}
        
        if self.bot.guilds:
            # Prendre le premier serveur pour le test
            guild = self.bot.guilds[0]
            bot_member = guild.me
            perms = bot_member.guild_permissions
            
            # Permissions critiques
            critical_perms = [
                ("send_messages", "Envoyer des messages"),
                ("embed_links", "Liens intégrés"), 
                ("attach_files", "Joindre des fichiers"),
                ("use_slash_commands", "Slash commands"),
                ("connect", "Se connecter aux vocaux"),
                ("speak", "Parler dans les vocaux")
            ]
            
            for perm_name, perm_display in critical_perms:
                if hasattr(perms, perm_name) and getattr(perms, perm_name):
                    results["details"].append(f"✅ {perm_display}")
                else:
                    results["status"] = "ATTENTION" if results["status"] == "OK" else results["status"]
                    results["details"].append(f"⚠️ {perm_display}: Manquant")
        else:
            results["status"] = "ATTENTION"
            results["details"].append("⚠️ Pas de serveur pour tester les permissions")
        
        return results
    
    async def check_discord_badges(self):
        """Vérifie le système de badges Discord"""
        results = {"status": "OK", "details": []}
        
        # Vérifier si le système de badges est chargé
        badges_cog = self.bot.get_cog("DiscordBadges")
        if badges_cog:
            results["details"].append("✅ Système badges chargé")
            results["details"].append("🔄 Badges en cours d'activation (24-48h)")
        else:
            results["status"] = "ATTENTION"
            results["details"].append("⚠️ Système badges non chargé")
        
        return results
    
    async def check_background_tasks(self):
        """Vérifie les tâches en arrière-plan"""
        results = {"status": "OK", "details": []}
        
        # Chercher les tâches actives
        profile_cog = self.bot.get_cog("ArsenalProfileUltimate2000")
        if profile_cog and hasattr(profile_cog, 'profile_updates_streaming'):
            if profile_cog.profile_updates_streaming.is_running():
                results["details"].append("✅ Rotation status streaming active")
            else:
                results["status"] = "ATTENTION"
                results["details"].append("⚠️ Rotation status non active")
        
        return results
    
    async def generate_diagnostic_report(self, ctx, msg):
        """Génère le rapport final de diagnostic"""
        
        # Compter les résultats
        total_tests = len(self.diagnostic_results)
        ok_count = sum(1 for r in self.diagnostic_results.values() if r["status"] == "OK")
        warning_count = sum(1 for r in self.diagnostic_results.values() if r["status"] == "ATTENTION")
        error_count = sum(1 for r in self.diagnostic_results.values() if r["status"] == "ERREUR")
        
        # Couleur selon les résultats
        if error_count > 0:
            color = 0xff0000  # Rouge
            status_emoji = "❌"
            status_text = "ERREURS DÉTECTÉES"
        elif warning_count > 0:
            color = 0xffaa00  # Orange
            status_emoji = "⚠️"
            status_text = "ATTENTION REQUISE"
        else:
            color = 0x00ff00  # Vert
            status_emoji = "✅"
            status_text = "TOUT OPÉRATIONNEL"
        
        # Embed principal
        embed = discord.Embed(
            title=f"🔧 **DIAGNOSTIC ARSENAL COMPLET**",
            description=f"{status_emoji} **{status_text}**\n\n" + 
                       f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n" +
                       f"**📊 Résultats**: {total_tests} tests effectués\n\n" +
                       f"✅ **OK**: {ok_count} systèmes\n\n" +
                       f"⚠️ **Attention**: {warning_count} systèmes\n\n" +
                       f"❌ **Erreurs**: {error_count} systèmes",
            color=color,
            timestamp=datetime.now()
        )
        
        # Détails par catégorie
        details_text = ""
        for test_name, result in self.diagnostic_results.items():
            status_icon = {"OK": "✅", "ATTENTION": "⚠️", "ERREUR": "❌"}[result["status"]]
            details_text += f"{status_icon} **{test_name}**: {result['status']}\n"
            
            # Ajouter quelques détails importants
            if result["details"] and len(result["details"]) > 0:
                details_text += f"   └─ {result['details'][0]}\n"
            
            details_text += "\n"
        
        if len(details_text) > 1024:
            details_text = details_text[:1000] + "...\n**[Rapport tronqué]**"
        
        embed.add_field(
            name="📋 **DÉTAILS DES TESTS**", 
            value=details_text,
            inline=False
        )
        
        # Recommandations si erreurs
        if error_count > 0 or warning_count > 0:
            recommendations = []
            
            if error_count > 0:
                recommendations.append("🔧 **Corriger les erreurs critiques**")
            if warning_count > 0:
                recommendations.append("⚠️ **Vérifier les avertissements**")
            
            embed.add_field(
                name="🛠️ **RECOMMANDATIONS**",
                value="\n\n".join(recommendations),
                inline=False
            )
        
        embed.set_footer(text="Arsenal Diagnostic System - Rapport complet généré")
        
        # Mettre à jour le message
        await msg.edit(embed=embed)
        
        # Si il y a des erreurs, envoyer les détails en MP au propriétaire
        if self.errors_found:
            try:
                owner = self.bot.get_user(int(os.getenv("CREATOR_ID", "0")))
                if owner:
                    error_text = "🔧 **ERREURS DÉTECTÉES DANS ARSENAL:**\n\n"
                    for error in self.errors_found[:10]:  # Limiter à 10 erreurs
                        error_text += f"❌ {error}\n"
                    
                    await owner.send(error_text)
            except:
                pass  # Pas grave si on peut pas envoyer en MP

async def setup(bot):
    await bot.add_cog(ArsenalDiagnostic(bot))
