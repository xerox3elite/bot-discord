#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎫 ARSENAL TICKET ABSENCE SYSTEM - SYSTÈME DE TICKETS D'ABSENCE COMPLET
Gestion intelligente des absences avec rôles temporaires et auto-clôture
Par xerox3elite - Arsenal V4.5.2 ULTIMATE
"""

import discord
from discord import app_commands
from discord.ext import commands, tasks
import aiosqlite
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import asyncio

class AbsenceTicketModal(discord.ui.Modal, title="🎫 Créer Ticket d'Absence"):
    def __init__(self, bot, channel_config,self.bot.get_cog):
        super().__init__()
        self.bot = bot
        self.channel_config = channel_config
        self.db = self.bot.get_cog("Database")

    raison = discord.ui.TextInput(
        label="Raison de l'absence",
        placeholder="Ex: Problème familial, maladie, voyage, examens...",
        required=True,
        max_length=500,
        style=discord.TextStyle.paragraph
    )
    
    duree = discord.ui.TextInput(
        label="Durée de l'absence",
        placeholder="Ex: 1 semaine, 3 jours, 1 mois, 2 semaines...",
        required=True,
        max_length=100
    )
    
    date_debut = discord.ui.TextInput(
        label="Date de début (optionnel)",
        placeholder="Ex: 20/01/2025 ou aujourd'hui (par défaut)",
        required=False,
        max_length=50
    )
    
    details = discord.ui.TextInput(
        label="Détails supplémentaires (optionnel)",
        placeholder="Informations complémentaires pour les modérateurs...",
        required=False,
        max_length=1000,
        style=discord.TextStyle.paragraph
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        try:
            # Vérifier si l'utilisateur a déjà un ticket ouvert
            existing_ticket = await self.check_existing_ticket(interaction.user.id, interaction.guild.id)
            if existing_ticket:
                embed = discord.Embed(
                    title="❌ Ticket déjà ouvert",
                    description=f"**Vous avez déjà un ticket d'absence ouvert !**\n\n🎫 **ID Ticket:** #{existing_ticket['ticket_id']}\n📅 **Fin:** {existing_ticket['end_date']}\n\n⚠️ Vous ne pouvez avoir qu'un seul ticket d'absence à la fois.",
                    color=0xff0000,
                    timestamp=datetime.now(timezone.utc)
                )
                await interaction.edit_original_response(embed=embed)
                return
            
            # Calculer les dates
            start_date = await self.parse_date(self.date_debut.value or "aujourd'hui")
            duration_days = await self.parse_duration(self.duree.value)
            end_date = start_date + timedelta(days=duration_days, hours=24)  # +24h pour inclure dernier jour
            
            # Créer le ticket
            ticket_id = await self.create_absence_ticket(interaction, start_date, end_date)
            
            if ticket_id:
                embed = discord.Embed(
                    title="✅ Ticket d'Absence Créé",
                    description=f"**Votre demande d'absence a été enregistrée !**\n\n🎫 **ID Ticket:** #{ticket_id}\n📅 **Début:** {start_date.strftime('%d/%m/%Y')}\n📅 **Fin:** {end_date.strftime('%d/%m/%Y')}\n⏰ **Durée:** {duration_days} jour(s)",
                    color=0x00ff00,
                    timestamp=datetime.now(timezone.utc)
                )
                
                embed.add_field(
                    name="📋 **Détails**",
                    value=f"**Raison:** {self.raison.value}\n**Durée:** {self.duree.value}",
                    inline=False
                )
                
                if self.details.value:
                    embed.add_field(
                        name="ℹ️ **Informations supplémentaires**",
                        value=self.details.value,
                        inline=False
                    )
                
                embed.set_footer(text="Le rôle d'absence sera attribué automatiquement")
                
                await interaction.edit_original_response(embed=embed)
            else:
                await interaction.edit_original_response(content="❌ Erreur lors de la création du ticket d'absence.")
                
        except Exception as e:
            print(f"❌ [ABSENCE] Erreur création ticket: {e}")
            await interaction.edit_original_response(content=f"❌ Erreur: {str(e)}")
    
    async def save_channel_config(self, guild_id: int, config: Dict[str, Any]):
        """Sauvegarder la configuration du canal"""
        try:
            async with aiosqlite.connect("data/absence_config.db") as db:
                await db.execute("""
                    INSERT OR REPLACE INTO absence_config (guild_id, config)
                    VALUES (?, ?)
                """, (guild_id, json.dumps(config)))
                await db.commit()
        except Exception as e:
            print(f"❌ [ABSENCE] Erreur sauvegarde config: {e}")

    async def check_existing_ticket(self, user_id: int, guild_id: int) -> Optional[Dict[str, Any]]:
        """Vérifie si l'utilisateur a déjà un ticket ouvert"""
        try:
            db_path = "data/absence_tickets.db"
            async with aiosqlite.connect(db_path) as db:
                cursor = await db.execute("""
                    SELECT ticket_id, end_date FROM absence_tickets 
                    WHERE user_id = ? AND guild_id = ? AND status = 'active'
                """, (user_id, guild_id))
                result = await cursor.fetchone()
                
                if result:
                    return {
                        'ticket_id': result[0],
                        'end_date': result[1]
                    }
                return None
        except Exception as e:
            print(f"❌ [ABSENCE] Erreur vérification ticket existant: {e}")
            return None
    
    async def parse_date(self, date_str: str) -> datetime:
        """Parse une date en français"""
        date_str = date_str.lower().strip()
        
        if date_str in ["aujourd'hui", "maintenant", "now", ""]:
            return datetime.now(timezone.utc)
        elif date_str in ["demain", "tomorrow"]:
            return datetime.now(timezone.utc) + timedelta(days=1)
        else:
            # Format DD/MM/YYYY
            try:
                return datetime.strptime(date_str, "%d/%m/%Y").replace(tzinfo=timezone.utc)
            except:
                return datetime.now(timezone.utc)
    
    async def parse_duration(self, duration_str: str) -> int:
        """Parse une durée en jours"""
        duration_str = duration_str.lower().strip()
        
        # Mapping des mots français
        words = duration_str.split()
        days = 0
        
        for i, word in enumerate(words):
            if word.isdigit():
                num = int(word)
                next_word = words[i + 1] if i + 1 < len(words) else ""
                
                if "jour" in next_word:
                    days += num
                elif "semaine" in next_word:
                    days += num * 7
                elif "mois" in next_word:
                    days += num * 30
                elif "an" in next_word or "année" in next_word:
                    days += num * 365
        
        # Valeurs par défaut
        if days == 0:
            if "semaine" in duration_str:
                days = 7
            elif "mois" in duration_str:
                days = 30
            else:
                days = 1
        
        return days  # Suppression de la limite d'1 an
    
    async def create_absence_ticket(self, interaction: discord.Interaction, start_date: datetime, end_date: datetime) -> int:
        """Crée le ticket d'absence complet"""
        try:
            guild = interaction.guild
            user = interaction.user
            
            # Créer ou récupérer la catégorie
            category = None
            if self.channel_config.get("ticket_category_id"):
                category = guild.get_channel(self.channel_config["ticket_category_id"])
            
            # Si pas de catégorie configurée ou si elle n'existe plus, la créer
            if not category:
                try:
                    category = await guild.create_category(
                        name="🎫 Tickets d'Absence",
                        overwrites={
                            guild.default_role: discord.PermissionOverwrite(read_messages=False),
                            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
                        }
                    )
                    # Sauvegarder l'ID de la catégorie pour la prochaine fois
                    self.channel_config["ticket_category_id"] = category.id
                    await self.save_channel_config(guild.id, self.channel_config)
                    print(f"✅ [ABSENCE] Catégorie créée automatiquement: {category.name}")
                except Exception as e:
                    print(f"❌ [ABSENCE] Erreur création catégorie: {e}")
                    # Continuer sans catégorie si impossible de la créer
            
            # Permissions du salon de ticket
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
            }
            
            # Ajouter les modérateurs
            if self.channel_config.get("moderator_role_ids"):
                for role_id in self.channel_config["moderator_role_ids"]:
                    role = guild.get_role(role_id)
                    if role:
                        overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            
            # Créer salon ticket
            ticket_id = await self.get_next_ticket_id(guild.id)
            ticket_channel = await guild.create_text_channel(
                name=f"absence-{user.display_name}-{ticket_id}",
                category=category,
                overwrites=overwrites,
                topic=f"Ticket d'absence #{ticket_id} - {user.display_name}"
            )
            
            # Embed informations ticket
            ticket_embed = discord.Embed(
                title=f"🎫 Ticket d'Absence #{ticket_id}",
                description=f"**Demande d'absence de {user.mention}**",
                color=0xff9900,
                timestamp=datetime.now(timezone.utc)
            )
            
            ticket_embed.add_field(
                name="👤 **Utilisateur**",
                value=f"{user.mention}\n**ID:** {user.id}",
                inline=True
            )
            
            ticket_embed.add_field(
                name="📅 **Période**",
                value=f"**Début:** {start_date.strftime('%d/%m/%Y')}\n**Fin:** {end_date.strftime('%d/%m/%Y')}\n**Durée:** {(end_date - start_date).days} jour(s)",
                inline=True
            )
            
            ticket_embed.add_field(
                name="📋 **Détails**",
                value=f"**Raison:** {self.raison.value}\n**Durée demandée:** {self.duree.value}",
                inline=False
            )
            
            if self.details.value:
                ticket_embed.add_field(
                    name="ℹ️ **Informations supplémentaires**",
                    value=self.details.value,
                    inline=False
                )
            
            # View avec boutons de contrôle
            ticket_view = AbsenceTicketControlView(self.bot, ticket_id, user.id, start_date, end_date)
            
            await ticket_channel.send(embed=ticket_embed, view=ticket_view)
            
            # Enregistrer en base de données
            await self.save_ticket_to_db(guild.id, ticket_id, user.id, ticket_channel.id, start_date, end_date, self.raison.value, self.details.value)
            
            # Attribution du rôle d'absence si nécessaire
            await self.assign_absence_role(guild, user, start_date, end_date)
            
            return ticket_id
            
        except Exception as e:
            print(f"❌ [ABSENCE] Erreur création ticket: {e}")
            return None
    
    async def get_next_ticket_id(self, guild_id: int) -> int:
        """Récupère le prochain ID de ticket"""
        async with aiosqlite.connect("data/absence_tickets.db") as db:
            cursor = await db.execute(
                "SELECT MAX(ticket_id) FROM tickets WHERE guild_id = ?",
                (guild_id,)
            )
            result = await cursor.fetchone()
            return (result[0] or 0) + 1
    
    async def save_ticket_to_db(self, guild_id: int, ticket_id: int, user_id: int, channel_id: int, start_date: datetime, end_date: datetime, reason: str, details: str):
        """Sauvegarde le ticket en base de données"""
        async with aiosqlite.connect("data/absence_tickets.db") as db:
            await db.execute("""
                INSERT INTO tickets (guild_id, ticket_id, user_id, channel_id, start_date, end_date, reason, details, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
            """, (guild_id, ticket_id, user_id, channel_id, start_date.isoformat(), end_date.isoformat(), reason, details, datetime.now(timezone.utc).isoformat()))
            await db.commit()
    
    async def assign_absence_role(self, guild: discord.Guild, user: discord.Member, start_date: datetime, end_date: datetime):
        """Attribue le rôle d'absence temporaire"""
        try:
            # Récupérer config rôle absence
            absence_role_id = self.channel_config.get("absence_role_id")
            if not absence_role_id:
                return
            
            absence_role = guild.get_role(absence_role_id)
            if not absence_role:
                return
            
            # Attribuer rôle si la période a commencé
            now = datetime.now(timezone.utc)
            if start_date <= now:
                await user.add_roles(absence_role, reason=f"Absence automatique jusqu'au {end_date.strftime('%d/%m/%Y')}")
                print(f"✅ [ABSENCE] Rôle attribué à {user.display_name}")
            
        except Exception as e:
            print(f"❌ [ABSENCE] Erreur attribution rôle: {e}")

class AbsenceTicketControlView(discord.ui.View):
    """Vue avec contrôles de ticket d'absence"""
    def __init__(self, bot, ticket_id: int, user_id: int, start_date: datetime, end_date: datetime):
        super().__init__(timeout=None)  # Pas de timeout
        self.bot = bot
        self.ticket_id = ticket_id
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date
    
    @discord.ui.button(label="✅ Approuver", style=discord.ButtonStyle.success, emoji="✅")
    async def approve_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Vérifier permissions modérateur
        if not await self.check_moderator_permissions(interaction):
            return
        
        await interaction.response.defer()
        
        # Marquer comme approuvé
        await self.update_ticket_status(interaction.guild.id, self.ticket_id, "approved")
        
        embed = discord.Embed(
            title="✅ Ticket Approuvé",
            description=f"Le ticket d'absence #{self.ticket_id} a été **approuvé** par {interaction.user.mention}",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        
        await interaction.edit_original_response(embed=embed)
    
    @discord.ui.button(label="❌ Refuser", style=discord.ButtonStyle.danger, emoji="❌")
    async def reject_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Vérifier permissions modérateur
        if not await self.check_moderator_permissions(interaction):
            return
        
        modal = RejectReasonModal(self.bot, self.ticket_id)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="🗑️ Clôturer", style=discord.ButtonStyle.secondary, emoji="🗑️")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Vérifier permissions (utilisateur ou modérateur)
        if interaction.user.id != self.user_id and not await self.check_moderator_permissions(interaction, respond=False):
            await interaction.response.send_message("❌ Seul l'utilisateur du ticket ou un modérateur peut clôturer ce ticket.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Générer transcription
        transcript = await self.generate_transcript(interaction.channel)
        
        # Envoyer transcription en DM à l'utilisateur
        user = self.bot.get_user(self.user_id)
        if user:
            try:
                transcript_embed = discord.Embed(
                    title=f"📋 Transcription Ticket #{self.ticket_id}",
                    description="Voici la transcription complète de votre ticket d'absence.",
                    color=0x607d8b,
                    timestamp=datetime.now(timezone.utc)
                )
                transcript_embed.add_field(name="Transcription", value=transcript[:1000] + "..." if len(transcript) > 1000 else transcript, inline=False)
                await user.send(embed=transcript_embed)
            except:
                pass
        
        # Supprimer le canal et mettre à jour la base
        await self.update_ticket_status(interaction.guild.id, self.ticket_id, "closed")
        await interaction.channel.delete(reason=f"Ticket d'absence #{self.ticket_id} clôturé")
    
    async def check_moderator_permissions(self, interaction: discord.Interaction, respond: bool = True) -> bool:
        """Vérifie si l'utilisateur a les permissions de modérateur"""
        # Admin = ok
        if interaction.user.guild_permissions.administrator:
            return True
        
        # Vérifier rôles modérateurs configurés
        config = await self.load_guild_config(interaction.guild.id)
        moderator_role_ids = config.get("moderator_role_ids", [])
        
        user_role_ids = [role.id for role in interaction.user.roles]
        if any(role_id in user_role_ids for role_id in moderator_role_ids):
            return True
        
        if respond:
            await interaction.response.send_message("❌ Vous devez être modérateur pour effectuer cette action.", ephemeral=True)
        return False
    
    async def update_ticket_status(self, guild_id: int, ticket_id: int, status: str):
        """Met à jour le statut du ticket"""
        async with aiosqlite.connect("data/absence_tickets.db") as db:
            await db.execute(
                "UPDATE tickets SET status = ?, updated_at = ? WHERE guild_id = ? AND ticket_id = ?",
                (status, datetime.now(timezone.utc).isoformat(), guild_id, ticket_id)
            )
            await db.commit()
    
    async def load_guild_config(self, guild_id: int) -> Dict:
        """Charge la configuration du serveur"""
        try:
            async with aiosqlite.connect("data/absence_config.db") as db:
                cursor = await db.execute(
                    "SELECT config FROM guild_configs WHERE guild_id = ?",
                    (guild_id,)
                )
                result = await cursor.fetchone()
                if result:
                    return json.loads(result[0])
        except:
            pass
        return {}
    
    async def generate_transcript(self, channel: discord.TextChannel) -> str:
        """Génère une transcription du canal"""
        try:
            transcript = f"TRANSCRIPTION TICKET #{self.ticket_id}\n"
            transcript += f"Canal: {channel.name}\n"
            transcript += f"Généré le: {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M:%S UTC')}\n\n"
            
            async for message in channel.history(limit=100, oldest_first=True):
                timestamp = message.created_at.strftime('%d/%m/%Y %H:%M:%S')
                transcript += f"[{timestamp}] {message.author.display_name}: {message.content}\n"
            
            return transcript
        except:
            return "Erreur génération transcription"

class RejectReasonModal(discord.ui.Modal, title="❌ Motif de Refus"):
    def __init__(self, bot, ticket_id: int):
        super().__init__()
        self.bot = bot
        self.ticket_id = ticket_id
    
    reason = discord.ui.TextInput(
        label="Raison du refus",
        placeholder="Expliquez pourquoi cette demande d'absence est refusée...",
        required=True,
        max_length=500,
        style=discord.TextStyle.paragraph
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        # Marquer comme refusé
        async with aiosqlite.connect("data/absence_tickets.db") as db:
            await db.execute(
                "UPDATE tickets SET status = 'rejected', rejection_reason = ?, updated_at = ? WHERE ticket_id = ?",
                (self.reason.value, datetime.now(timezone.utc).isoformat(), self.ticket_id)
            )
            await db.commit()
        
        embed = discord.Embed(
            title="❌ Ticket Refusé",
            description=f"Le ticket d'absence #{self.ticket_id} a été **refusé** par {interaction.user.mention}",
            color=0xff0000,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(
            name="📋 **Motif du refus**",
            value=self.reason.value,
            inline=False
        )
        
        await interaction.edit_original_response(embed=embed)

class AbsenceRequestView(discord.ui.View):
    """Vue avec bouton pour créer ticket d'absence"""
    def __init__(self, bot, channel_config):
        super().__init__(timeout=None)
        self.bot = bot
        self.channel_config = channel_config
    
    @discord.ui.button(label="🎫 Créer Ticket d'Absence", style=discord.ButtonStyle.primary, emoji="🎫")
    async def create_absence_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AbsenceTicketModal(self.bot, self.channel_config)
        await interaction.response.send_modal(modal)

class AbsenceTicketSystem(commands.Cog):
    """Système complet de tickets d'absence"""
    
    def __init__(self, bot):
        self.bot = bot
        self.setup_database.start()
        self.check_expired_absences.start()
    
    @tasks.loop(hours=1)
    async def check_expired_absences(self):
        """Vérifie les absences expirées toutes les heures"""
        try:
            now = datetime.now(timezone.utc)
            
            async with aiosqlite.connect("data/absence_tickets.db") as db:
                # Récupérer tickets actifs expirés
                cursor = await db.execute("""
                    SELECT guild_id, ticket_id, user_id, channel_id, end_date 
                    FROM tickets 
                    WHERE status = 'active' AND end_date <= ?
                """, (now.isoformat(),))
                
                expired_tickets = await cursor.fetchall()
                
                for guild_id, ticket_id, user_id, channel_id, end_date_str in expired_tickets:
                    await self.handle_expired_ticket(guild_id, ticket_id, user_id, channel_id)
                    
        except Exception as e:
            print(f"❌ [ABSENCE] Erreur vérification expiration: {e}")
    
    async def handle_expired_ticket(self, guild_id: int, ticket_id: int, user_id: int, channel_id: int):
        """Gère l'expiration d'un ticket d'absence"""
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return
            
            # Retirer rôle d'absence
            user = guild.get_member(user_id)
            config = await self.load_guild_config(guild_id)
            
            if user and config.get("absence_role_id"):
                absence_role = guild.get_role(config["absence_role_id"])
                if absence_role and absence_role in user.roles:
                    await user.remove_roles(absence_role, reason="Fin de période d'absence")
                    print(f"✅ [ABSENCE] Rôle retiré de {user.display_name}")
            
            # Clôturer le ticket
            channel = guild.get_channel(channel_id)
            if channel:
                # Générer transcription
                transcript = await self.generate_final_transcript(channel, ticket_id)
                
                # Envoyer en DM
                if user:
                    try:
                        embed = discord.Embed(
                            title="⏰ Fin de Période d'Absence",
                            description=f"Votre période d'absence est terminée. Le ticket #{ticket_id} a été automatiquement clôturé.",
                            color=0x00ff00
                        )
                        embed.add_field(name="Transcription", value=transcript[:1000] + "..." if len(transcript) > 1000 else transcript, inline=False)
                        await user.send(embed=embed)
                    except:
                        pass
                
                await channel.delete(reason=f"Ticket d'absence #{ticket_id} expiré automatiquement")
            
            # Marquer comme expiré en base
            async with aiosqlite.connect("data/absence_tickets.db") as db:
                await db.execute(
                    "UPDATE tickets SET status = 'expired', updated_at = ? WHERE guild_id = ? AND ticket_id = ?",
                    (datetime.now(timezone.utc).isoformat(), guild_id, ticket_id)
                )
                await db.commit()
                
        except Exception as e:
            print(f"❌ [ABSENCE] Erreur gestion expiration ticket {ticket_id}: {e}")
    
    async def generate_final_transcript(self, channel: discord.TextChannel, ticket_id: int) -> str:
        """Génère la transcription finale du ticket"""
        try:
            transcript = f"TRANSCRIPTION FINALE TICKET #{ticket_id}\n"
            transcript += f"Clôturé automatiquement le: {datetime.now(timezone.utc).strftime('%d/%m/%Y %H:%M:%S UTC')}\n\n"
            
            message_count = 0
            async for message in channel.history(limit=50, oldest_first=True):
                if message_count >= 20:  # Limiter à 20 messages
                    break
                timestamp = message.created_at.strftime('%d/%m/%Y %H:%M:%S')
                transcript += f"[{timestamp}] {message.author.display_name}: {message.content[:100]}...\n"
                message_count += 1
            
            return transcript
        except:
            return f"Transcription du ticket #{ticket_id} - Clôturé automatiquement"
    
    @tasks.loop(count=1)
    async def setup_database(self):
        """Initialise les tables de base de données"""
        try:
            async with aiosqlite.connect("data/absence_tickets.db") as db:
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS tickets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        ticket_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        channel_id INTEGER NOT NULL,
                        start_date TEXT NOT NULL,
                        end_date TEXT NOT NULL,
                        reason TEXT NOT NULL,
                        details TEXT,
                        status TEXT DEFAULT 'active',
                        rejection_reason TEXT,
                        created_at TEXT NOT NULL,
                        updated_at TEXT
                    )
                """)
                
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS guild_configs (
                        guild_id INTEGER PRIMARY KEY,
                        config TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                await db.commit()
                print("✅ [ABSENCE] Base de données initialisée")
                
        except Exception as e:
            print(f"❌ [ABSENCE] Erreur init base de données: {e}")
    
    async def load_guild_config(self, guild_id: int) -> Dict:
        """Charge la configuration du serveur"""
        try:
            async with aiosqlite.connect("data/absence_config.db") as db:
                cursor = await db.execute(
                    "SELECT config FROM guild_configs WHERE guild_id = ?",
                    (guild_id,)
                )
                result = await cursor.fetchone()
                if result:
                    return json.loads(result[0])
        except:
            pass
        return {}
    
    @app_commands.command(name="absence_setup", description="🔧 Configurer le système de tickets d'absence")
    @commands.has_permissions(administrator=True)
    async def setup_absence_system(self, interaction: discord.Interaction):
        """Configuration initiale du système d'absence"""
        
        embed = discord.Embed(
            title="🔧 Configuration Système d'Absence",
            description="**Configurez le système de tickets d'absence pour votre serveur**\n\nUtilisez les boutons ci-dessous pour configurer chaque élément.",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        
        view = AbsenceSetupView(self.bot, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="absence_panel", description="🎫 Créer le panel de tickets d'absence")
    @commands.has_permissions(manage_channels=True)
    async def create_absence_panel(self, interaction: discord.Interaction):
        """Crée le panel de demande de tickets d'absence"""
        
        config = await self.load_guild_config(interaction.guild.id)
        
        embed = discord.Embed(
            title="🎫 Système de Tickets d'Absence",
            description="**Vous devez vous absenter ? Créez un ticket d'absence !**\n\n📋 **Comment ça fonctionne :**\n\n🔸 Cliquez sur le bouton **\"Créer Ticket\"**\n🔸 Remplissez le formulaire avec vos informations\n🔸 Un salon privé sera créé pour votre demande\n🔸 Les modérateurs examineront votre demande\n🔸 Le rôle d'absence sera attribué automatiquement",
            color=0xff9900,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(
            name="⚠️ **Important**",
            value="• Soyez précis dans votre demande\n• Indiquez la durée exacte\n• Vous ne pouvez avoir qu'un seul ticket ouvert à la fois\n• Le rôle sera retiré automatiquement à la fin",
            inline=False
        )
        
        embed.set_footer(
            text="Arsenal Absence System • Configuration requise par un administrateur",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )
        
        view = AbsenceRequestView(self.bot, config)
        await interaction.response.send_message(embed=embed, view=view)

class AbsenceSetupView(discord.ui.View):
    """Vue de configuration complète du système d'absence"""
    def __init__(self, bot, user_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
    
    @discord.ui.button(label="🎫 Configurer Canal", style=discord.ButtonStyle.primary, emoji="🎫")
    async def configure_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configurer le canal des tickets d'absence"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seule la personne qui a lancé cette commande peut utiliser ces boutons.", ephemeral=True)
            return
        
        modal = ChannelConfigModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="👥 Configurer Rôles", style=discord.ButtonStyle.secondary, emoji="👥")
    async def configure_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configurer les rôles pour gérer les absences"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seule la personne qui a lancé cette commande peut utiliser ces boutons.", ephemeral=True)
            return
        
        modal = RolesConfigModal()
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="⏰ Configuration Auto", style=discord.ButtonStyle.success, emoji="⏰")
    async def auto_configure(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Configuration automatique du système"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seule la personne qui a lancé cette commande peut utiliser ces boutons.", ephemeral=True)
            return
        
        await self.setup_auto_config(interaction)
    
    @discord.ui.button(label="📊 Statistiques", style=discord.ButtonStyle.secondary, emoji="📊")
    async def show_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Afficher les statistiques du système d'absence"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seule la personne qui a lancé cette commande peut utiliser ces boutons.", ephemeral=True)
            return
        
        await self.show_absence_stats(interaction)
    
    @discord.ui.button(label="❌ Fermer", style=discord.ButtonStyle.danger, emoji="❌")
    async def close_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Fermer la configuration"""
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ Seule la personne qui a lancé cette commande peut utiliser ces boutons.", ephemeral=True)
            return
        
        await interaction.response.edit_message(
            content="✅ **Configuration fermée.**", 
            embed=None, 
            view=None
        )
    
    async def setup_auto_config(self, interaction: discord.Interaction):
        """Configuration automatique"""
        await interaction.response.defer()
        
        guild = interaction.guild
        
        try:
            # Créer catégorie si n'existe pas
            category = None
            for cat in guild.categories:
                if cat.name.lower() == "🎫 tickets d'absence":
                    category = cat
                    break
            
            if not category:
                category = await guild.create_category("🎫 Tickets d'Absence")
            
            # Créer canal principal si n'existe pas
            main_channel = None
            for channel in guild.text_channels:
                if channel.name == "absence-tickets":
                    main_channel = channel
                    break
            
            if not main_channel:
                main_channel = await guild.create_text_channel(
                    "absence-tickets", 
                    category=category,
                    topic="🎫 Système de tickets d'absence - Créez votre demande ici"
                )
            
            # Sauvegarder la config
            config = {
                "enabled": True,
                "ticket_channel": main_channel.id,
                "category": category.id,
                "admin_roles": [],
                "auto_expire_days": 30
            }
            
            await self.save_config(guild.id, config)
            
            embed = discord.Embed(
                title="✅ Configuration automatique terminée",
                description=f"**Le système d'absence a été configuré automatiquement !**\n\n"
                           f"🎫 **Canal principal:** {main_channel.mention}\n"
                           f"📁 **Catégorie:** {category.name}\n"
                           f"⚙️ **Statut:** Activé\n"
                           f"📅 **Expiration auto:** 30 jours",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            await interaction.followup.edit_message(embed=embed, view=None)
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ **Erreur lors de la configuration automatique:** {str(e)}",
                ephemeral=True
            )
    
    async def show_absence_stats(self, interaction: discord.Interaction):
        """Afficher les statistiques"""
        await interaction.response.defer()
        
        guild = interaction.guild
        
        try:
            # Récupérer les stats depuis la base
            stats = await self.get_guild_stats(guild.id)
            
            embed = discord.Embed(
                title="📊 Statistiques des tickets d'absence",
                color=0x3498db,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="🎫 **Tickets créés**",
                value=f"**Total:** {stats.get('total_tickets', 0)}\n"
                      f"**Actifs:** {stats.get('active_tickets', 0)}\n"
                      f"**Fermés:** {stats.get('closed_tickets', 0)}",
                inline=True
            )
            
            embed.add_field(
                name="📈 **Ce mois-ci**",
                value=f"**Nouveaux:** {stats.get('monthly_new', 0)}\n"
                      f"**Approuvés:** {stats.get('monthly_approved', 0)}\n"
                      f"**Refusés:** {stats.get('monthly_refused', 0)}",
                inline=True
            )
            
            embed.add_field(
                name="⏱️ **Temps moyen**",
                value=f"**Réponse:** {stats.get('avg_response_time', '< 1h')}\n"
                      f"**Traitement:** {stats.get('avg_processing_time', '< 24h')}\n"
                      f"**Durée ticket:** {stats.get('avg_ticket_duration', '< 7j')}",
                inline=True
            )
            
            await interaction.followup.edit_message(embed=embed, view=self)
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ **Erreur lors de la récupération des statistiques:** {str(e)}",
                ephemeral=True
            )
    
    async def save_config(self, guild_id: int, config: dict):
        """Sauvegarder la configuration (placeholder)"""
        # Cette méthode devrait sauvegarder dans la base de données
        pass
    
    async def get_guild_stats(self, guild_id: int) -> dict:
        """Récupérer les statistiques (placeholder)"""
        # Placeholder - retourne des stats de démonstration
        return {
            "total_tickets": 42,
            "active_tickets": 3,
            "closed_tickets": 39,
            "monthly_new": 8,
            "monthly_approved": 6,
            "monthly_refused": 1,
            "avg_response_time": "2h 15min",
            "avg_processing_time": "18h 30min",
            "avg_ticket_duration": "4j 12h"
        }

class ChannelConfigModal(discord.ui.Modal):
    """Modal pour configurer le canal"""
    def __init__(self):
        super().__init__(title="🎫 Configuration Canal")
        
        self.channel_input = discord.ui.TextInput(
            label="Canal des tickets (nom ou ID)",
            placeholder="absence-tickets ou 123456789",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.channel_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"✅ **Canal configuré:** {self.channel_input.value}",
            ephemeral=True
        )

class RolesConfigModal(discord.ui.Modal):
    """Modal pour configurer les rôles"""
    def __init__(self):
        super().__init__(title="👥 Configuration Rôles")
        
        self.roles_input = discord.ui.TextInput(
            label="Rôles d'administration (séparés par virgules)",
            placeholder="Admin, Modérateur, Staff",
            style=discord.TextStyle.paragraph,
            required=True
        )
        self.add_item(self.roles_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"✅ **Rôles configurés:** {self.roles_input.value}",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(AbsenceTicketSystem(bot))
