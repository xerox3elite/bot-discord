"""
🧪 Test du Système Arsenal Economy
Script de test pour vérifier le bon fonctionnement du système d'économie
"""

import json
import os

def test_economy_files():
    """Test la création et lecture des fichiers d'économie"""
    print("🧪 Test des Fichiers d'Économie")
    print("=" * 40)
    
    # Vérifier les fichiers existants
    files_to_check = [
        "data/economie.json",
        "data/users_economy.json"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} existe")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"   📊 Contient {len(data)} entrées")
                    if data:
                        # Afficher le premier utilisateur comme exemple
                        first_user = list(data.keys())[0]
                        balance = data[first_user].get('balance', 0)
                        print(f"   👤 Premier utilisateur: {balance:,} AC")
            except Exception as e:
                print(f"   ❌ Erreur lecture: {e}")
        else:
            print(f"❌ {file_path} n'existe pas")
    
    print()

def test_shop_config():
    """Test la configuration du shop"""
    print("🏪 Test Configuration Shop")
    print("=" * 40)
    
    shop_file = "data/shop_config.json"
    
    if os.path.exists(shop_file):
        print(f"✅ {shop_file} existe")
        try:
            with open(shop_file, 'r', encoding='utf-8') as f:
                shop_data = json.load(f)
                
            servers = shop_data.get("servers", {})
            global_items = shop_data.get("global_items", {})
            
            print(f"   🌍 Articles globaux: {len(global_items)}")
            print(f"   🏢 Serveurs configurés: {len(servers)}")
            
            # Afficher quelques articles globaux
            if global_items:
                print("   🌟 Articles Arsenal Premium:")
                for item_id, item_data in list(global_items.items())[:3]:
                    print(f"      • {item_data['name']} - {item_data['price']:,} AC")
                
        except Exception as e:
            print(f"   ❌ Erreur lecture: {e}")
    else:
        print(f"❌ {shop_file} n'existe pas")
    
    print()

def create_test_data():
    """Crée des données de test"""
    print("🔧 Création Données de Test")
    print("=" * 40)
    
    # Données d'économie de test
    test_economy = {
        "431359112039890945": {  # Creator ID
            "balance": 999999,
            "history": [
                {
                    "type": "Récompense Quotidienne",
                    "amount": 1000,
                    "old_balance": 998999,
                    "new_balance": 999999,
                    "date": "2025-08-14 14:30:00"
                }
            ],
            "daily_streak": 5,
            "last_daily": "2025-08-14"
        },
        "123456789012345678": {  # Utilisateur test
            "balance": 50000,
            "history": [
                {
                    "type": "Achat: Statut Premium",
                    "amount": -25000,
                    "old_balance": 75000,
                    "new_balance": 50000,
                    "date": "2025-08-14 12:15:00"
                }
            ],
            "daily_streak": 2,
            "last_daily": "2025-08-13"
        }
    }
    
    # Sauvegarder les données de test
    os.makedirs("data", exist_ok=True)
    
    with open("data/economie.json", 'w', encoding='utf-8') as f:
        json.dump(test_economy, f, ensure_ascii=False, indent=2)
    
    print("✅ Données d'économie de test créées")
    
    # Configuration shop de test
    test_shop = {
        "servers": {
            "123456789012345678": {  # Serveur test
                "items": {
                    "custom_role": {
                        "name": "🎨 Rôle Personnalisé",
                        "description": "Créez votre propre rôle avec couleur",
                        "price": 10000,
                        "type": "custom",
                        "created_by": "431359112039890945",
                        "created_at": "2025-08-14T14:30:00"
                    },
                    "server_boost": {
                        "name": "🚀 Boost Serveur",
                        "description": "Boost gratuit pour le serveur pendant 1 mois",
                        "price": 75000,
                        "type": "boost",
                        "created_by": "431359112039890945",
                        "created_at": "2025-08-14T14:30:00"
                    }
                }
            }
        },
        "global_items": {
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
    }
    
    with open("data/shop_config.json", 'w', encoding='utf-8') as f:
        json.dump(test_shop, f, ensure_ascii=False, indent=2)
    
    print("✅ Configuration shop de test créée")
    print()

def show_commands_list():
    """Affiche la liste des nouvelles commandes"""
    print("📋 Nouvelles Commandes Arsenal Economy")
    print("=" * 50)
    
    commands = [
        ("💰 /balance", "Affiche le solde ArsenalCoin"),
        ("🎁 /daily", "Récompense quotidienne"),
        ("🏪 /shop", "Ouvre la boutique Arsenal"),
        ("💳 /buy <item>", "Achète un article"),
        ("🏆 /leaderboard", "Classement des plus riches"),
        ("🛠️ /shop_admin", "Administration boutique (Admin)")
    ]
    
    for cmd, desc in commands:
        print(f"{cmd:<20} - {desc}")
    
    print("\n🎮 Exemples d'utilisation:")
    print("• /balance @utilisateur     - Voir le solde d'un autre")
    print("• /buy premium_status       - Acheter le statut premium") 
    print("• /shop_admin action:add item_id:mon_item name:\"Mon Article\" price:5000")
    print()

if __name__ == "__main__":
    print("🏪 Arsenal Economy System - Tests")
    print("=" * 50)
    print()
    
    # Tester les fichiers existants
    test_economy_files()
    test_shop_config()
    
    # Créer des données de test
    response = input("Voulez-vous créer des données de test ? (y/N): ")
    if response.lower() in ['y', 'yes', 'oui']:
        create_test_data()
    
    # Afficher les commandes
    show_commands_list()
    
    print("✅ Tests terminés !")
    print("🚀 Le système Arsenal Economy est prêt à être utilisé !")
