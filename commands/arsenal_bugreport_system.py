"""
🐛 ARSENAL BUG REPORT SYSTEM - Modal Ultra-Rapide
Système de signalement de bugs avec modal et sélection de commandes
Sauvegarde en JSON avec prédictions d'erreurs automatiques
"""

import discord
from discord import app_commands
from discord.ext import commands
import datetime
import json
import os
import glob
from typing import Optional, List

class BugReportModal(discord.ui.Modal, title='🐛 Signaler un Bug Arsenal'):
    """Modal ultra-rapide pour signaler des bugs"""
    
    def __init__(self, command_name: str = "Non spécifié"):
        super().__init__()
        self.command_name = command_name
    
    description = discord.ui.TextInput(
        label='📝 Décrivez le bug rapidement',
        placeholder='Ex: La commande ne répond pas, erreur timeout, embed cassé...',
        max_length=500,
        style=discord.TextStyle.paragraph,
        required=True
    )
    
    steps = discord.ui.TextInput(
        label='🔄 Comment reproduire le bug? (optionnel)',
        placeholder='Ex: Utiliser /music play puis /music stop...',
        max_length=300,
        style=discord.TextStyle.paragraph,
        required=False
    )
    
    expected = discord.ui.TextInput(
        label='✅ Résultat attendu (optionnel)', 
        placeholder='Ex: La musique devrait s\'arrêter...',
        max_length=200,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        """Traitement du bug report"""
        
        # Prédictions d'erreurs automatiques basées sur la commande
        error_predictions = get_error_predictions(self.command_name, self.description.value)
        
        bug_data = {
            "id": f"BUG_{int(datetime.datetime.now().timestamp())}",
            "timestamp": datetime.datetime.now().isoformat(),
            "user_id": interaction.user.id,
            "user_name": str(interaction.user),
            "guild_id": interaction.guild.id if interaction.guild else None,
            "guild_name": interaction.guild.name if interaction.guild else "DM",
            "command": self.command_name,
            "description": self.description.value,
            "reproduction_steps": self.steps.value or "Non spécifié",
            "expected_result": self.expected.value or "Non spécifié",
            "error_predictions": error_predictions,
            "status": "nouveau",
            "priority": determine_priority(self.description.value, self.command_name)
        }
        
        # Sauvegarder le bug
        save_bug_report(bug_data)
        
        # Réponse avec embed stylé
        embed = discord.Embed(
            title="🐛 Bug Report Enregistré !",
            description=f"**ID**: `{bug_data['id']}`\n**Commande**: `{self.command_name}`",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="📝 Description",
            value=f"```{self.description.value[:100]}{'...' if len(self.description.value) > 100 else ''}```",
            inline=False
        )
        
        if error_predictions:
            predictions_text = "\n".join([f"• {pred}" for pred in error_predictions[:3]])
            embed.add_field(
                name="🔮 Prédictions d'Erreurs",
                value=predictions_text,
                inline=False
            )
        
        embed.add_field(
            name="⚡ Temps de Traitement Estimé",
            value=f"**{get_estimated_time(bug_data['priority'])}**",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Priorité",
            value=f"**{bug_data['priority'].upper()}**",
            inline=True
        )
        
        embed.set_footer(
            text="Merci de contribuer à améliorer Arsenal ! • Utilisez /voirbug pour suivre",
            icon_url=interaction.user.display_avatar.url
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class CommandSelectView(discord.ui.View):
    """Vue avec sélecteur de commandes pour signaler un bug"""
    
    def __init__(self):
        super().__init__(timeout=300)
        
        # Récupérer les commandes disponibles
        commands = get_arsenal_commands()
        
        # Créer les options (max 25 par sélecteur)
        options = []
        for cmd in commands[:24]:  # Garder de la place pour "Autre"
            emoji = get_command_emoji(cmd)
            options.append(discord.SelectOption(
                label=cmd,
                description=f"Signaler un bug avec /{cmd}",
                emoji=emoji
            ))
        
        options.append(discord.SelectOption(
            label="🤷 Autre/Non listé",
            description="Commande non listée ou bug général",
            emoji="❓"
        ))
        
        self.command_select.options = options
    
    @discord.ui.select(placeholder="🎯 Sélectionnez la commande avec le bug...")
    async def command_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        """Sélection de commande"""
        selected_command = select.values[0]
        
        if selected_command == "🤷 Autre/Non listé":
            selected_command = "Autre"
        
        # Ouvrir le modal avec la commande pré-sélectionnée
        modal = BugReportModal(selected_command)
        await interaction.response.send_modal(modal)

class ArsenalBugReport(commands.Cog):
    """Système de signalement de bugs ultra-rapide pour Arsenal"""
    
    def __init__(self, bot):
        self.bot = bot
        self.bugs_file = "arsenal_bugs.json"
        self.ensure_bugs_file()
    
    def ensure_bugs_file(self):
        """S'assurer que le fichier bugs existe"""
        if not os.path.exists(self.bugs_file):
            with open(self.bugs_file, 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)
    
    @app_commands.command(name="bugreport", description="🐛 Signaler un bug Arsenal en 5 secondes")
    async def bug_report(self, interaction: discord.Interaction):
        """Commande pour signaler un bug rapidement"""
        
        embed = discord.Embed(
            title="🐛 Bug Report Arsenal",
            description="**Signalez un bug en 5 secondes chrono !**\n\n🎯 **Étape 1**: Sélectionnez la commande\n⚡ **Étape 2**: Décrivez rapidement le problème\n✅ **Étape 3**: C'est tout !",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="🚀 Pourquoi c'est rapide ?",
            value="• Sélection automatique de commande\n• Prédictions d'erreurs intégrées\n• Priorité calculée automatiquement\n• Sauvegarde instantanée",
            inline=True
        )
        
        embed.add_field(
            name="🔮 Intelligence Intégrée",
            value="• Détection d'erreurs communes\n• Suggestions de solutions\n• Estimation temps de fix\n• Classement par priorité",
            inline=True
        )
        
        embed.set_footer(text="Arsenal Bug Report System • Cliquez sur le menu ci-dessous")
        
        view = CommandSelectView()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="voirbug", description="👁️ Voir les bugs reportés (Créateur uniquement)")
    async def voir_bugs(self, interaction: discord.Interaction, status: Optional[str] = None, limit: Optional[int] = 10):
        """Voir les bugs reportés"""
        
        # Vérifier permissions (tu peux ajuster l'ID)
        creator_id = 123456789  # Remplace par ton ID Discord
        if interaction.user.id != creator_id:
            await interaction.response.send_message("❌ Seul le créateur peut voir les bugs !", ephemeral=True)
            return
        
        # Charger les bugs
        bugs = load_bug_reports()
        
        if not bugs:
            embed = discord.Embed(
                title="📋 Aucun Bug Reporté",
                description="Aucun bug n'a été signalé pour le moment !",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Filtrer par status si spécifié
        if status:
            bugs = [bug for bug in bugs if bug.get('status', 'nouveau') == status.lower()]
        
        # Limiter le nombre
        bugs = bugs[-limit:] if limit else bugs[-10:]  # Les plus récents
        
        embed = discord.Embed(
            title="🐛 Bug Reports Arsenal",
            description=f"**{len(bugs)} bugs** (sur {len(load_bug_reports())} total)",
            color=discord.Color.blue()
        )
        
        for bug in bugs:
            priority_emoji = {"critique": "🔥", "haute": "⚠️", "moyenne": "📌", "basse": "💭"}.get(bug.get('priority', 'moyenne'), "📌")
            
            embed.add_field(
                name=f"{priority_emoji} {bug['id']} - /{bug['command']}",
                value=(
                    f"**User**: {bug['user_name']}\n"
                    f"**Status**: {bug.get('status', 'nouveau').title()}\n"
                    f"**Description**: {bug['description'][:80]}{'...' if len(bug['description']) > 80 else ''}\n"
                    f"**Date**: <t:{int(datetime.datetime.fromisoformat(bug['timestamp']).timestamp())}:R>"
                ),
                inline=False
            )
        
        embed.set_footer(text=f"Utilisez /voirbug status:nouveau pour voir seulement les nouveaux")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# ========================================
# FONCTIONS UTILITAIRES 
# ========================================

def get_arsenal_commands() -> List[str]:
    """Récupère la liste des commandes Arsenal disponibles"""
    commands = [
        "music", "play", "stop", "skip", "queue", "volume",
        "ban", "kick", "mute", "warn", "timeout", 
        "help", "info", "ping", "stats", "profile",
        "economy", "balance", "shop", "buy", "daily",
        "hunt", "royal", "crypto", "wallet", "invest",
        "config", "setup", "automod", "logs", "welcome",
        "tempvoice", "ticket", "poll", "giveaway", "level",
        "leaderboard", "xp", "rank", "rep", "marriage"
    ]
    return sorted(commands)

def get_command_emoji(command: str) -> str:
    """Retourne un emoji pour une commande"""
    emojis = {
        "music": "🎵", "play": "▶️", "stop": "⏹️", "skip": "⏭️",
        "ban": "🔨", "kick": "👢", "mute": "🔇", "warn": "⚠️",
        "help": "❓", "info": "ℹ️", "ping": "🏓", "stats": "📊",
        "economy": "💰", "balance": "💳", "shop": "🛒", "daily": "📅",
        "config": "⚙️", "setup": "🔧", "automod": "🛡️", "logs": "📋"
    }
    return emojis.get(command, "🔧")

def get_error_predictions(command: str, description: str) -> List[str]:
    """Génère des prédictions d'erreurs basées sur la commande et description"""
    predictions = []
    
    desc_lower = description.lower()
    
    # Prédictions par commande
    if command in ["music", "play", "stop", "skip"]:
        if "timeout" in desc_lower or "lent" in desc_lower:
            predictions.append("Possible problème de connexion réseau")
        if "permission" in desc_lower or "erreur" in desc_lower:
            predictions.append("Vérifier les permissions vocales du bot")
        if "lag" in desc_lower or "coupé" in desc_lower:
            predictions.append("Problème de stabilité de connexion Discord")
    
    elif command in ["ban", "kick", "mute", "warn"]:
        if "permission" in desc_lower:
            predictions.append("Bot manque de permissions de modération")
        if "erreur" in desc_lower:
            predictions.append("Hiérarchie des rôles incorrecte")
    
    elif command in ["economy", "balance", "shop"]:
        if "erreur" in desc_lower or "bug" in desc_lower:
            predictions.append("Possible corruption de base de données")
        if "lent" in desc_lower:
            predictions.append("Optimisation requise pour les requêtes DB")
    
    # Prédictions générales
    if "crash" in desc_lower or "plante" in desc_lower:
        predictions.append("Exception non gérée dans le code")
    if "lent" in desc_lower or "timeout" in desc_lower:
        predictions.append("Problème de performance ou réseau")
    if "embed" in desc_lower:
        predictions.append("Formatage embed incorrect")
    
    return predictions[:3]  # Max 3 prédictions

def determine_priority(description: str, command: str) -> str:
    """Détermine la priorité du bug automatiquement"""
    desc_lower = description.lower()
    
    # Mots-clés critiques
    if any(word in desc_lower for word in ["crash", "plante", "erreur fatale", "impossible"]):
        return "critique"
    
    # Commandes importantes
    if command in ["ban", "kick", "music", "economy"] and "erreur" in desc_lower:
        return "haute"
    
    # Problèmes de performance
    if any(word in desc_lower for word in ["lent", "lag", "timeout", "freeze"]):
        return "moyenne"
    
    return "basse"

def get_estimated_time(priority: str) -> str:
    """Retourne le temps estimé de résolution"""
    times = {
        "critique": "🔥 24h max",
        "haute": "⚠️ 2-3 jours", 
        "moyenne": "📌 1 semaine",
        "basse": "💭 Prochaine mise à jour"
    }
    return times.get(priority, "📌 1 semaine")

def save_bug_report(bug_data: dict):
    """Sauvegarde un bug report"""
    bugs = load_bug_reports()
    bugs.append(bug_data)
    
    with open("arsenal_bugs.json", 'w', encoding='utf-8') as f:
        json.dump(bugs, f, indent=2, ensure_ascii=False)

def load_bug_reports() -> List[dict]:
    """Charge les bug reports"""
    if not os.path.exists("arsenal_bugs.json"):
        return []
    
    try:
        with open("arsenal_bugs.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

async def setup(bot):
    await bot.add_cog(ArsenalBugReport(bot))
