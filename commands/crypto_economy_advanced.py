# 🚀 Arsenal V4 - Système Crypto Économie Avancé
"""
Système de trading crypto avec:
- Portefeuille multi-devises
- Prix temps réel via CoinGecko
- Trading automatique et manuel
- Graphiques et analyses
- Alertes de prix
- Système de leaderboard
"""

import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import aiohttp
import json
import asyncio
from datetime import datetime, timedelta
import os
from typing import Optional, Dict, List, Tuple
import random

class CryptoEconomyAdvanced(commands.Cog):
    """Système d'économie crypto avancé pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/crypto_economy.db"
        self.price_cache = {}
        self.cache_expiry = {}
        
        # Configuration
        self.supported_cryptos = [
            'bitcoin', 'ethereum', 'binancecoin', 'cardano', 'solana',
            'polkadot', 'dogecoin', 'shiba-inu', 'chainlink', 'polygon'
        ]
        
        self.crypto_symbols = {
            'bitcoin': '₿',
            'ethereum': 'Ξ',
            'binancecoin': 'BNB',
            'cardano': '₳',
            'solana': '◎',
            'polkadot': '●',
            'dogecoin': 'Ð',
            'shiba-inu': '🐕',
            'chainlink': '⛓️',
            'polygon': '🔺'
        }
        
        asyncio.create_task(self.setup_database())
        asyncio.create_task(self.start_price_updater())

    async def setup_database(self):
        """Initialise la base de données crypto"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            # Table des portefeuilles
            await db.execute("""
                CREATE TABLE IF NOT EXISTS crypto_wallets (
                    user_id INTEGER NOT NULL,
                    crypto_id TEXT NOT NULL,
                    amount REAL DEFAULT 0.0,
                    avg_buy_price REAL DEFAULT 0.0,
                    total_invested REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (user_id, crypto_id)
                )
            """)
            
            # Table des transactions
            await db.execute("""
                CREATE TABLE IF NOT EXISTS crypto_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    crypto_id TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    price_usd REAL NOT NULL,
                    total_value REAL NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des alertes de prix
            await db.execute("""
                CREATE TABLE IF NOT EXISTS price_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    crypto_id TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    target_price REAL NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des coins virtuels
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_coins (
                    user_id INTEGER PRIMARY KEY,
                    balance REAL DEFAULT 10000.0,
                    total_profit_loss REAL DEFAULT 0.0,
                    best_trade REAL DEFAULT 0.0,
                    trades_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.commit()

    async def start_price_updater(self):
        """Démarre la mise à jour automatique des prix"""
        await asyncio.sleep(5)  # Attendre que le bot soit prêt
        
        while True:
            try:
                await self.update_all_prices()
                await self.check_price_alerts()
                await asyncio.sleep(300)  # Mise à jour toutes les 5 minutes
            except Exception as e:
                print(f"Erreur mise à jour prix: {e}")
                await asyncio.sleep(60)

    async def get_crypto_price(self, crypto_id: str) -> Optional[Dict]:
        """Récupère le prix d'une crypto depuis CoinGecko"""
        
        # Vérifier le cache
        if (crypto_id in self.price_cache and 
            crypto_id in self.cache_expiry and 
            datetime.now() < self.cache_expiry[crypto_id]):
            return self.price_cache[crypto_id]
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.coingecko.com/api/v3/simple/price"
                params = {
                    'ids': crypto_id,
                    'vs_currencies': 'usd',
                    'include_24hr_change': 'true',
                    'include_market_cap': 'true'
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if crypto_id in data:
                            price_data = data[crypto_id]
                            
                            # Mise en cache
                            self.price_cache[crypto_id] = price_data
                            self.cache_expiry[crypto_id] = datetime.now() + timedelta(minutes=2)
                            
                            return price_data
                    
        except Exception as e:
            print(f"Erreur API CoinGecko pour {crypto_id}: {e}")
        
        return None

    async def update_all_prices(self):
        """Met à jour tous les prix des cryptos supportées"""
        try:
            crypto_list = ','.join(self.supported_cryptos)
            async with aiohttp.ClientSession() as session:
                url = f"https://api.coingecko.com/api/v3/simple/price"
                params = {
                    'ids': crypto_list,
                    'vs_currencies': 'usd',
                    'include_24hr_change': 'true',
                    'include_market_cap': 'true'
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        for crypto_id, price_data in data.items():
                            self.price_cache[crypto_id] = price_data
                            self.cache_expiry[crypto_id] = datetime.now() + timedelta(minutes=5)
        except Exception as e:
            print(f"Erreur mise à jour globale: {e}")

    @app_commands.command(name="crypto_price", description="💰 Prix actuel d'une cryptomonnaie")
    @app_commands.describe(crypto="Nom de la crypto (ex: bitcoin, ethereum)")
    async def crypto_price(self, interaction: discord.Interaction, crypto: str):
        """Affiche le prix actuel d'une crypto"""
        
        await interaction.response.defer()
        
        crypto_id = crypto.lower().replace(' ', '-')
        if crypto_id not in self.supported_cryptos:
            # Recherche fuzzy
            matches = [c for c in self.supported_cryptos if crypto_id in c or c in crypto_id]
            if matches:
                crypto_id = matches[0]
            else:
                embed = discord.Embed(
                    title="❌ Crypto non trouvée",
                    description=f"Cryptos supportées: {', '.join(self.supported_cryptos)}",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
        
        price_data = await self.get_crypto_price(crypto_id)
        
        if not price_data:
            await interaction.followup.send("❌ Impossible de récupérer le prix", ephemeral=True)
            return
        
        # Création de l'embed
        crypto_name = crypto_id.replace('-', ' ').title()
        symbol = self.crypto_symbols.get(crypto_id, '🪙')
        price = price_data['usd']
        change_24h = price_data.get('usd_24h_change', 0)
        
        color = discord.Color.green() if change_24h >= 0 else discord.Color.red()
        change_emoji = "📈" if change_24h >= 0 else "📉"
        
        embed = discord.Embed(
            title=f"{symbol} {crypto_name}",
            color=color,
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="💵 Prix USD",
            value=f"**${price:,.4f}**",
            inline=True
        )
        
        embed.add_field(
            name=f"{change_emoji} 24h",
            value=f"{change_24h:+.2f}%",
            inline=True
        )
        
        if 'usd_market_cap' in price_data:
            market_cap = price_data['usd_market_cap']
            embed.add_field(
                name="📊 Market Cap",
                value=f"${market_cap:,.0f}",
                inline=True
            )
        
        embed.set_footer(text="Données par CoinGecko")
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="crypto_portfolio", description="📊 Votre portefeuille crypto")
    async def crypto_portfolio(self, interaction: discord.Interaction):
        """Affiche le portefeuille crypto de l'utilisateur"""
        
        await interaction.response.defer()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT crypto_id, amount, avg_buy_price, total_invested
                    FROM crypto_wallets 
                    WHERE user_id = ? AND amount > 0
                    ORDER BY total_invested DESC
                """, (interaction.user.id,))
                
                holdings = await cursor.fetchall()
                
                # Récupérer le solde en coins virtuels
                cursor = await db.execute("""
                    SELECT balance, total_profit_loss, trades_count
                    FROM user_coins WHERE user_id = ?
                """, (interaction.user.id,))
                
                user_data = await cursor.fetchone()
                if not user_data:
                    balance, total_pnl, trades_count = 10000.0, 0.0, 0
                else:
                    balance, total_pnl, trades_count = user_data
        
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur base de données: {e}", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📊 Votre Portefeuille Crypto",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="💰 Solde Virtuel",
            value=f"**${balance:,.2f}**",
            inline=True
        )
        
        embed.add_field(
            name="📈 P&L Total",
            value=f"**${total_pnl:+,.2f}**",
            inline=True
        )
        
        embed.add_field(
            name="🔄 Trades",
            value=f"**{trades_count}**",
            inline=True
        )
        
        if not holdings:
            embed.add_field(
                name="📭 Portefeuille vide",
                value="Utilisez `/crypto_buy` pour acheter des cryptos !",
                inline=False
            )
        else:
            # Calcul de la valeur totale actuelle
            total_current_value = 0
            portfolio_text = ""
            
            for crypto_id, amount, avg_buy_price, total_invested in holdings:
                price_data = await self.get_crypto_price(crypto_id)
                if price_data:
                    current_price = price_data['usd']
                    current_value = amount * current_price
                    profit_loss = current_value - total_invested
                    profit_loss_pct = (profit_loss / total_invested * 100) if total_invested > 0 else 0
                    
                    symbol = self.crypto_symbols.get(crypto_id, '🪙')
                    crypto_name = crypto_id.replace('-', ' ').title()
                    
                    pnl_emoji = "📈" if profit_loss >= 0 else "📉"
                    
                    portfolio_text += (
                        f"{symbol} **{crypto_name}**\n"
                        f"Quantité: {amount:.6f}\n"
                        f"Valeur: ${current_value:.2f} ({pnl_emoji}{profit_loss_pct:+.1f}%)\n\n"
                    )
                    
                    total_current_value += current_value
            
            embed.add_field(
                name="💼 Holdings",
                value=portfolio_text[:1024] if portfolio_text else "Aucune position",
                inline=False
            )
            
            if total_current_value > 0:
                embed.add_field(
                    name="💎 Valeur Totale",
                    value=f"**${total_current_value:,.2f}**",
                    inline=True
                )
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="crypto_buy", description="🛒 Acheter une cryptomonnaie")
    @app_commands.describe(crypto="Nom de la crypto", amount="Montant en USD à investir")
    async def crypto_buy(self, interaction: discord.Interaction, crypto: str, amount: float):
        """Acheter une cryptomonnaie"""
        
        await interaction.response.defer()
        
        if amount <= 0:
            await interaction.followup.send("❌ Le montant doit être positif !", ephemeral=True)
            return
        
        crypto_id = crypto.lower().replace(' ', '-')
        if crypto_id not in self.supported_cryptos:
            matches = [c for c in self.supported_cryptos if crypto_id in c]
            if matches:
                crypto_id = matches[0]
            else:
                await interaction.followup.send("❌ Crypto non supportée !", ephemeral=True)
                return
        
        # Vérifier le solde utilisateur
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT balance FROM user_coins WHERE user_id = ?
                """, (interaction.user.id,))
                
                result = await cursor.fetchone()
                if not result:
                    # Créer le compte
                    await db.execute("""
                        INSERT INTO user_coins (user_id, balance) VALUES (?, 10000.0)
                    """, (interaction.user.id,))
                    balance = 10000.0
                else:
                    balance = result[0]
                
                if balance < amount:
                    await interaction.followup.send(f"❌ Solde insuffisant ! Vous avez ${balance:.2f}", ephemeral=True)
                    return
                
                # Récupérer le prix actuel
                price_data = await self.get_crypto_price(crypto_id)
                if not price_data:
                    await interaction.followup.send("❌ Prix indisponible", ephemeral=True)
                    return
                
                current_price = price_data['usd']
                crypto_amount = amount / current_price
                
                # Mettre à jour le solde
                await db.execute("""
                    UPDATE user_coins 
                    SET balance = balance - ?, trades_count = trades_count + 1
                    WHERE user_id = ?
                """, (amount, interaction.user.id))
                
                # Ajouter/mettre à jour le portefeuille
                await db.execute("""
                    INSERT INTO crypto_wallets (user_id, crypto_id, amount, avg_buy_price, total_invested)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(user_id, crypto_id) DO UPDATE SET
                        amount = amount + excluded.amount,
                        avg_buy_price = (avg_buy_price * amount + excluded.avg_buy_price * excluded.amount) / (amount + excluded.amount),
                        total_invested = total_invested + excluded.total_invested,
                        last_updated = CURRENT_TIMESTAMP
                """, (interaction.user.id, crypto_id, crypto_amount, current_price, amount))
                
                # Enregistrer la transaction
                await db.execute("""
                    INSERT INTO crypto_transactions 
                    (user_id, crypto_id, transaction_type, amount, price_usd, total_value)
                    VALUES (?, ?, 'buy', ?, ?, ?)
                """, (interaction.user.id, crypto_id, crypto_amount, current_price, amount))
                
                await db.commit()
                
                # Embed de confirmation
                crypto_name = crypto_id.replace('-', ' ').title()
                symbol = self.crypto_symbols.get(crypto_id, '🪙')
                
                embed = discord.Embed(
                    title="✅ Achat Confirmé",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                
                embed.add_field(
                    name=f"{symbol} {crypto_name}",
                    value=f"**{crypto_amount:.6f}** unités",
                    inline=True
                )
                
                embed.add_field(
                    name="💵 Prix d'achat",
                    value=f"**${current_price:.4f}**",
                    inline=True
                )
                
                embed.add_field(
                    name="💰 Total investi",
                    value=f"**${amount:.2f}**",
                    inline=True
                )
                
                embed.add_field(
                    name="💳 Nouveau solde",
                    value=f"**${balance - amount:.2f}**",
                    inline=False
                )
                
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)

    @app_commands.command(name="crypto_sell", description="💸 Vendre une cryptomonnaie")
    @app_commands.describe(crypto="Nom de la crypto", percentage="Pourcentage à vendre (1-100)")
    async def crypto_sell(self, interaction: discord.Interaction, crypto: str, percentage: float):
        """Vendre une cryptomonnaie"""
        
        await interaction.response.defer()
        
        if not 1 <= percentage <= 100:
            await interaction.followup.send("❌ Pourcentage entre 1 et 100 !", ephemeral=True)
            return
        
        crypto_id = crypto.lower().replace(' ', '-')
        if crypto_id not in self.supported_cryptos:
            matches = [c for c in self.supported_cryptos if crypto_id in c]
            if matches:
                crypto_id = matches[0]
            else:
                await interaction.followup.send("❌ Crypto non supportée !", ephemeral=True)
                return
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Vérifier les holdings
                cursor = await db.execute("""
                    SELECT amount, avg_buy_price, total_invested
                    FROM crypto_wallets 
                    WHERE user_id = ? AND crypto_id = ? AND amount > 0
                """, (interaction.user.id, crypto_id))
                
                holding = await cursor.fetchone()
                if not holding:
                    await interaction.followup.send("❌ Vous ne possédez pas cette crypto !", ephemeral=True)
                    return
                
                owned_amount, avg_buy_price, total_invested = holding
                sell_amount = owned_amount * (percentage / 100)
                
                # Récupérer le prix actuel
                price_data = await self.get_crypto_price(crypto_id)
                if not price_data:
                    await interaction.followup.send("❌ Prix indisponible", ephemeral=True)
                    return
                
                current_price = price_data['usd']
                sell_value = sell_amount * current_price
                
                # Calculer le P&L
                invested_portion = total_invested * (percentage / 100)
                profit_loss = sell_value - invested_portion
                
                # Mettre à jour la base de données
                new_amount = owned_amount - sell_amount
                new_invested = total_invested - invested_portion
                
                if new_amount < 0.000001:  # Pratiquement 0
                    # Supprimer complètement
                    await db.execute("""
                        DELETE FROM crypto_wallets 
                        WHERE user_id = ? AND crypto_id = ?
                    """, (interaction.user.id, crypto_id))
                else:
                    # Mettre à jour
                    await db.execute("""
                        UPDATE crypto_wallets 
                        SET amount = ?, total_invested = ?, last_updated = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND crypto_id = ?
                    """, (new_amount, new_invested, interaction.user.id, crypto_id))
                
                # Ajouter à l'argent virtuel
                await db.execute("""
                    UPDATE user_coins 
                    SET balance = balance + ?, 
                        total_profit_loss = total_profit_loss + ?,
                        trades_count = trades_count + 1
                    WHERE user_id = ?
                """, (sell_value, profit_loss, interaction.user.id))
                
                # Enregistrer la transaction
                await db.execute("""
                    INSERT INTO crypto_transactions 
                    (user_id, crypto_id, transaction_type, amount, price_usd, total_value)
                    VALUES (?, ?, 'sell', ?, ?, ?)
                """, (interaction.user.id, crypto_id, sell_amount, current_price, sell_value))
                
                await db.commit()
                
                # Embed de confirmation
                crypto_name = crypto_id.replace('-', ' ').title()
                symbol = self.crypto_symbols.get(crypto_id, '🪙')
                
                color = discord.Color.green() if profit_loss >= 0 else discord.Color.red()
                pnl_emoji = "📈" if profit_loss >= 0 else "📉"
                
                embed = discord.Embed(
                    title="✅ Vente Confirmée",
                    color=color,
                    timestamp=datetime.now()
                )
                
                embed.add_field(
                    name=f"{symbol} {crypto_name}",
                    value=f"**{sell_amount:.6f}** unités ({percentage}%)",
                    inline=True
                )
                
                embed.add_field(
                    name="💵 Prix de vente",
                    value=f"**${current_price:.4f}**",
                    inline=True
                )
                
                embed.add_field(
                    name="💰 Montant reçu",
                    value=f"**${sell_value:.2f}**",
                    inline=True
                )
                
                embed.add_field(
                    name=f"{pnl_emoji} P&L",
                    value=f"**${profit_loss:+.2f}**",
                    inline=True
                )
                
                if new_amount > 0.000001:
                    embed.add_field(
                        name="📦 Restant",
                        value=f"**{new_amount:.6f}** unités",
                        inline=True
                    )
                
                await interaction.followup.send(embed=embed)
                
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {str(e)}", ephemeral=True)

    @app_commands.command(name="crypto_alert", description="🔔 Créer une alerte de prix")
    @app_commands.describe(crypto="Nom de la crypto", target_price="Prix cible en USD")
    async def crypto_alert(self, interaction: discord.Interaction, crypto: str, target_price: float):
        """Créer une alerte de prix"""
        
        crypto_id = crypto.lower().replace(' ', '-')
        if crypto_id not in self.supported_cryptos:
            await interaction.response.send_message("❌ Crypto non supportée !", ephemeral=True)
            return
        
        if target_price <= 0:
            await interaction.response.send_message("❌ Prix cible invalide !", ephemeral=True)
            return
        
        try:
            # Obtenir le prix actuel pour déterminer le type d'alerte
            price_data = await self.get_crypto_price(crypto_id)
            if not price_data:
                await interaction.response.send_message("❌ Prix actuel indisponible", ephemeral=True)
                return
            
            current_price = price_data['usd']
            alert_type = "above" if target_price > current_price else "below"
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO price_alerts (user_id, crypto_id, alert_type, target_price)
                    VALUES (?, ?, ?, ?)
                """, (interaction.user.id, crypto_id, alert_type, target_price))
                await db.commit()
            
            crypto_name = crypto_id.replace('-', ' ').title()
            symbol = self.crypto_symbols.get(crypto_id, '🪙')
            
            embed = discord.Embed(
                title="🔔 Alerte Créée",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name=f"{symbol} {crypto_name}",
                value=f"Prix actuel: **${current_price:.4f}**",
                inline=False
            )
            
            embed.add_field(
                name="🎯 Alerte",
                value=f"Vous serez notifié quand le prix {'dépasse' if alert_type == 'above' else 'descend sous'} **${target_price:.4f}**",
                inline=False
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur: {str(e)}", ephemeral=True)

    async def check_price_alerts(self):
        """Vérifie les alertes de prix et notifie les utilisateurs"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT id, user_id, crypto_id, alert_type, target_price
                    FROM price_alerts WHERE is_active = TRUE
                """)
                
                alerts = await cursor.fetchall()
                
                for alert_id, user_id, crypto_id, alert_type, target_price in alerts:
                    price_data = await self.get_crypto_price(crypto_id)
                    if not price_data:
                        continue
                    
                    current_price = price_data['usd']
                    
                    triggered = False
                    if alert_type == "above" and current_price >= target_price:
                        triggered = True
                    elif alert_type == "below" and current_price <= target_price:
                        triggered = True
                    
                    if triggered:
                        # Désactiver l'alerte
                        await db.execute("""
                            UPDATE price_alerts SET is_active = FALSE WHERE id = ?
                        """, (alert_id,))
                        
                        # Notifier l'utilisateur
                        user = self.bot.get_user(user_id)
                        if user:
                            crypto_name = crypto_id.replace('-', ' ').title()
                            symbol = self.crypto_symbols.get(crypto_id, '🪙')
                            
                            embed = discord.Embed(
                                title="🚨 Alerte Prix Déclenchée !",
                                color=discord.Color.orange(),
                                timestamp=datetime.now()
                            )
                            
                            embed.add_field(
                                name=f"{symbol} {crypto_name}",
                                value=f"Prix: **${current_price:.4f}**\nCible: **${target_price:.4f}**",
                                inline=False
                            )
                            
                            try:
                                await user.send(embed=embed)
                            except:
                                pass  # L'utilisateur a peut-être désactivé les DMs
                
                await db.commit()
                
        except Exception as e:
            print(f"Erreur vérification alertes: {e}")

    @app_commands.command(name="crypto_leaderboard", description="🏆 Classement des meilleurs traders")
    async def crypto_leaderboard(self, interaction: discord.Interaction):
        """Affiche le classement des traders"""
        
        await interaction.response.defer()
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute("""
                    SELECT user_id, total_profit_loss, trades_count, balance
                    FROM user_coins 
                    WHERE trades_count > 0
                    ORDER BY total_profit_loss DESC
                    LIMIT 10
                """)
                
                leaderboard = await cursor.fetchall()
        
        except Exception as e:
            await interaction.followup.send(f"❌ Erreur: {e}", ephemeral=True)
            return
        
        if not leaderboard:
            await interaction.followup.send("📭 Aucun trader trouvé !", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🏆 Top Traders Crypto",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        
        leaderboard_text = ""
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (user_id, total_pnl, trades_count, balance) in enumerate(leaderboard):
            user = self.bot.get_user(user_id)
            username = user.display_name if user else f"User#{user_id}"
            
            medal = medals[i] if i < 3 else f"{i+1}."
            pnl_emoji = "📈" if total_pnl >= 0 else "📉"
            
            leaderboard_text += (
                f"{medal} **{username}**\n"
                f"{pnl_emoji} P&L: ${total_pnl:+,.2f} | Trades: {trades_count}\n\n"
            )
        
        embed.description = leaderboard_text
        embed.set_footer(text="Basé sur les profits/pertes totaux")
        
        await interaction.followup.send(embed=embed)

async def setup(bot):
    """Charge le module CryptoEconomyAdvanced"""
    await bot.add_cog(CryptoEconomyAdvanced(bot))
    print("💰 [Crypto Economy Advanced] Module chargé avec succès!")
