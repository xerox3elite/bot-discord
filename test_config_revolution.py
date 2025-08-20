#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 TEST ARSENAL CONFIG REVOLUTION
Script de test pour le nouveau système de configuration révolutionnaire
"""

import asyncio
import discord
from discord.ext import commands
import os
import sys

# Ajouter le dossier Arsenal_propre au path
sys.path.append('a:/Arsenal_propre')

async def test_config_revolution():
    """Test du système de configuration révolutionnaire"""
    
    print("🚀 [TEST] Début du test Arsenal Config Revolution")
    
    # Test 1: Import du module
    try:
        from commands.config_revolution import ArsenalConfigRevolution
        print("✅ [TEST] Import ArsenalConfigRevolution réussi")
    except Exception as e:
        print(f"❌ [TEST] Erreur import ArsenalConfigRevolution: {e}")
        return False
    
    # Test 2: Création d'une instance factice du bot
    try:
        intents = discord.Intents.all()
        bot = commands.Bot(command_prefix="!", intents=intents)
        print("✅ [TEST] Création du bot factice réussie")
    except Exception as e:
        print(f"❌ [TEST] Erreur création bot: {e}")
        return False
    
    # Test 3: Création du Cog
    try:
        config_cog = ArsenalConfigRevolution(bot)
        print("✅ [TEST] Création du Cog ArsenalConfigRevolution réussie")
    except Exception as e:
        print(f"❌ [TEST] Erreur création Cog: {e}")
        return False
    
    # Test 4: Test de la configuration par défaut
    try:
        default_config = config_cog.get_default_config()
        assert "version" in default_config
        assert "moderation" in default_config
        assert "economy" in default_config
        assert "voice" in default_config
        print("✅ [TEST] Configuration par défaut valide")
        print(f"    Version: {default_config['version']}")
        print(f"    Modules: {len(default_config)} sections")
    except Exception as e:
        print(f"❌ [TEST] Erreur configuration par défaut: {e}")
        return False
    
    # Test 5: Test de sauvegarde/chargement
    try:
        test_guild_id = 12345
        config_cog.save_guild_config(test_guild_id, default_config)
        loaded_config = config_cog.load_guild_config(test_guild_id)
        assert loaded_config["version"] == default_config["version"]
        print("✅ [TEST] Sauvegarde/Chargement configuration réussi")
    except Exception as e:
        print(f"❌ [TEST] Erreur sauvegarde/chargement: {e}")
        return False
    
    # Test 6: Test des vues Discord (structure)
    try:
        from commands.config_revolution import ConfigMainView, QuickSetupStep1
        main_view = ConfigMainView(bot, 123456, test_guild_id)
        step1_view = QuickSetupStep1(bot, 123456, test_guild_id)
        print("✅ [TEST] Création des vues Discord réussie")
    except Exception as e:
        print(f"❌ [TEST] Erreur création vues: {e}")
        return False
    
    print("🎉 [TEST] Tous les tests Arsenal Config Revolution passés avec succès !")
    return True

async def test_integration():
    """Test d'intégration avec le main.py"""
    
    print("\n🔧 [TEST] Test d'intégration avec main.py")
    
    try:
        # Simulation d'import depuis main.py
        sys.path.append('a:/Arsenal_propre')
        from commands.config_revolution import ArsenalConfigRevolution
        print("✅ [TEST] Import depuis main.py simulé réussi")
        
        # Test de structure des commandes
        # Vérifier que la commande config_revolution existe
        import inspect
        from commands.config_revolution import config_revolution
        
        sig = inspect.signature(config_revolution)
        print(f"✅ [TEST] Commande config_revolution trouvée avec signature: {sig}")
        
        return True
    except Exception as e:
        print(f"❌ [TEST] Erreur intégration: {e}")
        return False

async def main():
    """Fonction principale de test"""
    
    print("=" * 60)
    print("🧪 ARSENAL CONFIG REVOLUTION - TESTS")
    print("=" * 60)
    
    # Créer le dossier de test si nécessaire
    os.makedirs("a:/Arsenal_propre/data/configs", exist_ok=True)
    
    # Exécuter les tests
    test1_result = await test_config_revolution()
    test2_result = await test_integration()
    
    print("\n" + "=" * 60)
    if test1_result and test2_result:
        print("🎉 TOUS LES TESTS PASSÉS AVEC SUCCÈS !")
        print("✅ Arsenal Config Revolution est prêt à l'emploi")
        print("🚀 Le système révolutionnaire peut être déployé")
    else:
        print("❌ CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez les erreurs ci-dessus")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
