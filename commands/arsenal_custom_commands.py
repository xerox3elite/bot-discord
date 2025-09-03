"""
ARSENAL CUSTOM COMMANDS SYSTEM - SYSTÈME DE COMMANDES PERSONNALISÉES
15 commandes gratuites par serveur, illimitées en premium
Par xerox3elite - Arsenal V4.5.1 ULTIMATE
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import aiosqlite
import json
import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

class CustomCommandModal(discord.ui.Modal):
    """Modal pour créer une commande personnalisée"""
    
    def __init__(self, custom_system, guild_id: int, edit_command: str = None):
        super().__init__(title="🛠️ Créer Commande Personnalisée" if not edit_command else f"✏️ Modifier /{edit_command}")
        self.custom_system = custom_system
        self.guild_id = guild_id
        self.edit_command = edit_command
        
        # Nom de la commande
        self.command_name = discord.ui.TextInput(
            label="Nom de la commande",
            placeholder="ma_commande (sans le /)",
            max_length=32,
            required=True,
            default=edit_command or ""
        )
        self.add_item(self.command_name)
        
        # Description
        self.description = discord.ui.TextInput(
            label="Description de la commande",
            placeholder="Description qui apparaîtra dans /help",
            max_length=100,
            required=True
        )
        self.add_item(self.description)
        
        # Réponse
        self.response = discord.ui.TextInput(
            label="Réponse de la commande",
            placeholder="Salut {user} ! Tu es sur {server}. Variables: {user}, {server}, {channel}, {mention}",
            style=discord.TextStyle.paragraph,
            max_length=1500,
            required=True
        )
        self.add_item(self.response)
        
        # Permissions requises
        self.permissions = discord.ui.TextInput(
            label="Permissions requises (optionnel)",
            placeholder="administrator, manage_messages, kick_members... (vide = tous)",
            max_length=100,
            required=False
        )
        self.add_item(self.permissions)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Validation du nom
            cmd_name = self.command_name.value.lower().strip()
            if not re.match(r'^[a-z0-9_]{1,32}$', cmd_name):
                await interaction.followup.send(
                    "❌ **Nom invalide !**\n"
                    "Le nom doit contenir uniquement des lettres minuscules, chiffres et underscores.",
                    ephemeral=True
                )
                return
            
            # Vérifier si la commande existe déjà dans Discord
            builtin_commands = [
                'help', 'config', 'ticket', 'huntroyal', 'balance', 'shop', 'level', 
                'warn', 'ban', 'kick', 'timeout', 'say', 'reglement', 'automod'
            ]
            
            if cmd_name in builtin_commands:
                await interaction.followup.send(
                    f"❌ **Commande réservée !**\n"
                    f"La commande `/{cmd_name}` est une commande système Arsenal.",
                    ephemeral=True
                )
                return
            
            # Vérifier quota gratuit
            current_count = await self.custom_system.get_command_count(self.guild_id)
            is_premium = await self.custom_system.is_premium_guild(self.guild_id)
            
            if not is_premium and not self.edit_command and current_count >= 15:
                await interaction.followup.send(
                    "❌ **Quota dépassé !**\n"
                    f"**{current_count}/15** commandes utilisées (gratuit)\n\n"
                    "🔥 **Arsenal Premium** :\n"
                    "• Commandes **illimitées**\n"
                    "• Variables avancées\n"
                    "• API externes\n"
                    "• Support prioritaire\n\n"
                    "*Contactez les développeurs pour upgrade*",
                    ephemeral=True
                )
                return
            
            # Traiter les permissions
            perm_list = []
            if self.permissions.value.strip():
                perms = [p.strip() for p in self.permissions.value.split(',')]
                valid_perms = [
                    'administrator', 'manage_guild', 'manage_channels', 'manage_roles',
                    'manage_messages', 'kick_members', 'ban_members', 'moderate_members'
                ]
                
                for perm in perms:
                    if perm in valid_perms:
                        perm_list.append(perm)
                    else:
                        await interaction.followup.send(
                            f"❌ **Permission invalide :** `{perm}`\n"
                            f"Permissions valides : {', '.join(valid_perms)}",
                            ephemeral=True
                        )
                        return
            
            # Sauvegarder la commande
            success = await self.custom_system.save_custom_command(
                self.guild_id,
                cmd_name,
                self.description.value,
                self.response.value,
                perm_list,
                interaction.user.id,
                edit_mode=bool(self.edit_command)
            )
            
            if success:
                # Recharger les commandes du bot
                await self.custom_system.reload_guild_commands(self.guild_id)
                
                embed = discord.Embed(
                    title="✅ Commande Sauvegardée !",
                    color=discord.Color.green(),
                    timestamp=datetime.now(timezone.utc)
                )
                
                embed.add_field(
                    name="📝 Commande",
                    value=f"`/{cmd_name}`",
                    inline=True
                )
                
                embed.add_field(
                    name="📋 Description",
                    value=self.description.value,
                    inline=True
                )
                
                embed.add_field(
                    name="🔐 Permissions",
                    value=', '.join(perm_list) if perm_list else "Tous",
                    inline=True
                )
                
                embed.add_field(
                    name="💬 Réponse (preview)",
                    value=self.response.value[:200] + ("..." if len(self.response.value) > 200 else ""),
                    inline=False
                )
                
                quota_text = f"**{current_count + (0 if self.edit_command else 1)}/15** (gratuit)" if not is_premium else "**Illimité** (premium)"
                embed.add_field(
                    name="📊 Quota",
                    value=quota_text,
                    inline=True
                )
                
                embed.set_footer(text="La commande est maintenant active !")
                
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send(
                    "❌ Erreur lors de la sauvegarde de la commande.",
                    ephemeral=True
                )
                
        except Exception as e:
            print(f"❌ [CUSTOM] Erreur modal: {e}")
            await interaction.followup.send(
                "❌ Erreur lors de la création de la commande.",
                ephemeral=True
            )

class CustomCommandView(discord.ui.View):
    """Vue pour gérer les commandes personnalisées"""
    
    def __init__(self, custom_system, guild_id: int, commands_data: List[Dict]):
        super().__init__(timeout=300)
        self.custom_system = custom_system
        self.guild_id = guild_id
        self.commands_data = commands_data
        
        # Select pour choisir une commande à modifier/supprimer
        if commands_data:
            options = []
            for cmd in commands_data[:25]:  # Max 25 options
                options.append(discord.SelectOption(
                    label=f"/{cmd['name']}",
                    description=cmd['description'][:50] + ("..." if len(cmd['description']) > 50 else ""),
                    value=cmd['name']
                ))
            
            self.command_select = discord.ui.Select(
                placeholder="Choisir une commande à modifier/supprimer...",
                options=options
            )
            self.command_select.callback = self.select_command_callback
            self.add_item(self.command_select)

    @discord.ui.button(label="➕ Nouvelle Commande", style=discord.ButtonStyle.primary, emoji="➕")
    async def create_command(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CustomCommandModal(self.custom_system, self.guild_id)
        await interaction.response.send_modal(modal)

    async def select_command_callback(self, interaction: discord.Interaction):
        selected_cmd = self.command_select.values[0]
        
        # Créer vue avec options pour la commande sélectionnée
        view = discord.ui.View(timeout=60)
        
        # Bouton modifier
        edit_button = discord.ui.Button(label="✏️ Modifier", style=discord.ButtonStyle.secondary)
        async def edit_callback(inter):
            # Récupérer données de la commande
            cmd_data = next((cmd for cmd in self.commands_data if cmd['name'] == selected_cmd), None)
            if cmd_data:
                modal = CustomCommandModal(self.custom_system, self.guild_id, selected_cmd)
                # Pré-remplir avec les données existantes
                modal.description.default = cmd_data['description']
                modal.response.default = cmd_data['response']
                modal.permissions.default = ', '.join(cmd_data.get('permissions', []))
                await inter.response.send_modal(modal)
        edit_button.callback = edit_callback
        view.add_item(edit_button)
        
        # Bouton supprimer
        delete_button = discord.ui.Button(label="🗑️ Supprimer", style=discord.ButtonStyle.danger)
        async def delete_callback(inter):
            success = await self.custom_system.delete_custom_command(self.guild_id, selected_cmd)
            if success:
                await self.custom_system.reload_guild_commands(self.guild_id)
                await inter.response.send_message(f"✅ Commande `/{selected_cmd}` supprimée !", ephemeral=True)
            else:
                await inter.response.send_message("❌ Erreur lors de la suppression.", ephemeral=True)
        delete_button.callback = delete_callback
        view.add_item(delete_button)
        
        embed = discord.Embed(
            title=f"🛠️ Gestion de /{selected_cmd}",
            description="Que souhaitez-vous faire avec cette commande ?",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ArsenalCustomCommands(commands.Cog):
    """Système de commandes personnalisées ultra-avancé"""
    
    def __init__(self, bot):
        self.bot = bot
        self.setup_database.start()
        # Cache des commandes par guilde
        self.guild_commands_cache = {}
    
    @tasks.loop(count=1)
    async def setup_database(self):
        """Initialise la base de données"""
        try:
            async with aiosqlite.connect("data/custom_commands.db") as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS custom_commands (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        command_name TEXT NOT NULL,
                        description TEXT NOT NULL,
                        response TEXT NOT NULL,
                        permissions TEXT DEFAULT '[]',
                        created_by INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT,
                        usage_count INTEGER DEFAULT 0,
                        UNIQUE(guild_id, command_name)
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS guild_settings (
                        guild_id INTEGER PRIMARY KEY,
                        is_premium BOOLEAN DEFAULT FALSE,
                        premium_until TEXT,
                        settings TEXT DEFAULT '{}'
                    )
                """)
                
                await db.commit()
                print("✅ [CUSTOM] Base de données initialisée")
                
        except Exception as e:
            print(f"❌ [CUSTOM] Erreur setup DB: {e}")
    
    @setup_database.before_loop
    async def before_setup_database(self):
        await self.bot.wait_until_ready()

    async def get_command_count(self, guild_id: int) -> int:
        """Récupère le nombre de commandes d'une guilde"""
        try:
            async with aiosqlite.connect("data/custom_commands.db") as db:
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM custom_commands WHERE guild_id = ?",
                    (guild_id,)
                )
                result = await cursor.fetchone()
                return result[0] if result else 0
        except Exception as e:
            print(f"❌ [CUSTOM] Erreur count: {e}")
            return 0

    async def is_premium_guild(self, guild_id: int) -> bool:
        """Vérifie si une guilde est premium"""
        try:
            async with aiosqlite.connect("data/custom_commands.db") as db:
                cursor = await db.execute(
                    "SELECT is_premium FROM guild_settings WHERE guild_id = ?",
                    (guild_id,)
                )
                result = await cursor.fetchone()
                return bool(result[0]) if result else False
        except Exception as e:
            print(f"❌ [CUSTOM] Erreur premium check: {e}")
            return False

    async def save_custom_command(self, guild_id: int, name: str, description: str, 
                                response: str, permissions: List[str], created_by: int, 
                                edit_mode: bool = False) -> bool:
        """Sauvegarde une commande personnalisée"""
        try:
            async with aiosqlite.connect("data/custom_commands.db") as db:
                if edit_mode:
                    await db.execute("""
                        UPDATE custom_commands 
                        SET description = ?, response = ?, permissions = ?, updated_at = ?
                        WHERE guild_id = ? AND command_name = ?
                    """, (description, response, json.dumps(permissions), 
                         datetime.now(timezone.utc).isoformat(), guild_id, name))
                else:
                    await db.execute("""
                        INSERT INTO custom_commands 
                        (guild_id, command_name, description, response, permissions, created_by, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (guild_id, name, description, response, json.dumps(permissions), 
                         created_by, datetime.now(timezone.utc).isoformat()))
                
                await db.commit()
                return True
        except Exception as e:
            print(f"❌ [CUSTOM] Erreur sauvegarde: {e}")
            return False

    async def delete_custom_command(self, guild_id: int, name: str) -> bool:
        """Supprime une commande personnalisée"""
        try:
            async with aiosqlite.connect("data/custom_commands.db") as db:
                await db.execute(
                    "DELETE FROM custom_commands WHERE guild_id = ? AND command_name = ?",
                    (guild_id, name)
                )
                await db.commit()
                return True
        except Exception as e:
            print(f"❌ [CUSTOM] Erreur suppression: {e}")
            return False

    async def get_guild_commands(self, guild_id: int) -> List[Dict]:
        """Récupère toutes les commandes d'une guilde"""
        try:
            async with aiosqlite.connect("data/custom_commands.db") as db:
                cursor = await db.execute("""
                    SELECT command_name, description, response, permissions, usage_count, created_at
                    FROM custom_commands 
                    WHERE guild_id = ? 
                    ORDER BY command_name
                """, (guild_id,))
                
                rows = await cursor.fetchall()
                
                commands = []
                for row in rows:
                    commands.append({
                        'name': row[0],
                        'description': row[1],
                        'response': row[2],
                        'permissions': json.loads(row[3]) if row[3] else [],
                        'usage_count': row[4],
                        'created_at': row[5]
                    })
                
                return commands
        except Exception as e:
            print(f"❌ [CUSTOM] Erreur récupération: {e}")
            return []

    async def reload_guild_commands(self, guild_id: int):
        """Recharge les commandes d'une guilde dans le cache"""
        try:
            commands = await self.get_guild_commands(guild_id)
            self.guild_commands_cache[guild_id] = commands
            print(f"🔄 [CUSTOM] {len(commands)} commandes rechargées pour guilde {guild_id}")
        except Exception as e:
            print(f"❌ [CUSTOM] Erreur reload: {e}")

    async def process_custom_command(self, interaction: discord.Interaction, command_name: str):
        """Traite l'exécution d'une commande personnalisée"""
        try:
            guild_id = interaction.guild.id
            
            # Récupérer depuis le cache ou la DB
            if guild_id not in self.guild_commands_cache:
                await self.reload_guild_commands(guild_id)
            
            commands = self.guild_commands_cache.get(guild_id, [])
            cmd_data = next((cmd for cmd in commands if cmd['name'] == command_name), None)
            
            if not cmd_data:
                return False
            
            # Vérifier permissions
            if cmd_data['permissions']:
                user_perms = interaction.user.guild_permissions
                has_permission = False
                
                for perm in cmd_data['permissions']:
                    if hasattr(user_perms, perm) and getattr(user_perms, perm):
                        has_permission = True
                        break
                
                if not has_permission:
                    await interaction.response.send_message(
                        f"❌ Vous n'avez pas la permission d'utiliser `/{command_name}`.",
                        ephemeral=True
                    )
                    return True
            
            # Traiter les variables dans la réponse
            response = cmd_data['response']
            
            variables = {
                '{user}': interaction.user.display_name,
                '{mention}': interaction.user.mention,
                '{server}': interaction.guild.name,
                '{channel}': interaction.channel.name,
                '{date}': datetime.now().strftime('%d/%m/%Y'),
                '{time}': datetime.now().strftime('%H:%M:%S'),
                '{member_count}': str(interaction.guild.member_count)
            }
            
            for var, value in variables.items():
                response = response.replace(var, value)
            
            # Envoyer la réponse
            if len(response) <= 2000:
                await interaction.response.send_message(response)
            else:
                # Si trop long, utiliser un embed
                embed = discord.Embed(
                    title=f"📝 Réponse de /{command_name}",
                    description=response[:4000],
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed)
            
            # Incrémenter compteur d'usage
            await self.increment_usage(guild_id, command_name)
            
            return True
            
        except Exception as e:
            print(f"❌ [CUSTOM] Erreur execution: {e}")
            return False

    async def increment_usage(self, guild_id: int, command_name: str):
        """Incrémente le compteur d'usage d'une commande"""
        try:
            async with aiosqlite.connect("data/custom_commands.db") as db:
                await db.execute("""
                    UPDATE custom_commands 
                    SET usage_count = usage_count + 1 
                    WHERE guild_id = ? AND command_name = ?
                """, (guild_id, command_name))
                await db.commit()
        except Exception as e:
            print(f"❌ [CUSTOM] Erreur usage: {e}")

    # Commandes slash
    custom_group = app_commands.Group(name="custom", description="🛠️ Gestion des commandes personnalisées")

    @custom_group.command(name="manage", description="🛠️ Gérer les commandes personnalisées")
    async def custom_manage(self, interaction: discord.Interaction):
        """Interface de gestion des commandes personnalisées"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Seuls les **administrateurs** peuvent gérer les commandes personnalisées.",
                ephemeral=True
            )
            return
        
        try:
            guild_id = interaction.guild.id
            commands = await self.get_guild_commands(guild_id)
            command_count = len(commands)
            is_premium = await self.is_premium_guild(guild_id)
            
            embed = discord.Embed(
                title="🛠️ Gestion Commandes Personnalisées",
                description="**Créez vos propres commandes Discord !**",
                color=discord.Color.gold()
            )
            
            embed.add_field(
                name="📊 **Statut actuel**",
                value=f"**{command_count}/{'∞' if is_premium else '15'}** commandes utilisées\n"
                      f"**Statut :** {'🔥 Premium' if is_premium else '🆓 Gratuit'}",
                inline=True
            )
            
            if commands:
                command_list = '\n'.join([f"`/{cmd['name']}` - {cmd['description'][:30]}{'...' if len(cmd['description']) > 30 else ''}" 
                                        for cmd in commands[:10]])
                if len(commands) > 10:
                    command_list += f"\n*... et {len(commands) - 10} autres*"
                
                embed.add_field(
                    name="📝 **Commandes existantes**",
                    value=command_list,
                    inline=False
                )
            else:
                embed.add_field(
                    name="📝 **Commandes existantes**",
                    value="*Aucune commande personnalisée*",
                    inline=False
                )
            
            embed.add_field(
                name="✨ **Fonctionnalités**",
                value="• Variables dynamiques (`{user}`, `{server}`, etc.)\n"
                      "• Permissions personnalisées\n"
                      "• Réponses jusqu'à 1500 caractères\n"
                      "• Interface simple et intuitive",
                inline=False
            )
            
            if not is_premium:
                embed.add_field(
                    name="🔥 **Arsenal Premium**",
                    value="• **Commandes illimitées**\n"
                          "• Variables avancées\n"
                          "• Intégration API externes\n"
                          "• Support prioritaire",
                    inline=False
                )
            
            view = CustomCommandView(self, guild_id, commands)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            print(f"❌ [CUSTOM] Erreur manage: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de l'accès à la gestion des commandes.",
                ephemeral=True
            )

    @custom_group.command(name="list", description="📋 Lister toutes les commandes personnalisées")
    async def custom_list(self, interaction: discord.Interaction):
        """Liste toutes les commandes personnalisées du serveur"""
        try:
            guild_id = interaction.guild.id
            commands = await self.get_guild_commands(guild_id)
            
            if not commands:
                await interaction.response.send_message(
                    "📝 **Aucune commande personnalisée**\n"
                    "Utilisez `/custom manage` pour en créer !",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title=f"📋 Commandes Personnalisées ({len(commands)})",
                description=f"**Serveur :** {interaction.guild.name}",
                color=discord.Color.blue()
            )
            
            for i, cmd in enumerate(commands[:10]):  # Max 10 par page
                usage_text = f"📈 {cmd['usage_count']} utilisations"
                perm_text = f"🔐 {', '.join(cmd['permissions'])}" if cmd['permissions'] else "🔓 Tous"
                
                embed.add_field(
                    name=f"/{cmd['name']}",
                    value=f"**Description :** {cmd['description']}\n"
                          f"{usage_text} • {perm_text}",
                    inline=True
                )
            
            if len(commands) > 10:
                embed.set_footer(text=f"... et {len(commands) - 10} autres commandes")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"❌ [CUSTOM] Erreur list: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la récupération des commandes.",
                ephemeral=True
            )

    @custom_group.command(name="stats", description="📊 Statistiques des commandes personnalisées")
    async def custom_stats(self, interaction: discord.Interaction):
        """Affiche les statistiques des commandes personnalisées"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Seuls les **administrateurs** peuvent voir les statistiques.",
                ephemeral=True
            )
            return
        
        try:
            guild_id = interaction.guild.id
            commands = await self.get_guild_commands(guild_id)
            
            if not commands:
                await interaction.response.send_message(
                    "📊 **Aucune statistique disponible**\n"
                    "Créez des commandes avec `/custom manage` !",
                    ephemeral=True
                )
                return
            
            # Calculer statistiques
            total_usage = sum(cmd['usage_count'] for cmd in commands)
            most_used = max(commands, key=lambda x: x['usage_count']) if commands else None
            least_used = min(commands, key=lambda x: x['usage_count']) if commands else None
            is_premium = await self.is_premium_guild(guild_id)
            
            embed = discord.Embed(
                title="📊 Statistiques Commandes Personnalisées",
                description=f"**Serveur :** {interaction.guild.name}",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="📈 **Utilisation générale**",
                value=f"**Commandes créées :** {len(commands)}\n"
                      f"**Utilisations totales :** {total_usage}\n"
                      f"**Moyenne par commande :** {total_usage // len(commands) if commands else 0}",
                inline=True
            )
            
            embed.add_field(
                name="🎯 **Statut compte**",
                value=f"**Type :** {'🔥 Premium' if is_premium else '🆓 Gratuit'}\n"
                      f"**Limite :** {'Illimitées' if is_premium else f'{len(commands)}/15'}",
                inline=True
            )
            
            if most_used:
                embed.add_field(
                    name="🏆 **Plus utilisée**",
                    value=f"`/{most_used['name']}`\n{most_used['usage_count']} utilisations",
                    inline=True
                )
            
            if least_used and least_used != most_used:
                embed.add_field(
                    name="📉 **Moins utilisée**",
                    value=f"`/{least_used['name']}`\n{least_used['usage_count']} utilisations",
                    inline=True
                )
            
            # Top 5 des commandes
            top_commands = sorted(commands, key=lambda x: x['usage_count'], reverse=True)[:5]
            if top_commands:
                top_text = '\n'.join([f"**{i+1}.** `/{cmd['name']}` - {cmd['usage_count']} fois" 
                                    for i, cmd in enumerate(top_commands)])
                embed.add_field(
                    name="🎖️ **Top 5 commandes**",
                    value=top_text,
                    inline=False
                )
            
            embed.set_footer(text="Utilisez /custom manage pour créer plus de commandes !")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"❌ [CUSTOM] Erreur stats: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors du calcul des statistiques.",
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(ArsenalCustomCommands(bot))
