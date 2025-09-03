import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import aiosqlite
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
import os

class TicketCategorySelect(discord.ui.Select):
    """Select pour choisir la catégorie de ticket"""
    def __init__(self, categories: Dict[str, Dict]):
        options = []
        for category_id, category_data in categories.items():
            options.append(discord.SelectOption(
                label=category_data['name'],
                description=category_data['description'],
                emoji=category_data.get('emoji', '🎫'),
                value=category_id
            ))
        
        super().__init__(placeholder="Choisissez une catégorie de ticket...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        # Récupérer la configuration de la catégorie sélectionnée
        ticket_system = self.view.ticket_system
        guild_config = await ticket_system.get_guild_config(interaction.guild.id)
        category_config = guild_config.get('ticket_categories', {}).get(self.values[0], {})
        
        # Créer le modal approprié
        modal = AdvancedTicketModal(ticket_system, self.values[0], category_config)
        await interaction.response.send_modal(modal)

class TicketCategoryView(discord.ui.View):
    """Vue pour la sélection de catégorie"""
    def __init__(self, ticket_system, categories: Dict[str, Dict]):
        super().__init__(timeout=300)
        self.ticket_system = ticket_system
        self.add_item(TicketCategorySelect(categories))

class AdvancedTicketModal(discord.ui.Modal):
    """Modal avancé pour création de tickets"""
    def __init__(self, ticket_system, category_id: str, category_config: Dict):
        super().__init__(title=f"Nouveau Ticket - {category_config.get('name', 'Support')}")
        self.ticket_system = ticket_system
        self.category_id = category_id
        self.category_config = category_config
        
        # Champs dynamiques selon la catégorie
        self.subject = discord.ui.TextInput(
            label="Sujet du ticket",
            placeholder="Décrivez brièvement votre demande...",
            max_length=100,
            required=True
        )
        self.add_item(self.subject)
        
        self.description = discord.ui.TextInput(
            label="Description détaillée",
            placeholder="Expliquez votre problème ou demande en détail...",
            style=discord.TextStyle.paragraph,
            max_length=1000,
            required=True
        )
        self.add_item(self.description)
        
        # Champs spécifiques selon la catégorie
        if category_id == "huntroyal":
            self.game_mode = discord.ui.TextInput(
                label="Mode de jeu",
                placeholder="BR, Duos, Trios, etc.",
                max_length=50,
                required=False
            )
            self.add_item(self.game_mode)
            
            self.player_id = discord.ui.TextInput(
                label="ID Joueur Hunt Royal",
                placeholder="Votre ID dans le jeu...",
                max_length=50,
                required=False
            )
            self.add_item(self.player_id)
        
        elif category_id == "arsenal_support":
            self.error_type = discord.ui.TextInput(
                label="Type d'erreur",
                placeholder="Bot, Commande, Permission, etc.",
                max_length=50,
                required=False
            )
            self.add_item(self.error_type)
        
        elif category_id == "absence":
            self.start_date = discord.ui.TextInput(
                label="Date de début (JJ/MM/AAAA)",
                placeholder="01/01/2024",
                max_length=10,
                required=True
            )
            self.add_item(self.start_date)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Créer le ticket
            ticket_data = {
                'subject': self.subject.value,
                'description': self.description.value,
                'category_id': self.category_id,
                'guild_id': interaction.guild.id,
                'user_id': interaction.user.id,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Ajouter données spécifiques
            if hasattr(self, 'game_mode') and self.game_mode.value:
                ticket_data['game_mode'] = self.game_mode.value
            if hasattr(self, 'player_id') and self.player_id.value:
                ticket_data['player_id'] = self.player_id.value
            if hasattr(self, 'error_type') and self.error_type.value:
                ticket_data['error_type'] = self.error_type.value
            if hasattr(self, 'start_date') and self.start_date.value:
                ticket_data['start_date'] = self.start_date.value
            
            ticket_id = await self.ticket_system.create_ticket(interaction, ticket_data)
            
            if ticket_id:
                await interaction.followup.send(
                    f"✅ **Ticket #{ticket_id} créé avec succès !**\n"
                    f"📝 **Sujet:** {self.subject.value}\n"
                    f"📂 **Catégorie:** {self.category_config.get('name', 'Support')}",
                    ephemeral=True
                )
            else:
                await interaction.followup.send("❌ Erreur lors de la création du ticket.", ephemeral=True)
                
        except Exception as e:
            print(f"❌ [TICKET] Erreur modal: {e}")
            await interaction.followup.send("❌ Erreur lors de la création du ticket.", ephemeral=True)

class TicketControlView(discord.ui.View):
    """Vue de contrôle pour les tickets"""
    def __init__(self, ticket_system, ticket_id: int, ticket_data: Dict):
        super().__init__(timeout=None)
        self.ticket_system = ticket_system
        self.ticket_id = ticket_id
        self.ticket_data = ticket_data
        
        # Personnaliser les boutons selon la catégorie
        category_id = ticket_data.get('category_id', 'general')
        
        if category_id == "huntroyal":
            self.add_huntroyal_buttons()
        elif category_id == "arsenal_support":
            self.add_support_buttons()
        else:
            self.add_default_buttons()
    
    def add_default_buttons(self):
        """Boutons par défaut"""
        self.add_item(discord.ui.Button(
            label="✅ Résoudre",
            style=discord.ButtonStyle.success,
            custom_id=f"resolve_{self.ticket_id}"
        ))
        self.add_item(discord.ui.Button(
            label="🔒 Fermer",
            style=discord.ButtonStyle.danger,
            custom_id=f"close_{self.ticket_id}"
        ))
        self.add_item(discord.ui.Button(
            label="🏷️ Étiquette",
            style=discord.ButtonStyle.secondary,
            custom_id=f"label_{self.ticket_id}"
        ))
    
    def add_huntroyal_buttons(self):
        """Boutons spécifiques Hunt Royal"""
        self.add_item(discord.ui.Button(
            label="🎮 Vérifier Joueur",
            style=discord.ButtonStyle.primary,
            custom_id=f"check_player_{self.ticket_id}"
        ))
        self.add_item(discord.ui.Button(
            label="📊 Stats Joueur",
            style=discord.ButtonStyle.secondary,
            custom_id=f"player_stats_{self.ticket_id}"
        ))
        self.add_default_buttons()
    
    def add_support_buttons(self):
        """Boutons spécifiques support Arsenal"""
        self.add_item(discord.ui.Button(
            label="🔧 Diagnostic",
            style=discord.ButtonStyle.primary,
            custom_id=f"diagnostic_{self.ticket_id}"
        ))
        self.add_item(discord.ui.Button(
            label="📚 Doc",
            style=discord.ButtonStyle.secondary,
            custom_id=f"documentation_{self.ticket_id}"
        ))
        self.add_default_buttons()

    @discord.ui.button(label="👁️ Transcript", style=discord.ButtonStyle.secondary, emoji="📄")
    async def create_transcript(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Générer transcript
        transcript = await self.ticket_system.generate_transcript(interaction.channel)
        
        # Envoyer en DM au créateur du ticket
        try:
            user = interaction.guild.get_member(self.ticket_data['user_id'])
            if user:
                embed = discord.Embed(
                    title=f"📄 Transcript du Ticket #{self.ticket_id}",
                    description=f"**Sujet:** {self.ticket_data.get('subject', 'N/A')}\n"
                               f"**Catégorie:** {self.ticket_data.get('category_id', 'N/A')}",
                    color=0x3498db,
                    timestamp=datetime.now(timezone.utc)
                )
                
                # Créer fichier transcript
                with open(f"temp_transcript_{self.ticket_id}.txt", "w", encoding="utf-8") as f:
                    f.write(transcript)
                
                await user.send(embed=embed, file=discord.File(f"temp_transcript_{self.ticket_id}.txt"))
                
                # Supprimer fichier temporaire
                os.remove(f"temp_transcript_{self.ticket_id}.txt")
                
            await interaction.followup.send("✅ Transcript envoyé en privé au créateur du ticket.")
            
        except Exception as e:
            print(f"❌ [TICKET] Erreur transcript: {e}")
            await interaction.followup.send("❌ Erreur lors de l'envoi du transcript.")

class AdvancedTicketSystem(commands.Cog):
    """Système de tickets ultra-avancé avec groupes et modals"""
    
    def __init__(self, bot):
        self.bot = bot
        self.setup_database.start()
        self.check_ticket_reminders.start()
    
    @tasks.loop(count=1)
    async def setup_database(self):
        """Initialise les tables de base de données"""
        try:
            async with aiosqlite.connect("data/advanced_tickets.db") as db:
                # Table principale des tickets
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS tickets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_id INTEGER NOT NULL,
                        guild_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        channel_id INTEGER,
                        category_id TEXT NOT NULL,
                        subject TEXT NOT NULL,
                        description TEXT NOT NULL,
                        status TEXT DEFAULT 'open',
                        priority TEXT DEFAULT 'normal',
                        assigned_to INTEGER,
                        created_at TEXT NOT NULL,
                        updated_at TEXT,
                        closed_at TEXT,
                        extra_data TEXT,
                        tags TEXT
                    )
                """)
                
                # Table de configuration des guildes
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS guild_configs (
                        guild_id INTEGER PRIMARY KEY,
                        config_data TEXT NOT NULL
                    )
                """)
                
                # Table des messages de tickets
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS ticket_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_id INTEGER NOT NULL,
                        message_id INTEGER NOT NULL,
                        author_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        FOREIGN KEY (ticket_id) REFERENCES tickets (ticket_id)
                    )
                """)
                
                await db.commit()
                print("✅ [TICKET] Base de données initialisée")
                
        except Exception as e:
            print(f"❌ [TICKET] Erreur setup DB: {e}")
    
    @setup_database.before_loop
    async def before_setup_database(self):
        await self.bot.wait_until_ready()
    
    @tasks.loop(hours=6)
    async def check_ticket_reminders(self):
        """Vérifie les tickets nécessitant des rappels"""
        try:
            async with aiosqlite.connect("data/advanced_tickets.db") as db:
                # Tickets ouverts depuis plus de 24h sans réponse
                cutoff_time = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
                
                cursor = await db.execute("""
                    SELECT ticket_id, guild_id, user_id, channel_id, subject 
                    FROM tickets 
                    WHERE status = 'open' AND created_at < ? AND updated_at IS NULL
                """, (cutoff_time,))
                
                old_tickets = await cursor.fetchall()
                
                for ticket_id, guild_id, user_id, channel_id, subject in old_tickets:
                    await self.send_ticket_reminder(guild_id, channel_id, ticket_id, subject)
                    
        except Exception as e:
            print(f"❌ [TICKET] Erreur rappels: {e}")
    
    async def send_ticket_reminder(self, guild_id: int, channel_id: int, ticket_id: int, subject: str):
        """Envoie un rappel pour un ticket"""
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return
            
            channel = guild.get_channel(channel_id)
            if not channel:
                return
            
            embed = discord.Embed(
                title="⏰ Rappel de Ticket",
                description=f"Ce ticket n'a pas eu de réponse depuis 24 heures.",
                color=0xffa500
            )
            embed.add_field(name="Ticket", value=f"#{ticket_id}", inline=True)
            embed.add_field(name="Sujet", value=subject, inline=True)
            
            await channel.send(embed=embed)
            
        except Exception as e:
            print(f"❌ [TICKET] Erreur rappel: {e}")

    async def get_guild_config(self, guild_id: int) -> Dict:
        """Récupère la configuration d'une guilde"""
        try:
            async with aiosqlite.connect("data/advanced_tickets.db") as db:
                cursor = await db.execute(
                    "SELECT config_data FROM guild_configs WHERE guild_id = ?",
                    (guild_id,)
                )
                result = await cursor.fetchone()
                
                if result:
                    return json.loads(result[0])
                else:
                    # Configuration par défaut
                    default_config = {
                        'ticket_categories': {
                            'general': {
                                'name': '📋 Support Général',
                                'description': 'Questions générales et support',
                                'emoji': '📋'
                            },
                            'huntroyal': {
                                'name': '🎮 Hunt Royal',
                                'description': 'Support pour le jeu Hunt Royal',
                                'emoji': '🎮'
                            },
                            'arsenal_support': {
                                'name': '🤖 Support Arsenal',
                                'description': 'Aide avec le bot Arsenal',
                                'emoji': '🤖'
                            },
                            'absence': {
                                'name': '📅 Demande d\'Absence',
                                'description': 'Signaler une absence',
                                'emoji': '📅'
                            }
                        },
                        'ticket_channel': None,
                        'staff_roles': [],
                        'log_channel': None
                    }
                    await self.save_guild_config(guild_id, default_config)
                    return default_config
                    
        except Exception as e:
            print(f"❌ [TICKET] Erreur config: {e}")
            return {}

    async def save_guild_config(self, guild_id: int, config: Dict):
        """Sauvegarde la configuration d'une guilde"""
        try:
            async with aiosqlite.connect("data/advanced_tickets.db") as db:
                await db.execute("""
                    INSERT OR REPLACE INTO guild_configs (guild_id, config_data)
                    VALUES (?, ?)
                """, (guild_id, json.dumps(config, ensure_ascii=False)))
                await db.commit()
        except Exception as e:
            print(f"❌ [TICKET] Erreur sauvegarde config: {e}")

    async def get_next_ticket_id(self, guild_id: int) -> int:
        """Récupère le prochain ID de ticket pour une guilde"""
        try:
            async with aiosqlite.connect("data/advanced_tickets.db") as db:
                cursor = await db.execute(
                    "SELECT MAX(ticket_id) FROM tickets WHERE guild_id = ?",
                    (guild_id,)
                )
                result = await cursor.fetchone()
                return (result[0] or 0) + 1
        except Exception as e:
            print(f"❌ [TICKET] Erreur next ID: {e}")
            return 1

    async def create_ticket(self, interaction: discord.Interaction, ticket_data: Dict) -> Optional[int]:
        """Crée un nouveau ticket"""
        try:
            guild = interaction.guild
            user = interaction.user
            
            # Récupérer config
            config = await self.get_guild_config(guild.id)
            category_config = config.get('ticket_categories', {}).get(ticket_data['category_id'], {})
            
            # Générer ID ticket
            ticket_id = await self.get_next_ticket_id(guild.id)
            
            # Créer catégorie si nécessaire
            category = await self.get_or_create_ticket_category(guild)
            
            # Permissions du salon
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
            }
            
            # Ajouter staff
            for role_id in config.get('staff_roles', []):
                role = guild.get_role(role_id)
                if role:
                    overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
            # Créer salon
            channel_name = f"{ticket_data['category_id']}-{user.display_name}-{ticket_id}"
            ticket_channel = await guild.create_text_channel(
                name=channel_name[:50],  # Limiter la longueur
                category=category,
                overwrites=overwrites,
                topic=f"Ticket #{ticket_id} - {ticket_data['subject']}"
            )
            
            # Embed du ticket
            embed = discord.Embed(
                title=f"🎫 Ticket #{ticket_id}",
                description=f"**{category_config.get('name', 'Support')}**",
                color=0x3498db,
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.add_field(
                name="👤 Créé par",
                value=f"{user.mention}\n`{user.id}`",
                inline=True
            )
            
            embed.add_field(
                name="📝 Sujet",
                value=ticket_data['subject'],
                inline=True
            )
            
            embed.add_field(
                name="📋 Description",
                value=ticket_data['description'][:500] + ("..." if len(ticket_data['description']) > 500 else ""),
                inline=False
            )
            
            # Ajouter champs spécifiques
            if 'game_mode' in ticket_data:
                embed.add_field(name="🎮 Mode de jeu", value=ticket_data['game_mode'], inline=True)
            if 'player_id' in ticket_data:
                embed.add_field(name="🆔 ID Joueur", value=ticket_data['player_id'], inline=True)
            if 'error_type' in ticket_data:
                embed.add_field(name="⚠️ Type d'erreur", value=ticket_data['error_type'], inline=True)
            
            # Vue de contrôle
            view = TicketControlView(self, ticket_id, ticket_data)
            
            await ticket_channel.send(
                content=f"{user.mention}, votre ticket a été créé !",
                embed=embed, 
                view=view
            )
            
            # Sauvegarder en BDD
            ticket_data['ticket_id'] = ticket_id
            ticket_data['channel_id'] = ticket_channel.id
            await self.save_ticket_to_db(ticket_data)
            
            return ticket_id
            
        except Exception as e:
            print(f"❌ [TICKET] Erreur création: {e}")
            return None

    async def get_or_create_ticket_category(self, guild: discord.Guild):
        """Récupère ou crée la catégorie des tickets"""
        try:
            # Chercher catégorie existante
            for category in guild.categories:
                if "ticket" in category.name.lower():
                    return category
            
            # Créer nouvelle catégorie
            return await guild.create_category(
                name="🎫 Tickets Arsenal",
                overwrites={
                    guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    guild.me: discord.PermissionOverwrite(read_messages=True, manage_channels=True)
                }
            )
            
        except Exception as e:
            print(f"❌ [TICKET] Erreur catégorie: {e}")
            return None

    async def save_ticket_to_db(self, ticket_data: Dict):
        """Sauvegarde le ticket en base de données"""
        try:
            async with aiosqlite.connect("data/advanced_tickets.db") as db:
                await db.execute("""
                    INSERT INTO tickets (
                        ticket_id, guild_id, user_id, channel_id, category_id, 
                        subject, description, created_at, extra_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    ticket_data['ticket_id'],
                    ticket_data['guild_id'],
                    ticket_data['user_id'],
                    ticket_data.get('channel_id'),
                    ticket_data['category_id'],
                    ticket_data['subject'],
                    ticket_data['description'],
                    ticket_data['created_at'],
                    json.dumps({k: v for k, v in ticket_data.items() 
                              if k not in ['ticket_id', 'guild_id', 'user_id', 'channel_id', 
                                         'category_id', 'subject', 'description', 'created_at']})
                ))
                await db.commit()
        except Exception as e:
            print(f"❌ [TICKET] Erreur sauvegarde: {e}")

    async def generate_transcript(self, channel: discord.TextChannel) -> str:
        """Génère un transcript du canal"""
        try:
            messages = []
            async for message in channel.history(limit=None, oldest_first=True):
                timestamp = message.created_at.strftime("%d/%m/%Y %H:%M:%S")
                author = f"{message.author.display_name} ({message.author.id})"
                content = message.content or "[Embed/Fichier]"
                messages.append(f"[{timestamp}] {author}: {content}")
            
            return "\n".join(messages)
            
        except Exception as e:
            print(f"❌ [TICKET] Erreur transcript: {e}")
            return f"Erreur lors de la génération du transcript: {e}"

    # Commandes slash
    @app_commands.command(name="ticket", description="Créer un nouveau ticket")
    async def ticket_command(self, interaction: discord.Interaction):
        """Commande pour créer un ticket"""
        try:
            config = await self.get_guild_config(interaction.guild.id)
            categories = config.get('ticket_categories', {})
            
            if not categories:
                await interaction.response.send_message(
                    "❌ Aucune catégorie de ticket configurée.", 
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="🎫 Création de Ticket",
                description="Choisissez une catégorie pour votre ticket :",
                color=0x3498db
            )
            
            view = TicketCategoryView(self, categories)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            print(f"❌ [TICKET] Erreur commande: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de l'ouverture du système de tickets.", 
                ephemeral=True
            )

    ticket_group = app_commands.Group(name="ticket", description="Gestion des tickets")

    @ticket_group.command(name="setup", description="Configurer le système de tickets")
    @app_commands.describe(
        ticket_channel="Canal pour les boutons de création de tickets",
        log_channel="Canal pour les logs des tickets"
    )
    async def ticket_setup(
        self, 
        interaction: discord.Interaction,
        ticket_channel: Optional[discord.TextChannel] = None,
        log_channel: Optional[discord.TextChannel] = None
    ):
        """Configuration du système de tickets"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ Vous devez avoir la permission `Gérer le serveur`.", 
                ephemeral=True
            )
            return
        
        try:
            config = await self.get_guild_config(interaction.guild.id)
            
            if ticket_channel:
                config['ticket_channel'] = ticket_channel.id
            if log_channel:
                config['log_channel'] = log_channel.id
            
            await self.save_guild_config(interaction.guild.id, config)
            
            embed = discord.Embed(
                title="✅ Configuration des Tickets",
                description="Le système de tickets a été configuré !",
                color=0x00ff00
            )
            
            if ticket_channel:
                embed.add_field(
                    name="📋 Canal des tickets", 
                    value=ticket_channel.mention, 
                    inline=True
                )
            if log_channel:
                embed.add_field(
                    name="📊 Canal des logs", 
                    value=log_channel.mention, 
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"❌ [TICKET] Erreur setup: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la configuration.", 
                ephemeral=True
            )

    @ticket_group.command(name="panel", description="Créer un panneau de création de tickets")
    async def ticket_panel(self, interaction: discord.Interaction):
        """Crée un panneau de création de tickets"""
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message(
                "❌ Vous devez avoir la permission `Gérer le serveur`.", 
                ephemeral=True
            )
            return
        
        try:
            config = await self.get_guild_config(interaction.guild.id)
            categories = config.get('ticket_categories', {})
            
            embed = discord.Embed(
                title="🎫 Système de Tickets Arsenal",
                description="Cliquez sur le bouton ci-dessous pour créer un ticket selon votre besoin.",
                color=0x3498db
            )
            
            embed.add_field(
                name="📋 Catégories disponibles",
                value="\n".join([f"{cat['emoji']} **{cat['name']}** - {cat['description']}" 
                               for cat in categories.values()]),
                inline=False
            )
            
            embed.add_field(
                name="ℹ️ Informations",
                value="• Un salon privé sera créé pour votre ticket\n"
                      "• Seuls vous et le staff peuvent voir votre ticket\n"
                      "• Soyez précis dans votre demande",
                inline=False
            )
            
            class QuickTicketView(discord.ui.View):
                def __init__(self, ticket_system):
                    super().__init__(timeout=None)
                    self.ticket_system = ticket_system
                
                @discord.ui.button(label="🎫 Créer un Ticket", style=discord.ButtonStyle.primary)
                async def create_ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                    categories = await self.ticket_system.get_guild_config(interaction.guild.id)
                    categories = categories.get('ticket_categories', {})
                    
                    embed = discord.Embed(
                        title="🎫 Création de Ticket",
                        description="Choisissez une catégorie pour votre ticket :",
                        color=0x3498db
                    )
                    
                    view = TicketCategoryView(self.ticket_system, categories)
                    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
            view = QuickTicketView(self)
            await interaction.response.send_message(embed=embed, view=view)
            
        except Exception as e:
            print(f"❌ [TICKET] Erreur panel: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la création du panneau.", 
                ephemeral=True
            )

    @ticket_group.command(name="close", description="Fermer le ticket actuel")
    async def close_ticket(self, interaction: discord.Interaction, reason: Optional[str] = None):
        """Ferme le ticket actuel"""
        try:
            # Vérifier que c'est un canal de ticket
            if not interaction.channel.name.startswith(('general-', 'huntroyal-', 'arsenal_support-', 'absence-')):
                await interaction.response.send_message(
                    "❌ Cette commande ne peut être utilisée que dans un canal de ticket.", 
                    ephemeral=True
                )
                return
            
            # Vérifier permissions
            is_staff = any(role.permissions.manage_messages for role in interaction.user.roles)
            is_owner = interaction.channel.topic and str(interaction.user.id) in interaction.channel.topic
            
            if not (is_staff or is_owner):
                await interaction.response.send_message(
                    "❌ Vous n'avez pas la permission de fermer ce ticket.", 
                    ephemeral=True
                )
                return
            
            # Générer transcript
            transcript = await self.generate_transcript(interaction.channel)
            
            # Embed de fermeture
            embed = discord.Embed(
                title="🔒 Ticket Fermé",
                description=f"Ce ticket a été fermé par {interaction.user.mention}",
                color=0xff0000,
                timestamp=datetime.now(timezone.utc)
            )
            
            if reason:
                embed.add_field(name="📋 Raison", value=reason, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
            # Attendre puis supprimer le canal
            await asyncio.sleep(10)
            await interaction.channel.delete(reason=f"Ticket fermé par {interaction.user}")
            
        except Exception as e:
            print(f"❌ [TICKET] Erreur fermeture: {e}")
            await interaction.response.send_message(
                "❌ Erreur lors de la fermeture du ticket.", 
                ephemeral=True
            )

async def setup(bot):
    await bot.add_cog(AdvancedTicketSystem(bot))
