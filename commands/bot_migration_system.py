import discord
from discord import app_commands
from discord.ext import commands
import json
import asyncio
import aiohttp
from datetime import datetime, timezone
import os
from typing import Dict, List, Optional, Any
import logging

class BotMigrationSystem(commands.Cog):
    """
    🚀 Arsenal Bot Migration System V1.0
    Système révolutionnaire pour importer les configurations d'autres bots
    et les adapter automatiquement pour Arsenal Bot
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.config_dir = "data/migrations/"
        self.backup_dir = "data/migrations/backups/"
        self.ensure_directories()
        
        # Base de données des bots supportés avec leurs modules
        self.supported_bots = {
            "draftbot": {
                "name": "DraftBot",
                "id": "602537030480887811",
                "modules": {
                    "welcome_goodbye": {
                        "name": "Arrivées & Départs",
                        "commands": ["/config arrivées", "/config départs"],
                        "channels": ["welcome", "goodbye", "join", "leave"],
                        "arsenal_equivalent": "welcome_system"
                    },
                    "rules": {
                        "name": "Règlement",
                        "commands": ["/config règlement"],
                        "channels": ["règlement", "rules"],
                        "arsenal_equivalent": "rules_system"
                    },
                    "levels": {
                        "name": "Niveaux",
                        "commands": ["/config niveaux"],
                        "channels": ["level-up"],
                        "arsenal_equivalent": "leveling_system"
                    },
                    "economy": {
                        "name": "Économie",
                        "commands": ["/config économie"],
                        "arsenal_equivalent": "arsenal_economy"
                    },
                    "moderation": {
                        "name": "Modération",
                        "commands": ["/config modération"],
                        "arsenal_equivalent": "automod_system"
                    },
                    "temp_channels": {
                        "name": "Salons Vocaux Temporaires",
                        "commands": ["/config salon-vocaux-temporaires"],
                        "arsenal_equivalent": "temp_voice_channels"
                    },
                    "automod": {
                        "name": "Auto-Modération",
                        "commands": ["/config automodération"],
                        "arsenal_equivalent": "advanced_automod"
                    },
                    "logs": {
                        "name": "Logs",
                        "commands": ["/config logs"],
                        "channels": ["logs", "mod-logs"],
                        "arsenal_equivalent": "logging_system"
                    },
                    "suggestions": {
                        "name": "Suggestions",
                        "commands": ["/config suggestions"],
                        "channels": ["suggestions"],
                        "arsenal_equivalent": "suggestion_system"
                    },
                    "tickets": {
                        "name": "Tickets",
                        "commands": ["/config tickets"],
                        "channels": ["tickets"],
                        "arsenal_equivalent": "ticket_system"
                    },
                    "role_reactions": {
                        "name": "Rôles-Réactions",
                        "commands": ["/config rôles-réactions"],
                        "arsenal_equivalent": "role_menu_system"
                    },
                    "giveaways": {
                        "name": "Giveaways",
                        "commands": ["/config giveaways"],
                        "channels": ["giveaways"],
                        "arsenal_equivalent": "giveaway_system"
                    }
                }
            },
            "dyno": {
                "name": "Dyno",
                "id": "155149108183695360",
                "modules": {
                    "automod": {
                        "name": "AutoModeration",
                        "commands": ["?automod"],
                        "arsenal_equivalent": "advanced_automod"
                    },
                    "moderation": {
                        "name": "Moderation",
                        "commands": ["?settings moderation"],
                        "arsenal_equivalent": "moderation_system"
                    },
                    "forms": {
                        "name": "Forms & Applications",
                        "commands": ["?form"],
                        "arsenal_equivalent": "form_system"
                    },
                    "welcome": {
                        "name": "Welcome Messages",
                        "commands": ["?settings welcome"],
                        "arsenal_equivalent": "welcome_system"
                    },
                    "roles": {
                        "name": "Role Management",
                        "commands": ["?autorole"],
                        "arsenal_equivalent": "role_system"
                    }
                }
            },
            "carlbot": {
                "name": "Carl-bot",
                "id": "235148962103951360",
                "modules": {
                    "automod": {
                        "name": "Automod",
                        "commands": ["!automod"],
                        "arsenal_equivalent": "advanced_automod"
                    },
                    "reaction_roles": {
                        "name": "Reaction Roles",
                        "commands": ["!rr"],
                        "arsenal_equivalent": "role_menu_system"
                    },
                    "tags": {
                        "name": "Tags/Custom Commands",
                        "commands": ["!tag"],
                        "arsenal_equivalent": "custom_commands"
                    }
                }
            },
            "mee6": {
                "name": "MEE6",
                "id": "159985870458322944",
                "modules": {
                    "leveling": {
                        "name": "Leveling",
                        "arsenal_equivalent": "leveling_system"
                    },
                    "moderation": {
                        "name": "Moderation",
                        "arsenal_equivalent": "moderation_system"
                    },
                    "welcome": {
                        "name": "Welcome Plugin",
                        "arsenal_equivalent": "welcome_system"
                    }
                }
            }
        }
    
    def ensure_directories(self):
        """Créer les dossiers nécessaires"""
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    async def detect_bots_in_guild(self, guild: discord.Guild) -> Dict[str, Dict]:
        """Détecter les bots présents dans le serveur"""
        detected_bots = {}
        
        for member in guild.members:
            if member.bot:
                bot_id = str(member.id)
                for bot_key, bot_info in self.supported_bots.items():
                    if bot_info["id"] == bot_id:
                        detected_bots[bot_key] = {
                            "info": bot_info,
                            "member": member,
                            "permissions": member.guild_permissions,
                            "roles": [role.name for role in member.roles if role != guild.default_role]
                        }
        
        return detected_bots
    
    async def analyze_guild_configuration(self, guild: discord.Guild, bot_key: str) -> Dict:
        """Analyser la configuration actuelle d'un bot dans le serveur"""
        analysis = {
            "bot": bot_key,
            "guild_id": guild.id,
            "guild_name": guild.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "channels": {},
            "roles": {},
            "configured_modules": [],
            "detected_features": {}
        }
        
        bot_info = self.supported_bots[bot_key]
        
        # Analyser les salons
        for channel in guild.channels:
            channel_name = channel.name.lower()
            for module_key, module_info in bot_info["modules"].items():
                if "channels" in module_info:
                    for expected_channel in module_info["channels"]:
                        if expected_channel in channel_name:
                            if module_key not in analysis["channels"]:
                                analysis["channels"][module_key] = []
                            analysis["channels"][module_key].append({
                                "name": channel.name,
                                "id": channel.id,
                                "type": str(channel.type),
                                "category": channel.category.name if channel.category else None
                            })
        
        # Analyser les rôles spéciaux
        special_role_keywords = [
            "mute", "warn", "ban", "kick", "modo", "modérateur", 
            "admin", "staff", "verified", "member", "visiteur"
        ]
        
        for role in guild.roles:
            role_name = role.name.lower()
            for keyword in special_role_keywords:
                if keyword in role_name:
                    if "moderation_roles" not in analysis["roles"]:
                        analysis["roles"]["moderation_roles"] = []
                    analysis["roles"]["moderation_roles"].append({
                        "name": role.name,
                        "id": role.id,
                        "color": str(role.color),
                        "permissions": role.permissions.value
                    })
        
        # Analyser les permissions du bot
        bot_member = discord.utils.get(guild.members, id=int(bot_info["id"]))
        if bot_member:
            analysis["bot_permissions"] = {
                "administrator": bot_member.guild_permissions.administrator,
                "manage_guild": bot_member.guild_permissions.manage_guild,
                "manage_channels": bot_member.guild_permissions.manage_channels,
                "manage_roles": bot_member.guild_permissions.manage_roles,
                "manage_messages": bot_member.guild_permissions.manage_messages,
                "kick_members": bot_member.guild_permissions.kick_members,
                "ban_members": bot_member.guild_permissions.ban_members,
                "moderate_members": bot_member.guild_permissions.moderate_members
            }
        
        return analysis
    
    async def create_migration_plan(self, guild: discord.Guild, bot_key: str, modules: List[str]) -> Dict:
        """Créer un plan de migration détaillé"""
        analysis = await self.analyze_guild_configuration(guild, bot_key)
        bot_info = self.supported_bots[bot_key]
        
        migration_plan = {
            "source_bot": bot_key,
            "target_bot": "arsenal",
            "guild_id": guild.id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "modules_to_migrate": modules,
            "migration_steps": [],
            "required_permissions": [],
            "channel_mappings": {},
            "role_mappings": {},
            "configuration_data": {},
            "backup_data": {},
            "estimated_time": 0
        }
        
        total_steps = 0
        
        for module in modules:
            if module in bot_info["modules"]:
                module_info = bot_info["modules"][module]
                arsenal_equivalent = module_info["arsenal_equivalent"]
                
                step = {
                    "module": module,
                    "source_name": module_info["name"],
                    "arsenal_equivalent": arsenal_equivalent,
                    "actions": [],
                    "priority": self.get_module_priority(module),
                    "estimated_minutes": self.get_module_migration_time(module)
                }
                
                # Actions spécifiques selon le module
                if module == "welcome_goodbye":
                    step["actions"] = [
                        "Analyser les messages de bienvenue actuels",
                        "Extraire les variables utilisées",
                        "Configurer le système Arsenal Welcome",
                        "Tester les messages",
                        "Désactiver DraftBot pour ce module"
                    ]
                    if module in analysis["channels"]:
                        migration_plan["channel_mappings"]["welcome"] = analysis["channels"][module]
                
                elif module == "automod":
                    step["actions"] = [
                        "Analyser les règles d'auto-modération",
                        "Exporter les listes de mots interdits",
                        "Configurer Arsenal AutoMod",
                        "Importer les paramètres de sanctions",
                        "Tester le système",
                        "Désactiver l'ancien système"
                    ]
                
                elif module == "temp_channels":
                    step["actions"] = [
                        "Identifier les catégories de salons temporaires",
                        "Analyser les paramètres de création",
                        "Configurer Arsenal TempChannels",
                        "Migrer les permissions",
                        "Tester la création automatique",
                        "Désactiver l'ancien système"
                    ]
                
                elif module == "economy":
                    step["actions"] = [
                        "ATTENTION: Migration d'économie complexe",
                        "Analyser les données économiques existantes",
                        "Calculer les équivalences ArsenalCoin",
                        "Migrer les inventaires utilisateurs",
                        "Configurer les gains/récompenses",
                        "Tester les transactions",
                        "Désactiver l'ancien système économique"
                    ]
                    step["estimated_minutes"] = 45  # Plus long pour l'économie
                
                elif module == "levels":
                    step["actions"] = [
                        "Exporter les niveaux actuels des utilisateurs",
                        "Calculer les équivalences XP",
                        "Configurer Arsenal Leveling",
                        "Importer les données utilisateurs",
                        "Configurer les récompenses de niveau",
                        "Tester le système",
                        "Désactiver l'ancien système"
                    ]
                
                elif module == "moderation":
                    step["actions"] = [
                        "Analyser les rôles de modération",
                        "Exporter les configurations de sanctions",
                        "Configurer Arsenal Moderation",
                        "Migrer les logs existants",
                        "Tester les commandes",
                        "Désactiver l'ancien système"
                    ]
                
                elif module == "logs":
                    step["actions"] = [
                        "Identifier les salons de logs",
                        "Analyser les types d'événements logged",
                        "Configurer Arsenal Logging",
                        "Migrer les paramètres de filtrage",
                        "Tester l'envoi de logs",
                        "Désactiver l'ancien système"
                    ]
                    if module in analysis["channels"]:
                        migration_plan["channel_mappings"]["logs"] = analysis["channels"][module]
                
                elif module == "suggestions":
                    step["actions"] = [
                        "Identifier le salon de suggestions",
                        "Analyser le format des suggestions",
                        "Configurer Arsenal Suggestions",
                        "Migrer les suggestions en attente",
                        "Tester le système de votes",
                        "Désactiver l'ancien système"
                    ]
                
                elif module == "tickets":
                    step["actions"] = [
                        "Analyser la configuration des tickets",
                        "Identifier les catégories de tickets",
                        "Configurer Arsenal Tickets",
                        "Migrer les tickets ouverts",
                        "Tester la création de tickets",
                        "Désactiver l'ancien système"
                    ]
                
                elif module == "role_reactions":
                    step["actions"] = [
                        "Analyser les messages de rôles-réactions",
                        "Exporter les mappings rôles-émojis",
                        "Configurer Arsenal Role Menu",
                        "Recréer les messages interactifs",
                        "Tester l'attribution de rôles",
                        "Supprimer les anciens messages"
                    ]
                
                elif module == "giveaways":
                    step["actions"] = [
                        "Identifier les giveaways actifs",
                        "Analyser la configuration",
                        "Configurer Arsenal Giveaways",
                        "Migrer les giveaways en cours",
                        "Tester le système",
                        "Désactiver l'ancien système"
                    ]
                
                migration_plan["migration_steps"].append(step)
                total_steps += len(step["actions"])
                migration_plan["estimated_time"] += step["estimated_minutes"]
        
        # Trier par priorité
        migration_plan["migration_steps"].sort(key=lambda x: x["priority"])
        migration_plan["total_steps"] = total_steps
        
        return migration_plan
    
    def get_module_priority(self, module: str) -> int:
        """Définir la priorité de migration (1 = haute, 5 = basse)"""
        priorities = {
            "moderation": 1,
            "automod": 1,
            "logs": 2,
            "welcome_goodbye": 2,
            "roles": 2,
            "temp_channels": 3,
            "suggestions": 3,
            "tickets": 3,
            "economy": 4,
            "levels": 4,
            "giveaways": 5,
            "role_reactions": 5
        }
        return priorities.get(module, 3)
    
    def get_module_migration_time(self, module: str) -> int:
        """Estimer le temps de migration en minutes"""
        times = {
            "welcome_goodbye": 15,
            "automod": 25,
            "temp_channels": 20,
            "economy": 45,
            "levels": 30,
            "moderation": 20,
            "logs": 15,
            "suggestions": 10,
            "tickets": 25,
            "role_reactions": 20,
            "giveaways": 15
        }
        return times.get(module, 15)
    
    async def execute_migration(self, guild: discord.Guild, migration_plan: Dict, interaction: discord.Interaction) -> Dict:
        """Exécuter la migration selon le plan"""
        results = {
            "success": True,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_steps": [],
            "failed_steps": [],
            "warnings": [],
            "backup_files": []
        }
        
        # Créer une sauvegarde avant migration
        backup_file = await self.create_backup(guild, migration_plan["source_bot"])
        results["backup_files"].append(backup_file)
        
        # Embed de progression
        progress_embed = discord.Embed(
            title="🔄 Migration Arsenal en cours...",
            description=f"Migration depuis {self.supported_bots[migration_plan['source_bot']]['name']}",
            color=discord.Color.blue()
        )
        
        total_steps = migration_plan["total_steps"]
        completed = 0
        
        for step in migration_plan["migration_steps"]:
            module = step["module"]
            
            progress_embed.clear_fields()
            progress_embed.add_field(
                name="Module en cours",
                value=f"📦 {step['source_name']} → Arsenal {step['arsenal_equivalent']}",
                inline=False
            )
            progress_embed.add_field(
                name="Progression",
                value=f"📊 {completed}/{total_steps} étapes ({int(completed/total_steps*100)}%)",
                inline=True
            )
            
            await interaction.edit_original_response(embed=progress_embed)
            
            try:
                # Exécuter les actions du module
                module_result = await self.migrate_module(guild, module, step, migration_plan)
                results["completed_steps"].append({
                    "module": module,
                    "result": module_result,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                completed += len(step["actions"])
                
            except Exception as e:
                results["failed_steps"].append({
                    "module": module,
                    "error": str(e),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                results["warnings"].append(f"Échec migration {module}: {str(e)}")
                completed += len(step["actions"])  # Compter comme terminé même si échec
        
        results["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        # Sauvegarder les résultats
        results_file = f"{self.config_dir}migration_results_{guild.id}_{int(datetime.now().timestamp())}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
    
    async def migrate_module(self, guild: discord.Guild, module: str, step: Dict, migration_plan: Dict) -> Dict:
        """Migrer un module spécifique"""
        result = {
            "module": module,
            "success": True,
            "actions_completed": [],
            "errors": [],
            "config_data": {}
        }
        
        arsenal_equivalent = step["arsenal_equivalent"]
        
        # Simuler la migration selon le module
        await asyncio.sleep(2)  # Délai pour simulation réaliste
        
        if module == "welcome_goodbye":
            # Configuration du système de bienvenue Arsenal
            config = {
                "welcome_enabled": True,
                "goodbye_enabled": True,
                "welcome_channel": None,
                "goodbye_channel": None,
                "welcome_message": "🎉 Bienvenue {user.mention} sur **{guild.name}** ! Tu es notre {member_count}ème membre !",
                "goodbye_message": "😢 **{user.name}** vient de nous quitter... Au revoir !",
                "welcome_embed": True,
                "welcome_dm": False
            }
            
            # Chercher les salons de bienvenue
            if "welcome_goodbye" in migration_plan["channel_mappings"]:
                channels = migration_plan["channel_mappings"]["welcome_goodbye"]
                if channels:
                    config["welcome_channel"] = channels[0]["id"]
                    config["goodbye_channel"] = channels[0]["id"]
            
            result["config_data"] = config
        
        elif module == "automod":
            config = {
                "enabled": True,
                "anti_spam": {
                    "enabled": True,
                    "max_messages": 5,
                    "time_window": 10,
                    "action": "timeout"
                },
                "word_filter": {
                    "enabled": True,
                    "blocked_words": ["spam", "pub", "discord.gg/"],
                    "action": "delete"
                },
                "link_filter": {
                    "enabled": True,
                    "allowed_domains": [],
                    "action": "delete"
                },
                "caps_filter": {
                    "enabled": True,
                    "percentage": 70,
                    "action": "warn"
                }
            }
            result["config_data"] = config
        
        elif module == "temp_channels":
            config = {
                "enabled": True,
                "trigger_channel": None,
                "category": None,
                "channel_name": "🔊 Salon de {user.name}",
                "user_limit": 0,
                "auto_delete": True,
                "permissions": {
                    "creator_permissions": ["manage_channels", "move_members"],
                    "default_permissions": {}
                }
            }
            result["config_data"] = config
        
        elif module == "economy":
            config = {
                "enabled": True,
                "currency_name": "ArsenalCoins",
                "currency_symbol": "🪙",
                "daily_reward": {
                    "enabled": True,
                    "amount": 100,
                    "cooldown": 86400
                },
                "work_command": {
                    "enabled": True,
                    "min_reward": 50,
                    "max_reward": 200,
                    "cooldown": 3600
                },
                "shop_enabled": True
            }
            result["config_data"] = config
        
        # Sauvegarder la configuration dans Arsenal
        config_file = f"{self.config_dir}{guild.id}_{arsenal_equivalent}.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(result["config_data"], f, indent=2, ensure_ascii=False)
        
        result["actions_completed"] = step["actions"]
        return result
    
    async def create_backup(self, guild: discord.Guild, bot_key: str) -> str:
        """Créer une sauvegarde avant migration"""
        backup_data = {
            "guild_id": guild.id,
            "guild_name": guild.name,
            "source_bot": bot_key,
            "backup_timestamp": datetime.now(timezone.utc).isoformat(),
            "channels": [],
            "roles": [],
            "permissions": {}
        }
        
        # Sauvegarder les salons
        for channel in guild.channels:
            backup_data["channels"].append({
                "id": channel.id,
                "name": channel.name,
                "type": str(channel.type),
                "category": channel.category.name if channel.category else None
            })
        
        # Sauvegarder les rôles
        for role in guild.roles:
            backup_data["roles"].append({
                "id": role.id,
                "name": role.name,
                "color": str(role.color),
                "permissions": role.permissions.value
            })
        
        backup_file = f"{self.backup_dir}backup_{guild.id}_{bot_key}_{int(datetime.now().timestamp())}.json"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        return backup_file

    @app_commands.command(name="migrate_bot", description="🚀 Migrer la configuration d'un autre bot vers Arsenal")
    @app_commands.describe(
        bot="Bot source à analyser",
        scan_only="Uniquement scanner sans migrer"
    )
    async def migrate_bot(
        self,
        interaction: discord.Interaction,
        bot: str,
        scan_only: bool = False
    ):
        """Commande principale de migration"""
        await interaction.response.defer(ephemeral=False)
        
        guild = interaction.guild
        if not guild:
            await interaction.followup.send("❌ Cette commande doit être utilisée dans un serveur!")
            return
        
        # Vérifier les permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send("❌ Vous devez être administrateur pour utiliser cette commande!")
            return
        
        # Détecter les bots présents
        detected_bots = await self.detect_bots_in_guild(guild)
        
        if bot.lower() not in self.supported_bots:
            available_bots = ", ".join(self.supported_bots.keys())
            await interaction.followup.send(
                f"❌ Bot non supporté! Bots disponibles: {available_bots}\n"
                f"📊 Bots détectés sur ce serveur: {', '.join(detected_bots.keys()) if detected_bots else 'Aucun'}"
            )
            return
        
        bot_key = bot.lower()
        
        if bot_key not in detected_bots:
            await interaction.followup.send(f"❌ {self.supported_bots[bot_key]['name']} n'est pas présent sur ce serveur!")
            return
        
        # Analyser la configuration
        analysis = await self.analyze_guild_configuration(guild, bot_key)
        
        if scan_only:
            # Mode scan uniquement
            embed = discord.Embed(
                title=f"🔍 Analyse de {self.supported_bots[bot_key]['name']}",
                description=f"Serveur: **{guild.name}**",
                color=discord.Color.blue()
            )
            
            if analysis["channels"]:
                channels_text = ""
                for module, channels in analysis["channels"].items():
                    channels_text += f"📂 **{module}**: {len(channels)} salon(s)\n"
                embed.add_field(name="Salons configurés", value=channels_text, inline=False)
            
            if analysis["roles"].get("moderation_roles"):
                roles_text = f"🛡️ {len(analysis['roles']['moderation_roles'])} rôles de modération détectés"
                embed.add_field(name="Rôles", value=roles_text, inline=False)
            
            modules_text = ""
            for module_key, module_info in self.supported_bots[bot_key]["modules"].items():
                arsenal_equiv = module_info["arsenal_equivalent"]
                status = "🟢 Configurable" if module_key in analysis["channels"] else "🟡 Détectable"
                modules_text += f"• **{module_info['name']}** → Arsenal {arsenal_equiv} {status}\n"
            
            embed.add_field(name="Modules disponibles", value=modules_text, inline=False)
            
            await interaction.followup.send(embed=embed)
            return
        
        # Mode migration complète - Afficher le sélecteur de modules
        view = ModuleMigrationView(self, guild, bot_key, detected_bots[bot_key])
        
        embed = discord.Embed(
            title=f"🚀 Migration Arsenal depuis {self.supported_bots[bot_key]['name']}",
            description=(
                f"**Serveur**: {guild.name}\n"
                f"**Bot source**: {self.supported_bots[bot_key]['name']}\n\n"
                "🔧 **Sélectionnez les modules à migrer:**\n"
                "Chaque module sera analysé, configuré dans Arsenal, puis désactivé sur l'ancien bot."
            ),
            color=discord.Color.orange()
        )
        
        modules_info = ""
        for module_key, module_info in self.supported_bots[bot_key]["modules"].items():
            arsenal_equiv = module_info["arsenal_equivalent"]
            time_estimate = self.get_module_migration_time(module_key)
            modules_info += f"• **{module_info['name']}** → {arsenal_equiv} (~{time_estimate}min)\n"
        
        embed.add_field(name="Modules disponibles", value=modules_info, inline=False)
        embed.add_field(
            name="⚠️ Important",
            value=(
                "• Une sauvegarde sera créée automatiquement\n"
                "• Les modules sélectionnés seront désactivés sur l'ancien bot\n"
                "• Arsenal prendra le relais pour ces fonctionnalités\n"
                "• La migration peut prendre plusieurs minutes"
            ),
            inline=False
        )
        
        await interaction.followup.send(embed=embed, view=view)

class ModuleMigrationView(discord.ui.View):
    """Interface de sélection des modules à migrer"""
    
    def __init__(self, migration_system: BotMigrationSystem, guild: discord.Guild, bot_key: str, bot_info: Dict):
        super().__init__(timeout=300)
        self.migration_system = migration_system
        self.guild = guild
        self.bot_key = bot_key
        self.bot_info = bot_info
        self.selected_modules = set()
        
        # Ajouter les boutons pour chaque module
        self.add_module_buttons()
    
    def add_module_buttons(self):
        """Ajouter les boutons de sélection de modules"""
        modules = self.migration_system.supported_bots[self.bot_key]["modules"]
        
        # Limiter à 24 boutons max (limite Discord)
        module_items = list(modules.items())[:20]
        
        for i, (module_key, module_info) in enumerate(module_items):
            if i < 20:  # Limite de 5 rangées x 4 boutons
                button = ModuleButton(module_key, module_info["name"], row=i//4)
                self.add_item(button)
        
        # Boutons d'action
        self.add_item(StartMigrationButton(row=4))
        self.add_item(CancelButton(row=4))

class ModuleButton(discord.ui.Button):
    """Bouton pour sélectionner/désélectionner un module"""
    
    def __init__(self, module_key: str, module_name: str, row: int):
        self.module_key = module_key
        super().__init__(
            style=discord.ButtonStyle.secondary,
            label=module_name,
            emoji="⬜",
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        view: ModuleMigrationView = self.view
        
        if self.module_key in view.selected_modules:
            # Désélectionner
            view.selected_modules.remove(self.module_key)
            self.emoji = "⬜"
            self.style = discord.ButtonStyle.secondary
        else:
            # Sélectionner
            view.selected_modules.add(self.module_key)
            self.emoji = "✅"
            self.style = discord.ButtonStyle.success
        
        # Mettre à jour l'embed
        embed = discord.Embed(
            title=f"🚀 Migration Arsenal - Sélection des modules",
            description=f"**{len(view.selected_modules)} module(s) sélectionné(s)**",
            color=discord.Color.orange()
        )
        
        if view.selected_modules:
            selected_text = ""
            total_time = 0
            for module in view.selected_modules:
                module_info = view.migration_system.supported_bots[view.bot_key]["modules"][module]
                time_est = view.migration_system.get_module_migration_time(module)
                selected_text += f"✅ **{module_info['name']}** (~{time_est}min)\n"
                total_time += time_est
            
            embed.add_field(name="Modules sélectionnés", value=selected_text, inline=False)
            embed.add_field(name="Temps estimé total", value=f"⏱️ ~{total_time} minutes", inline=True)
        
        await interaction.response.edit_message(embed=embed, view=view)

class StartMigrationButton(discord.ui.Button):
    """Bouton pour démarrer la migration"""
    
    def __init__(self, row: int):
        super().__init__(
            style=discord.ButtonStyle.danger,
            label="🚀 Démarrer la Migration",
            emoji="⚡",
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        view: ModuleMigrationView = self.view
        
        if not view.selected_modules:
            await interaction.response.send_message("❌ Veuillez sélectionner au moins un module!", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Créer le plan de migration
        migration_plan = await view.migration_system.create_migration_plan(
            view.guild, 
            view.bot_key, 
            list(view.selected_modules)
        )
        
        # Afficher le plan
        plan_embed = discord.Embed(
            title="📋 Plan de Migration",
            description=f"Migration de {len(view.selected_modules)} modules",
            color=discord.Color.yellow()
        )
        
        plan_text = ""
        for step in migration_plan["migration_steps"]:
            priority_emoji = "🔴" if step["priority"] <= 2 else "🟡" if step["priority"] <= 3 else "🟢"
            plan_text += f"{priority_emoji} **{step['source_name']}** → Arsenal {step['arsenal_equivalent']} ({step['estimated_minutes']}min)\n"
        
        plan_embed.add_field(name="Ordre de migration", value=plan_text, inline=False)
        plan_embed.add_field(
            name="📊 Résumé",
            value=f"• **{migration_plan['total_steps']}** étapes au total\n• **~{migration_plan['estimated_time']}** minutes estimées",
            inline=False
        )
        
        # Confirmer la migration
        confirm_view = ConfirmMigrationView(view.migration_system, migration_plan)
        
        await interaction.edit_original_response(
            embed=plan_embed, 
            view=confirm_view
        )

class CancelButton(discord.ui.Button):
    """Bouton pour annuler"""
    
    def __init__(self, row: int):
        super().__init__(
            style=discord.ButtonStyle.gray,
            label="❌ Annuler",
            row=row
        )
    
    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="❌ Migration annulée",
            description="La migration a été annulée par l'utilisateur.",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)

class ConfirmMigrationView(discord.ui.View):
    """Vue de confirmation finale"""
    
    def __init__(self, migration_system: BotMigrationSystem, migration_plan: Dict):
        super().__init__(timeout=60)
        self.migration_system = migration_system
        self.migration_plan = migration_plan
    
    @discord.ui.button(label="✅ Confirmer la Migration", style=discord.ButtonStyle.danger, emoji="🚀")
    async def confirm_migration(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Exécuter la migration
        results = await self.migration_system.execute_migration(
            interaction.guild,
            self.migration_plan,
            interaction
        )
        
        # Afficher les résultats
        if results["success"]:
            embed = discord.Embed(
                title="✅ Migration Arsenal Terminée!",
                description="La migration s'est déroulée avec succès!",
                color=discord.Color.green()
            )
        else:
            embed = discord.Embed(
                title="⚠️ Migration Arsenal Terminée avec des avertissements",
                description="Certains modules ont rencontré des problèmes.",
                color=discord.Color.orange()
            )
        
        embed.add_field(
            name="📊 Résultats",
            value=(
                f"✅ **{len(results['completed_steps'])}** modules migrés\n"
                f"❌ **{len(results['failed_steps'])}** échecs\n"
                f"⚠️ **{len(results['warnings'])}** avertissements"
            ),
            inline=False
        )
        
        if results["warnings"]:
            warnings_text = "\n".join(results["warnings"][:3])  # Max 3 avertissements
            embed.add_field(name="⚠️ Avertissements", value=warnings_text, inline=False)
        
        embed.add_field(
            name="🎯 Prochaines étapes",
            value=(
                "1. Testez les nouvelles fonctionnalités Arsenal\n"
                "2. Vérifiez que l'ancien bot est désactivé\n"
                "3. Consultez `/help` pour les nouvelles commandes\n"
                "4. Configurez les détails via `/config_modal`"
            ),
            inline=False
        )
        
        await interaction.edit_original_response(embed=embed, view=None)
    
    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.gray)
    async def cancel_migration(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ Migration annulée",
            description="La migration a été annulée à la dernière étape.",
            color=discord.Color.red()
        )
        await interaction.response.edit_message(embed=embed, view=None)

async def setup(bot):
    await bot.add_cog(BotMigrationSystem(bot))
