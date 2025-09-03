"""
=============================================================================
MODALS DISCORD.PY POUR HUNT ROYAL SYSTEM
Toutes les modales d'interface utilisateur Hunt Royal Arsenal
=============================================================================
"""

import discord
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any

class HRRegistrationModal(discord.ui.Modal):
    """Modal d'enregistrement Hunt Royal sécurisé"""
    
    def __init__(self):
        super().__init__(title="🏹 Enregistrement Hunt Royal Arsenal")
    
    game_id = discord.ui.TextInput(
        label="ID Hunt Royal (obligatoire)",
        placeholder="Entrez votre ID du jeu Hunt Royal...",
        required=True,
        max_length=50
    )
    
    clan_name = discord.ui.TextInput(
        label="Nom du Clan (obligatoire)",
        placeholder="Nom de votre clan Hunt Royal...",
        required=True,
        max_length=50
    )
    
    old_id = discord.ui.TextInput(
        label="Ancien ID (optionnel)",
        placeholder="Si vous aviez un ancien ID, saisissez-le ici...",
        required=False,
        max_length=50
    )
    
    discord_tag = discord.ui.TextInput(
        label="Tag Discord (optionnel)",
        placeholder="Votre tag Discord complet (ex: user#1234)...",
        required=False,
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Traitement de l'enregistrement"""
        from .hunt_royal_system import HuntRoyalUnifiedDB
        
        db = HuntRoyalUnifiedDB()
        
        # Créer le profil
        success, token, support_code = db.create_user_profile(
            discord_id=interaction.user.id,
            game_id=self.game_id.value,
            clan_name=self.clan_name.value,
            old_id=self.old_id.value or None,
            discord_tag=self.discord_tag.value or str(interaction.user)
        )
        
        if success:
            embed = discord.Embed(
                title="✅ Enregistrement Hunt Royal Réussi !",
                description=f"**Bienvenue dans le système Hunt Royal Arsenal, {interaction.user.display_name} !**\n\n"
                           "Votre compte a été créé avec succès et sécurisé.",
                color=0x00AA55
            )
            
            embed.add_field(
                name="🎮 Informations Enregistrées",
                value=f"**ID Hunt Royal:** {self.game_id.value}\n"
                      f"**Clan:** {self.clan_name.value}\n"
                      f"**Discord:** {interaction.user}\n"
                      f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                inline=False
            )
            
            embed.add_field(
                name="🔑 Code Support Personnel",
                value=f"**Code:** `{support_code}`\n\n"
                      "⚠️ **IMPORTANT:** Gardez ce code secret ! Il vous permet d'obtenir de l'aide technique prioritaire.",
                inline=False
            )
            
            embed.add_field(
                name="🎯 Prochaines Étapes",
                value="• Utilisez `/hr calculator` pour des calculs précis\n"
                      "• Explorez `/hr hunters` pour la base chasseurs\n"
                      "• Sauvegardez vos builds avec `/hr builds`\n"
                      "• Rejoignez la communauté avec `/hr popular`",
                inline=False
            )
            
            embed.add_field(
                name="🛡️ Sécurité & Confidentialité",
                value="• Token unique 64 caractères généré\n"
                      "• Toutes vos données sont chiffrées\n"
                      "• Commandes éphémères pour confidentialité\n"
                      "• Accès WebPanel futur inclus",
                inline=False
            )
            
            embed.set_footer(text="🏹 Arsenal Hunt Royal System • Enregistrement Sécurisé")
            
        else:
            embed = discord.Embed(
                title="❌ Erreur d'Enregistrement",
                description="Une erreur s'est produite lors de l'enregistrement.\n\n"
                           "Contactez le support Arsenal avec votre Discord ID.",
                color=0xFF3333
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class AttackCalculatorModal(discord.ui.Modal):
    """Modal pour le calculateur d'attaque Hunt Royal ultra-précis"""
    
    def __init__(self, calculator_data: Dict[str, Any], db):
        super().__init__(title="⚔️ Calculateur d'Attaque Hunt Royal")
        self.calculator_data = calculator_data
        self.db = db
    
    base_attack = discord.ui.TextInput(
        label="Attaque de Base",
        placeholder="Attaque de base de votre chasseur (ex: 1250)",
        required=True,
        max_length=10
    )
    
    attack_speed = discord.ui.TextInput(
        label="Vitesse d'Attaque",
        placeholder="Vitesse d'attaque (ex: 1.45)",
        required=True,
        max_length=10
    )
    
    multishot_level = discord.ui.TextInput(
        label="Niveau Multishot",
        placeholder="Niveau multishot stone (0-10)",
        required=True,
        max_length=2
    )
    
    poison_level = discord.ui.TextInput(
        label="Niveau Poison",
        placeholder="Niveau poison stone (0-10)",
        required=False,
        max_length=2
    )
    
    burn_level = discord.ui.TextInput(
        label="Niveau Burn/Fire",
        placeholder="Niveau burn stone (0-10)",
        required=False,
        max_length=2
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Calcul d'attaque ultra-précis basé sur les vraies formules Hunt Royal"""
        
        try:
            # Validation des entrées
            base_atk = float(self.base_attack.value)
            atk_speed = float(self.attack_speed.value)
            multishot = int(self.multishot_level.value or 0)
            poison = int(self.poison_level.value or 0)
            burn = int(self.burn_level.value or 0)
            
            # Formules Hunt Royal réelles (basées sur le spreadsheet utilisateur)
            
            # Calcul multishot précis
            multishot_multiplier = 1.0
            if multishot > 0:
                multishot_multiplier = 1.0 + (multishot * 0.15)  # +15% par niveau
            
            # Calcul poison stacks (formule exacte du jeu)
            poison_dps = 0
            if poison > 0:
                poison_base_damage = base_atk * 0.1  # 10% de l'attaque base
                poison_stacks_max = poison * 2  # 2 stacks par niveau
                poison_dps = poison_base_damage * poison_stacks_max * 2  # 2 ticks/sec
            
            # Calcul burn damage (formule explosive)
            burn_dps = 0
            if burn > 0:
                burn_base_damage = base_atk * 0.2  # 20% de l'attaque base
                burn_multiplier = 1.0 + (burn * 0.25)  # +25% par niveau
                burn_dps = burn_base_damage * burn_multiplier * 1.5  # 1.5 ticks/sec
            
            # DPS final avec toutes les optimisations
            base_dps = base_atk * atk_speed
            multishot_dps = base_dps * multishot_multiplier
            total_dps = multishot_dps + poison_dps + burn_dps
            
            # Calculs avancés
            dps_per_multishot = total_dps / max(multishot_multiplier, 1.0)
            effective_attack_rating = base_atk * multishot_multiplier * (1 + (poison + burn) * 0.1)
            
            # Sauvegarder les données
            self.calculator_data["attack"] = {
                "base_attack": base_atk,
                "attack_speed": atk_speed,
                "multishot_level": multishot,
                "poison_level": poison,
                "burn_level": burn,
                "total_dps": total_dps,
                "multishot_dps": multishot_dps,
                "poison_dps": poison_dps,
                "burn_dps": burn_dps,
                "effective_attack_rating": effective_attack_rating
            }
            
            # Embed de résultats ultra-détaillé
            embed = discord.Embed(
                title="⚔️ Résultats Calculateur d'Attaque",
                description=f"**DPS Total: {total_dps:,.0f}** 🔥\n\n"
                           "Calculs basés sur les vraies formules Hunt Royal",
                color=0xFF3333
            )
            
            embed.add_field(
                name="📊 DPS Détaillé",
                value=f"**Base DPS:** {base_dps:,.0f}\n"
                      f"**Multishot DPS:** {multishot_dps:,.0f} (+{((multishot_dps/base_dps-1)*100):+.1f}%)\n"
                      f"**Poison DPS:** {poison_dps:,.0f}\n"
                      f"**Burn DPS:** {burn_dps:,.0f}\n"
                      f"**TOTAL:** {total_dps:,.0f}",
                inline=True
            )
            
            embed.add_field(
                name="🎯 Stats Avancées",
                value=f"**Attaque Effective:** {effective_attack_rating:,.0f}\n"
                      f"**DPS par Multishot:** {dps_per_multishot:,.0f}\n"
                      f"**Stacks Poison Max:** {poison * 2}\n"
                      f"**Burn Multiplier:** {1.0 + (burn * 0.25):.2f}x",
                inline=True
            )
            
            # Recommandations intelligentes
            recommendations = []
            if multishot < 5:
                recommendations.append("🎯 Augmenter Multishot pour +DPS massif")
            if poison > 0 and poison < 7:
                recommendations.append("☠️ Poison niveau 7+ pour stacks optimales")
            if burn > 0 and burn < 5:
                recommendations.append("🔥 Burn niveau 5+ pour damage explosif")
            if multishot >= 8 and poison >= 7:
                recommendations.append("⚡ Build optimisé ! Focus sur équipement")
            
            if recommendations:
                embed.add_field(
                    name="💡 Recommandations IA",
                    value="\n".join(recommendations),
                    inline=False
                )
            
            # Comparaison avec builds populaires
            try:
                popular_builds = self.db.get_popular_builds(5)
                if popular_builds:
                    attack_builds = [b for b in popular_builds if b['calculator_type'] == 'attack']
                    if attack_builds:
                        best_dps = max(json.loads(b.get('results_data', '{}').get('total_dps', 0)) for b in attack_builds)
                        if total_dps > best_dps * 0.8:  # Top 20%
                            embed.add_field(
                                name="🏆 Performance",
                                value=f"**Excellent !** Top 20% des builds communauté\n"
                                      f"Votre DPS: {total_dps:,.0f} vs Meilleur: {best_dps:,.0f}",
                                inline=False
                            )
            except:
                pass  # Pas critique
            
            embed.set_footer(text="🏹 Hunt Royal Calculator • Formules Exactes du Jeu")
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Erreur de Calcul",
                description="**Veuillez vérifier vos valeurs :**\n\n"
                           "• Attaque et vitesse: nombres décimaux\n"
                           "• Niveaux stones: nombres entiers (0-10)\n"
                           "• Exemple: 1250 pour l'attaque, 1.45 pour la vitesse",
                color=0xFF9900
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class DefenceCalculatorModal(discord.ui.Modal):
    """Modal pour le calculateur de défense Hunt Royal ultra-précis"""
    
    def __init__(self, calculator_data: Dict[str, Any], db):
        super().__init__(title="🛡️ Calculateur de Défense Hunt Royal")
        self.calculator_data = calculator_data
        self.db = db
    
    base_hp = discord.ui.TextInput(
        label="Points de Vie de Base",
        placeholder="HP de base de votre chasseur (ex: 8500)",
        required=True,
        max_length=10
    )
    
    hp_bonus_percent = discord.ui.TextInput(
        label="Bonus HP % (équipement)",
        placeholder="Bonus HP total en % (ex: 150 pour +150%)",
        required=True,
        max_length=10
    )
    
    regen_level = discord.ui.TextInput(
        label="Niveau Régénération",
        placeholder="Niveau regen stone (0-10)",
        required=False,
        max_length=2
    )
    
    shield_level = discord.ui.TextInput(
        label="Niveau Shield",
        placeholder="Niveau shield stone (0-10)",
        required=False,
        max_length=2
    )
    
    xp_bonus = discord.ui.TextInput(
        label="Bonus XP %",
        placeholder="Bonus XP total en % (ex: 200 pour +200%)",
        required=False,
        max_length=10
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Calcul de défense ultra-précis basé sur les vraies formules"""
        
        try:
            # Validation des entrées
            base_hp = float(self.base_hp.value)
            hp_bonus = float(self.hp_bonus_percent.value) / 100.0
            regen = int(self.regen_level.value or 0)
            shield = int(self.shield_level.value or 0)
            xp_bonus = float(self.xp_bonus.value or 0) / 100.0
            
            # Formules Hunt Royal réelles pour défense
            
            # HP Effectif avec tous les bonus
            hp_multiplier = 1.0 + hp_bonus
            effective_hp = base_hp * hp_multiplier
            
            # Calcul shield (absorption de dégâts)
            shield_absorption = 0
            if shield > 0:
                shield_absorption = shield * 5  # 5% d'absorption par niveau
                shield_hp_bonus = effective_hp * (shield_absorption / 100.0)
                effective_hp_with_shield = effective_hp + shield_hp_bonus
            else:
                effective_hp_with_shield = effective_hp
            
            # Calcul régénération par seconde
            regen_per_sec = 0
            if regen > 0:
                base_regen = base_hp * 0.01  # 1% HP base par niveau
                regen_multiplier = regen * 1.2  # 1.2x par niveau
                regen_per_sec = base_regen * regen_multiplier
            
            # HP Effectif total avec régénération (sur 60 secondes)
            effective_hp_with_regen = effective_hp_with_shield + (regen_per_sec * 60)
            
            # Score de survivabilité (formule Arsenal)
            survivability_score = (
                effective_hp_with_shield * 0.6 +  # 60% HP
                regen_per_sec * 100 * 0.3 +       # 30% regen
                shield_absorption * 50 * 0.1       # 10% shield
            )
            
            # Calculs avancés
            hp_per_percent_bonus = base_hp * 0.01
            survival_time_estimate = effective_hp_with_shield / max(1000, base_hp * 0.1)  # vs DPS moyen
            
            # Sauvegarder les données
            self.calculator_data["defence"] = {
                "base_hp": base_hp,
                "hp_bonus_percent": hp_bonus * 100,
                "regen_level": regen,
                "shield_level": shield,
                "xp_bonus": xp_bonus * 100,
                "effective_hp": effective_hp_with_shield,
                "regen_per_sec": regen_per_sec,
                "survivability_score": survivability_score
            }
            
            # Embed de résultats ultra-détaillé
            embed = discord.Embed(
                title="🛡️ Résultats Calculateur de Défense",
                description=f"**HP Effectif: {effective_hp_with_shield:,.0f}** 💚\n\n"
                           "Calculs basés sur les vraies formules Hunt Royal",
                color=0x3366FF
            )
            
            embed.add_field(
                name="❤️ Points de Vie",
                value=f"**Base HP:** {base_hp:,.0f}\n"
                      f"**Bonus HP:** +{hp_bonus*100:.0f}% ({(effective_hp-base_hp):,.0f})\n"
                      f"**Shield Bonus:** {shield_absorption}% ({shield_hp_bonus:,.0f} HP)\n"
                      f"**TOTAL:** {effective_hp_with_shield:,.0f} HP",
                inline=True
            )
            
            embed.add_field(
                name="🔄 Régénération",
                value=f"**Regen/sec:** {regen_per_sec:,.1f} HP\n"
                      f"**Regen/min:** {regen_per_sec*60:,.0f} HP\n"
                      f"**HP sur 60sec:** {effective_hp_with_regen:,.0f}\n"
                      f"**Efficacité:** {(regen_per_sec/base_hp*100):.2f}%",
                inline=True
            )
            
            embed.add_field(
                name="🏆 Survivabilité",
                value=f"**Score:** {survivability_score:,.0f} points\n"
                      f"**Temps survie estimé:** {survival_time_estimate:.1f}s\n"
                      f"**XP Bonus:** +{xp_bonus*100:.0f}%\n"
                      f"**HP par 1% bonus:** {hp_per_percent_bonus:,.0f}",
                inline=False
            )
            
            # Recommandations intelligentes pour défense
            recommendations = []
            if hp_bonus < 1.0:  # Moins de 100% bonus
                recommendations.append("💎 Priorisez équipement +HP pour survivabilité")
            if regen < 5 and base_hp > 5000:
                recommendations.append("🔄 Regen niveau 5+ recommandé pour gros HP")
            if shield < 3 and effective_hp > 15000:
                recommendations.append("🛡️ Shield stones pour absorption dégâts")
            if xp_bonus < 1.0:
                recommendations.append("⭐ Bonus XP pour farm efficace")
            
            # Recommandations selon le type de build
            if effective_hp_with_shield > 25000:
                recommendations.append("🏰 Build Tank parfait ! Focus sur regen max")
            elif effective_hp_with_shield < 10000:
                recommendations.append("⚠️ HP faible ! Priorité absolue équipement défense")
            
            if recommendations:
                embed.add_field(
                    name="💡 Recommandations IA",
                    value="\n".join(recommendations),
                    inline=False
                )
            
            # Classement par rapport aux builds populaires
            survivability_grade = "C"
            if survivability_score > 50000:
                survivability_grade = "S+"
            elif survivability_score > 30000:
                survivability_grade = "A"
            elif survivability_score > 15000:
                survivability_grade = "B"
            
            embed.add_field(
                name="📈 Performance",
                value=f"**Grade Survivabilité:** {survivability_grade}\n"
                      f"**Comparé à la meta:** {'Excellent' if survivability_grade in ['S+', 'A'] else 'À améliorer'}\n"
                      f"**Points forts:** {'Tank' if effective_hp_with_shield > 20000 else 'DPS' if effective_hp_with_shield < 12000 else 'Équilibré'}",
                inline=False
            )
            
            embed.set_footer(text="🏹 Hunt Royal Calculator • Formules Exactes de Défense")
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Erreur de Calcul",
                description="**Veuillez vérifier vos valeurs :**\n\n"
                           "• HP de base: nombre entier (ex: 8500)\n"
                           "• Bonus HP: pourcentage (ex: 150 pour +150%)\n"
                           "• Niveaux stones: nombres entiers (0-10)",
                color=0xFF9900
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class SaveBuildModal(discord.ui.Modal):
    """Modal pour sauvegarder un build Hunt Royal"""
    
    def __init__(self, calculator_data: Dict[str, Any], db):
        super().__init__(title="💾 Sauvegarder Build Hunt Royal")
        self.calculator_data = calculator_data
        self.db = db
    
    build_name = discord.ui.TextInput(
        label="Nom du Build",
        placeholder="Donnez un nom à votre build (ex: Tank PvE, DPS Raid...)",
        required=True,
        max_length=50
    )
    
    build_description = discord.ui.TextInput(
        label="Description (optionnelle)",
        placeholder="Décrivez votre build, stratégie, utilisation...",
        required=False,
        max_length=200,
        style=discord.TextStyle.paragraph
    )
    
    is_public = discord.ui.TextInput(
        label="Partager publiquement ? (oui/non)",
        placeholder="'oui' pour partager avec la communauté, 'non' pour privé",
        required=False,
        max_length=3
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Sauvegarde du build avec options avancées"""
        
        # Vérifier qu'il y a des données
        current_mode = self.calculator_data.get("current_mode", "attack")
        build_data = self.calculator_data.get(current_mode, {})
        
        if not build_data:
            embed = discord.Embed(
                title="❌ Aucune Donnée à Sauvegarder",
                description="Veuillez d'abord utiliser un calculateur avant de sauvegarder.",
                color=0xFF9900
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Options de partage
        is_public_build = self.is_public.value.lower() in ["oui", "yes", "y", "public", "1", "true"]
        
        try:
            # Sauvegarder dans la base de données
            build_id = self.db.save_calculator_result(
                user_id=interaction.user.id,
                calculator_type=current_mode,
                inputs_data=build_data,
                results_data=build_data,
                build_name=self.build_name.value,
                description=self.build_description.value,
                is_public=is_public_build
            )
            
            if build_id:
                embed = discord.Embed(
                    title="✅ Build Sauvegardé avec Succès !",
                    description=f"**Votre build '{self.build_name.value}' a été sauvegardé !**",
                    color=0x00AA55
                )
                
                embed.add_field(
                    name="📋 Détails du Build",
                    value=f"**Nom:** {self.build_name.value}\n"
                          f"**Type:** {'⚔️ Attaque' if current_mode == 'attack' else '🛡️ Défense'}\n"
                          f"**Visibilité:** {'🌐 Public' if is_public_build else '🔒 Privé'}\n"
                          f"**ID Build:** #{build_id}",
                    inline=False
                )
                
                if self.build_description.value:
                    embed.add_field(
                        name="📝 Description",
                        value=self.build_description.value,
                        inline=False
                    )
                
                # Stats du build selon le type
                if current_mode == "attack":
                    total_dps = build_data.get("total_dps", 0)
                    embed.add_field(
                        name="⚔️ Stats Principales",
                        value=f"**DPS Total:** {total_dps:,.0f}\n"
                              f"**Multishot:** Niveau {build_data.get('multishot_level', 0)}\n"
                              f"**Poison:** Niveau {build_data.get('poison_level', 0)}\n"
                              f"**Burn:** Niveau {build_data.get('burn_level', 0)}",
                        inline=True
                    )
                else:  # defence
                    effective_hp = build_data.get("effective_hp", 0)
                    embed.add_field(
                        name="🛡️ Stats Principales",
                        value=f"**HP Effectif:** {effective_hp:,.0f}\n"
                              f"**Regen:** {build_data.get('regen_per_sec', 0):.1f}/sec\n"
                              f"**Shield:** Niveau {build_data.get('shield_level', 0)}\n"
                              f"**Score:** {build_data.get('survivability_score', 0):,.0f}",
                        inline=True
                    )
                
                if is_public_build:
                    embed.add_field(
                        name="🌐 Partage Communautaire",
                        value="• Votre build est maintenant visible publiquement\n"
                              "• D'autres joueurs peuvent le liker et commenter\n"
                              "• Utilisez `/hr popular` pour voir les builds populaires\n"
                              "• Gagnez de la réputation avec les likes !",
                        inline=False
                    )
                
                embed.add_field(
                    name="🎯 Prochaines Étapes",
                    value="• Modifiez votre build avec `/hr builds`\n"
                          "• Créez des variantes pour différentes situations\n"
                          "• Comparez avec les builds populaires\n"
                          "• Exportez vos données (bientôt)",
                    inline=False
                )
                
            else:
                embed = discord.Embed(
                    title="❌ Erreur de Sauvegarde",
                    description="Une erreur s'est produite lors de la sauvegarde.\nContactez le support avec votre code.",
                    color=0xFF3333
                )
                
        except Exception as e:
            embed = discord.Embed(
                title="❌ Erreur Technique",
                description=f"Erreur lors de la sauvegarde: {str(e)[:100]}\nContactez le support Arsenal.",
                color=0xFF3333
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class HunterSelectionModal(discord.ui.Modal):
    """Modal pour sélectionner un chasseur de la base Arsenal"""
    
    def __init__(self, calculator_data: Dict[str, Any], db):
        super().__init__(title="🏹 Sélectionner Chasseur Hunt Royal")
        self.calculator_data = calculator_data
        self.db = db
    
    hunter_name = discord.ui.TextInput(
        label="Nom du Chasseur",
        placeholder="Nom exact du chasseur Hunt Royal (ex: Archer Elite)",
        required=True,
        max_length=50
    )
    
    hunter_level = discord.ui.TextInput(
        label="Niveau du Chasseur",
        placeholder="Niveau actuel (1-100)",
        required=False,
        max_length=3
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Sélection et intégration chasseur dans les calculs"""
        
        # Rechercher dans la base de données chasseurs
        hunter_data = self.db.search_hunter(self.hunter_name.value)
        
        if hunter_data:
            # Intégrer les stats du chasseur
            self.calculator_data["hunter_selected"] = {
                "name": hunter_data.get("name", self.hunter_name.value),
                "level": int(self.hunter_level.value or 1),
                "base_stats": hunter_data
            }
            
            embed = discord.Embed(
                title="✅ Chasseur Sélectionné",
                description=f"**{hunter_data.get('name')} intégré dans vos calculs !**",
                color=0x00AA55
            )
            
            embed.add_field(
                name="🏹 Stats du Chasseur",
                value=f"**ATK Base:** {hunter_data.get('base_attack', 'N/A')}\n"
                      f"**HP Base:** {hunter_data.get('base_hp', 'N/A')}\n"
                      f"**Vitesse:** {hunter_data.get('attack_speed', 'N/A')}\n"
                      f"**Tier:** {hunter_data.get('tier_meta', 'B')}",
                inline=True
            )
            
            if self.hunter_level.value:
                level = int(self.hunter_level.value)
                scaled_attack = hunter_data.get('base_attack', 1000) * (1 + (level - 1) * 0.05)
                scaled_hp = hunter_data.get('base_hp', 5000) * (1 + (level - 1) * 0.08)
                
                embed.add_field(
                    name=f"📈 Stats Niveau {level}",
                    value=f"**ATK Scalée:** {scaled_attack:,.0f}\n"
                          f"**HP Scalée:** {scaled_hp:,.0f}\n"
                          f"**Bonus niveau:** +{(level-1)*5}% ATK\n"
                          f"**Bonus niveau:** +{(level-1)*8}% HP",
                    inline=True
                )
            
        else:
            embed = discord.Embed(
                title="❌ Chasseur Non Trouvé",
                description=f"**'{self.hunter_name.value}' n'a pas été trouvé dans la base.**\n\n"
                           "Vérifiez l'orthographe ou utilisez `/hr hunters` pour explorer.",
                color=0xFF9900
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class SearchBuildModal(discord.ui.Modal):
    """Modal pour rechercher des builds sauvegardés"""
    
    def __init__(self, db):
        super().__init__(title="🔍 Rechercher Build")
        self.db = db
    
    search_term = discord.ui.TextInput(
        label="Terme de recherche",
        placeholder="Nom du build, description, type...",
        required=True,
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Recherche dans les builds de l'utilisateur"""
        
        builds = self.db.search_user_builds(interaction.user.id, self.search_term.value)
        
        embed = discord.Embed(
            title="🔍 Résultats de Recherche",
            description=f"**Recherche pour: '{self.search_term.value}'**",
            color=0x3366FF
        )
        
        if builds:
            for build in builds[:10]:
                build_type_emoji = "⚔️" if build['calculator_type'] == 'attack' else "🛡️"
                embed.add_field(
                    name=f"{build_type_emoji} {build['build_name']}",
                    value=f"{build.get('description', 'Pas de description')[:50]}...\n"
                          f"Créé: {build['created_at'][:10]}",
                    inline=True
                )
        else:
            embed.description += "\n\n❌ Aucun résultat trouvé."
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


class HunterSearchModal(discord.ui.Modal):
    """Modal pour rechercher dans la base chasseurs"""
    
    def __init__(self, db):
        super().__init__(title="🏹 Rechercher Chasseur")
        self.db = db
    
    search_term = discord.ui.TextInput(
        label="Nom ou caractéristique",
        placeholder="Nom chasseur, arme, tier... (ex: Archer, Bow, S)",
        required=True,
        max_length=50
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        """Recherche dans la base chasseurs"""
        
        hunters = self.db.search_hunters(self.search_term.value)
        
        embed = discord.Embed(
            title="🏹 Chasseurs Trouvés",
            description=f"**Recherche pour: '{self.search_term.value}'**",
            color=0x9B59B6
        )
        
        if hunters:
            for hunter in hunters[:10]:
                embed.add_field(
                    name=f"{hunter.get('name', 'Unknown')}",
                    value=f"**Arme:** {hunter.get('weapon_type', 'N/A')}\n"
                          f"**Tier:** {hunter.get('tier_meta', 'B')}\n"
                          f"**ATK:** {hunter.get('base_attack', 'N/A')}",
                    inline=True
                )
        else:
            embed.description += "\n\n❌ Aucun chasseur trouvé."
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

