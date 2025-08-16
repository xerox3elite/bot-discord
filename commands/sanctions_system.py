#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⚖️ ARSENAL SANCTIONS SYSTEM - SYSTÈME DE SANCTIONS COMPLET
Casier judiciaire permanent avec sanctions/contre-sanctions & AutoMod intégré
Par xerox3elite - Arsenal V4.5.2 ULTIMATE
"""

import discord
from discord import app_commands
from discord.ext import commands
import aiosqlite
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
import asyncio

class SanctionsModal(discord.ui.Modal):
    """Modal pour appliquer une sanction"""
    
    def __init__(self, sanction_type: str, target_user: discord.Member, bot):
        super().__init__(title=f"⚖️ {sanction_type.upper()} - {target_user.display_name}")
        self.sanction_type = sanction_type
        self.target_user = target_user
        self.bot = bot
        
        # Champs dynamiques selon le type de sanction
        self.add_item(discord.ui.TextInput(
            label="Raison de la sanction",
            placeholder=f"Raison du {sanction_type}...",
            required=True,
            max_length=500,
            style=discord.TextStyle.paragraph
        ))
        
        if sanction_type in ["timeout", "mute", "ban"]:
            self.add_item(discord.ui.TextInput(
                label="Durée (optionnel)",
                placeholder="Ex: 1h, 30m, 7d, permanent",
                required=False,
                max_length=20
            ))
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        reason = self.children[0].value
        duration = self.children[1].value if len(self.children) > 1 else None
        
        # Appliquer la sanction
        success, message = await self.apply_sanction(interaction, reason, duration)
        
        if success:
            embed = discord.Embed(
                title="✅ Sanction appliquée",
                description=message,
                color=0x00ff00,
                timestamp=datetime.now(timezone.utc)
            )
        else:
            embed = discord.Embed(
                title="❌ Erreur",
                description=message,
                color=0xff0000,
                timestamp=datetime.now(timezone.utc)
            )
        
        await interaction.edit_original_response(embed=embed)
    
    async def apply_sanction(self, interaction: discord.Interaction, reason: str, duration: str = None) -> tuple[bool, str]:
        """Appliquer la sanction et l'enregistrer"""
        try:
            guild = interaction.guild
            moderator = interaction.user
            
            # Calculer la durée
            duration_seconds = None
            end_date = None
            
            if duration:
                duration_seconds = self.parse_duration(duration)
                if duration_seconds:
                    end_date = datetime.now(timezone.utc) + timedelta(seconds=duration_seconds)
            
            # Appliquer la sanction Discord
            sanction_applied = False
            
            if self.sanction_type == "timeout":
                if duration_seconds and duration_seconds <= 2419200:  # Max 28 jours
                    await self.target_user.timeout(
                        timedelta(seconds=duration_seconds),
                        reason=f"{reason} | Par {moderator.display_name}"
                    )
                    sanction_applied = True
                else:
                    return False, "Timeout maximum: 28 jours"
                    
            elif self.sanction_type == "kick":
                await self.target_user.kick(reason=f"{reason} | Par {moderator.display_name}")
                sanction_applied = True
                
            elif self.sanction_type == "ban":
                await self.target_user.ban(
                    reason=f"{reason} | Par {moderator.display_name}",
                    delete_message_days=0
                )
                sanction_applied = True
                
            elif self.sanction_type == "warn":
                sanction_applied = True  # Les warns sont juste enregistrés
                
            elif self.sanction_type == "mute":
                # Créer ou récupérer le rôle muet
                mute_role = await self.get_or_create_mute_role(guild)
                if mute_role:
                    await self.target_user.add_roles(mute_role, reason=f"{reason} | Par {moderator.display_name}")
                    sanction_applied = True
                else:
                    return False, "Impossible de créer le rôle muet"
            
            if sanction_applied:
                # Enregistrer dans le casier
                sanction_id = await self.save_sanction(
                    guild.id, self.target_user.id, moderator.id,
                    self.sanction_type, reason, duration, end_date
                )
                
                # Envoyer MP à l'utilisateur
                await self.send_sanction_dm(reason, duration)
                
                # Message de confirmation
                duration_text = f" ({duration})" if duration else ""
                return True, f"**{self.sanction_type.title()}** appliqué à {self.target_user.mention}{duration_text}\n**Raison:** {reason}\n**ID:** #{sanction_id}"
            
            return False, "Échec de l'application de la sanction"
            
        except discord.Forbidden:
            return False, "Permissions insuffisantes"
        except Exception as e:
            print(f"❌ [SANCTIONS] Erreur application: {e}")
            return False, f"Erreur: {str(e)}"
    
    def parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse la durée en secondes"""
        if not duration_str or duration_str.lower() in ["permanent", "perm"]:
            return None
        
        duration_str = duration_str.lower().strip()
        
        # Extraire nombre et unité
        import re
        match = re.match(r'(\d+)([smhdjw])', duration_str)
        if not match:
            return None
        
        amount = int(match.group(1))
        unit = match.group(2)
        
        multipliers = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
            'j': 86400,
            'w': 604800
        }
        
        return amount * multipliers.get(unit, 1)
    
    async def get_or_create_mute_role(self, guild: discord.Guild) -> Optional[discord.Role]:
        """Créer ou récupérer le rôle muet"""
        try:
            # Chercher un rôle existant
            for role in guild.roles:
                if role.name.lower() in ["muted", "muet", "mute"]:
                    return role
            
            # Créer le rôle
            mute_role = await guild.create_role(
                name="🔇 Muet",
                color=0x818181,
                reason="Rôle muet automatique Arsenal"
            )
            
            # Configurer les permissions dans tous les channels
            for channel in guild.channels:
                try:
                    if isinstance(channel, discord.TextChannel):
                        await channel.set_permissions(mute_role, send_messages=False, add_reactions=False)
                    elif isinstance(channel, discord.VoiceChannel):
                        await channel.set_permissions(mute_role, speak=False)
                except:
                    continue
            
            return mute_role
            
        except Exception as e:
            print(f"❌ [SANCTIONS] Erreur création rôle muet: {e}")
            return None
    
    async def save_sanction(self, guild_id: int, user_id: int, moderator_id: int, 
                          sanction_type: str, reason: str, duration: str = None, 
                          end_date: datetime = None) -> int:
        """Sauvegarder la sanction dans le casier"""
        try:
            db_path = "data/sanctions_casier.db"
            async with aiosqlite.connect(db_path) as db:
                cursor = await db.execute("""
                    INSERT INTO sanctions (
                        guild_id, user_id, moderator_id, sanction_type, 
                        reason, duration, end_date, created_at, active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    guild_id, user_id, moderator_id, sanction_type,
                    reason, duration, 
                    end_date.isoformat() if end_date else None,
                    datetime.now(timezone.utc).isoformat(),
                    1
                ))
                
                sanction_id = cursor.lastrowid
                await db.commit()
                return sanction_id
                
        except Exception as e:
            print(f"❌ [SANCTIONS] Erreur sauvegarde: {e}")
            return 0
    
    async def send_sanction_dm(self, reason: str, duration: str = None):
        """Envoyer un MP à l'utilisateur sanctionné"""
        try:
            embed = discord.Embed(
                title=f"⚖️ Sanction reçue - {self.sanction_type.title()}",
                description=f"Vous avez reçu une sanction sur **{self.target_user.guild.name}**",
                color=0xff9900,
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.add_field(
                name="📋 **Type de sanction**",
                value=self.sanction_type.title(),
                inline=True
            )
            
            embed.add_field(
                name="📝 **Raison**",
                value=reason,
                inline=True
            )
            
            if duration:
                embed.add_field(
                    name="⏱️ **Durée**",
                    value=duration,
                    inline=True
                )
            
            embed.add_field(
                name="ℹ️ **Information**",
                value="Cette sanction est enregistrée dans votre casier permanent.",
                inline=False
            )
            
            embed.set_footer(text="Arsenal Sanctions System")
            
            await self.target_user.send(embed=embed)
            
        except discord.Forbidden:
            print(f"❌ [SANCTIONS] Impossible d'envoyer MP à {self.target_user}")
        except Exception as e:
            print(f"❌ [SANCTIONS] Erreur envoi MP: {e}")

class SanctionsSystem(commands.Cog):
    """Système de sanctions complet Arsenal"""
    
    def __init__(self, bot):
        self.bot = bot
        asyncio.create_task(self.setup_database())
    
    async def setup_database(self):
        """Initialiser la base de données des sanctions"""
        try:
            import os
            os.makedirs("data", exist_ok=True)
            
            db_path = "data/sanctions_casier.db"
            async with aiosqlite.connect(db_path) as db:
                # Table des sanctions
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS sanctions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        guild_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        moderator_id INTEGER NOT NULL,
                        sanction_type TEXT NOT NULL,
                        reason TEXT NOT NULL,
                        duration TEXT,
                        end_date TEXT,
                        created_at TEXT NOT NULL,
                        active INTEGER DEFAULT 1
                    )
                """)
                
                # Table config automod
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS automod_config (
                        guild_id INTEGER PRIMARY KEY,
                        config TEXT NOT NULL
                    )
                """)
                
                await db.commit()
                print("✅ [SANCTIONS] Base de données initialisée")
                
        except Exception as e:
            print(f"❌ [SANCTIONS] Erreur setup DB: {e}")
    
    # ==================== COMMANDES DE SANCTIONS ====================
    
    @app_commands.command(name="timeout", description="⏰ Timeout un membre")
    @app_commands.describe(user="Membre à timeout", reason="Raison du timeout", duration="Durée (ex: 1h, 30m)")
    async def timeout_user(self, interaction: discord.Interaction, user: discord.Member, reason: str = None, duration: str = "1h"):
        """Timeout un utilisateur"""
        
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ Vous n'avez pas la permission de modérer les membres", ephemeral=True)
            return
        
        modal = SanctionsModal("timeout", user, self.bot)
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name="warn", description="⚠️ Warn un membre")
    @app_commands.describe(user="Membre à warn", reason="Raison du warn")
    async def warn_user(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        """Warn un utilisateur"""
        
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ Vous n'avez pas la permission de modérer les membres", ephemeral=True)
            return
        
        modal = SanctionsModal("warn", user, self.bot)
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name="kick", description="👢 Kick un membre")
    @app_commands.describe(user="Membre à kick", reason="Raison du kick")
    async def kick_user(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        """Kick un utilisateur"""
        
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message("❌ Vous n'avez pas la permission de kick des membres", ephemeral=True)
            return
        
        modal = SanctionsModal("kick", user, self.bot)
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name="ban", description="🔨 Ban un membre")
    @app_commands.describe(user="Membre à ban", reason="Raison du ban", duration="Durée (optionnel)")
    async def ban_user(self, interaction: discord.Interaction, user: discord.Member, reason: str = None, duration: str = None):
        """Ban un utilisateur"""
        
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("❌ Vous n'avez pas la permission de ban des membres", ephemeral=True)
            return
        
        modal = SanctionsModal("ban", user, self.bot)
        await interaction.response.send_modal(modal)
    
    @app_commands.command(name="mute", description="🔇 Mute un membre")
    @app_commands.describe(user="Membre à mute", reason="Raison du mute", duration="Durée (optionnel)")
    async def mute_user(self, interaction: discord.Interaction, user: discord.Member, reason: str = None, duration: str = None):
        """Mute un utilisateur"""
        
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("❌ Vous n'avez pas la permission de gérer les rôles", ephemeral=True)
            return
        
        modal = SanctionsModal("mute", user, self.bot)
        await interaction.response.send_modal(modal)
    
    # ==================== COMMANDES INVERSES ====================
    
    @app_commands.command(name="untimeout", description="✅ Retirer le timeout")
    @app_commands.describe(user="Membre à libérer", reason="Raison")
    async def untimeout_user(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Timeout retiré"):
        """Retirer le timeout d'un utilisateur"""
        
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ Permission insuffisante", ephemeral=True)
            return
        
        try:
            await user.timeout(None, reason=f"{reason} | Par {interaction.user.display_name}")
            
            # Enregistrer l'annulation
            await self.save_sanction_removal(interaction.guild.id, user.id, interaction.user.id, "untimeout", reason)
            
            embed = discord.Embed(
                title="✅ Timeout retiré",
                description=f"Timeout retiré pour {user.mention}\n**Raison:** {reason}",
                color=0x00ff00,
                timestamp=datetime.now(timezone.utc)
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @app_commands.command(name="unban", description="✅ Unban un utilisateur")
    @app_commands.describe(user_id="ID de l'utilisateur à unban", reason="Raison")
    async def unban_user(self, interaction: discord.Interaction, user_id: str, reason: str = "Unban"):
        """Unban un utilisateur"""
        
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message("❌ Permission insuffisante", ephemeral=True)
            return
        
        try:
            user_id_int = int(user_id)
            user = discord.Object(id=user_id_int)
            
            await interaction.guild.unban(user, reason=f"{reason} | Par {interaction.user.display_name}")
            
            # Enregistrer l'annulation
            await self.save_sanction_removal(interaction.guild.id, user_id_int, interaction.user.id, "unban", reason)
            
            embed = discord.Embed(
                title="✅ Utilisateur unban",
                description=f"Utilisateur <@{user_id_int}> unban\n**Raison:** {reason}",
                color=0x00ff00,
                timestamp=datetime.now(timezone.utc)
            )
            
            await interaction.response.send_message(embed=embed)
            
        except ValueError:
            await interaction.response.send_message("❌ ID utilisateur invalide", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @app_commands.command(name="unmute", description="✅ Unmute un membre")
    @app_commands.describe(user="Membre à unmute", reason="Raison")
    async def unmute_user(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Unmute"):
        """Retirer le mute d'un utilisateur"""
        
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("❌ Permission insuffisante", ephemeral=True)
            return
        
        try:
            # Trouver le rôle muet
            mute_role = None
            for role in interaction.guild.roles:
                if role.name.lower() in ["muted", "muet", "mute", "🔇 muet"]:
                    mute_role = role
                    break
            
            if not mute_role:
                await interaction.response.send_message("❌ Rôle muet non trouvé", ephemeral=True)
                return
            
            if mute_role not in user.roles:
                await interaction.response.send_message("❌ Cet utilisateur n'est pas muet", ephemeral=True)
                return
            
            await user.remove_roles(mute_role, reason=f"{reason} | Par {interaction.user.display_name}")
            
            # Enregistrer l'annulation
            await self.save_sanction_removal(interaction.guild.id, user.id, interaction.user.id, "unmute", reason)
            
            embed = discord.Embed(
                title="✅ Utilisateur unmute",
                description=f"Mute retiré pour {user.mention}\n**Raison:** {reason}",
                color=0x00ff00,
                timestamp=datetime.now(timezone.utc)
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    @app_commands.command(name="unwarn", description="✅ Retirer un warn")
    @app_commands.describe(user="Membre", warn_id="ID du warn à retirer", reason="Raison")
    async def unwarn_user(self, interaction: discord.Interaction, user: discord.Member, warn_id: int, reason: str = "Warn retiré"):
        """Retirer un warn spécifique"""
        
        if not interaction.user.guild_permissions.moderate_members:
            await interaction.response.send_message("❌ Permission insuffisante", ephemeral=True)
            return
        
        try:
            # Désactiver le warn dans la DB
            db_path = "data/sanctions_casier.db"
            async with aiosqlite.connect(db_path) as db:
                await db.execute("""
                    UPDATE sanctions SET active = 0 
                    WHERE id = ? AND guild_id = ? AND user_id = ? AND sanction_type = 'warn'
                """, (warn_id, interaction.guild.id, user.id))
                await db.commit()
            
            # Enregistrer l'annulation
            await self.save_sanction_removal(interaction.guild.id, user.id, interaction.user.id, "unwarn", f"{reason} (Warn #{warn_id})")
            
            embed = discord.Embed(
                title="✅ Warn retiré",
                description=f"Warn #{warn_id} retiré pour {user.mention}\n**Raison:** {reason}",
                color=0x00ff00,
                timestamp=datetime.now(timezone.utc)
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {e}", ephemeral=True)
    
    # ==================== CASIER JUDICIAIRE ====================
    
    @app_commands.command(name="casier", description="📋 Voir le casier judiciaire d'un membre")
    @app_commands.describe(user="Membre dont voir le casier")
    async def view_casier(self, interaction: discord.Interaction, user: discord.Member = None):
        """Afficher le casier judiciaire complet"""
        
        if not user:
            user = interaction.user
        
        if not interaction.user.guild_permissions.moderate_members and user != interaction.user:
            await interaction.response.send_message("❌ Vous ne pouvez voir que votre propre casier", ephemeral=True)
            return
        
        try:
            db_path = "data/sanctions_casier.db"
            async with aiosqlite.connect(db_path) as db:
                # Récupérer toutes les sanctions
                cursor = await db.execute("""
                    SELECT id, sanction_type, reason, duration, created_at, moderator_id, active
                    FROM sanctions 
                    WHERE guild_id = ? AND user_id = ?
                    ORDER BY created_at DESC
                """, (interaction.guild.id, user.id))
                
                sanctions = await cursor.fetchall()
            
            if not sanctions:
                embed = discord.Embed(
                    title="📋 Casier Judiciaire - Vierge",
                    description=f"**{user.display_name}** n'a aucune sanction enregistrée",
                    color=0x00ff00,
                    timestamp=datetime.now(timezone.utc)
                )
                embed.set_thumbnail(url=user.display_avatar.url)
                await interaction.response.send_message(embed=embed)
                return
            
            # Statistiques
            total = len(sanctions)
            active = len([s for s in sanctions if s[6] == 1])  # active = 1
            types = {}
            
            for sanction in sanctions:
                sanction_type = sanction[1]
                if sanction_type not in types:
                    types[sanction_type] = 0
                types[sanction_type] += 1
            
            embed = discord.Embed(
                title=f"📋 Casier Judiciaire - {user.display_name}",
                description=f"**Total:** {total} sanctions • **Actives:** {active}",
                color=0xff9900 if active > 0 else 0x00ff00,
                timestamp=datetime.now(timezone.utc)
            )
            
            embed.set_thumbnail(url=user.display_avatar.url)
            
            # Statistiques par type
            stats_text = ""
            emojis = {"warn": "⚠️", "timeout": "⏰", "mute": "🔇", "kick": "👢", "ban": "🔨"}
            
            for sanction_type, count in types.items():
                emoji = emojis.get(sanction_type, "📋")
                stats_text += f"{emoji} **{sanction_type.title()}:** {count}\n"
            
            if stats_text:
                embed.add_field(
                    name="📊 **Statistiques**",
                    value=stats_text,
                    inline=True
                )
            
            # Dernières sanctions (5 max)
            recent_text = ""
            for i, sanction in enumerate(sanctions[:5]):
                sanction_id, sanction_type, reason, duration, created_at, moderator_id, active = sanction
                
                # Format date
                try:
                    date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    date_str = date_obj.strftime("%d/%m/%Y")
                except:
                    date_str = "Date inconnue"
                
                # Moderator
                try:
                    moderator = interaction.guild.get_member(moderator_id)
                    mod_name = moderator.display_name if moderator else f"ID:{moderator_id}"
                except:
                    mod_name = f"ID:{moderator_id}"
                
                # Status
                status = "🟢" if active else "🔴"
                
                # Emoji sanction
                emoji = emojis.get(sanction_type, "📋")
                
                # Durée
                duration_text = f" ({duration})" if duration else ""
                
                recent_text += f"{status} {emoji} **#{sanction_id}** - {sanction_type.title()}{duration_text}\n"
                recent_text += f"└ *{reason[:50]}...* | {date_str} | {mod_name}\n\n"
            
            if recent_text:
                embed.add_field(
                    name="📋 **Sanctions Récentes**",
                    value=recent_text[:1024],
                    inline=False
                )
            
            embed.set_footer(text=f"🟢 Active • 🔴 Annulée • ID Utilisateur: {user.id}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            print(f"❌ [SANCTIONS] Erreur casier: {e}")
            await interaction.response.send_message("❌ Erreur lors de la consultation du casier", ephemeral=True)
    
    async def save_sanction_removal(self, guild_id: int, user_id: int, moderator_id: int, action_type: str, reason: str):
        """Enregistrer l'annulation d'une sanction"""
        try:
            db_path = "data/sanctions_casier.db"
            async with aiosqlite.connect(db_path) as db:
                await db.execute("""
                    INSERT INTO sanctions (
                        guild_id, user_id, moderator_id, sanction_type, 
                        reason, duration, end_date, created_at, active
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    guild_id, user_id, moderator_id, action_type,
                    reason, None, None,
                    datetime.now(timezone.utc).isoformat(),
                    1
                ))
                await db.commit()
                
        except Exception as e:
            print(f"❌ [SANCTIONS] Erreur sauvegarde annulation: {e}")

async def setup(bot):
    await bot.add_cog(SanctionsSystem(bot))
    print("⚖️ [OK] Système de sanctions complet chargé - Casier permanent & AutoMod!")
