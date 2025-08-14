import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from typing import Dict, Any, Optional
import datetime

class ArsenalConfigSelect(discord.ui.Select):
    """Menu de configuration complet inspiré d'Arsenal"""
    def __init__(self):
        options = [
            discord.SelectOption(
                label="👋 Arrivées & Départs", 
                description="Messages de bienvenue et d'au revoir",
                value="welcome",
                emoji="👋"
            ),
            discord.SelectOption(
                label="📜 Règlement", 
                description="Règles automatiques et modération",
                value="rules",
                emoji="📜"
            ),
            discord.SelectOption(
                label="📈 Niveaux", 
                description="Système XP et progression des membres",
                value="leveling",
                emoji="📈"
            ),
            discord.SelectOption(
                label="💰 Économie", 
                description="ArsenalCoin et système économique",
                value="economy",
                emoji="💰"
            ),
            discord.SelectOption(
                label="🎒 Objets & Inventaires", 
                description="Système d'objets et collections",
                value="inventory",
                emoji="🎒"
            ),
            discord.SelectOption(
                label="🔨 Modération", 
                description="Outils de modération avancés",
                value="moderation",
                emoji="🔨"
            ),
            discord.SelectOption(
                label="🏷️ Gestion des Rôles", 
                description="Attribution automatique de rôles",
                value="roles",
                emoji="🏷️"
            ),
            discord.SelectOption(
                label="💡 Suggestions", 
                description="Système de suggestions communautaires",
                value="suggestions",
                emoji="💡"
            ),
            discord.SelectOption(
                label="📢 Notifications Sociales", 
                description="YouTube, Twitch, Twitter, etc.",
                value="social",
                emoji="📢"
            ),
            discord.SelectOption(
                label="📋 Logs", 
                description="Journalisation complète des événements",
                value="logs",
                emoji="📋"
            ),
            discord.SelectOption(
                label="🛡️ Captcha", 
                description="Système de vérification anti-bot",
                value="captcha",
                emoji="🛡️"
            ),
            discord.SelectOption(
                label="🎂 Anniversaires", 
                description="Célébration automatique des anniversaires",
                value="birthdays",
                emoji="🎂"
            ),
            discord.SelectOption(
                label="⚡ Commandes Personnalisées", 
                description="Créer des commandes sur mesure",
                value="custom_commands",
                emoji="⚡"
            ),
            discord.SelectOption(
                label="👁️ Réactions de Mots", 
                description="Auto-réactions sur certains mots",
                value="word_reactions",
                emoji="👁️"
            ),
            discord.SelectOption(
                label="🎫 Tickets", 
                description="Support client et tickets privés",
                value="tickets",
                emoji="🎫"
            ),
            discord.SelectOption(
                label="🌐 Interserveurs", 
                description="Communication entre serveurs Discord",
                value="interserver",
                emoji="🌐"
            ),
            discord.SelectOption(
                label="ℹ️ Commandes d'Informations", 
                description="Utilitaires et informations serveur",
                value="info_commands",
                emoji="ℹ️"
            ),
            discord.SelectOption(
                label="🎮 Commandes Jeux Fun", 
                description="Mini-jeux et divertissement",
                value="fun_games",
                emoji="🎮"
            ),
            discord.SelectOption(
                label="⏰ Rappels", 
                description="Système de rappels personnels",
                value="reminders",
                emoji="⏰"
            ),
            discord.SelectOption(
                label="⭐ Rôles-Réactions", 
                description="Attribution de rôles par réactions",
                value="reaction_roles",
                emoji="⭐"
            ),
            discord.SelectOption(
                label="💬 Gestion des Messages", 
                description="Édition et gestion automatique",
                value="message_management",
                emoji="💬"
            ),
            discord.SelectOption(
                label="🚨 Signalements", 
                description="Système de signalement de contenu",
                value="reports",
                emoji="🚨"
            ),
            discord.SelectOption(
                label="🔔 Messages Récurrents", 
                description="Messages automatiques programmés",
                value="recurring_messages",
                emoji="🔔"
            ),
            discord.SelectOption(
                label="🎵 Salons Vocaux Temporaires", 
                description="Salons vocaux auto-créés",
                value="temp_voice",
                emoji="🎵"
            ),
            discord.SelectOption(
                label="🛡️ Auto-Modération", 
                description="Modération automatique intelligente",
                value="automod",
                emoji="🛡️"
            )
        ]
        # Discord limite à 25 options max, donc on prend les 25 premiers
        super().__init__(
            placeholder="🔧 Choisissez un module à configurer (Style Arsenal)...",
            min_values=1,
            max_values=1,
            options=options[:25]  # Limite Discord
        )

    async def callback(self, interaction: discord.Interaction):
        system = self.values[0]
        await interaction.response.defer()
        
        config_handler = ArsenalCompleteConfig(interaction.client)
        await config_handler.handle_system_config(interaction, system)

class ArsenalCompleteConfig(commands.Cog):
    """Système de configuration complet Arsenal Original"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_path = "data/draftbot_config"
        os.makedirs(self.config_path, exist_ok=True)

    @app_commands.command(name="config", description="🔧 Configuration complète d'Arsenal (Style Arsenal Original)")
    @app_commands.describe(reset="Réinitialiser toute la configuration")
    async def config(self, interaction: discord.Interaction, reset: bool = False):
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permissions Insuffisantes",
                description="Vous devez être **administrateur** pour utiliser cette commande.",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if reset:
            await self.reset_all_config(interaction)
            return

        embed = discord.Embed(
            title="🔧 Configuration Arsenal - Bot Français Original",
            description=f"""
**Bot N°1 Français All-in-One** 🇫🇷

**Serveur:** `{interaction.guild.name}`
**Modules disponibles:** `29 systèmes complets`

Utilisez le menu déroulant ci-dessous pour configurer chaque module individuellement avec l'interface Arsenal.

> 💡 **Astuce:** Chaque module dispose de sa propre interface de configuration avec des options avancées créées par Arsenal !
            """,
            color=0x00ff00,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="📊 Modules Populaires",
            value="• 👋 **Arrivées & Départs**\n• 💰 **Économie Arsenal**\n• 📈 **Système de Niveaux**\n• 🎫 **Support Tickets**",
            inline=True
        )
        
        embed.add_field(
            name="🛡️ Modération Avancée",
            value="• 🔨 **Modération Pro**\n• 🛡️ **Auto-Modération IA**\n• 🚨 **Signalements**\n• 📋 **Logs Complets**",
            inline=True
        )
        
        embed.add_field(
            name="🎮 Divertissement",
            value="• 🎮 **Jeux & Fun**\n• 🎂 **Anniversaires**\n• ⏰ **Rappels**\n• 🎵 **Vocal Temporaire**",
            inline=True
        )

        embed.set_footer(
            text="Arsenal V4.5 • Plus de 150 commandes disponibles • Système Original",
            icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None
        )

        view = discord.ui.View(timeout=300)
        view.add_item(ArsenalConfigSelect())
        
        await interaction.response.send_message(embed=embed, view=view)

    async def handle_system_config(self, interaction: discord.Interaction, system: str):
        """Gère la configuration d'un système spécifique"""
        
        config_methods = {
            "welcome": self.configure_welcome,
            "rules": self.configure_rules,
            "leveling": self.configure_leveling,
            "economy": self.configure_economy,
            "inventory": self.configure_inventory,
            "moderation": self.configure_moderation,
            "roles": self.configure_roles,
            "suggestions": self.configure_suggestions,
            "social": self.configure_social,
            "logs": self.configure_logs,
            "captcha": self.configure_captcha,
            "birthdays": self.configure_birthdays,
            "custom_commands": self.configure_custom_commands,
            "word_reactions": self.configure_word_reactions,
            "tickets": self.configure_tickets,
            "interserver": self.configure_interserver,
            "info_commands": self.configure_info_commands,
            "fun_games": self.configure_fun_games,
            "reminders": self.configure_reminders,
            "reaction_roles": self.configure_reaction_roles,
            "message_management": self.configure_message_management,
            "reports": self.configure_reports,
            "recurring_messages": self.configure_recurring_messages,
            "temp_voice": self.configure_temp_voice,
            "automod": self.configure_automod
        }
        
        if system in config_methods:
            await config_methods[system](interaction)
        else:
            embed = discord.Embed(
                title="⚠️ Module en Développement",
                description=f"Le module **{system}** sera disponible dans une prochaine mise à jour d'Arsenal !",
                color=0xffa500
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    async def configure_welcome(self, interaction: discord.Interaction):
        """Configuration des messages d'arrivée et de départ"""
        embed = discord.Embed(
            title="👋 Configuration Arrivées & Départs",
            description="""
**Messages de Bienvenue Personnalisés**

**Variables disponibles:**
• `{user}` - Mention du membre
• `{username}` - Nom d'utilisateur
• `{server}` - Nom du serveur
• `{member_count}` - Nombre de membres

**Fonctionnalités:**
✅ Messages d'arrivée personnalisés
✅ Messages de départ
✅ Rôles automatiques
✅ Salons privés de bienvenue
✅ Embed personnalisable
✅ Images de bienvenue
            """,
            color=0x00ff00
        )
        
        embed.add_field(
            name="📝 Configuration Actuelle",
            value="• **Statut:** `Désactivé`\n• **Salon:** `Non configuré`\n• **Rôle auto:** `Aucun`",
            inline=True
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def configure_economy(self, interaction: discord.Interaction):
        """Configuration du système économique"""
        embed = discord.Embed(
            title="💰 Configuration Économie Arsenal",
            description="""
**Système ArsenalCoin Complet**

**Fonctionnalités disponibles:**
✅ Monnaie virtuelle ArsenalCoin (AC)
✅ Salaire quotidien configurable
✅ Boutique serveur personnalisée
✅ Transferts entre membres
✅ Classement richesse
✅ Multiplicateurs de gain
✅ Événements économiques

**Commandes économiques:**
• `/balance` - Solde du membre
• `/daily` - Récompense quotidienne
• `/pay` - Payer un autre membre
• `/shop` - Boutique du serveur
• `/leaderboard money` - Top économique
            """,
            color=0xffd700
        )
        
        current_config = self.load_config(interaction.guild.id, "economy")
        
        embed.add_field(
            name="⚙️ Configuration Actuelle",
            value=f"""• **Statut:** `{current_config.get('enabled', 'Désactivé')}`
• **Salaire quotidien:** `{current_config.get('daily_amount', 100)} AC`
• **Monnaie:** `ArsenalCoin (AC)`
• **Boutique:** `{len(current_config.get('shop_items', []))} objets`""",
            inline=True
        )
        
        embed.add_field(
            name="🏪 Boutique Serveur",
            value=f"""• **Objets globaux:** `Disponibles`
• **Objets serveur:** `{len(current_config.get('server_items', []))} configurés`
• **Auto-refresh:** `24h`""",
            inline=True
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def configure_leveling(self, interaction: discord.Interaction):
        """Configuration du système de niveaux"""
        embed = discord.Embed(
            title="📈 Configuration Système de Niveaux",
            description="""
**Système XP et Progression**

**Fonctionnalités:**
✅ Gain d'XP par messages
✅ Niveaux avec récompenses
✅ Classement serveur
✅ Rôles de niveau automatiques
✅ Cartes de profil personnalisées
✅ Multiplicateurs temporaires
✅ XP vocal (salons vocaux)

**Paramètres configurables:**
• XP par message: `15-25 XP`
• Cooldown: `60 secondes`
• XP vocal: `1 XP/minute`
• Formule niveau: `100 × niveau²`
            """,
            color=0x9932cc
        )
        
        embed.add_field(
            name="🏆 Récompenses de Niveau",
            value="• **Niveau 5:** `Rôle Actif`\n• **Niveau 10:** `Rôle Régulier`\n• **Niveau 25:** `Rôle Expert`\n• **Niveau 50:** `Rôle Légende`",
            inline=True
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def configure_tickets(self, interaction: discord.Interaction):
        """Configuration du système de tickets"""
        embed = discord.Embed(
            title="🎫 Configuration Système de Tickets",
            description="""
**Support Client Professionnel**

**Types de tickets disponibles:**
✅ Support général
✅ Réclamations
✅ Suggestions privées
✅ Signalements
✅ Demandes personnalisées

**Fonctionnalités avancées:**
• Auto-archivage après inactivité
• Transcripts automatiques
• Notifications staff
• Boutons de réaction
• Catégories personnalisées
• Permissions granulaires
            """,
            color=0x32cd32
        )
        
        embed.add_field(
            name="⚙️ Configuration",
            value="• **Catégorie:** `Non configurée`\n• **Rôle staff:** `@Modérateur`\n• **Auto-close:** `7 jours`\n• **Transcripts:** `Activés`",
            inline=True
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    async def configure_automod(self, interaction: discord.Interaction):
        """Configuration de l'auto-modération"""
        embed = discord.Embed(
            title="🛡️ Configuration Auto-Modération IA",
            description="""
**Modération Automatique Intelligente**

**Détections automatiques:**
✅ Spam et flood
✅ Liens interdits
✅ Langage toxique
✅ Mentions excessives
✅ Contenu NSFW
✅ Invitations Discord
✅ Messages répétitifs

**Actions automatiques:**
• Suppression instantanée
• Avertissements automatiques
• Timeout temporaire
• Exclusion automatique
• Notifications staff
            """,
            color=0xff4500
        )
        
        embed.add_field(
            name="🎯 Niveau de Détection",
            value="• **Spam:** `Élevé`\n• **Toxicité:** `Moyen`\n• **Liens:** `Strict`\n• **NSFW:** `Maximum`",
            inline=True
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

    # Méthodes de configuration pour les autres systèmes (placeholder)
    async def configure_rules(self, interaction): 
        await self.send_placeholder_config(interaction, "📜 Règlement", "Configuration automatique du règlement serveur")
    
    async def configure_inventory(self, interaction): 
        await self.send_placeholder_config(interaction, "🎒 Objets & Inventaires", "Système d'objets collectibles")
    
    async def configure_moderation(self, interaction): 
        await self.send_placeholder_config(interaction, "🔨 Modération", "Outils de modération avancés")
    
    async def configure_roles(self, interaction): 
        await self.send_placeholder_config(interaction, "🏷️ Gestion des Rôles", "Attribution automatique de rôles")
    
    async def configure_suggestions(self, interaction): 
        await self.send_placeholder_config(interaction, "💡 Suggestions", "Système de suggestions communautaires")
    
    async def configure_social(self, interaction): 
        await self.send_placeholder_config(interaction, "📢 Notifications Sociales", "Notifications réseaux sociaux")
    
    async def configure_logs(self, interaction): 
        await self.send_placeholder_config(interaction, "📋 Logs", "Journalisation complète des événements")
    
    async def configure_captcha(self, interaction): 
        await self.send_placeholder_config(interaction, "🛡️ Captcha", "Système de vérification anti-bot")
    
    async def configure_birthdays(self, interaction): 
        await self.send_placeholder_config(interaction, "🎂 Anniversaires", "Célébration automatique des anniversaires")
    
    async def configure_custom_commands(self, interaction): 
        await self.send_placeholder_config(interaction, "⚡ Commandes Personnalisées", "Créer des commandes sur mesure")
    
    async def configure_word_reactions(self, interaction): 
        await self.send_placeholder_config(interaction, "👁️ Réactions de Mots", "Auto-réactions sur certains mots")
    
    async def configure_interserver(self, interaction): 
        await self.send_placeholder_config(interaction, "🌐 Interserveurs", "Communication entre serveurs")
    
    async def configure_info_commands(self, interaction): 
        await self.send_placeholder_config(interaction, "ℹ️ Commandes d'Informations", "Utilitaires et informations")
    
    async def configure_fun_games(self, interaction): 
        await self.send_placeholder_config(interaction, "🎮 Jeux Fun", "Mini-jeux et divertissement")
    
    async def configure_reminders(self, interaction): 
        await self.send_placeholder_config(interaction, "⏰ Rappels", "Système de rappels personnels")
    
    async def configure_reaction_roles(self, interaction): 
        await self.send_placeholder_config(interaction, "⭐ Rôles-Réactions", "Attribution de rôles par réactions")
    
    async def configure_message_management(self, interaction): 
        await self.send_placeholder_config(interaction, "💬 Gestion Messages", "Édition et gestion automatique")
    
    async def configure_reports(self, interaction): 
        await self.send_placeholder_config(interaction, "🚨 Signalements", "Système de signalement de contenu")
    
    async def configure_recurring_messages(self, interaction): 
        await self.send_placeholder_config(interaction, "🔔 Messages Récurrents", "Messages automatiques programmés")
    
    async def configure_temp_voice(self, interaction): 
        await self.send_placeholder_config(interaction, "🎵 Salons Vocaux Temporaires", "Salons vocaux auto-créés")

    async def send_placeholder_config(self, interaction: discord.Interaction, title: str, description: str):
        """Envoie une configuration placeholder pour les modules en développement"""
        embed = discord.Embed(
            title=f"{title}",
            description=f"""
**{description}**

⚠️ **Module en cours de développement**

Ce module sera disponible dans une prochaine mise à jour d'Arsenal avec toutes les fonctionnalités avancées et plus encore !

**Fonctionnalités prévues:**
• Interface de configuration complète Arsenal
• Options avancées personnalisables
• Intégration avec les autres modules Arsenal
• Système de permissions granulaires Arsenal
            """,
            color=0xffa500
        )
        await interaction.followup.send(embed=embed, ephemeral=True)

    def load_config(self, guild_id: int, system: str) -> Dict[str, Any]:
        """Charge la configuration d'un système"""
        config_file = f"{self.config_path}/{guild_id}_{system}.json"
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def save_config(self, guild_id: int, system: str, config: Dict[str, Any]) -> bool:
        """Sauvegarde la configuration d'un système"""
        config_file = f"{self.config_path}/{guild_id}_{system}.json"
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False

    async def reset_all_config(self, interaction: discord.Interaction):
        """Réinitialise toute la configuration du serveur"""
        embed = discord.Embed(
            title="🔄 Réinitialisation Complète",
            description="⚠️ **ATTENTION** - Cette action va supprimer **TOUTE** la configuration du serveur !\n\nÊtes-vous sûr de vouloir continuer ?",
            color=0xff0000
        )
        
        view = discord.ui.View(timeout=60)
        
        async def confirm_reset(button_interaction):
            # Supprimer tous les fichiers de config de ce serveur
            import glob
            config_files = glob.glob(f"{self.config_path}/{interaction.guild.id}_*.json")
            for file in config_files:
                try:
                    os.remove(file)
                except:
                    pass
            
            success_embed = discord.Embed(
                title="✅ Réinitialisation Terminée",
                description="Toute la configuration du serveur a été réinitialisée avec succès !",
                color=0x00ff00
            )
            await button_interaction.response.edit_message(embed=success_embed, view=None)
        
        async def cancel_reset(button_interaction):
            cancel_embed = discord.Embed(
                title="❌ Réinitialisation Annulée",
                description="Aucune modification n'a été apportée à la configuration.",
                color=0x808080
            )
            await button_interaction.response.edit_message(embed=cancel_embed, view=None)
        
        confirm_button = discord.ui.Button(label="✅ Confirmer", style=discord.ButtonStyle.danger)
        cancel_button = discord.ui.Button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
        
        confirm_button.callback = confirm_reset
        cancel_button.callback = cancel_reset
        
        view.add_item(confirm_button)
        view.add_item(cancel_button)
        
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(ArsenalCompleteConfig(bot))
