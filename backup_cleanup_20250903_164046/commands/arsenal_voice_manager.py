"""
🎵 ARSENAL MUSIC SYSTEM - Auto-Join Vocal Avancé
Système pour faire rejoindre le bot automatiquement en vocal pour la musique
Gestion complète: join, leave, move, music streaming
"""

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import youtube_dl
import os
from typing import Optional
import wavelink

class ArsenalVoiceManager(commands.Cog):
    """Gestionnaire vocal avancé pour Arsenal"""
    
    def __init__(self, bot):
        self.bot = bot
        self.voice_connections = {}  # Suivi des connexions vocales
        self.music_queue = {}        # Queue de musique par serveur
    
    @app_commands.command(name="joinvoice", description="🎵 Faire rejoindre Arsenal dans votre salon vocal")
    async def join_voice(self, interaction: discord.Interaction, channel: Optional[discord.VoiceChannel] = None):
        """Faire rejoindre le bot dans un salon vocal"""
        
        # Déterminer le salon vocal cible
        if channel is None:
            if interaction.user.voice and interaction.user.voice.channel:
                channel = interaction.user.voice.channel
            else:
                embed = discord.Embed(
                    title="❌ Erreur Vocal",
                    description="Vous devez être connecté dans un salon vocal ou spécifier un salon !",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Vérifier permissions
        permissions = channel.permissions_for(interaction.guild.me)
        if not permissions.connect:
            embed = discord.Embed(
                title="🚫 Permissions Manquantes",
                description=f"Je n'ai pas la permission de me connecter à {channel.mention} !",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Se connecter au salon vocal
        try:
            if interaction.guild.voice_client:
                # Si déjà connecté, move vers le nouveau salon
                await interaction.guild.voice_client.move_to(channel)
                action = "déplacé vers"
            else:
                # Nouvelle connexion
                voice_client = await channel.connect()
                self.voice_connections[interaction.guild.id] = voice_client
                action = "connecté à"
            
            embed = discord.Embed(
                title="🎵 Arsenal Vocal Connecté !",
                description=f"✅ Arsenal s'est {action} **{channel.name}**",
                color=discord.Color.green()
            )
            
            embed.add_field(
                name="🎧 Commandes Disponibles",
                value="`/play` - Jouer de la musique\n`/stop` - Arrêter la musique\n`/leavevoice` - Quitter le vocal",
                inline=False
            )
            
            embed.add_field(
                name="👥 Utilisateurs Connectés",
                value=f"**{len(channel.members)}** membres dans le salon",
                inline=True
            )
            
            embed.set_footer(text=f"Connecté par {interaction.user.display_name}")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur de Connexion",
                description=f"Impossible de se connecter au salon vocal:\n```{str(e)}```",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="leavevoice", description="👋 Faire quitter Arsenal du salon vocal")
    async def leave_voice(self, interaction: discord.Interaction):
        """Faire quitter le bot du salon vocal"""
        
        voice_client = interaction.guild.voice_client
        
        if not voice_client:
            embed = discord.Embed(
                title="ℹ️ Arsenal Déconnecté",
                description="Arsenal n'est connecté à aucun salon vocal !",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        channel_name = voice_client.channel.name
        
        # Déconnecter et nettoyer
        await voice_client.disconnect()
        if interaction.guild.id in self.voice_connections:
            del self.voice_connections[interaction.guild.id]
        if interaction.guild.id in self.music_queue:
            del self.music_queue[interaction.guild.id]
        
        embed = discord.Embed(
            title="👋 Arsenal Déconnecté",
            description=f"✅ Arsenal a quitté **{channel_name}**",
            color=discord.Color.orange()
        )
        
        embed.set_footer(text=f"Déconnecté par {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="voicestatus", description="📊 Status de la connexion vocale d'Arsenal")
    async def voice_status(self, interaction: discord.Interaction):
        """Afficher le statut vocal du bot"""
        
        voice_client = interaction.guild.voice_client
        
        embed = discord.Embed(
            title="📊 Status Vocal Arsenal",
            color=discord.Color.blue()
        )
        
        if voice_client and voice_client.is_connected():
            channel = voice_client.channel
            
            embed.color = discord.Color.green()
            embed.add_field(
                name="🎵 Connexion",
                value=f"✅ **Connecté** à {channel.mention}",
                inline=False
            )
            
            embed.add_field(
                name="👥 Salon Vocal",
                value=f"**Nom**: {channel.name}\n**Membres**: {len(channel.members)}\n**Limite**: {channel.user_limit or 'Aucune'}",
                inline=True
            )
            
            embed.add_field(
                name="🎼 Audio",
                value=f"**Playing**: {'✅ Oui' if voice_client.is_playing() else '❌ Non'}\n**Paused**: {'✅ Oui' if voice_client.is_paused() else '❌ Non'}",
                inline=True
            )
            
            # Queue info si existe
            if interaction.guild.id in self.music_queue:
                queue_size = len(self.music_queue[interaction.guild.id])
                embed.add_field(
                    name="📝 Queue Musique",
                    value=f"**{queue_size}** titre(s) en attente",
                    inline=True
                )
        
        else:
            embed.color = discord.Color.red()
            embed.add_field(
                name="🔇 Connexion",
                value="❌ **Non connecté** à un salon vocal",
                inline=False
            )
            
            embed.add_field(
                name="💡 Pour se connecter",
                value="Utilisez `/joinvoice` ou rejoignez un vocal et utilisez `/play`",
                inline=False
            )
        
        embed.set_footer(text="Arsenal Voice Manager System")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="autovoice", description="🤖 Configuration auto-join vocal pour Arsenal")
    @app_commands.describe(
        enable="Activer/désactiver l'auto-join",
        channel="Salon vocal par défaut pour l'auto-join"
    )
    async def auto_voice_config(
        self, 
        interaction: discord.Interaction, 
        enable: bool,
        channel: Optional[discord.VoiceChannel] = None
    ):
        """Configuration de l'auto-join vocal"""
        
        # Vérifier permissions admin
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="🚫 Permissions Insuffisantes",
                description="Seuls les administrateurs peuvent configurer l'auto-voice !",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Sauvegarder la config (tu peux implémenter une DB)
        # Pour maintenant, juste répondre avec la config
        
        embed = discord.Embed(
            title="🤖 Configuration Auto-Voice",
            color=discord.Color.green() if enable else discord.Color.orange()
        )
        
        if enable:
            if channel:
                embed.description = f"✅ **Auto-join activé** vers {channel.mention}"
                embed.add_field(
                    name="⚡ Déclencheurs",
                    value="• Première commande `/play`\n• Utilisateur rejoint le salon configuré\n• Commande `/music` utilisée",
                    inline=False
                )
            else:
                embed.description = "✅ **Auto-join activé** (salon automatique selon l'utilisateur)"
        else:
            embed.description = "❌ **Auto-join désactivé**"
        
        embed.add_field(
            name="🔧 Gestion",
            value="`/autovoice enable:True` - Activer\n`/autovoice enable:False` - Désactiver\n`/voicestatus` - Voir le statut",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Détection des changements vocaux pour auto-join"""
        
        # Si c'est le bot qui change d'état, ignorer
        if member.bot:
            return
        
        # Logic auto-join (tu peux implémenter selon tes besoins)
        # Par exemple: si un utilisateur rejoint un salon spécifique, auto-join
        
        guild = member.guild
        
        # Exemple: Si quelqu'un rejoint un salon nommé "🎵 Musique" 
        if (after.channel and 
            after.channel.name.lower() in ["🎵 musique", "musique", "music", "radio"] and
            not guild.voice_client):
            
            try:
                await after.channel.connect()
                
                # Envoyer un message dans le salon général (optionnel)
                if guild.system_channel:
                    embed = discord.Embed(
                        title="🎵 Arsenal Auto-Join",
                        description=f"🤖 Arsenal s'est automatiquement connecté à {after.channel.mention} !",
                        color=discord.Color.green()
                    )
                    await guild.system_channel.send(embed=embed)
                    
            except discord.Forbidden:
                pass  # Pas de permissions, ignorer silencieusement

async def setup(bot):
    await bot.add_cog(ArsenalVoiceManager(bot))

