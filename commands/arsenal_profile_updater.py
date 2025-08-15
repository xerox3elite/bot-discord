import discord
from discord.ext import commands, tasks
import json
import asyncio
from datetime import datetime, timezone

class ArsenalProfileUpdater(commands.Cog):
    """
    🎯 Arsenal Profile Updater
    Met à jour automatiquement le profil Discord d'Arsenal pour afficher
    toutes les fonctionnalités supportées
    """
    
    def __init__(self, bot):
        self.bot = bot
        self.profile_data = {
            "supported_features": [
                "⚡ Commandes Slash (/)",
                "🛡️ AutoMod Discord Natif", 
                "🔘 Boutons Interactifs",
                "📋 Menus Déroulants",
                "📝 Modales/Formulaires",
                "🖱️ Menus Contextuels (Clic Droit)",
                "⭐ Réactions Automatiques",
                "👑 Gestion Rôles & Permissions",
                "🎫 Système de Tickets",
                "📊 Logs d'Audit Avancés",
                "⚡ Événements Temps Réel",
                "🔗 Intégrations Externes",
                "🎵 Système Musical HD",
                "🏆 Niveaux & Gamification",
                "🌍 Traduction Automatique",
                "🔒 Protection Anti-Raid",
                "🌐 Dashboard Web",
                "🤖 IA de Modération",
                "🔊 Fonctionnalités Vocales",
                "💰 Économie ArsenalCoins"
            ],
            "integrations": [
                "YouTube", "Twitch", "Spotify", "GitHub", "Google Sheets", 
                "Twitter", "Instagram", "TikTok", "Reddit", "Steam"
            ],
            "stats": {
                "commands": 150,
                "features": 20,
                "integrations": 10,
                "servers": 0,  # Sera mis à jour automatiquement
                "users": 0     # Sera mis à jour automatiquement
            }
        }
        
        # Démarrer la tâche de mise à jour
        self.update_profile_task.start()
    
    def cog_unload(self):
        """Arrêter les tâches quand le cog est déchargé"""
        self.update_profile_task.cancel()
    
    @tasks.loop(hours=1)  # Mise à jour toutes les heures
    async def update_profile_task(self):
        """Tâche automatique pour mettre à jour le profil"""
        try:
            await self.update_bot_profile()
        except Exception as e:
            print(f"Erreur mise à jour profil: {e}")
    
    @update_profile_task.before_loop
    async def before_update_profile(self):
        """Attendre que le bot soit prêt avant de démarrer"""
        await self.bot.wait_until_ready()
        # Attendre 30 secondes après le démarrage pour la première mise à jour
        await asyncio.sleep(30)
    
    async def update_bot_profile(self):
        """Met à jour le profil du bot avec les dernières statistiques"""
        try:
            # Mettre à jour les statistiques
            self.profile_data["stats"]["servers"] = len(self.bot.guilds)
            self.profile_data["stats"]["users"] = sum(guild.member_count for guild in self.bot.guilds if guild.member_count)
            
            # Créer une biographie complète
            bio_parts = [
                "🚀 **Arsenal Bot V4.5.1** - Bot Discord révolutionnaire",
                f"⚡ {self.profile_data['stats']['commands']}+ commandes slash",
                f"🎯 {self.profile_data['stats']['features']} catégories de fonctionnalités",
                "",
                "✨ **FONCTIONNALITÉS DISCORD NATIVES:**",
                "• Commandes Slash (/) avec auto-complétion",
                "• AutoMod Discord intégré + IA avancée", 
                "• Boutons & Menus interactifs",
                "• Modales/Formulaires pour saisie",
                "• Menus contextuels (clic droit)",
                "• Réactions & rôles automatiques",
                "",
                "🔥 **SYSTÈMES AVANCÉS:**",
                "• 💰 ArsenalCoins - Économie complète",
                "• 🎵 Musique HD multi-sources",
                "• 🛡️ Protection anti-raid IA",
                "• 🌍 Traduction 50+ langues",
                "• 🎫 Système tickets professionnel",
                "• 📊 Analytics temps réel",
                "",
                "🔗 **INTÉGRATIONS:**",
                "• YouTube • Twitch • Spotify • GitHub",
                "• Google APIs • Discord Natif • IA",
                "",
                f"📈 **{self.profile_data['stats']['servers']} serveurs** • **{self.profile_data['stats']['users']} utilisateurs**",
                "",
                "🌐 Dashboard: panel.arsenal-bot.xyz",
                "📚 Support: /help • /features • /migration_help"
            ]
            
            # Créer la biographie (limite Discord: 190 caractères pour le statut)
            short_bio = (
                f"🚀 Arsenal V4.5.1 | "
                f"⚡{self.profile_data['stats']['commands']}+ commandes | "
                f"🎯{self.profile_data['stats']['features']} fonctionnalités Discord natives | "
                f"💰 ArsenalCoins | 🎵 Musique HD | 🛡️ AutoMod IA"
            )
            
            # Note: Discord ne permet pas de modifier la biographie du bot via l'API
            # Mais on peut mettre à jour le statut et l'activité
            
            # Mettre à jour l'activité avec les statistiques
            activity_text = (
                f"Arsenal V4.5.1 | "
                f"{self.profile_data['stats']['servers']} serveurs | "
                f"{self.profile_data['stats']['commands']}+ commandes | "
                f"🎯 Toutes fonctionnalités Discord"
            )
            
            # Créer l'activité streaming (statut violet)
            activity = discord.Streaming(
                name=activity_text[:128],  # Limite Discord pour les noms d'activité
                url="https://twitch.tv/xerox3elite"
            )
            
            await self.bot.change_presence(activity=activity)
            
            print(f"✅ Profil Arsenal mis à jour: {self.profile_data['stats']['servers']} serveurs, {self.profile_data['stats']['users']} utilisateurs")
            
        except Exception as e:
            print(f"❌ Erreur mise à jour profil Arsenal: {e}")
    
    @commands.command(name="update_profile")
    @commands.is_owner()
    async def force_update_profile(self, ctx):
        """Force la mise à jour du profil (commande owner uniquement)"""
        await self.update_bot_profile()
        await ctx.send("✅ Profil Arsenal mis à jour!")
    
    @commands.command(name="profile_info")
    async def show_profile_info(self, ctx):
        """Affiche les informations du profil Arsenal"""
        embed = discord.Embed(
            title="🎯 Arsenal Bot - Informations Profil",
            description="**Configuration actuelle du profil Discord**",
            color=discord.Color.blue()
        )
        
        # Statistiques actuelles
        stats = self.profile_data["stats"]
        embed.add_field(
            name="📊 Statistiques",
            value=(
                f"🏠 **{stats['servers']}** serveurs\n"
                f"👥 **{stats['users']}** utilisateurs\n"
                f"⚡ **{stats['commands']}+** commandes\n"
                f"🎯 **{stats['features']}** catégories fonctionnalités"
            ),
            inline=True
        )
        
        # Fonctionnalités mises en avant
        featured_functions = [
            "⚡ Commandes Slash (/)",
            "🛡️ AutoMod Discord Natif",
            "💰 Économie ArsenalCoins", 
            "🎵 Système Musical HD",
            "🌍 Traduction Auto",
            "🤖 IA de Modération"
        ]
        
        embed.add_field(
            name="✨ Fonctionnalités Mises en Avant",
            value="\n".join(featured_functions[:6]),
            inline=True
        )
        
        # Intégrations
        integrations_text = " • ".join(self.profile_data["integrations"][:6])
        if len(self.profile_data["integrations"]) > 6:
            integrations_text += f" • +{len(self.profile_data['integrations'])-6} autres"
        
        embed.add_field(
            name="🔗 Intégrations",
            value=integrations_text,
            inline=False
        )
        
        # Statut actuel
        current_activity = self.bot.activity
        if current_activity:
            embed.add_field(
                name="📺 Statut Actuel",
                value=f"**{current_activity.type.name}**: {current_activity.name}",
                inline=False
            )
        
        embed.add_field(
            name="🔄 Mise à Jour Auto",
            value="Profil mis à jour automatiquement toutes les heures",
            inline=False
        )
        
        embed.set_footer(text="Arsenal V4.5.1 - Profil Discord optimisé")
        
        await ctx.send(embed=embed)
    
    async def generate_features_list(self) -> str:
        """Génère une liste formatée des fonctionnalités"""
        features_text = ""
        for i, feature in enumerate(self.profile_data["supported_features"], 1):
            features_text += f"{i:2d}. {feature}\n"
        return features_text
    
    def get_profile_summary(self) -> dict:
        """Retourne un résumé du profil pour d'autres modules"""
        return {
            "total_features": len(self.profile_data["supported_features"]),
            "total_integrations": len(self.profile_data["integrations"]),
            "stats": self.profile_data["stats"].copy(),
            "last_update": datetime.now(timezone.utc).isoformat()
        }

async def setup(bot):
    await bot.add_cog(ArsenalProfileUpdater(bot))
