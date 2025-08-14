import discord
from discord import app_commands
from discord.ext import commands
import datetime

class CommunityCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="info", description="Informations sur Arsenal Bot")
    async def info(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=" Arsenal Bot V4.5.0",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.timezone.utc)
        )
        embed.add_field(name=" Status", value="En ligne", inline=True)
        embed.add_field(name=" ArsenalCoin", value="Actif", inline=True)
        embed.add_field(name=" Commandes", value="150+", inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="report", description="Signaler un membre")
    @app_commands.describe(member="Membre à signaler", reason="Raison")
    async def report(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        await interaction.response.send_message(
            f" Signalement de {member.mention} reçu: {reason}", 
            ephemeral=True
        )

    @app_commands.command(name="top_vocal", description="Classement vocal (en développement)")
    async def top_vocal(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            " Système de classement vocal en cours d'implémentation!", 
            ephemeral=True
        )

    @app_commands.command(name="top_messages", description="Classement messages (en développement)")
    async def top_messages(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            " Système de classement messages en cours d'implémentation!", 
            ephemeral=True
        )

    @app_commands.command(name="version", description="Version du bot")
    async def version(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title=" Arsenal V4.5.0", 
            color=discord.Color.orange()
        )
        embed.add_field(name="Status", value="Production", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(CommunityCommands(bot))
