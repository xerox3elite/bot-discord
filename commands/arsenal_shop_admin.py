"""
🛠️ Arsenal Shop Management System
Système de gestion de boutique personnalisable pour les administrateurs
Développé par XeRoX - Arsenal Bot V4
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from typing import Optional

class ArsenalShopAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.shop_config_file = "data/shop_config.json"

    def load_shop_config(self):
        """Charge la configuration du shop"""
        try:
            with open(self.shop_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"servers": {}, "global_items": {}}

    def save_shop_config(self, data):
        """Sauvegarde la configuration du shop"""
        with open(self.shop_config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @app_commands.command(name="shop_admin", description="🛠️ Interface d'administration de la boutique (Admin uniquement)")
    @app_commands.describe(
        action="Action à effectuer",
        item_id="ID de l'article",
        name="Nom de l'article",
        description="Description de l'article",
        price="Prix en ArsenalCoin"
    )
    @app_commands.choices(action=[
        app_commands.Choice(name="📋 Voir les articles", value="list"),
        app_commands.Choice(name="➕ Ajouter un article", value="add"),
        app_commands.Choice(name="❌ Supprimer un article", value="remove"),
        app_commands.Choice(name="✏️ Modifier un article", value="edit"),
        app_commands.Choice(name="🔄 Reset du shop", value="reset")
    ])
    async def shop_admin(
        self, 
        interaction: discord.Interaction, 
        action: str,
        item_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[int] = None
    ):
        """Interface d'administration du shop"""
        
        # Vérifier les permissions d'admin
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Accès Refusé",
                description="Cette commande nécessite les permissions d'administrateur.",
                color=0xff6b6b
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        shop_config = self.load_shop_config()
        guild_id = str(interaction.guild_id)
        
        # Initialiser le serveur dans la config si nécessaire
        if guild_id not in shop_config.get("servers", {}):
            if "servers" not in shop_config:
                shop_config["servers"] = {}
            shop_config["servers"][guild_id] = {"items": {}}

        if action == "list":
            await self.show_shop_items(interaction, shop_config, guild_id)
        elif action == "add":
            await self.add_shop_item(interaction, shop_config, guild_id, item_id, name, description, price)
        elif action == "remove":
            await self.remove_shop_item(interaction, shop_config, guild_id, item_id)
        elif action == "edit":
            await self.edit_shop_item(interaction, shop_config, guild_id, item_id, name, description, price)
        elif action == "reset":
            await self.reset_shop(interaction, shop_config, guild_id)

    async def show_shop_items(self, interaction: discord.Interaction, shop_config, guild_id: str):
        """Affiche les articles du shop"""
        embed = discord.Embed(
            title="🛠️ Administration - Articles du Serveur",
            color=0x3498db,
            timestamp=discord.utils.utcnow()
        )

        server_items = shop_config.get("servers", {}).get(guild_id, {}).get("items", {})
        
        if not server_items:
            embed.description = "Aucun article personnalisé pour ce serveur."
            embed.add_field(
                name="💡 Comment Ajouter",
                value="`/shop_admin action:Ajouter item_id:mon_item name:Mon Article description:Description price:1000`",
                inline=False
            )
        else:
            items_text = ""
            for item_id, item_data in server_items.items():
                items_text += f"🏷️ **{item_id}**\n"
                items_text += f"   📝 {item_data['name']} - {item_data['price']:,} AC\n"
                items_text += f"   📄 {item_data['description'][:60]}...\n\n"
            
            embed.add_field(
                name=f"🏪 Articles Actifs ({len(server_items)})",
                value=items_text,
                inline=False
            )

        # Articles globaux Arsenal (lecture seule)
        global_items = shop_config.get("global_items", {})
        if global_items:
            global_text = ""
            for item_id, item_data in list(global_items.items())[:3]:
                global_text += f"🌟 **{item_data['name']}** - {item_data['price']:,} AC\n"
            
            embed.add_field(
                name="🌟 Articles Arsenal (Global)",
                value=global_text + f"\n*+{len(global_items)-3} autres articles Arsenal...*" if len(global_items) > 3 else global_text,
                inline=False
            )

        embed.set_footer(text="Arsenal Shop Management", icon_url=self.bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def add_shop_item(self, interaction: discord.Interaction, shop_config, guild_id: str, item_id: str, name: str, description: str, price: int):
        """Ajoute un article au shop"""
        if not all([item_id, name, description, price]):
            embed = discord.Embed(
                title="❌ Paramètres Manquants",
                description="Tous les paramètres sont requis pour ajouter un article.",
                color=0xff6b6b
            )
            embed.add_field(
                name="📋 Paramètres Requis",
                value="`item_id`, `name`, `description`, `price`",
                inline=False
            )
            embed.add_field(
                name="💡 Exemple",
                value="`/shop_admin action:add item_id:vip_role name:Rôle VIP description:Accès VIP au serveur price:5000`",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if price < 1:
            embed = discord.Embed(
                title="❌ Prix Invalide",
                description="Le prix doit être supérieur à 0 AC.",
                color=0xff6b6b
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        server_items = shop_config["servers"][guild_id]["items"]
        
        if item_id in server_items:
            embed = discord.Embed(
                title="❌ Article Existant",
                description=f"L'article `{item_id}` existe déjà.",
                color=0xff6b6b
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Ajouter l'article
        server_items[item_id] = {
            "name": name,
            "description": description,
            "price": price,
            "type": "custom",
            "created_by": str(interaction.user.id),
            "created_at": discord.utils.utcnow().isoformat()
        }

        self.save_shop_config(shop_config)

        embed = discord.Embed(
            title="✅ Article Ajouté",
            description=f"L'article **{name}** a été ajouté au shop du serveur !",
            color=0x00ff88,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="🏷️ ID", value=item_id, inline=True)
        embed.add_field(name="📝 Nom", value=name, inline=True)
        embed.add_field(name="💰 Prix", value=f"{price:,} AC", inline=True)
        embed.add_field(name="📄 Description", value=description, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def remove_shop_item(self, interaction: discord.Interaction, shop_config, guild_id: str, item_id: str):
        """Supprime un article du shop"""
        if not item_id:
            embed = discord.Embed(
                title="❌ ID Manquant",
                description="Vous devez spécifier l'ID de l'article à supprimer.",
                color=0xff6b6b
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        server_items = shop_config["servers"][guild_id]["items"]
        
        if item_id not in server_items:
            embed = discord.Embed(
                title="❌ Article Introuvable",
                description=f"L'article `{item_id}` n'existe pas.",
                color=0xff6b6b
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Sauvegarder les infos avant suppression
        item_name = server_items[item_id]["name"]
        
        # Supprimer l'article
        del server_items[item_id]
        self.save_shop_config(shop_config)

        embed = discord.Embed(
            title="🗑️ Article Supprimé",
            description=f"L'article **{item_name}** (`{item_id}`) a été supprimé du shop.",
            color=0xff9500,
            timestamp=discord.utils.utcnow()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def edit_shop_item(self, interaction: discord.Interaction, shop_config, guild_id: str, item_id: str, name: str, description: str, price: int):
        """Modifie un article du shop"""
        if not item_id:
            embed = discord.Embed(
                title="❌ ID Manquant",
                description="Vous devez spécifier l'ID de l'article à modifier.",
                color=0xff6b6b
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        server_items = shop_config["servers"][guild_id]["items"]
        
        if item_id not in server_items:
            embed = discord.Embed(
                title="❌ Article Introuvable",
                description=f"L'article `{item_id}` n'existe pas.",
                color=0xff6b6b
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Mettre à jour les champs fournis
        item = server_items[item_id]
        changes = []

        if name:
            old_name = item["name"]
            item["name"] = name
            changes.append(f"Nom: `{old_name}` → `{name}`")

        if description:
            item["description"] = description
            changes.append(f"Description mise à jour")

        if price is not None:
            if price < 1:
                embed = discord.Embed(
                    title="❌ Prix Invalide",
                    description="Le prix doit être supérieur à 0 AC.",
                    color=0xff6b6b
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            old_price = item["price"]
            item["price"] = price
            changes.append(f"Prix: `{old_price:,} AC` → `{price:,} AC`")

        if not changes:
            embed = discord.Embed(
                title="❌ Aucun Changement",
                description="Vous devez spécifier au moins un paramètre à modifier.",
                color=0xff6b6b
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        item["modified_at"] = discord.utils.utcnow().isoformat()
        item["modified_by"] = str(interaction.user.id)

        self.save_shop_config(shop_config)

        embed = discord.Embed(
            title="✏️ Article Modifié",
            description=f"L'article **{item['name']}** a été mis à jour !",
            color=0x3498db,
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(
            name="🔄 Changements",
            value="\n".join(changes),
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def reset_shop(self, interaction: discord.Interaction, shop_config, guild_id: str):
        """Reset le shop du serveur"""
        server_items = shop_config["servers"][guild_id]["items"]
        items_count = len(server_items)
        
        if items_count == 0:
            embed = discord.Embed(
                title="ℹ️ Shop Déjà Vide",
                description="Le shop de ce serveur ne contient aucun article personnalisé.",
                color=0x3498db
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Créer une vue de confirmation
        view = ConfirmResetView()
        
        embed = discord.Embed(
            title="⚠️ Confirmation de Reset",
            description=f"Êtes-vous sûr de vouloir supprimer **{items_count} article(s)** du shop ?",
            color=0xff9500
        )
        
        embed.add_field(
            name="⚠️ Attention",
            value="Cette action est **irréversible** !",
            inline=False
        )

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
        # Attendre la réponse
        await view.wait()
        
        if view.value:
            # Reset confirmé
            shop_config["servers"][guild_id]["items"] = {}
            self.save_shop_config(shop_config)
            
            embed = discord.Embed(
                title="🔄 Shop Reseté",
                description=f"**{items_count} article(s)** supprimé(s) avec succès.",
                color=0x00ff88,
                timestamp=discord.utils.utcnow()
            )
            
            await interaction.edit_original_response(embed=embed, view=None)

class ConfirmResetView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=30)
        self.value = None

    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = True
        self.stop()

    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        self.value = False
        self.stop()

async def setup(bot):
    await bot.add_cog(ArsenalShopAdmin(bot))
    print("✅ [Arsenal Shop Admin] Système d'administration de boutique chargé")

