"""
🧪 TEST HUNT ROYAL SYSTEM V2.0
Tests du système Hunt Royal avec authentification et calculateurs

Tests inclus:
- Base de données Hunt Royal
- Système d'authentification
- Calculateurs Attack/Defence
- Génération tokens/codes support
- Validation fonctionnalités

Author: Arsenal Bot Team
Version: 2.0.0
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import unittest
import sqlite3
import json
import tempfile
from unittest.mock import MagicMock, patch
from commands.hunt_royal_system import HuntRoyalDB, HuntRoyalCalculator

class TestHuntRoyalSystem(unittest.TestCase):
    """Tests du système Hunt Royal complet"""
    
    def setUp(self):
        """Configuration des tests"""
        # Créer une DB temporaire pour les tests
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.db = HuntRoyalDB(self.temp_db.name)
        self.calculator = HuntRoyalCalculator()
        
        # Données de test
        self.test_discord_id = 123456789
        self.test_game_id = "TestPlayer123"
        self.test_clan_name = "TestClan"
        self.test_old_id = "OldPlayer456"
    
    def tearDown(self):
        """Nettoyage après tests"""
        os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test initialisation base de données"""
        print("🧪 Test: Initialisation base de données...")
        
        # Vérifier que les tables existent
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            
            # Vérifier table hr_profiles
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hr_profiles'")
            self.assertIsNotNone(cursor.fetchone(), "Table hr_profiles non créée")
            
            # Vérifier table hr_calculators
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hr_calculators'")
            self.assertIsNotNone(cursor.fetchone(), "Table hr_calculators non créée")
            
            # Vérifier table hr_webpanel_sessions
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hr_webpanel_sessions'")
            self.assertIsNotNone(cursor.fetchone(), "Table hr_webpanel_sessions non créée")
        
        print("✅ Base de données initialisée correctement")
    
    def test_user_registration(self):
        """Test enregistrement utilisateur"""
        print("🧪 Test: Enregistrement utilisateur...")
        
        # Test enregistrement réussi
        result = self.db.register_user(
            discord_id=self.test_discord_id,
            game_id=self.test_game_id,
            clan_name=self.test_clan_name,
            old_id=self.test_old_id
        )
        
        self.assertTrue(result["success"], "Enregistrement échoué")
        self.assertIn("token", result, "Token non généré")
        self.assertIn("support_code", result, "Code support non généré")
        
        # Vérifier que le token fait 64 caractères
        self.assertEqual(len(result["token"]), 64, "Token incorrect (doit faire 64 caractères)")
        
        # Vérifier format code support
        expected_code = f"{self.test_discord_id}{result['token'][-8:].upper()}"
        self.assertEqual(result["support_code"], expected_code, "Code support incorrect")
        
        print(f"✅ Utilisateur enregistré: Token={result['token'][:10]}..., Code={result['support_code']}")
        
        # Test enregistrement en double (doit échouer)
        result2 = self.db.register_user(
            discord_id=self.test_discord_id,
            game_id="AnotherID",
            clan_name="AnotherClan"
        )
        
        self.assertFalse(result2["success"], "Double enregistrement autorisé (erreur)")
        self.assertIn("déjà enregistré", result2["error"], "Message d'erreur incorrect")
        
        print("✅ Protection contre double enregistrement fonctionne")
    
    def test_user_profile_retrieval(self):
        """Test récupération profil utilisateur"""
        print("🧪 Test: Récupération profil utilisateur...")
        
        # Enregistrer un utilisateur d'abord
        self.db.register_user(
            discord_id=self.test_discord_id,
            game_id=self.test_game_id,
            clan_name=self.test_clan_name,
            old_id=self.test_old_id
        )
        
        # Récupérer le profil
        profile = self.db.get_user_profile(self.test_discord_id)
        
        self.assertIsNotNone(profile, "Profil non trouvé")
        self.assertEqual(profile["discord_id"], self.test_discord_id, "Discord ID incorrect")
        self.assertEqual(profile["game_id"], self.test_game_id, "Game ID incorrect")
        self.assertEqual(profile["clan_name"], self.test_clan_name, "Nom clan incorrect")
        self.assertEqual(profile["old_id"], self.test_old_id, "Ancien ID incorrect")
        
        print(f"✅ Profil récupéré: {profile['game_id']} du clan {profile['clan_name']}")
        
        # Test utilisateur inexistant
        fake_profile = self.db.get_user_profile(999999999)
        self.assertIsNone(fake_profile, "Profil inexistant retourné")
        
        print("✅ Gestion utilisateur inexistant correcte")
    
    def test_last_active_update(self):
        """Test mise à jour dernière activité"""
        print("🧪 Test: Mise à jour activité...")
        
        # Enregistrer un utilisateur
        self.db.register_user(
            discord_id=self.test_discord_id,
            game_id=self.test_game_id,
            clan_name=self.test_clan_name
        )
        
        # Récupérer compteur initial
        profile_before = self.db.get_user_profile(self.test_discord_id)
        commands_before = profile_before["total_commands"]
        
        # Mettre à jour l'activité
        self.db.update_last_active(self.test_discord_id)
        
        # Vérifier mise à jour
        profile_after = self.db.get_user_profile(self.test_discord_id)
        commands_after = profile_after["total_commands"]
        
        self.assertEqual(commands_after, commands_before + 1, "Compteur commandes non mis à jour")
        
        print(f"✅ Activité mise à jour: {commands_before} → {commands_after} commandes")
    
    def test_attack_calculator(self):
        """Test calculateur d'attaque"""
        print("🧪 Test: Calculateur d'attaque...")
        
        # Données de test similaires à l'image
        base_stats = {
            "att_spd": 70.0,
            "att_dmg": 123.0,
            "hunter": "Multi Shot (like AO)",
            "multishot_perks": 2
        }
        
        gear = {
            "weapon_bonus": 0,
            "ring_bonus": 0
        }
        
        stones = {
            "poison": {"level": 6, "value": 39.525},
            "burn": {"level": 6, "value": 0},
            "damage": {"level": 6, "value": 0},
            "drain_life": {"level": 6, "value": 0},
            "tentacles": {"level": 6, "value": 0}
        }
        
        # Effectuer le calcul
        results = self.calculator.calculate_attack_damage(base_stats, gear, stones)
        
        # Vérifications des résultats
        self.assertIn("base_damage", results, "Base damage manquant")
        self.assertIn("final_damage", results, "Final damage manquant")
        self.assertIn("dps_base", results, "DPS base manquant")
        self.assertIn("dps_final", results, "DPS final manquant")
        self.assertIn("poison_value", results, "Poison value manquant")
        self.assertIn("total_dps", results, "DPS total manquant")
        
        # Vérifier que les valeurs sont cohérentes
        self.assertEqual(results["base_damage"], 123.0, "Base damage incorrect")
        self.assertGreater(results["dps_final"], results["dps_base"], "DPS final doit être > DPS base avec multishot")
        self.assertGreater(results["total_dps"], 0, "DPS total doit être positif")
        
        print(f"✅ Calcul attaque réussi:")
        print(f"   • Base damage: {results['base_damage']}")
        print(f"   • DPS final: {results['dps_final']}")
        print(f"   • Poison value: {results['poison_value']}")
        print(f"   • DPS total: {results['total_dps']}")
    
    def test_defence_calculator(self):
        """Test calculateur de défense"""
        print("🧪 Test: Calculateur de défense...")
        
        # Données de test
        base_stats = {
            "hp": 750.0
        }
        
        gear = {
            "helmet_bonus": 0,
            "chest_bonus": 0
        }
        
        stones = {
            "regen": {"level": 6, "value": 5.0},
            "exp": {"level": 6, "value": 10.0}
        }
        
        # Effectuer le calcul
        results = self.calculator.calculate_defence_stats(base_stats, gear, stones)
        
        # Vérifications des résultats
        self.assertIn("base_hp", results, "Base HP manquant")
        self.assertIn("effective_hp", results, "HP effectif manquant")
        self.assertIn("regen_per_sec", results, "Regen/sec manquant")
        self.assertIn("exp_bonus_percent", results, "Bonus XP manquant")
        self.assertIn("survivability_score", results, "Score survivabilité manquant")
        
        # Vérifier valeurs
        self.assertEqual(results["base_hp"], 750.0, "Base HP incorrect")
        self.assertEqual(results["effective_hp"], 750.0, "HP effectif incorrect (sans bonus)")
        self.assertEqual(results["regen_per_sec"], 30.0, "Regen incorrect (5*6=30)")
        self.assertEqual(results["exp_bonus_percent"], 60.0, "Bonus XP incorrect (10*6=60)")
        
        print(f"✅ Calcul défense réussi:")
        print(f"   • HP effectif: {results['effective_hp']}")
        print(f"   • Regen/sec: {results['regen_per_sec']}")
        print(f"   • Bonus XP: {results['exp_bonus_percent']}%")
        print(f"   • Score survivabilité: {results['survivability_score']}")
    
    def test_calculator_save(self):
        """Test sauvegarde calculateur"""
        print("🧪 Test: Sauvegarde calculateur...")
        
        # Enregistrer un utilisateur d'abord
        self.db.register_user(
            discord_id=self.test_discord_id,
            game_id=self.test_game_id,
            clan_name=self.test_clan_name
        )
        
        # Sauvegarder un calculateur
        stats = {"att_spd": 70, "att_dmg": 123}
        gear = {"weapon_bonus": 0}
        results = {"dps_total": 1000}
        
        calc_id = self.db.save_calculator(
            discord_id=self.test_discord_id,
            calc_type="attack",
            name="Test Build",
            stats=stats,
            gear=gear,
            results=results
        )
        
        self.assertIsNotNone(calc_id, "ID calculateur non retourné")
        self.assertGreater(calc_id, 0, "ID calculateur invalide")
        
        # Vérifier en base
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM hr_calculators WHERE id = ?", (calc_id,))
            saved_calc = cursor.fetchone()
            
            self.assertIsNotNone(saved_calc, "Calculateur non sauvegardé")
            
            # Vérifier données JSON
            saved_stats = json.loads(saved_calc[4])  # stats_data
            self.assertEqual(saved_stats, stats, "Stats mal sauvegardées")
        
        print(f"✅ Calculateur sauvegardé avec ID: {calc_id}")
    
    def test_token_generation(self):
        """Test génération tokens et codes"""
        print("🧪 Test: Génération tokens et codes...")
        
        # Test génération token
        token1 = self.db._generate_token()
        token2 = self.db._generate_token()
        
        self.assertEqual(len(token1), 64, "Token 1 longueur incorrecte")
        self.assertEqual(len(token2), 64, "Token 2 longueur incorrecte")
        self.assertNotEqual(token1, token2, "Tokens identiques (problème aléatoire)")
        
        # Test génération code support
        test_discord_id = 123456789
        test_token = "abcdef" + "x" * 58  # 64 chars total
        
        support_code = self.db._generate_support_code(test_discord_id, test_token)
        expected_code = f"{test_discord_id}{'x' * 8}".upper()
        
        self.assertEqual(support_code, expected_code, "Code support incorrect")
        
        print(f"✅ Tokens générés: {len(token1)} chars chacun")
        print(f"✅ Code support: {support_code}")

def run_hunt_royal_tests():
    """Lance tous les tests Hunt Royal"""
    print("🏹" + "="*60)
    print("🏹 ARSENAL HUNT ROYAL SYSTEM - TESTS V2.0")
    print("🏹" + "="*60)
    print()
    
    # Configuration du test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestHuntRoyalSystem)
    test_runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
    
    # Lancer les tests avec output custom
    test_cases = [
        'test_database_initialization',
        'test_user_registration', 
        'test_user_profile_retrieval',
        'test_last_active_update',
        'test_attack_calculator',
        'test_defence_calculator',
        'test_calculator_save',
        'test_token_generation'
    ]
    
    results = {}
    test_instance = TestHuntRoyalSystem()
    test_instance.setUp()
    
    try:
        for test_case in test_cases:
            try:
                print(f"🔄 Exécution: {test_case}...")
                test_method = getattr(test_instance, test_case)
                test_method()
                results[test_case] = "✅ PASSED"
                print()
            except Exception as e:
                results[test_case] = f"❌ FAILED: {str(e)}"
                print(f"❌ Erreur: {str(e)}")
                print()
    finally:
        test_instance.tearDown()
    
    # Résumé des résultats
    print("🏹" + "="*60)
    print("📊 RÉSULTATS DES TESTS")
    print("🏹" + "="*60)
    
    passed = sum(1 for result in results.values() if result.startswith("✅"))
    total = len(results)
    
    for test_name, result in results.items():
        print(f"{result} {test_name}")
    
    print()
    print(f"📊 Score: {passed}/{total} tests réussis ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 TOUS LES TESTS SONT PASSÉS !")
        print("✅ Hunt Royal System V2.0 est prêt pour la production !")
        print()
        print("🏹 Fonctionnalités validées:")
        print("   ✅ Base de données et tables")
        print("   ✅ Système d'authentification")
        print("   ✅ Enregistrement utilisateurs")
        print("   ✅ Génération tokens/codes sécurisés") 
        print("   ✅ Calculateur d'attaque (DPS, poison, multishot)")
        print("   ✅ Calculateur de défense (HP, regen, XP)")
        print("   ✅ Sauvegarde builds")
        print("   ✅ Gestion profils utilisateurs")
        print()
        print("🚀 Le système est prêt pour le déploiement !")
    else:
        print(f"⚠️  {total-passed} tests ont échoué")
        print("❌ Corrigez les erreurs avant déploiement")
    
    print("🏹" + "="*60)
    
    return passed == total

if __name__ == "__main__":
    success = run_hunt_royal_tests()
    exit(0 if success else 1)
