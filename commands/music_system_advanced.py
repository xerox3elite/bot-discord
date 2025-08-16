# Arsenal V4 - Système Musical Avancé avec installation automatique des dépendances
import sys
import subprocess
import importlib

def install_and_import(package_name, import_name=None):
    """Installe et importe un package automatiquement"""
    if import_name is None:
        import_name = package_name
    
    try:
        return importlib.import_module(import_name)
    except ImportError:
        print(f"Installation de {package_name}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        return importlib.import_module(import_name)

# Installation automatique des dépendances
wavelink = install_and_import("wavelink")
spotipy = install_and_import("spotipy")
youtube_dl = install_and_import("youtube-dl", "youtube_dl")

import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import json
import os
import aiosqlite
from datetime import datetime, timedelta
import random
import re
from typing import Optional
import aiohttp

class MusicSystemAdvanced(commands.Cog):
    """Système musical YouTube/Spotify avancé pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/music_advanced.db"
        self.playlists = {}
        self.queue_history = {}
        self.user_preferences = {}
        self.setup_database()
        
        # Configuration Spotify
        self.spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.spotify_client = None
        
        if self.spotify_client_id and self.spotify_client_secret:
            try:
                self.spotify_client = spotipy.Spotify(
                    client_credentials_manager=spotipy.SpotifyClientCredentials(
                        client_id=self.spotify_client_id,
                        client_secret=self.spotify_client_secret
                    )
                )
            except Exception as e:
                print(f"Erreur initialisation Spotify: {e}")
    
    async def setup_database(self):
        """Initialise la base de données musique"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    tracks TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    plays INTEGER DEFAULT 0
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS music_stats (
                    user_id INTEGER PRIMARY KEY,
                    total_plays INTEGER DEFAULT 0,
                    favorite_genre TEXT,
                    total_time INTEGER DEFAULT 0,
                    last_played TEXT,
                    achievements TEXT DEFAULT '[]'
                )
            """)
            
            await db.commit()

    @app_commands.command(name="play", description="🎵 Jouer de la musique depuis YouTube ou Spotify")
    @app_commands.describe(query="Nom de la musique, URL YouTube/Spotify ou playlist")
    async def play_music(self, interaction: discord.Interaction, query: str):
        """Commande principale pour jouer de la musique"""
        
        await interaction.response.defer()
        
        try:
            # Vérification si l'utilisateur est dans un salon vocal
            if not interaction.user.voice:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Vous devez être connecté à un salon vocal !",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Connexion au salon vocal si nécessaire
            if not interaction.guild.voice_client:
                try:
                    vc = await interaction.user.voice.channel.connect(cls=wavelink.Player)
                except Exception as e:
                    embed = discord.Embed(
                        title="❌ Erreur de connexion",
                        description=f"Impossible de se connecter: {str(e)}",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed)
                    return
            else:
                vc = interaction.guild.voice_client
            
            # Détection du type de query et recherche
            if "spotify.com" in query:
                tracks = await self._search_spotify(query)
            elif "youtube.com" in query or "youtu.be" in query:
                tracks = await self._search_youtube(query)
            else:
                # Recherche générale
                tracks = await self._search_youtube(f"ytsearch:{query}")
            
            if not tracks:
                embed = discord.Embed(
                    title="❌ Aucun résultat",
                    description="Aucune musique trouvée pour votre recherche.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Ajout à la queue
            for track in tracks[:10]:  # Limite à 10 tracks
                await vc.queue.put_wait(track)
            
            # Démarrage de la lecture si pas déjà en cours
            if not vc.playing:
                await vc.play(await vc.queue.get_wait())
            
            # Embed de confirmation
            embed = discord.Embed(
                title="🎵 Musique ajoutée",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            
            if len(tracks) == 1:
                embed.description = f"**{tracks[0].title}**\nDurée: {self._format_duration(tracks[0].duration)}"
                embed.set_thumbnail(url=tracks[0].thumbnail)
            else:
                embed.description = f"**{len(tracks)} musiques ajoutées** à la file d'attente"
            
            embed.add_field(
                name="📊 File d'attente",
                value=f"{vc.queue.qsize()} musique(s) en attente",
                inline=True
            )
            
            embed.add_field(
                name="🔊 Volume",
                value=f"{vc.volume}%",
                inline=True
            )
            
            await interaction.followup.send(embed=embed)
            
            # Mise à jour des statistiques
            await self._update_user_stats(interaction.user.id, len(tracks))
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur",
                description=f"Une erreur s'est produite: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)

    @app_commands.command(name="queue", description="📋 Afficher la file d'attente musicale")
    async def show_queue(self, interaction: discord.Interaction):
        """Affiche la file d'attente actuelle"""
        
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Aucun bot connecté !", ephemeral=True)
            return
        
        vc = interaction.guild.voice_client
        
        if vc.queue.is_empty:
            embed = discord.Embed(
                title="📋 File d'attente vide",
                description="Aucune musique en attente.",
                color=discord.Color.orange()
            )
        else:
            embed = discord.Embed(
                title="📋 File d'attente musicale",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            queue_list = []
            for i, track in enumerate(list(vc.queue)[:10], 1):
                queue_list.append(f"`{i}.` **{track.title}** - {self._format_duration(track.duration)}")
            
            embed.description = "\n".join(queue_list)
            
            if vc.queue.qsize() > 10:
                embed.set_footer(text=f"... et {vc.queue.qsize() - 10} autres musiques")
        
        # Musique actuellement jouée
        if vc.playing:
            embed.insert_field_at(0,
                name="🎵 Actuellement",
                value=f"**{vc.current.title}**\n{self._format_duration(vc.position)}/{self._format_duration(vc.current.duration)}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="skip", description="⏭️ Passer à la musique suivante")
    async def skip_track(self, interaction: discord.Interaction):
        """Passe à la musique suivante"""
        
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Aucun bot connecté !", ephemeral=True)
            return
        
        vc = interaction.guild.voice_client
        
        if not vc.playing:
            await interaction.response.send_message("❌ Aucune musique en cours !", ephemeral=True)
            return
        
        await vc.stop()
        
        embed = discord.Embed(
            title="⏭️ Musique passée",
            description="Passage à la musique suivante...",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="volume", description="🔊 Changer le volume (0-100)")
    @app_commands.describe(level="Niveau de volume entre 0 et 100")
    async def set_volume(self, interaction: discord.Interaction, level: int):
        """Change le volume du lecteur"""
        
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Aucun bot connecté !", ephemeral=True)
            return
        
        if not 0 <= level <= 100:
            await interaction.response.send_message("❌ Le volume doit être entre 0 et 100 !", ephemeral=True)
            return
        
        vc = interaction.guild.voice_client
        await vc.set_volume(level)
        
        embed = discord.Embed(
            title="🔊 Volume modifié",
            description=f"Volume réglé à **{level}%**",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="stop", description="⏹️ Arrêter la musique et déconnecter")
    async def stop_music(self, interaction: discord.Interaction):
        """Arrête la musique et déconnecte le bot"""
        
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Aucun bot connecté !", ephemeral=True)
            return
        
        vc = interaction.guild.voice_client
        vc.queue.clear()
        await vc.disconnect()
        
        embed = discord.Embed(
            title="⏹️ Musique arrêtée",
            description="Bot déconnecté et file d'attente vidée.",
            color=discord.Color.red()
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shuffle", description="🔀 Mélanger la file d'attente")
    async def shuffle_queue(self, interaction: discord.Interaction):
        """Mélange la file d'attente"""
        
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Aucun bot connecté !", ephemeral=True)
            return
        
        vc = interaction.guild.voice_client
        
        if vc.queue.is_empty:
            await interaction.response.send_message("❌ File d'attente vide !", ephemeral=True)
            return
        
        # Mélange de la queue
        queue_list = list(vc.queue)
        random.shuffle(queue_list)
        vc.queue.clear()
        
        for track in queue_list:
            await vc.queue.put_wait(track)
        
        embed = discord.Embed(
            title="🔀 File d'attente mélangée",
            description=f"{len(queue_list)} musiques mélangées !",
            color=discord.Color.purple()
        )
        
        await interaction.response.send_message(embed=embed)

    async def _search_spotify(self, query: str):
        """Recherche sur Spotify"""
        if not self.spotify_client:
            return []
        
        try:
            if "playlist" in query:
                playlist_id = query.split("/")[-1].split("?")[0]
                results = self.spotify_client.playlist_items(playlist_id)
                tracks = []
                for item in results['items'][:20]:  # Limite à 20 tracks
                    track = item['track']
                    search_query = f"{track['name']} {track['artists'][0]['name']}"
                    try:
                        # Compatible avec différentes versions de Wavelink
                        if hasattr(wavelink, 'YouTubeTrack'):
                            yt_tracks = await wavelink.YouTubeTrack.search(search_query)
                        elif hasattr(wavelink, 'tracks'):
                            yt_tracks = await wavelink.tracks.YouTubeTrack.search(search_query)
                        else:
                            yt_tracks = []
                        if yt_tracks:
                            tracks.append(yt_tracks[0])
                    except Exception as e:
                        print(f"[MUSIC] Erreur track search: {e}")
                        continue
                return tracks
            else:
                # Recherche de track individuel
                track_id = query.split("/")[-1].split("?")[0]
                track = self.spotify_client.track(track_id)
                search_query = f"{track['name']} {track['artists'][0]['name']}"
                try:
                    # Compatible avec différentes versions de Wavelink
                    if hasattr(wavelink, 'YouTubeTrack'):
                        return await wavelink.YouTubeTrack.search(search_query)
                    elif hasattr(wavelink, 'tracks'):
                        return await wavelink.tracks.YouTubeTrack.search(search_query)
                    else:
                        return []
                except Exception as e:
                    print(f"[MUSIC] Erreur track search individuel: {e}")
                    return []
        except Exception as e:
            print(f"Erreur Spotify: {e}")
            return []

    async def _search_youtube(self, query: str):
        """Recherche sur YouTube"""
        try:
            # Compatible avec différentes versions de Wavelink
            if hasattr(wavelink, 'YouTubeTrack'):
                tracks = await wavelink.YouTubeTrack.search(query)
            elif hasattr(wavelink, 'tracks'):
                tracks = await wavelink.tracks.YouTubeTrack.search(query)
            else:
                tracks = []
            return tracks
        except Exception as e:
            print(f"[MUSIC] Erreur YouTube: {e}")
            return []

    async def _update_user_stats(self, user_id: int, tracks_count: int):
        """Met à jour les statistiques utilisateur"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT OR IGNORE INTO music_stats (user_id, total_plays, last_played)
                    VALUES (?, ?, ?)
                """, (user_id, 0, datetime.now().isoformat()))
                
                await db.execute("""
                    UPDATE music_stats 
                    SET total_plays = total_plays + ?, last_played = ?
                    WHERE user_id = ?
                """, (tracks_count, datetime.now().isoformat(), user_id))
                
                await db.commit()
        except Exception as e:
            print(f"Erreur stats: {e}")

    def _format_duration(self, milliseconds):
        """Formate la durée en mm:ss"""
        if not milliseconds:
            return "00:00"
        
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        
        return f"{minutes:02d}:{seconds:02d}"

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload):
        """Événement de fin de track - Compatible toutes versions Wavelink"""
        try:
            vc = payload.player
            
            if hasattr(vc, 'queue') and not vc.queue.is_empty:
                next_track = await vc.queue.get_wait()
                await vc.play(next_track)
        except Exception as e:
            print(f"[MUSIC] Erreur lecture auto: {e}")
            # Continuer sans crash

async def setup(bot):
    """Charge le module MusicSystemAdvanced"""
    await bot.add_cog(MusicSystemAdvanced(bot))
    print("🎵 [Music System Advanced] Module chargé avec succès!")

def setup_audio(bot=None):
    """Configuration audio pour compatibilité avec main.py"""
    print("🎵 [Audio Setup] Configuration audio initialisée")
    return True
