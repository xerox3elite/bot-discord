"""
🏪 Arsenal Economy & Shop System
Système d'économie complet avec ArsenalCoin et boutiques personnalisables
Développé par XeRoX - Arsenal Bot V4
"""

import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime
from typing import Optional, Dict, Any

class ArsenalEconomySystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.economy_file = "data/economie.json"
        self.users_economy_file = "data/users_economy.json"
        self.shop_config_file = "data/shop_config.json"
        
        # Shop prédéfini Arsenal (AVANT init_files)
        self.default_arsenal_shop = {
            "premium_status": {
                "name": "🌟 Statut Premium",
                "description": "Statut premium pour 30 jours avec avantages exclusifs",
                "price": 50000,
                "type": "premium",
                "duration": 30,
                "benefits": ["Commandes exclusives", "Priorité support", "Badge premium"]
            },
            "vip_role": {
                "name": "👑 Rôle VIP",
                "description": "Rôle VIP permanent sur le serveur",
                "price": 25000,
                "type": "role",
                "role_name": "Arsenal VIP"
            },
            "custom_embed": {
                "name": "📝 Embed Personnalisé",
                "description": "Création d'un embed personnalisé",
                "price": 15000,
                "type": "service",
                "category": "design"
            },
            "boost_xp": {
                "name": "⚡ Boost XP x2",
                "description": "Double l'XP gagné pendant 7 jours",
                "price": 30000,
                "type": "boost",
                "multiplier": 2,
                "duration": 7
            },
            "exclusive_color": {
                "name": "🎨 Couleur Exclusive",
                "description": "Couleur de rôle personnalisée",
                "price": 20000,
                "type": "customization",
                "category": "color"
            }
        }

        # Initialiser les fichiers APRÈS avoir défini default_arsenal_shop
        self.init_files()

    def init_files(self):
        """Initialise les fichiers de données"""
        # Économie principale
        if not os.path.exists(self.economy_file):
            with open(self.economy_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        
        # Économie utilisateurs
        if not os.path.exists(self.users_economy_file):
            with open(self.users_economy_file, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        
        # Configuration du shop
        if not os.path.exists(self.shop_config_file):
            with open(self.shop_config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "servers": {},
                    "global_items": self.default_arsenal_shop
                }, f, ensure_ascii=False, indent=2)

    def load_economy_data(self) -> Dict[str, Any]:
        """Charge les données d'économie"""
        try:
            with open(self.economy_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    def save_economy_data(self, data: Dict[str, Any]):
        """Sauvegarde les données d'économie"""
        with open(self.economy_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_shop_config(self) -> Dict[str, Any]:
        """Charge la configuration du shop"""
        try:
            with open(self.shop_config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"servers": {}, "global_items": self.default_arsenal_shop}

    def save_shop_config(self, data: Dict[str, Any]):
        """Sauvegarde la configuration du shop"""
        with open(self.shop_config_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_user_balance(self, user_id: str) -> int:
        """Récupère le solde d'un utilisateur"""
        economy_data = self.load_economy_data()
        return economy_data.get(user_id, {}).get('balance', 0)

    def update_user_balance(self, user_id: str, amount: int, reason: str = "Transaction"):
        """Met à jour le solde d'un utilisateur"""
        economy_data = self.load_economy_data()
        
        if user_id not in economy_data:
            economy_data[user_id] = {"balance": 0, "history": []}
        
        old_balance = economy_data[user_id]["balance"]
        economy_data[user_id]["balance"] += amount
        
        # Ajouter à l'historique
        history_entry = {
            "type": reason,
            "amount": amount,
            "old_balance": old_balance,
            "new_balance": economy_data[user_id]["balance"],
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        economy_data[user_id]["history"].append(history_entry)
        
        # Garder seulement les 50 dernières transactions
        if len(economy_data[user_id]["history"]) > 50:
            economy_data[user_id]["history"] = economy_data[user_id]["history"][-50:]
        
        self.save_economy_data(economy_data)
        return economy_data[user_id]["balance"]

    @app_commands.command(name="balance", description="💰 Affiche votre solde ArsenalCoin")
    async def balance(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Affiche le solde ArsenalCoin"""
        target_user = user or interaction.user
        user_id = str(target_user.id)
        
        balance = self.get_user_balance(user_id)
        economy_data = self.load_economy_data()
        
        # Statistiques
        total_users = len(economy_data)
        user_rank = 1
        for uid, data in economy_data.items():
            if data.get('balance', 0) > balance:
                user_rank += 1
        
        embed = discord.Embed(
            title=f"💰 ArsenalCoin - {target_user.display_name}",
            color=0x00ff88,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="💳 Solde Actuel",
            value=f"**{balance:,} AC** 🪙",
            inline=True
        )
        
        embed.add_field(
            name="📊 Classement",
            value=f"**#{user_rank}** / {total_users}",
            inline=True
        )
        
        embed.add_field(
            name="📈 Statut",
            value="🌟 Premium" if balance > 100000 else "⭐ Standard",
            inline=True
        )
        
        # Historique récent
        if user_id in economy_data and economy_data[user_id].get("history"):
            recent = economy_data[user_id]["history"][-3:]
            history_text = "\n".join([
                f"• {entry['type']}: {'+' if entry['amount'] > 0 else ''}{entry['amount']:,} AC"
                for entry in reversed(recent)
            ])
            embed.add_field(
                name="📜 Transactions Récentes",
                value=history_text or "Aucune transaction",
                inline=False
            )
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        embed.set_footer(text="Arsenal Economy System", icon_url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="daily", description="🎁 Récupère ta récompense quotidienne ArsenalCoin")
    async def daily_reward(self, interaction: discord.Interaction):
        """Récompense quotidienne"""
        user_id = str(interaction.user.id)
        economy_data = self.load_economy_data()
        
        # Vérifier la dernière récupération
        if user_id in economy_data:
            last_daily = economy_data[user_id].get("last_daily")
            if last_daily:
                last_date = datetime.datetime.strptime(last_daily, "%Y-%m-%d")
                if last_date.date() == datetime.date.today():
                    embed = discord.Embed(
                        title="⏰ Récompense Déjà Récupérée",
                        description="Vous avez déjà récupéré votre récompense aujourd'hui !",
                        color=0xff6b6b,
                        timestamp=datetime.datetime.now()
                    )
                    embed.add_field(
                        name="⏳ Prochaine Récompense",
                        value="Demain à 00:00",
                        inline=False
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
        
        # Calculer la récompense
        base_reward = 1000
        streak_bonus = economy_data.get(user_id, {}).get("daily_streak", 0) * 100
        total_reward = base_reward + min(streak_bonus, 2000)  # Max 3000 AC
        
        # Mettre à jour le solde
        new_balance = self.update_user_balance(user_id, total_reward, "Récompense Quotidienne")
        
        # Mettre à jour la streak
        if user_id not in economy_data:
            economy_data[user_id] = {}
        
        economy_data[user_id]["last_daily"] = datetime.date.today().strftime("%Y-%m-%d")
        economy_data[user_id]["daily_streak"] = economy_data[user_id].get("daily_streak", 0) + 1
        
        self.save_economy_data(economy_data)
        
        embed = discord.Embed(
            title="🎁 Récompense Quotidienne",
            description=f"Vous avez reçu **{total_reward:,} ArsenalCoin** !",
            color=0x00ff88,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="💰 Nouveau Solde",
            value=f"**{new_balance:,} AC** 🪙",
            inline=True
        )
        
        embed.add_field(
            name="🔥 Série Quotidienne",
            value=f"**{economy_data[user_id]['daily_streak']} jours**",
            inline=True
        )
        
        if streak_bonus > 0:
            embed.add_field(
                name="⭐ Bonus Série",
                value=f"+{streak_bonus:,} AC",
                inline=True
            )
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shop", description="🏪 Ouvre la boutique Arsenal")
    async def shop(self, interaction: discord.Interaction):
        """Affiche la boutique Arsenal"""
        shop_config = self.load_shop_config()
        guild_id = str(interaction.guild_id)
        user_balance = self.get_user_balance(str(interaction.user.id))
        
        embed = discord.Embed(
            title="🏪 Boutique Arsenal",
            description="Achetez des avantages exclusifs avec vos ArsenalCoins !",
            color=0x00ff88,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="💰 Votre Solde",
            value=f"**{user_balance:,} AC** 🪙",
            inline=False
        )
        
        # Articles globaux Arsenal
        global_items = shop_config.get("global_items", {})
        if global_items:
            global_text = ""
            for item_id, item in list(global_items.items())[:5]:
                emoji = "🌟" if item["price"] > 30000 else "⭐" if item["price"] > 15000 else "🔹"
                global_text += f"{emoji} **{item['name']}**\n"
                global_text += f"   💰 {item['price']:,} AC - {item['description'][:50]}...\n\n"
            
            embed.add_field(
                name="🌟 Articles Arsenal Premium",
                value=global_text,
                inline=False
            )
        
        # Articles du serveur
        server_items = shop_config.get("servers", {}).get(guild_id, {}).get("items", {})
        if server_items:
            server_text = ""
            for item_id, item in list(server_items.items())[:3]:
                server_text += f"🛍️ **{item['name']}** - {item['price']:,} AC\n"
                server_text += f"   {item['description'][:50]}...\n\n"
            
            embed.add_field(
                name="🏪 Articles du Serveur",
                value=server_text,
                inline=False
            )
        
        embed.add_field(
            name="💡 Comment Utiliser",
            value="• `/buy <item>` - Acheter un article\n• `/shop_admin` - Gérer le shop (Admin)\n• `/daily` - Récompense quotidienne",
            inline=False
        )
        
        embed.set_footer(text="Arsenal Economy System", icon_url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="buy", description="💳 Achète un article de la boutique")
    async def buy_item(self, interaction: discord.Interaction, item: str):
        """Achète un article de la boutique"""
        await interaction.response.defer()
        
        user_id = str(interaction.user.id)
        guild_id = str(interaction.guild_id)
        user_balance = self.get_user_balance(user_id)
        
        shop_config = self.load_shop_config()
        
        # Rechercher l'article
        item_data = None
        item_location = None
        
        # Dans les articles globaux
        global_items = shop_config.get("global_items", {})
        for item_id, item_info in global_items.items():
            if item_id.lower() == item.lower() or item_info["name"].lower() == item.lower():
                item_data = item_info
                item_location = "global"
                break
        
        # Dans les articles du serveur
        if not item_data:
            server_items = shop_config.get("servers", {}).get(guild_id, {}).get("items", {})
            for item_id, item_info in server_items.items():
                if item_id.lower() == item.lower() or item_info["name"].lower() == item.lower():
                    item_data = item_info
                    item_location = "server"
                    break
        
        if not item_data:
            embed = discord.Embed(
                title="❌ Article Introuvable",
                description=f"L'article `{item}` n'existe pas dans la boutique.",
                color=0xff6b6b
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Vérifier le solde
        if user_balance < item_data["price"]:
            embed = discord.Embed(
                title="💸 Solde Insuffisant",
                description=f"Il vous faut **{item_data['price'] - user_balance:,} AC** de plus pour acheter cet article.",
                color=0xff6b6b
            )
            embed.add_field(
                name="💰 Votre Solde",
                value=f"{user_balance:,} AC",
                inline=True
            )
            embed.add_field(
                name="💳 Prix Article",
                value=f"{item_data['price']:,} AC",
                inline=True
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Effectuer l'achat
        new_balance = self.update_user_balance(user_id, -item_data["price"], f"Achat: {item_data['name']}")
        
        # Enregistrer l'achat
        self.record_purchase(user_id, guild_id, item_data)
        
        embed = discord.Embed(
            title="🛍️ Achat Réussi !",
            description=f"Vous avez acheté **{item_data['name']}** !",
            color=0x00ff88,
            timestamp=datetime.datetime.now()
        )
        
        embed.add_field(
            name="💰 Nouveau Solde",
            value=f"**{new_balance:,} AC** 🪙",
            inline=True
        )
        
        embed.add_field(
            name="💳 Prix Payé",
            value=f"{item_data['price']:,} AC",
            inline=True
        )
        
        embed.add_field(
            name="📦 Détails",
            value=item_data['description'],
            inline=False
        )
        
        if item_data.get("type") == "premium":
            embed.add_field(
                name="⭐ Activation",
                value="Votre statut premium sera activé sous peu.",
                inline=False
            )
        
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        
        await interaction.followup.send(embed=embed)

    def record_purchase(self, user_id: str, guild_id: str, item_data: Dict[str, Any]):
        """Enregistre un achat"""
        purchase_file = "data/purchases.json"
        
        try:
            with open(purchase_file, 'r', encoding='utf-8') as f:
                purchases = json.load(f)
        except:
            purchases = {}
        
        if user_id not in purchases:
            purchases[user_id] = []
        
        purchase_record = {
            "item_name": item_data["name"],
            "price": item_data["price"],
            "guild_id": guild_id,
            "date": datetime.datetime.now().isoformat(),
            "type": item_data.get("type", "unknown")
        }
        
        purchases[user_id].append(purchase_record)
        
        with open(purchase_file, 'w', encoding='utf-8') as f:
            json.dump(purchases, f, ensure_ascii=False, indent=2)

    @app_commands.command(name="leaderboard", description="🏆 Classement des plus riches en ArsenalCoin")
    async def leaderboard(self, interaction: discord.Interaction):
        """Affiche le leaderboard ArsenalCoin"""
        economy_data = self.load_economy_data()
        
        if not economy_data:
            embed = discord.Embed(
                title="🏆 Classement ArsenalCoin",
                description="Aucune donnée d'économie disponible.",
                color=0xff6b6b
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Trier par solde
        sorted_users = sorted(
            economy_data.items(),
            key=lambda x: x[1].get('balance', 0),
            reverse=True
        )[:10]
        
        embed = discord.Embed(
            title="🏆 Classement ArsenalCoin",
            description="Top 10 des utilisateurs les plus riches",
            color=0xffd700,
            timestamp=datetime.datetime.now()
        )
        
        leaderboard_text = ""
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        for i, (user_id, user_data) in enumerate(sorted_users):
            try:
                user = self.bot.get_user(int(user_id))
                username = user.display_name if user else f"Utilisateur {user_id[:8]}"
                balance = user_data.get('balance', 0)
                
                leaderboard_text += f"{medals[i]} **{username}** - {balance:,} AC\n"
            except:
                continue
        
        embed.add_field(
            name="💰 Top Millionnaires",
            value=leaderboard_text or "Aucun utilisateur",
            inline=False
        )
        
        # Position de l'utilisateur actuel
        user_id = str(interaction.user.id)
        user_rank = 1
        user_balance = self.get_user_balance(user_id)
        
        for uid, data in economy_data.items():
            if data.get('balance', 0) > user_balance:
                user_rank += 1
        
        embed.add_field(
            name="📍 Votre Position",
            value=f"#{user_rank} - {user_balance:,} AC",
            inline=False
        )
        
        embed.set_footer(text="Arsenal Economy System", icon_url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ArsenalEconomySystem(bot))
    print("✅ [Arsenal Economy] Système d'économie et boutique chargé")

