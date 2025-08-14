# 🚀 Arsenal V4 - Système de Jeux Complet
"""
Collection de jeux avancés pour Arsenal V4:
- Casino virtuel (Blackjack, Roulette, Slots)
- Trivia avec base de questions
- Dés personnalisés
- Système d'achievements
- Leaderboards dynamiques
"""

import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import json
import random
import asyncio
from datetime import datetime, timedelta
import os
from typing import Optional, Dict, List
import math

class GamesSystem(commands.Cog):
    """Système de jeux complet pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db_path = "data/games.db"
        self.trivia_db_path = "data/trivia_questions.json"
        self.games_config = "data/games_config.json"
        
        self.active_games = {}
        self.leaderboards = {}
        
        asyncio.create_task(self.setup_database())
        self.load_trivia_questions()
        self.load_games_config()

    async def setup_database(self):
        """Initialise la base de données des jeux"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            # Table des joueurs
            await db.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    coins INTEGER DEFAULT 1000,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    total_games INTEGER DEFAULT 0,
                    wins INTEGER DEFAULT 0,
                    achievements TEXT DEFAULT '[]',
                    last_daily TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des statistiques par jeu
            await db.execute("""
                CREATE TABLE IF NOT EXISTS game_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    game_type TEXT NOT NULL,
                    result TEXT NOT NULL,
                    coins_won INTEGER DEFAULT 0,
                    xp_gained INTEGER DEFAULT 0,
                    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES players (user_id)
                )
            """)
            
            # Table des achievements
            await db.execute("""
                CREATE TABLE IF NOT EXISTS achievements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT NOT NULL,
                    icon TEXT DEFAULT '🏆',
                    requirement INTEGER DEFAULT 1,
                    reward_coins INTEGER DEFAULT 100,
                    reward_xp INTEGER DEFAULT 50
                )
            """)
            
            await db.commit()
            await self.create_default_achievements()

    def load_trivia_questions(self):
        """Charge les questions de trivia"""
        if not os.path.exists(self.trivia_db_path):
            os.makedirs(os.path.dirname(self.trivia_db_path), exist_ok=True)
            
            default_questions = {
                "general": [
                    {
                        "question": "Quelle est la capitale de la France ?",
                        "options": ["Madrid", "Paris", "Rome", "Berlin"],
                        "correct": 1,
                        "difficulty": "facile"
                    },
                    {
                        "question": "Combien y a-t-il de continents ?",
                        "options": ["5", "6", "7", "8"],
                        "correct": 2,
                        "difficulty": "facile"
                    }
                ],
                "gaming": [
                    {
                        "question": "Quel jeu a popularisé le genre Battle Royale ?",
                        "options": ["PUBG", "Fortnite", "Apex Legends", "H1Z1"],
                        "correct": 0,
                        "difficulty": "moyen"
                    }
                ],
                "tech": [
                    {
                        "question": "Que signifie 'GPU' ?",
                        "options": ["General Processing Unit", "Graphics Processing Unit", "Game Processing Unit", "Global Processing Unit"],
                        "correct": 1,
                        "difficulty": "moyen"
                    }
                ]
            }
            
            with open(self.trivia_db_path, 'w', encoding='utf-8') as f:
                json.dump(default_questions, f, indent=2, ensure_ascii=False)
        
        try:
            with open(self.trivia_db_path, 'r', encoding='utf-8') as f:
                self.trivia_questions = json.load(f)
        except:
            self.trivia_questions = {"general": []}

    def load_games_config(self):
        """Charge la configuration des jeux"""
        if not os.path.exists(self.games_config):
            default_config = {
                "casino": {
                    "min_bet": 10,
                    "max_bet": 1000,
                    "blackjack_payout": 1.5,
                    "roulette_payouts": {
                        "number": 35,
                        "color": 2,
                        "even_odd": 2
                    }
                },
                "daily_bonus": {
                    "amount": 500,
                    "streak_bonus": 100
                },
                "level_up": {
                    "xp_base": 100,
                    "xp_multiplier": 1.5
                }
            }
            
            with open(self.games_config, 'w') as f:
                json.dump(default_config, f, indent=2)
        
        try:
            with open(self.games_config, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = {"casino": {"min_bet": 10, "max_bet": 1000}}

    async def create_default_achievements(self):
        """Crée les achievements par défaut"""
        achievements = [
            ("Première Partie", "Jouer votre premier jeu", "🎮", 1, 100, 50),
            ("Gagnant", "Gagner 10 parties", "🏆", 10, 500, 200),
            ("Chanceux", "Gagner 1000 coins en une partie", "🍀", 1, 1000, 300),
            ("Vétéran", "Jouer 100 parties", "⭐", 100, 2000, 500),
            ("Maître du Casino", "Gagner au blackjack 50 fois", "♠️", 50, 5000, 1000)
        ]
        
        async with aiosqlite.connect(self.db_path) as db:
            for achievement in achievements:
                await db.execute("""
                    INSERT OR IGNORE INTO achievements 
                    (name, description, icon, requirement, reward_coins, reward_xp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, achievement)
            await db.commit()

    @app_commands.command(name="casino", description="🎰 Accéder au casino virtuel")
    async def casino_menu(self, interaction: discord.Interaction):
        """Menu principal du casino"""
        
        player = await self.get_or_create_player(interaction.user)
        
        embed = discord.Embed(
            title="🎰 Casino Arsenal - Bienvenue !",
            description=f"**Vos fonds**: {player['coins']} 🪙",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🎮 Jeux Disponibles",
            value=(
                "🃏 **Blackjack** - Battez le croupier !\n"
                "🎰 **Machine à Sous** - Tentez votre chance\n" 
                "🔴 **Roulette** - Rouge ou noir ?\n"
                "🎲 **Dés** - Lancez les dés"
            ),
            inline=False
        )
        
        embed.add_field(
            name="💰 Limites",
            value=f"Min: {self.config['casino']['min_bet']} 🪙\nMax: {self.config['casino']['max_bet']} 🪙",
            inline=True
        )
        
        embed.add_field(
            name="📊 Vos Stats",
            value=f"Niveau: {player['level']}\nVictoires: {player['wins']}/{player['total_games']}",
            inline=True
        )
        
        view = CasinoView(self, player)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="blackjack", description="🃏 Jouer au Blackjack")
    @app_commands.describe(bet="Montant à parier")
    async def blackjack(self, interaction: discord.Interaction, bet: int):
        """Jeu de Blackjack"""
        
        player = await self.get_or_create_player(interaction.user)
        
        if not self._validate_bet(bet, player['coins']):
            await interaction.response.send_message("❌ Mise invalide !", ephemeral=True)
            return
        
        # Création du jeu
        game = BlackjackGame(bet)
        self.active_games[interaction.user.id] = game
        
        embed = game.create_embed(interaction.user)
        view = BlackjackView(self, game, interaction.user)
        
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="slots", description="🎰 Machine à sous")
    @app_commands.describe(bet="Montant à parier")
    async def slots(self, interaction: discord.Interaction, bet: int):
        """Machine à sous"""
        
        player = await self.get_or_create_player(interaction.user)
        
        if not self._validate_bet(bet, player['coins']):
            await interaction.response.send_message("❌ Mise invalide !", ephemeral=True)
            return
        
        # Symboles de la machine
        symbols = ["🍎", "🍊", "🍋", "🍇", "🔔", "💎", "7️⃣"]
        weights = [25, 25, 20, 15, 10, 4, 1]  # Probabilités
        
        # Tirage des 3 rouleaux
        result = random.choices(symbols, weights=weights, k=3)
        
        # Calcul des gains
        winnings = 0
        if result[0] == result[1] == result[2]:  # Triple
            if result[0] == "7️⃣":
                winnings = bet * 50  # Jackpot
            elif result[0] == "💎":
                winnings = bet * 25
            elif result[0] == "🔔":
                winnings = bet * 10
            else:
                winnings = bet * 5
        elif result[0] == result[1] or result[1] == result[2]:  # Double
            winnings = bet * 2
        
        # Mise à jour du joueur
        net_gain = winnings - bet
        await self.update_player_coins(interaction.user.id, net_gain)
        
        # Embed résultat
        embed = discord.Embed(
            title="🎰 Machine à Sous",
            color=discord.Color.gold() if winnings > 0 else discord.Color.red(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="🎯 Résultat",
            value=f"║ {result[0]} ║ {result[1]} ║ {result[2]} ║",
            inline=False
        )
        
        if winnings > 0:
            embed.add_field(
                name="🎉 Félicitations !",
                value=f"Vous gagnez **{winnings}** 🪙\n(Net: +{net_gain} 🪙)",
                inline=False
            )
        else:
            embed.add_field(
                name="😔 Dommage",
                value=f"Vous perdez **{bet}** 🪙",
                inline=False
            )
        
        embed.set_footer(text=f"Nouveau solde: {player['coins'] + net_gain} 🪙")
        
        await interaction.response.send_message(embed=embed)
        
        # Enregistrement des stats
        await self.record_game_result(
            interaction.user.id, 
            "slots", 
            "win" if winnings > 0 else "loss", 
            net_gain
        )

    @app_commands.command(name="trivia", description="🧠 Quiz de culture générale")
    @app_commands.describe(category="Catégorie de questions", difficulty="Difficulté")
    async def trivia(self, interaction: discord.Interaction, 
                    category: Optional[str] = "general", 
                    difficulty: Optional[str] = "all"):
        """Jeu de trivia"""
        
        if category not in self.trivia_questions:
            category = "general"
        
        questions = self.trivia_questions[category]
        if not questions:
            await interaction.response.send_message("❌ Aucune question disponible !", ephemeral=True)
            return
        
        # Filtrage par difficulté
        if difficulty != "all":
            questions = [q for q in questions if q.get("difficulty") == difficulty]
        
        if not questions:
            questions = self.trivia_questions[category]
        
        question_data = random.choice(questions)
        
        embed = discord.Embed(
            title="🧠 Quiz Arsenal",
            description=f"**{question_data['question']}**",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        # Ajout des options
        options_text = ""
        for i, option in enumerate(question_data['options']):
            options_text += f"{chr(65+i)}. {option}\n"
        
        embed.add_field(
            name="📝 Options",
            value=options_text,
            inline=False
        )
        
        embed.add_field(
            name="💰 Récompense",
            value="50 🪙 + 25 XP",
            inline=True
        )
        
        embed.add_field(
            name="⏱️ Temps",
            value="30 secondes",
            inline=True
        )
        
        view = TriviaView(self, question_data, interaction.user)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="dice", description="🎲 Lancer des dés personnalisés")
    @app_commands.describe(sides="Nombre de faces", count="Nombre de dés")
    async def dice_roll(self, interaction: discord.Interaction, 
                       sides: Optional[int] = 6, count: Optional[int] = 1):
        """Lancer de dés personnalisés"""
        
        if sides < 2 or sides > 100:
            await interaction.response.send_message("❌ Nombre de faces entre 2 et 100 !", ephemeral=True)
            return
        
        if count < 1 or count > 20:
            await interaction.response.send_message("❌ Nombre de dés entre 1 et 20 !", ephemeral=True)
            return
        
        results = [random.randint(1, sides) for _ in range(count)]
        total = sum(results)
        
        embed = discord.Embed(
            title="🎲 Lancer de Dés",
            color=discord.Color.purple(),
            timestamp=datetime.now()
        )
        
        if count == 1:
            embed.add_field(
                name="🎯 Résultat",
                value=f"**{results[0]}** (sur D{sides})",
                inline=False
            )
        else:
            dice_display = " + ".join(map(str, results))
            embed.add_field(
                name="🎯 Résultats",
                value=f"{dice_display} = **{total}**",
                inline=False
            )
            
            embed.add_field(
                name="📊 Statistiques",
                value=f"Moyenne: {total/count:.1f}\nMax possible: {sides * count}",
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)

    async def get_or_create_player(self, user: discord.User) -> Dict:
        """Récupère ou crée un joueur"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT * FROM players WHERE user_id = ?", 
                (user.id,)
            )
            player = await cursor.fetchone()
            
            if not player:
                await db.execute("""
                    INSERT INTO players (user_id, username, coins, xp, level)
                    VALUES (?, ?, 1000, 0, 1)
                """, (user.id, user.display_name))
                await db.commit()
                
                return {
                    'user_id': user.id,
                    'username': user.display_name,
                    'coins': 1000,
                    'xp': 0,
                    'level': 1,
                    'total_games': 0,
                    'wins': 0,
                    'achievements': '[]'
                }
            else:
                return dict(zip([
                    'user_id', 'username', 'coins', 'xp', 'level',
                    'total_games', 'wins', 'achievements', 'last_daily', 'created_at'
                ], player))

    def _validate_bet(self, bet: int, player_coins: int) -> bool:
        """Valide une mise"""
        return (self.config['casino']['min_bet'] <= bet <= 
                min(self.config['casino']['max_bet'], player_coins))

    async def update_player_coins(self, user_id: int, amount: int):
        """Met à jour les coins d'un joueur"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE players SET coins = coins + ? WHERE user_id = ?",
                (amount, user_id)
            )
            await db.commit()

    async def record_game_result(self, user_id: int, game_type: str, result: str, coins_won: int):
        """Enregistre le résultat d'une partie"""
        xp_gained = 10 if result == "win" else 5
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO game_stats (user_id, game_type, result, coins_won, xp_gained)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, game_type, result, coins_won, xp_gained))
            
            # Mise à jour des stats joueur
            await db.execute("""
                UPDATE players 
                SET total_games = total_games + 1, 
                    wins = wins + ?, 
                    xp = xp + ?
                WHERE user_id = ?
            """, (1 if result == "win" else 0, xp_gained, user_id))
            
            await db.commit()

# Classes pour les jeux
class BlackjackGame:
    def __init__(self, bet):
        self.bet = bet
        self.player_hand = []
        self.dealer_hand = []
        self.deck = self.create_deck()
        self.game_over = False
        self.result = None
        
        # Distribution initiale
        self.player_hand.append(self.draw_card())
        self.dealer_hand.append(self.draw_card())
        self.player_hand.append(self.draw_card())
        self.dealer_hand.append(self.draw_card())

    def create_deck(self):
        suits = ["♠️", "♥️", "♦️", "♣️"]
        values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        deck = []
        for suit in suits:
            for value in values:
                deck.append({"suit": suit, "value": value})
        random.shuffle(deck)
        return deck

    def draw_card(self):
        return self.deck.pop() if self.deck else {"suit": "❓", "value": "?"}

    def calculate_hand_value(self, hand):
        value = 0
        aces = 0
        
        for card in hand:
            if card["value"] in ["J", "Q", "K"]:
                value += 10
            elif card["value"] == "A":
                aces += 1
                value += 11
            else:
                value += int(card["value"])
        
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value

    def create_embed(self, user):
        embed = discord.Embed(
            title="🃏 Blackjack",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        # Main du joueur
        player_cards = " ".join([f"{c['value']}{c['suit']}" for c in self.player_hand])
        player_value = self.calculate_hand_value(self.player_hand)
        
        embed.add_field(
            name=f"🎮 {user.display_name} ({player_value})",
            value=player_cards,
            inline=False
        )
        
        # Main du croupier
        if not self.game_over:
            dealer_cards = f"{self.dealer_hand[0]['value']}{self.dealer_hand[0]['suit']} 🎴"
            dealer_value = "?"
        else:
            dealer_cards = " ".join([f"{c['value']}{c['suit']}" for c in self.dealer_hand])
            dealer_value = self.calculate_hand_value(self.dealer_hand)
        
        embed.add_field(
            name=f"🤵 Croupier ({dealer_value})",
            value=dealer_cards,
            inline=False
        )
        
        embed.add_field(
            name="💰 Mise",
            value=f"{self.bet} 🪙",
            inline=True
        )
        
        return embed

# Vues UI pour les jeux
class CasinoView(discord.ui.View):
    def __init__(self, games_system, player):
        super().__init__(timeout=300)
        self.games_system = games_system
        self.player = player

    @discord.ui.button(label="🃏 Blackjack", style=discord.ButtonStyle.primary)
    async def blackjack_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Redirection vers la commande blackjack
        embed = discord.Embed(
            title="🃏 Blackjack",
            description="Utilisez `/blackjack <mise>` pour jouer !",
            color=discord.Color.blue()
        )
        await interaction.response.edit_message(embed=embed, view=None)

class BlackjackView(discord.ui.View):
    def __init__(self, games_system, game, user):
        super().__init__(timeout=300)
        self.games_system = games_system
        self.game = game
        self.user = user

    @discord.ui.button(label="📈 Tirer", style=discord.ButtonStyle.primary)
    async def hit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Ce n'est pas votre partie !", ephemeral=True)
            return
        
        self.game.player_hand.append(self.game.draw_card())
        player_value = self.game.calculate_hand_value(self.game.player_hand)
        
        if player_value > 21:
            await self.end_game(interaction, "bust")
        else:
            embed = self.game.create_embed(self.user)
            await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="✋ Rester", style=discord.ButtonStyle.secondary)
    async def stand_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("❌ Ce n'est pas votre partie !", ephemeral=True)
            return
        
        # Le croupier joue
        dealer_value = self.game.calculate_hand_value(self.game.dealer_hand)
        while dealer_value < 17:
            self.game.dealer_hand.append(self.game.draw_card())
            dealer_value = self.game.calculate_hand_value(self.game.dealer_hand)
        
        player_value = self.game.calculate_hand_value(self.game.player_hand)
        
        if dealer_value > 21:
            await self.end_game(interaction, "dealer_bust")
        elif player_value > dealer_value:
            await self.end_game(interaction, "win")
        elif player_value < dealer_value:
            await self.end_game(interaction, "lose")
        else:
            await self.end_game(interaction, "tie")

    async def end_game(self, interaction, result):
        self.game.game_over = True
        self.game.result = result
        
        # Calcul des gains
        winnings = 0
        if result == "win" or result == "dealer_bust":
            winnings = int(self.game.bet * 2)
        elif result == "tie":
            winnings = self.game.bet
        
        net_gain = winnings - self.game.bet
        
        # Mise à jour du joueur
        await self.games_system.update_player_coins(self.user.id, net_gain)
        
        # Enregistrement des stats
        await self.games_system.record_game_result(
            self.user.id,
            "blackjack",
            "win" if net_gain > 0 else "loss",
            net_gain
        )
        
        embed = self.game.create_embed(self.user)
        
        # Message de résultat
        if result == "bust":
            embed.add_field(name="💥 Résultat", value="Vous avez dépassé 21 !", inline=False)
        elif result == "win":
            embed.add_field(name="🎉 Résultat", value=f"Victoire ! Vous gagnez {winnings} 🪙", inline=False)
        elif result == "dealer_bust":
            embed.add_field(name="🎉 Résultat", value=f"Le croupier dépasse 21 ! Vous gagnez {winnings} 🪙", inline=False)
        elif result == "lose":
            embed.add_field(name="😔 Résultat", value="Vous avez perdu...", inline=False)
        else:
            embed.add_field(name="🤝 Résultat", value="Égalité ! Mise remboursée", inline=False)
        
        embed.color = discord.Color.green() if net_gain > 0 else discord.Color.red()
        
        # Désactiver les boutons
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)

class TriviaView(discord.ui.View):
    def __init__(self, games_system, question_data, user):
        super().__init__(timeout=30)
        self.games_system = games_system
        self.question_data = question_data
        self.user = user
        self.answered = False

    @discord.ui.button(label="A", style=discord.ButtonStyle.secondary)
    async def option_a(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_answer(interaction, 0)

    @discord.ui.button(label="B", style=discord.ButtonStyle.secondary)
    async def option_b(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_answer(interaction, 1)

    @discord.ui.button(label="C", style=discord.ButtonStyle.secondary)
    async def option_c(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_answer(interaction, 2)

    @discord.ui.button(label="D", style=discord.ButtonStyle.secondary)
    async def option_d(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_answer(interaction, 3)

    async def handle_answer(self, interaction, choice):
        if interaction.user != self.user or self.answered:
            await interaction.response.send_message("❌ Question déjà répondue ou pas votre tour !", ephemeral=True)
            return
        
        self.answered = True
        correct = choice == self.question_data['correct']
        
        embed = discord.Embed(
            title="🧠 Quiz Arsenal - Résultat",
            color=discord.Color.green() if correct else discord.Color.red(),
            timestamp=datetime.now()
        )
        
        embed.add_field(
            name="❓ Question",
            value=self.question_data['question'],
            inline=False
        )
        
        embed.add_field(
            name="✅ Bonne réponse",
            value=f"{chr(65 + self.question_data['correct'])}. {self.question_data['options'][self.question_data['correct']]}",
            inline=False
        )
        
        if correct:
            embed.add_field(
                name="🎉 Félicitations !",
                value="Bonne réponse ! +50 🪙 +25 XP",
                inline=False
            )
            await self.games_system.update_player_coins(self.user.id, 50)
            await self.games_system.record_game_result(self.user.id, "trivia", "win", 50)
        else:
            embed.add_field(
                name="😔 Dommage",
                value="Mauvaise réponse... +5 XP pour la participation",
                inline=False
            )
            await self.games_system.record_game_result(self.user.id, "trivia", "loss", 0)
        
        # Désactiver les boutons
        for item in self.children:
            item.disabled = True
            if hasattr(item, 'style'):
                if self.children.index(item) == self.question_data['correct']:
                    item.style = discord.ButtonStyle.success
                elif self.children.index(item) == choice and not correct:
                    item.style = discord.ButtonStyle.danger
        
        await interaction.response.edit_message(embed=embed, view=self)

async def setup(bot):
    """Charge le module GamesSystem"""
    await bot.add_cog(GamesSystem(bot))
    print("🎮 [Games System] Module chargé avec succès!")
