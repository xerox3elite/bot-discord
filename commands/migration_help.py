import discord
from discord import app_commands
from discord.ext import commands
import datetime

class MigrationHelp(commands.Cog):
    """Système d'aide dédié à la migration Arsenal"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="migration_help", description="🚀 Guide complet du système de migration Arsenal")
    async def migration_help(self, interaction: discord.Interaction):
        """Affiche l'aide complète pour la migration"""
        
        # Embed principal
        embed = discord.Embed(
            title="🚀 Arsenal Bot Migration System",
            description="**Système révolutionnaire de migration de configurations**",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        
        embed.add_field(
            name="🎯 Concept",
            value=(
                "Importez automatiquement les configurations d'autres bots Discord populaires "
                "vers Arsenal Bot avec des améliorations révolutionnaires !"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🤖 Bots Supportés",
            value=(
                "• **DraftBot** - 12 modules (bienvenue, automod, niveaux, économie...)\n"
                "• **Dyno** - 5 modules (automod, modération, formulaires...)\n"
                "• **Carl-bot** - 3 modules (automod, rôles-réactions, tags...)\n"
                "• **MEE6** - 3 modules (niveaux, modération, bienvenue...)"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚡ Commandes Essentielles",
            value=(
                "`/migrate_bot bot:draftbot scan_only:True` - **Scanner uniquement**\n"
                "`/migrate_bot bot:draftbot scan_only:False` - **Migration complète**\n"
                "`/migration_help` - **Afficher cette aide**\n"
                "`/config_modal` - **Configuration Arsenal post-migration**"
            ),
            inline=False
        )
        
        embed.set_footer(text="Arsenal V4.5.1 - Migration System", icon_url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        
        # Boutons d'action
        view = MigrationHelpView()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class MigrationHelpView(discord.ui.View):
    """Interface d'aide pour la migration"""
    
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="📚 Guide Détaillé", style=discord.ButtonStyle.primary, emoji="📖")
    async def detailed_guide(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Guide détaillé de migration"""
        embed = discord.Embed(
            title="📚 Guide Détaillé de Migration",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📋 Étapes de Migration",
            value=(
                "**1.** Scanner le bot source avec `scan_only:True`\n"
                "**2.** Analyser les résultats et modules détectés\n"
                "**3.** Lancer la migration avec `scan_only:False`\n"
                "**4.** Sélectionner les modules à migrer via boutons\n"
                "**5.** Confirmer et attendre la fin du processus\n"
                "**6.** Tester les nouvelles fonctionnalités Arsenal\n"
                "**7.** Désactiver l'ancien bot pour éviter les conflits"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Précautions Importantes",
            value=(
                "• **Sauvegarde automatique** créée avant migration\n"
                "• **Permissions administrateur** requises\n"
                "• **Arsenal doit avoir** les mêmes permissions que l'ancien bot\n"
                "• **Test recommandé** sur serveur de développement d'abord\n"
                "• **Une seule migration** par serveur à la fois"
            ),
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🔧 Exemples Pratiques", style=discord.ButtonStyle.secondary, emoji="⚙️")
    async def practical_examples(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Exemples pratiques de migration"""
        embed = discord.Embed(
            title="🔧 Exemples Pratiques de Migration",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="🎯 Scénario 1: Migration DraftBot complète",
            value=(
                "```\n"
                "/migrate_bot bot:draftbot scan_only:False\n"
                "```\n"
                "**Résultat:** Tous les modules DraftBot analysés et proposés\n"
                "**Modules populaires:** Bienvenue, AutoMod, Niveaux, Économie\n"
                "**Temps estimé:** 45-60 minutes pour migration complète"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎯 Scénario 2: Migration Dyno ciblée",
            value=(
                "```\n"
                "/migrate_bot bot:dyno scan_only:False\n"
                "```\n"
                "**Résultat:** Focus sur AutoMod et Modération\n"
                "**Modules spécialisés:** Formulaires, Gestion rôles\n"
                "**Temps estimé:** 20-30 minutes pour modules essentiels"
            ),
            inline=False
        )
        
        embed.add_field(
            name="✨ Bonus Arsenal après Migration",
            value=(
                "🤖 **IA de modération** - Détection contextuelle avancée\n"
                "🎨 **Interface moderne** - Boutons et modals Discord\n"
                "📊 **Analytics temps réel** - Statistiques détaillées\n"
                "⚡ **Performance optimisée** - Conçu pour gros serveurs\n"
                "💎 **ArsenalCoins** - Économie révolutionnaire"
            ),
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🚨 Résolution Problèmes", style=discord.ButtonStyle.danger, emoji="🛠️")
    async def troubleshooting(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Guide de résolution de problèmes"""
        embed = discord.Embed(
            title="🚨 Résolution de Problèmes Migration",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="❌ Erreurs Communes",
            value=(
                "**Bot non supporté**\n"
                "→ Vérifiez l'orthographe: `draftbot`, `dyno`, `carlbot`, `mee6`\n\n"
                "**Bot non présent**\n"
                "→ Le bot source doit être sur le serveur\n\n"
                "**Permissions insuffisantes**\n"
                "→ Vous devez être administrateur du serveur\n\n"
                "**Migration échoue**\n"
                "→ Arsenal doit avoir les mêmes permissions que l'ancien bot"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔧 Solutions Rapides",
            value=(
                "**1.** Vérifier les permissions d'Arsenal\n"
                "**2.** Relancer avec moins de modules sélectionnés\n"
                "**3.** Scanner d'abord (`scan_only:True`)\n"
                "**4.** Vérifier que l'ancien bot est actif\n"
                "**5.** Attendre quelques minutes entre tentatives"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📞 Support Avancé",
            value=(
                "• Logs détaillés sauvegardés automatiquement\n"
                "• Sauvegarde de sécurité toujours créée\n"
                "• Possibilité de restauration manuelle\n"
                "• Support communautaire disponible"
            ),
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🎉 Démo Interactive", style=discord.ButtonStyle.success, emoji="🚀")
    async def interactive_demo(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Démo interactive du système"""
        embed = discord.Embed(
            title="🎉 Démo Arsenal Migration System",
            description="**Simulation d'une migration DraftBot → Arsenal**",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="📥 Configuration DraftBot Détectée",
            value=(
                "• **Bienvenue**: `#bienvenue` - Message basique\n"
                "• **AutoMod**: Anti-spam + Anti-pub activés\n"
                "• **Niveaux**: Système XP avec 150 utilisateurs\n"
                "• **Économie**: DraftCoins avec 50 utilisateurs actifs\n"
                "• **Logs**: `#mod-logs` configuré\n"
                "• **Suggestions**: `#suggestions` avec votes"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚡ Transformation Arsenal Prévue",
            value=(
                "• **Bienvenue Elite**: Variables {member_count}, embeds stylés\n"
                "• **AutoMod IA**: Détection contextuelle + protection raids\n"
                "• **Niveaux+**: Conserve XP + nouveaux paliers/récompenses\n"
                "• **ArsenalCoins**: Migration DraftCoins + shop/daily/work\n"
                "• **Logs Pro**: Plus d'événements + analytics temps réel\n"
                "• **Suggestions 2.0**: Threading + modération intégrée"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎯 Résultat Final",
            value=(
                "✅ **100%** des fonctionnalités DraftBot préservées\n"
                "🚀 **+75** nouvelles fonctionnalités exclusives Arsenal\n"
                "⭐ **Interface révolutionnaire** avec boutons Discord\n"
                "📊 **Analytics avancées** et statistiques temps réel\n"
                "🛡️ **Sécurité renforcée** avec IA de modération"
            ),
            inline=False
        )
        
        embed.set_footer(text="🎬 Cette démo représente les résultats typiques d'une migration DraftBot")
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🏠 Retour", style=discord.ButtonStyle.gray, emoji="↩️", row=1)
    async def back_to_main(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Retour au menu principal"""
        embed = discord.Embed(
            title="🚀 Arsenal Bot Migration System",
            description="**Système révolutionnaire de migration de configurations**",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🎯 Concept",
            value=(
                "Importez automatiquement les configurations d'autres bots Discord populaires "
                "vers Arsenal Bot avec des améliorations révolutionnaires !"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🤖 Bots Supportés",
            value=(
                "• **DraftBot** - 12 modules (bienvenue, automod, niveaux, économie...)\n"
                "• **Dyno** - 5 modules (automod, modération, formulaires...)\n"
                "• **Carl-bot** - 3 modules (automod, rôles-réactions, tags...)\n"
                "• **MEE6** - 3 modules (niveaux, modération, bienvenue...)"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚡ Commandes Essentielles",
            value=(
                "`/migrate_bot bot:draftbot scan_only:True` - **Scanner uniquement**\n"
                "`/migrate_bot bot:draftbot scan_only:False` - **Migration complète**\n"
                "`/migration_help` - **Afficher cette aide**\n"
                "`/config_modal` - **Configuration Arsenal post-migration**"
            ),
            inline=False
        )
        
        await interaction.response.edit_message(embed=embed, view=self)

async def setup(bot):
    await bot.add_cog(MigrationHelp(bot))
