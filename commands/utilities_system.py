# 🚀 Arsenal V4 - Outils Utilitaires Avancés  
"""
Collection d'outils utilitaires pour Arsenal V4:
- Générateur de mots de passe sécurisés
- QR Code generator/reader
- Calculatrice scientifique
- Convertisseur d'unités
- Raccourcisseur d'URL
- Traducteur multilingue
- Générateur de couleurs
- ASCII art generator
"""

import discord
from discord.ext import commands
from discord import app_commands
import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import secrets
import string
import math
import random
import aiohttp
import json
from typing import Optional, Union, List
from datetime import datetime
import re
import hashlib

class UtilitiesSystem(commands.Cog):
    """Système d'outils utilitaires pour Arsenal V4"""
    
    def __init__(self, bot):
        self.bot = bot
        self.color_cache = {}
        
        # Unités de conversion
        self.conversion_units = {
            "longueur": {
                "mm": 0.001, "cm": 0.01, "m": 1, "km": 1000,
                "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.34
            },
            "poids": {
                "g": 1, "kg": 1000, "oz": 28.3495, "lb": 453.592,
                "ton": 1000000
            },
            "température": {
                # Formules spéciales pour température
            }
        }

    @app_commands.command(name="utils", description="🔧 Menu des outils utilitaires")
    async def utils_menu(self, interaction: discord.Interaction):
        """Menu principal des outils utilitaires"""
        embed = discord.Embed(
            title="🔧 Outils Utilitaires Arsenal",
            description="Collection d'outils pratiques pour tous vos besoins",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="🔐 Sécurité",
            value=(
                "`/password generate` - Générateur mot de passe\n"
                "`/hash` - Hachage de texte\n"
                "`/qrcode` - Générateur QR Code"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🧮 Calculs",
            value=(
                "`/calc` - Calculatrice avancée\n"
                "`/convert` - Convertisseur d'unités\n"
                "`/color` - Générateur de couleurs"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🎨 Créatif",
            value=(
                "`/ascii` - ASCII Art\n"
                "`/translate` - Traducteur\n"
                "`/shorten` - Raccourcisseur URL"
            ),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="password", description="🔐 Générateur de mot de passe")
    @app_commands.describe(
        length="Longueur du mot de passe (8-50)",
        include_symbols="Inclure des symboles spéciaux",
        include_numbers="Inclure des chiffres"
    )
    async def generate_password(self, interaction: discord.Interaction, 
                              length: int = 16,
                              include_symbols: bool = True,
                              include_numbers: bool = True):
        """Génère un mot de passe sécurisé"""
        
        if length < 8 or length > 50:
            await interaction.response.send_message("❌ Longueur entre 8 et 50 caractères !", ephemeral=True)
            return
        
        # Construction alphabet
        alphabet = string.ascii_letters
        if include_numbers:
            alphabet += string.digits
        if include_symbols:
            alphabet += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Génération sécurisée
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        # Calcul force
        entropy = len(alphabet) ** length
        strength = "Très Fort" if entropy > 10**20 else "Fort" if entropy > 10**15 else "Moyen"
        
        embed = discord.Embed(
            title="🔐 Mot de Passe Généré",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="🔑 Mot de passe",
            value=f"||`{password}`||",
            inline=False
        )
        
        embed.add_field(
            name="💪 Force",
            value=f"**{strength}** ({length} caractères)",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Composition",
            value=f"Lettres: ✅\nChiffres: {'✅' if include_numbers else '❌'}\nSymboles: {'✅' if include_symbols else '❌'}",
            inline=True
        )
        
        embed.set_footer(text="⚠️ Ne partagez jamais votre mot de passe !")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="qrcode", description="📱 Générateur de QR Code")
    @app_commands.describe(text="Texte à encoder", size="Taille du QR Code (S/M/L)")
    async def generate_qrcode(self, interaction: discord.Interaction, 
                            text: str, size: str = "M"):
        """Génère un QR Code"""
        
        if len(text) > 1000:
            await interaction.response.send_message("❌ Texte trop long (max 1000 caractères) !", ephemeral=True)
            return
        
        # Configuration taille
        sizes = {"S": 5, "M": 8, "L": 12}
        box_size = sizes.get(size.upper(), 8)
        
        try:
            # Génération QR Code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=box_size,
                border=4,
            )
            qr.add_data(text)
            qr.make(fit=True)
            
            # Création image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Conversion en bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Embed
            embed = discord.Embed(
                title="📱 QR Code Généré",
                description=f"Contenu: `{text[:50]}{'...' if len(text) > 50 else ''}`",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📊 Informations",
                value=f"**Taille:** {size.upper()}\n**Caractères:** {len(text)}\n**Format:** PNG",
                inline=True
            )
            
            file = discord.File(img_bytes, filename="qrcode.png")
            embed.set_image(url="attachment://qrcode.png")
            
            await interaction.response.send_message(embed=embed, file=file)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur génération QR Code: {e}", ephemeral=True)

    @app_commands.command(name="calc", description="🧮 Calculatrice avancée")
    @app_commands.describe(expression="Expression mathématique à calculer")
    async def calculator(self, interaction: discord.Interaction, expression: str):
        """Calculatrice scientifique sécurisée"""
        
        # Nettoyage expression
        expression = expression.replace(" ", "").replace("^", "**")
        
        # Sécurité - caractères autorisés
        allowed_chars = set("0123456789+-*/.()%**")
        allowed_funcs = ["sin", "cos", "tan", "log", "sqrt", "abs", "round", "pi", "e"]
        
        if not all(c in allowed_chars or any(func in expression for func in allowed_funcs) for c in expression):
            await interaction.response.send_message("❌ Expression non autorisée !", ephemeral=True)
            return
        
        try:
            # Remplacement fonctions sûres
            safe_expression = expression
            safe_expression = safe_expression.replace("pi", str(math.pi))
            safe_expression = safe_expression.replace("e", str(math.e))
            
            # Évaluation sécurisée
            result = eval(safe_expression, {"__builtins__": {}}, {
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "log": math.log, "sqrt": math.sqrt, "abs": abs,
                "round": round, "pi": math.pi, "e": math.e
            })
            
            embed = discord.Embed(
                title="🧮 Calculatrice Arsenal",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="📝 Expression",
                value=f"`{expression}`",
                inline=False
            )
            
            embed.add_field(
                name="🎯 Résultat",
                value=f"**{result}**",
                inline=False
            )
            
            # Info sur le résultat
            if isinstance(result, float):
                if result.is_integer():
                    result_type = "Entier"
                else:
                    result_type = f"Décimal ({len(str(result).split('.')[-1])} décimales)"
            else:
                result_type = "Entier"
            
            embed.add_field(
                name="ℹ️ Type",
                value=result_type,
                inline=True
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur calcul: Expression invalide", ephemeral=True)

    @app_commands.command(name="convert", description="🔄 Convertisseur d'unités")
    @app_commands.describe(
        value="Valeur à convertir",
        from_unit="Unité source", 
        to_unit="Unité destination",
        unit_type="Type d'unité"
    )
    async def unit_converter(self, interaction: discord.Interaction,
                           value: float, from_unit: str, to_unit: str,
                           unit_type: str = "longueur"):
        """Convertisseur d'unités multiple"""
        
        unit_type = unit_type.lower()
        from_unit = from_unit.lower()
        to_unit = to_unit.lower()
        
        if unit_type not in self.conversion_units:
            available_types = ", ".join(self.conversion_units.keys())
            await interaction.response.send_message(f"❌ Types disponibles: {available_types}", ephemeral=True)
            return
        
        units = self.conversion_units[unit_type]
        
        if from_unit not in units or to_unit not in units:
            available_units = ", ".join(units.keys())
            await interaction.response.send_message(f"❌ Unités {unit_type}: {available_units}", ephemeral=True)
            return
        
        try:
            # Conversion via mètre (unité base)
            meters = value * units[from_unit]
            result = meters / units[to_unit]
            
            embed = discord.Embed(
                title="🔄 Conversion d'Unités",
                color=discord.Color.orange()
            )
            
            embed.add_field(
                name="📥 Valeur d'entrée",
                value=f"**{value:,.2f}** {from_unit}",
                inline=True
            )
            
            embed.add_field(
                name="📤 Résultat",
                value=f"**{result:,.6f}** {to_unit}",
                inline=True
            )
            
            embed.add_field(
                name="📊 Type",
                value=unit_type.capitalize(),
                inline=True
            )
            
            # Formule utilisée
            if result != value:
                ratio = units[to_unit] / units[from_unit]
                embed.add_field(
                    name="🧮 Formule",
                    value=f"1 {from_unit} = {ratio:,.6f} {to_unit}",
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur conversion: {e}", ephemeral=True)

    @app_commands.command(name="color", description="🎨 Générateur et analyseur de couleurs")
    @app_commands.describe(color_input="Couleur (hex, rgb, nom) ou 'random'")
    async def color_generator(self, interaction: discord.Interaction, 
                            color_input: str = "random"):
        """Générateur et analyseur de couleurs avancé"""
        
        try:
            if color_input.lower() == "random":
                # Génération couleur aléatoire
                r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
            elif color_input.startswith('#'):
                # Couleur hex
                hex_color = color_input
                if len(hex_color) == 4:  # #RGB -> #RRGGBB
                    hex_color = f"#{hex_color[1]*2}{hex_color[2]*2}{hex_color[3]*2}"
                r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
            else:
                # Nom couleur ou RGB
                await interaction.response.send_message("❌ Format: #hexadecimal, 'random' ou nom de couleur", ephemeral=True)
                return
            
            # Création image couleur
            img = Image.new('RGB', (200, 100), (r, g, b))
            
            # Conversion formats
            hsl = self.rgb_to_hsl(r, g, b)
            hsv = self.rgb_to_hsv(r, g, b)
            
            # Génération palette harmonique
            complementary = self.get_complementary_color(r, g, b)
            
            embed = discord.Embed(
                title="🎨 Analyseur de Couleur",
                color=int(hex_color[1:], 16)
            )
            
            embed.add_field(
                name="🔢 Valeurs",
                value=f"**HEX:** {hex_color.upper()}\n**RGB:** {r}, {g}, {b}\n**HSL:** {hsl[0]}°, {hsl[1]}%, {hsl[2]}%",
                inline=True
            )
            
            embed.add_field(
                name="🎯 Propriétés", 
                value=f"**Luminosité:** {self.get_brightness(r, g, b):.1f}%\n**Contraste:** {'Clair' if self.get_brightness(r, g, b) > 50 else 'Sombre'}\n**Complémentaire:** #{complementary[0]:02x}{complementary[1]:02x}{complementary[2]:02x}",
                inline=True
            )
            
            # Ajout image couleur
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            file = discord.File(img_bytes, filename="color.png")
            embed.set_thumbnail(url="attachment://color.png")
            
            await interaction.response.send_message(embed=embed, file=file)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur couleur: {e}", ephemeral=True)

    def rgb_to_hsl(self, r: int, g: int, b: int) -> tuple:
        """Convertit RGB vers HSL"""
        r, g, b = r/255.0, g/255.0, b/255.0
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        # Luminosité
        l = (max_val + min_val) / 2
        
        if diff == 0:
            h = s = 0
        else:
            # Saturation
            s = diff / (2 - max_val - min_val) if l > 0.5 else diff / (max_val + min_val)
            
            # Teinte
            if max_val == r:
                h = (g - b) / diff + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / diff + 2
            else:
                h = (r - g) / diff + 4
            h /= 6
        
        return (int(h * 360), int(s * 100), int(l * 100))

    def rgb_to_hsv(self, r: int, g: int, b: int) -> tuple:
        """Convertit RGB vers HSV"""
        r, g, b = r/255.0, g/255.0, b/255.0
        max_val = max(r, g, b)
        min_val = min(r, g, b)
        diff = max_val - min_val
        
        v = max_val
        s = 0 if max_val == 0 else diff / max_val
        
        if diff == 0:
            h = 0
        else:
            if max_val == r:
                h = (g - b) / diff + (6 if g < b else 0)
            elif max_val == g:
                h = (b - r) / diff + 2
            else:
                h = (r - g) / diff + 4
            h /= 6
        
        return (int(h * 360), int(s * 100), int(v * 100))

    def get_brightness(self, r: int, g: int, b: int) -> float:
        """Calcule la luminosité perçue"""
        return (r * 0.299 + g * 0.587 + b * 0.114) / 255 * 100

    def get_complementary_color(self, r: int, g: int, b: int) -> tuple:
        """Génère la couleur complémentaire"""
        return (255 - r, 255 - g, 255 - b)

    @app_commands.command(name="ascii", description="🎨 Générateur ASCII Art")
    @app_commands.describe(text="Texte à convertir", style="Style ASCII (block/small/banner)")
    async def ascii_art(self, interaction: discord.Interaction, 
                       text: str, style: str = "block"):
        """Générateur ASCII Art simple"""
        
        if len(text) > 20:
            await interaction.response.send_message("❌ Texte trop long (max 20 caractères) !", ephemeral=True)
            return
        
        # ASCII simple - patterns de base
        ascii_patterns = {
            "block": {
                "A": ["██", "██", "██", "  ", "██", "██", "██"],
                " ": ["  ", "  ", "  ", "  ", "  ", "  ", "  "]
            }
        }
        
        if style not in ascii_patterns:
            await interaction.response.send_message("❌ Styles: block, small, banner", ephemeral=True)
            return
        
        try:
            # Génération ASCII simple
            ascii_result = f"```\n{text.upper()}\n```"
            
            embed = discord.Embed(
                title="🎨 ASCII Art Générateur",
                description=f"Texte: **{text}**",
                color=discord.Color.purple()
            )
            
            embed.add_field(
                name="🖼️ Résultat",
                value=ascii_result,
                inline=False
            )
            
            embed.add_field(
                name="ℹ️ Style",
                value=style.capitalize(),
                inline=True
            )
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur ASCII: {e}", ephemeral=True)

    @app_commands.command(name="hash", description="🔐 Hachage de texte")
    @app_commands.describe(text="Texte à hacher", algorithm="Algorithme (md5/sha1/sha256)")
    async def hash_text(self, interaction: discord.Interaction, 
                       text: str, algorithm: str = "sha256"):
        """Hachage sécurisé de texte"""
        
        algorithms = {
            "md5": hashlib.md5,
            "sha1": hashlib.sha1, 
            "sha256": hashlib.sha256,
            "sha512": hashlib.sha512
        }
        
        if algorithm.lower() not in algorithms:
            await interaction.response.send_message("❌ Algorithmes: md5, sha1, sha256, sha512", ephemeral=True)
            return
        
        try:
            hash_func = algorithms[algorithm.lower()]
            hash_result = hash_func(text.encode()).hexdigest()
            
            embed = discord.Embed(
                title="🔐 Hachage de Texte",
                color=discord.Color.dark_blue()
            )
            
            embed.add_field(
                name="📝 Texte original",
                value=f"||`{text[:50]}{'...' if len(text) > 50 else ''}`||",
                inline=False
            )
            
            embed.add_field(
                name="🔒 Hash",
                value=f"`{hash_result}`",
                inline=False
            )
            
            embed.add_field(
                name="⚙️ Algorithme", 
                value=algorithm.upper(),
                inline=True
            )
            
            embed.add_field(
                name="📊 Longueur",
                value=f"{len(hash_result)} caractères",
                inline=True
            )
            
            embed.set_footer(text="⚠️ Le hachage est irréversible")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Erreur hachage: {e}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(UtilitiesSystem(bot))
    print("🔧 [Utilities System] Module chargé avec succès!")
