"""
🧪 Test de chargement Arsenal - Vérification complète
Vérifie que tous les modules Arsenal se chargent correctement
Auteur: Arsenal Studio
"""

import asyncio
import sys
import os

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_arsenal_loading():
    """Test de chargement complet des modules Arsenal"""
    
    print("🧪 === TEST DE CHARGEMENT ARSENAL ===")
    print()
    
    modules_to_test = [
        # Modules prioritaires
        ("Arsenal Registration System", "commands.arsenal_registration_system", "ArsenalRegistrationSystem"),
        ("Arsenal Protection Middleware", "commands.arsenal_protection_middleware", "ArsenalProtectionSystem"),
        ("Arsenal Utilities Basic", "commands.arsenal_utilities_basic", "ArsenalUtilitiesBasic"),
        
        # Modules essentiels
        ("Arsenal Economy Unified", "commands.arsenal_economy_unified", "ArsenalEconomyUnified"),
        ("Arsenal Profile Ultimate 2000", "commands.arsenal_profile_ultimate_2000", "ArsenalProfileUltimate2000"),
        ("Config Revolution", "commands.config_revolution", "ArsenalConfigRevolution"),
        
        # Modules avancés
        ("Arsenal Features", "commands.arsenal_features", "ArsenalBotFeatures"),
        ("Arsenal Bug Reporter", "commands.arsenal_bug_reporter", "ArsenalBugReporter"),
        ("Hunt Royal System", "commands.hunt_royal_system", "HuntRoyalSystem"),
        ("Advanced Ticket System", "commands.advanced_ticket_system", "AdvancedTicketSystem"),
        
        # Modules spécialisés
        ("Gaming API System", "commands.gaming_api_system", "GamingAPISystem"),
        ("Music Enhanced System", "commands.music_enhanced_system", "MusicEnhancedSystem"),
        ("Social Fun System", "commands.social_fun_system", "SocialFunSystem"),
        ("Server Management System", "commands.server_management_system", "ServerManagementSystem"),
        ("Sanctions System", "commands.sanctions_system", "SanctionsSystem"),
    ]
    
    success_count = 0
    failed_modules = []
    
    for name, module_path, class_name in modules_to_test:
        try:
            # Test d'importation du module
            module = __import__(module_path, fromlist=[class_name])
            
            # Test d'accès à la classe
            cls = getattr(module, class_name)
            
            print(f"✅ {name:<35} - OK")
            success_count += 1
            
        except ImportError as e:
            print(f"❌ {name:<35} - IMPORT ERROR: {e}")
            failed_modules.append((name, "ImportError", str(e)))
            
        except AttributeError as e:
            print(f"❌ {name:<35} - CLASS ERROR: {e}")
            failed_modules.append((name, "AttributeError", str(e)))
            
        except Exception as e:
            print(f"❌ {name:<35} - OTHER ERROR: {e}")
            failed_modules.append((name, "Exception", str(e)))
    
    print()
    print("📊 === RÉSULTATS DU TEST ===")
    print(f"✅ Modules réussis: {success_count}/{len(modules_to_test)}")
    print(f"❌ Modules échoués: {len(failed_modules)}/{len(modules_to_test)}")
    print(f"📈 Taux de réussite: {(success_count/len(modules_to_test)*100):.1f}%")
    
    if failed_modules:
        print()
        print("🔍 === DÉTAILS DES ERREURS ===")
        for name, error_type, error_msg in failed_modules:
            print(f"❌ {name}:")
            print(f"   Type: {error_type}")
            print(f"   Message: {error_msg}")
            print()
    
    # Test spécifique du système de protection
    print("🛡️ === TEST PROTECTION MIDDLEWARE ===")
    try:
        from commands.arsenal_protection_middleware import require_registration
        print("✅ Décorateur require_registration importé")
        
        # Test de création d'une fonction protégée
        @require_registration(level="basic")
        async def test_function():
            return "test"
        
        print("✅ Décorateur appliqué avec succès")
        
    except Exception as e:
        print(f"❌ Erreur protection middleware: {e}")
    
    # Test du système d'enregistrement
    print()
    print("🔥 === TEST REGISTRATION SYSTEM ===")
    try:
        from commands.arsenal_registration_system import ArsenalUserDatabase
        db = ArsenalUserDatabase()
        print("✅ Base de données Arsenal initialisable")
        
    except Exception as e:
        print(f"❌ Erreur registration system: {e}")
    
    print()
    if success_count == len(modules_to_test):
        print("🎉 TOUS LES MODULES SE CHARGENT CORRECTEMENT !")
        print("🚀 Arsenal est prêt pour le déploiement !")
    else:
        print("⚠️ Certains modules ont des problèmes de chargement.")
        print("🔧 Vérifiez les erreurs ci-dessus et corrigez les imports.")
    
    return success_count, len(modules_to_test), failed_modules

if __name__ == "__main__":
    asyncio.run(test_arsenal_loading())
