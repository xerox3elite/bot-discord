import discord
from discord import app_commands
import os, sys, asyncio, json
from manager.config_manager import config_data, save_config
from core.logger import log

# 🔒 Arsenal Protection Middleware
from commands.arsenal_protection_middleware import require_registration

creator_group = app_commands.Group(name="creator", description="Commandes réservées au créateur d'Arsenal.")
CREATOR_ID = 431359112039890945  # Ton ID Discord ici
creator_tools_group = app_commands.Group(name="creator_tools", description="🔧 Outils avancés du créateur Arsenal")

def is_creator(user: discord.User) -> bool:
    return user.id == CREATOR_ID

# 🔄 Reload complet du bot
@creator_group.command(name="reload", description="Redémarre le bot proprement.")
@require_registration("creator")  # Réservé au créateur Arsenal
async def reload(interaction: discord.Interaction):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Accès refusé. Commande réservée au créateur.", ephemeral=True)
        return

    await interaction.response.send_message("♻️ Redémarrage du bot dans 3 secondes...", ephemeral=True)
    await asyncio.sleep(3)
    try:
        save_config()
        os.execl(sys.executable, sys.executable, *sys.argv)
    except Exception as e:
        await interaction.followup.send(f"❌ Erreur reboot : {e}", ephemeral=True)

# 🔧 Modifier un paramètre global du bot
@creator_group.command(name="config_set", description="Modifie une clé dans config.json")
@require_registration("creator")  # Réservé au créateur Arsenal
@app_commands.describe(cle="Nom du paramètre", valeur="Nouvelle valeur")
async def config_set(interaction: discord.Interaction, cle: str, valeur: str):
    if not is_creator(interaction.user):
        await interaction.response.send_message("🚫 Non autorisé", ephemeral=True)
        return

    config_data[cle] = valeur
    save_config()
    await interaction.response.send_message(f"✅ `{cle}` mis à jour → `{valeur}`", ephemeral=True)
    log.info(f"[CREATOR CONFIG] {cle} = {valeur}")

@app_commands.command(name="reset_bugs", description="🧹 Supprime tous les bugs signalés")
@require_registration("creator")  # Réservé au créateur Arsenal
async def reset_bugs(interaction: discord.Interaction):
    if interaction.user.id != CREATOR_ID:
        await interaction.response.send_message("🚫 Réservé au créateur Arsenal", ephemeral=True)
        return

    try:
        path = "bug_reports.json"
        if os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)
            embed = discord.Embed(title="🧹 Bugs réinitialisés", description="Tous les signalements ont été effacés.", color=discord.Color.green())
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("❌ Le fichier bug_reports.json est introuvable", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Erreur : {e}", ephemeral=True)
