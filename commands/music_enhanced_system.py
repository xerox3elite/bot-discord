# 🚀 Arsenal V4 - Enhanced Music System
"""
Système musical avancé basé sur les fonctionnalités du client.py:
- Lecture playlist YouTube complète
- Gestion du volume avec mémoire
- Queue avancée avec shuffle
- Support FFmpeg optimisé
- Auto-disconnect intelligent
- Contrôles interactifs
"""

import discord
from discord.ext import commands
from discord import app_commands, FFmpegPCMAudio, PCMVolumeTransformer
import asyncio
import json
import os
import random
from typing import Optional, List, Dict
import yt_dlp
from collections import deque
import time

class EnhancedMusicSystem(commands.Cog):
    """Système musical avancé pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.music_queues = {}  # {guild_id: deque()}
        self.voice_clients = {}  # {guild_id: voice_client}
        self.current_tracks = {}  # {guild_id: track_info}
        self.volumes = {}  # {guild_id: volume}
        self.memory_file = "data/music_memory.json"
        self.load_music_memory()
        
        # Configuration yt-dlp optimisée
        self.ytdl_options = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'logtostderr': False,
            'ignoreerrors': False,
            'noplaylist': False,
        }
        
        # FFmpeg configuré pour Arsenal
        self.ffmpeg_options = {
            'options': '-vn -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
        }

    def load_music_memory(self):
        """Charge la mémoire musicale"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    memory = json.load(f)
                    self.volumes = memory.get('volumes', {})
            except:
                self.volumes = {}
        else:
            self.volumes = {}

    def save_music_memory(self):
        """Sauvegarde la mémoire musicale"""
        os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
        memory = {'volumes': self.volumes}
        with open(self.memory_file, 'w') as f:
            json.dump(memory, f, indent=2)

    def get_guild_volume(self, guild_id: int) -> float:
        """Récupère le volume d'un serveur"""
        return self.volumes.get(str(guild_id), 0.5)

    def set_guild_volume(self, guild_id: int, volume: float):
        """Définit le volume d'un serveur"""
        self.volumes[str(guild_id)] = volume
        self.save_music_memory()

    async def ensure_voice_connection(self, interaction: discord.Interaction) -> Optional[discord.VoiceClient]:
        """Assure une connexion vocale"""
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ Vous devez être dans un salon vocal !", ephemeral=True)
            return None
        
        channel = interaction.user.voice.channel
        guild_id = interaction.guild.id
        
        # Vérifier connexion existante
        if guild_id in self.voice_clients:
            vc = self.voice_clients[guild_id]
            if vc.is_connected():
                return vc
        
        # Nouvelle connexion
        try:
            vc = await channel.connect()
            self.voice_clients[guild_id] = vc
            return vc
        except Exception as e:
            await interaction.response.send_message(f"❌ Impossible de se connecter: {e}", ephemeral=True)
            return None

    @app_commands.command(name="music_enhanced", description="🎵 Menu musical Arsenal avancé")
    async def music_menu(self, interaction: discord.Interaction):
        """Menu principal du système musical avancé"""
        guild_id = interaction.guild.id
        queue_size = len(self.music_queues.get(guild_id, []))
        current = self.current_tracks.get(guild_id)
        volume = self.get_guild_volume(guild_id) * 100
        
        embed = discord.Embed(
            title="🎵 Arsenal Music Studio",
            description="Système musical avancé avec toutes les fonctionnalités",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="🎧 Status Actuel",
            value=f"**En cours:** {current['title'] if current else 'Rien'}\n**Volume:** {volume:.0f}%\n**File d'attente:** {queue_size} pistes",
            inline=True
        )
        
        embed.add_field(
            name="🎵 Commandes de Base",
            value="`/play_enhanced` - Jouer une piste\n`/playlist_enhanced` - Playlist YouTube\n`/queue_enhanced` - Voir la queue",
            inline=True
        )
        
        embed.add_field(
            name="🔧 Contrôles Avancés",
            value="`/volume_enhanced` - Volume\n`/shuffle_enhanced` - Mélanger\n`/music_controls` - Panel interactif",
            inline=True
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="play_enhanced", description="🎵 Lecture musicale avancée")
    @app_commands.describe(query="URL YouTube ou terme de recherche")
    async def play_enhanced(self, interaction: discord.Interaction, query: str):
        """Lecture musicale avec queue intelligente"""
        
        await interaction.response.defer()
        
        vc = await self.ensure_voice_connection(interaction)
        if not vc:
            return
        
        guild_id = interaction.guild.id
        
        try:
            with yt_dlp.YoutubeDL(self.ytdl_options) as ydl:
                # Extraction des informations
                info = ydl.extract_info(query, download=False)
                
                if 'entries' in info:
                    # Playlist
                    entries = info['entries'][:50]  # Limite à 50 pistes
                    await interaction.followup.send(f"🎵 Ajout de {len(entries)} pistes à la queue...")
                    
                    for entry in entries:
                        if entry:
                            track_info = {
                                'title': entry.get('title', 'Titre inconnu'),
                                'url': entry.get('url'),
                                'duration': entry.get('duration', 0),
                                'thumbnail': entry.get('thumbnail'),
                                'requested_by': interaction.user.display_name
                            }
                            
                            if guild_id not in self.music_queues:
                                self.music_queues[guild_id] = deque()
                            
                            self.music_queues[guild_id].append(track_info)
                else:
                    # Piste unique
                    track_info = {
                        'title': info.get('title', 'Titre inconnu'),
                        'url': info.get('url'),
                        'duration': info.get('duration', 0),
                        'thumbnail': info.get('thumbnail'),
                        'requested_by': interaction.user.display_name
                    }
                    
                    if guild_id not in self.music_queues:
                        self.music_queues[guild_id] = deque()
                    
                    self.music_queues[guild_id].append(track_info)
                    
                    embed = discord.Embed(
                        title="🎵 Piste Ajoutée",
                        description=f"**{track_info['title']}**",
                        color=discord.Color.green()
                    )
                    
                    if track_info['thumbnail']:
                        embed.set_thumbnail(url=track_info['thumbnail'])
                    
                    embed.add_field(
                        name="📋 Queue",
                        value=f"Position: {len(self.music_queues[guild_id])}",
                        inline=True
                    )
                    
                    if track_info['duration']:
                        mins, secs = divmod(track_info['duration'], 60)
                        embed.add_field(
                            name="⏱️ Durée",
                            value=f"{mins}:{secs:02d}",
                            inline=True
                        )
                    
                    await interaction.followup.send(embed=embed)
                
                # Démarrer la lecture si rien ne joue
                if not vc.is_playing():
                    await self.play_next(guild_id)
                    
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur lors de l'extraction: {str(e)[:100]}...")

    async def play_next(self, guild_id: int):
        """Joue la piste suivante dans la queue"""
        if guild_id not in self.music_queues or not self.music_queues[guild_id]:
            return
        
        if guild_id not in self.voice_clients:
            return
        
        vc = self.voice_clients[guild_id]
        if not vc.is_connected():
            return
        
        track = self.music_queues[guild_id].popleft()
        self.current_tracks[guild_id] = track
        
        try:
            source = FFmpegPCMAudio(track['url'], **self.ffmpeg_options)
            volume = self.get_guild_volume(guild_id)
            audio = PCMVolumeTransformer(source, volume=volume)
            
            def after_playing(error):
                if error:
                    print(f"Erreur lecture: {error}")
                else:
                    # Auto-next
                    asyncio.create_task(self.play_next(guild_id))
            
            vc.play(audio, after=after_playing)
            
            # Message de lecture
            guild = self.bot.get_guild(guild_id)
            if guild:
                # Trouver un canal pour envoyer le message
                channel = discord.utils.get(guild.text_channels, name='général') or guild.text_channels[0]
                if channel:
                    embed = discord.Embed(
                        title="🎵 En cours de lecture",
                        description=f"**{track['title']}**",
                        color=discord.Color.blue()
                    )
                    
                    if track['thumbnail']:
                        embed.set_thumbnail(url=track['thumbnail'])
                    
                    embed.add_field(
                        name="🎧 Demandé par",
                        value=track['requested_by'],
                        inline=True
                    )
                    
                    queue_size = len(self.music_queues[guild_id])
                    embed.add_field(
                        name="📋 Queue",
                        value=f"{queue_size} pistes restantes",
                        inline=True
                    )
                    
                    await channel.send(embed=embed)
                    
        except Exception as e:
            print(f"Erreur lecture audio: {e}")
            await self.play_next(guild_id)  # Essayer la piste suivante

    @app_commands.command(name="playlist_enhanced", description="🎵 Lecture playlist YouTube complète")
    @app_commands.describe(url="URL de la playlist YouTube")
    async def playlist_enhanced(self, interaction: discord.Interaction, url: str):
        """Lecture complète d'une playlist YouTube"""
        
        if "playlist" not in url.lower():
            await interaction.response.send_message("❌ Veuillez fournir une URL de playlist YouTube valide", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        vc = await self.ensure_voice_connection(interaction)
        if not vc:
            return
        
        try:
            playlist_opts = self.ytdl_options.copy()
            playlist_opts['extract_flat'] = True
            
            with yt_dlp.YoutubeDL(playlist_opts) as ydl:
                playlist_info = ydl.extract_info(url, download=False)
                entries = playlist_info.get('entries', [])
                
                if not entries:
                    await interaction.followup.send("❌ Playlist vide ou introuvable")
                    return
                
                # Limiter à 100 pistes pour éviter les abus
                entries = entries[:100]
                
                embed = discord.Embed(
                    title="🎵 Playlist Ajoutée",
                    description=f"**{playlist_info.get('title', 'Playlist')}**\n{len(entries)} pistes ajoutées à la queue",
                    color=discord.Color.green()
                )
                
                await interaction.followup.send(embed=embed)
                
                # Ajouter toutes les pistes à la queue
                guild_id = interaction.guild.id
                if guild_id not in self.music_queues:
                    self.music_queues[guild_id] = deque()
                
                for entry in entries:
                    if entry:
                        track_info = {
                            'title': entry.get('title', 'Titre inconnu'),
                            'url': f"https://www.youtube.com/watch?v={entry['id']}",
                            'duration': entry.get('duration', 0),
                            'thumbnail': entry.get('thumbnail'),
                            'requested_by': interaction.user.display_name
                        }
                        self.music_queues[guild_id].append(track_info)
                
                # Commencer la lecture si rien ne joue
                if not vc.is_playing():
                    await self.play_next(guild_id)
                    
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur playlist: {str(e)[:100]}...")

    @app_commands.command(name="volume_enhanced", description="🔊 Contrôle du volume avancé")
    @app_commands.describe(level="Niveau de volume (0-100)")
    async def volume_enhanced(self, interaction: discord.Interaction, level: app_commands.Range[int, 0, 100]):
        """Contrôle du volume avec mémoire"""
        
        guild_id = interaction.guild.id
        volume = level / 100.0
        
        # Sauvegarder le volume
        self.set_guild_volume(guild_id, volume)
        
        # Appliquer au lecteur actuel
        if guild_id in self.voice_clients:
            vc = self.voice_clients[guild_id]
            if vc.source and hasattr(vc.source, 'volume'):
                vc.source.volume = volume
        
        embed = discord.Embed(
            title="🔊 Volume Modifié",
            description=f"Volume défini à **{level}%**",
            color=discord.Color.blue()
        )
        
        # Emoji selon le niveau
        if level == 0:
            emoji = "🔇"
        elif level < 30:
            emoji = "🔈"
        elif level < 70:
            emoji = "🔉"
        else:
            emoji = "🔊"
        
        embed.add_field(
            name=f"{emoji} Niveau",
            value=f"{level}% / 100%",
            inline=True
        )
        
        embed.set_footer(text="Volume sauvegardé pour ce serveur")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="queue_enhanced", description="📋 File d'attente musicale avancée")
    async def queue_enhanced(self, interaction: discord.Interaction):
        """Affiche la queue avec plus de détails"""
        
        guild_id = interaction.guild.id
        queue = self.music_queues.get(guild_id, deque())
        current = self.current_tracks.get(guild_id)
        
        if not queue and not current:
            embed = discord.Embed(
                title="📋 File d'Attente Vide",
                description="Aucune piste dans la queue\nUtilisez `/play_enhanced` pour ajouter de la musique",
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title="📋 File d'Attente Musicale",
            color=discord.Color.blue()
        )
        
        # Piste actuelle
        if current:
            embed.add_field(
                name="🎵 En cours",
                value=f"**{current['title']}**\nDemandé par: {current['requested_by']}",
                inline=False
            )
        
        # Prochaines pistes (limite à 10)
        if queue:
            next_tracks = []
            for i, track in enumerate(list(queue)[:10]):
                duration = ""
                if track.get('duration'):
                    mins, secs = divmod(track['duration'], 60)
                    duration = f" [{mins}:{secs:02d}]"
                
                next_tracks.append(f"{i+1}. **{track['title']}**{duration}")
            
            embed.add_field(
                name=f"⏭️ Prochaines pistes ({len(queue)} total)",
                value="\n".join(next_tracks) or "Aucune",
                inline=False
            )
            
            if len(queue) > 10:
                embed.add_field(
                    name="📊 Statistiques",
                    value=f"**Total:** {len(queue)} pistes\n**Affichage:** 10 premières\n**Volume:** {self.get_guild_volume(guild_id)*100:.0f}%",
                    inline=True
                )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shuffle_enhanced", description="🔀 Mélanger la file d'attente")
    async def shuffle_enhanced(self, interaction: discord.Interaction):
        """Mélange intelligemment la queue"""
        
        guild_id = interaction.guild.id
        queue = self.music_queues.get(guild_id, deque())
        
        if len(queue) < 2:
            await interaction.response.send_message("❌ Il faut au moins 2 pistes dans la queue pour mélanger", ephemeral=True)
            return
        
        # Convertir en liste, mélanger, reconvertir
        queue_list = list(queue)
        random.shuffle(queue_list)
        self.music_queues[guild_id] = deque(queue_list)
        
        embed = discord.Embed(
            title="🔀 Queue Mélangée",
            description=f"**{len(queue_list)} pistes** ont été mélangées aléatoirement",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="🎵 Prochaines pistes",
            value="\n".join([f"{i+1}. {track['title']}" for i, track in enumerate(queue_list[:5])]),
            inline=False
        )
        
        if len(queue_list) > 5:
            embed.set_footer(text=f"... et {len(queue_list)-5} autres pistes")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stop_enhanced", description="⏹️ Arrêter et déconnecter")
    async def stop_enhanced(self, interaction: discord.Interaction):
        """Arrêt complet avec nettoyage"""
        
        guild_id = interaction.guild.id
        
        # Arrêter la lecture
        if guild_id in self.voice_clients:
            vc = self.voice_clients[guild_id]
            if vc.is_connected():
                vc.stop()
                await vc.disconnect()
            del self.voice_clients[guild_id]
        
        # Nettoyer les données
        if guild_id in self.music_queues:
            del self.music_queues[guild_id]
        if guild_id in self.current_tracks:
            del self.current_tracks[guild_id]
        
        embed = discord.Embed(
            title="⏹️ Musique Arrêtée",
            description="Bot déconnecté et queue vidée",
            color=discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(EnhancedMusicSystem(bot))
    print("🎵 [Enhanced Music System] Module chargé avec succès!")

