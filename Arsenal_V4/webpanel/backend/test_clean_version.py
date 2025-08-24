#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script pour Arsenal V4 WebPanel - Version Propre
Vérifie que tous les endpoints fonctionnent correctement
"""

import requests
import json
import sys
import time

class WebPanelTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.results = []

    def test_endpoint(self, endpoint, method="GET", expected_status=200, description=""):
        """Tester un endpoint spécifique"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url, timeout=10)
            elif method == "POST":
                response = self.session.post(url, timeout=10)
            else:
                response = self.session.request(method, url, timeout=10)
            
            success = response.status_code == expected_status
            result = {
                'endpoint': endpoint,
                'method': method,
                'expected_status': expected_status,
                'actual_status': response.status_code,
                'success': success,
                'description': description,
                'response_size': len(response.content),
                'response_time': response.elapsed.total_seconds()
            }
            
            # Essayer de parser le JSON si possible
            try:
                result['response_json'] = response.json()
            except:
                result['response_text'] = response.text[:200] + "..." if len(response.text) > 200 else response.text
            
            self.results.append(result)
            
            status_icon = "✅" if success else "❌"
            print(f"{status_icon} {method} {endpoint} - {response.status_code} ({response.elapsed.total_seconds():.3f}s)")
            if description:
                print(f"   📝 {description}")
            
            return success, response
            
        except requests.exceptions.RequestException as e:
            result = {
                'endpoint': endpoint,
                'method': method,
                'expected_status': expected_status,
                'actual_status': 'ERROR',
                'success': False,
                'description': description,
                'error': str(e)
            }
            self.results.append(result)
            print(f"❌ {method} {endpoint} - ERROR: {e}")
            return False, None

    def run_tests(self):
        """Exécuter tous les tests"""
        print("🧪 Démarrage des tests Arsenal V4 WebPanel - Version Propre")
        print("=" * 60)
        
        # Tests des pages principales
        print("\n📄 Tests des Pages Principales")
        print("-" * 30)
        self.test_endpoint("/", description="Page d'accueil (login)")
        self.test_endpoint("/dashboard", expected_status=302, description="Dashboard (redirection si non auth)")
        
        # Tests des API publiques
        print("\n🌐 Tests des API Publiques")
        print("-" * 30)
        self.test_endpoint("/api/health", description="API de santé du service")
        
        # Tests des API d'authentification (sans auth)
        print("\n🔐 Tests des API d'Authentification")
        print("-" * 35)
        self.test_endpoint("/api/auth/user", description="Vérification auth (sans session)")
        
        # Tests des API protégées (sans auth - doivent retourner 401)
        print("\n🛡️ Tests des API Protégées (sans auth)")
        print("-" * 40)
        self.test_endpoint("/api/bot/stats", expected_status=401, description="Stats bot (non autorisé)")
        self.test_endpoint("/api/status", expected_status=401, description="Statut général (non autorisé)")
        
        # Tests des routes d'authentification
        print("\n🔑 Tests des Routes d'Authentification")
        print("-" * 40)
        self.test_endpoint("/auth/discord", expected_status=302, description="Redirection Discord OAuth")
        self.test_endpoint("/auth/login", expected_status=302, description="Redirection login")
        
        # Tests des endpoints inexistants (404)
        print("\n🚫 Tests des Endpoints Inexistants")
        print("-" * 35)
        self.test_endpoint("/api/nonexistent", expected_status=404, description="API inexistante")
        self.test_endpoint("/nonexistent", expected_status=404, description="Page inexistante")
        
        # Résumé des tests
        self.print_summary()

    def test_local_server(self):
        """Test spécifique pour serveur local"""
        print("🏠 Test du serveur local")
        print("-" * 25)
        
        # Vérifier si le serveur local répond
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=5)
            if response.status_code == 200:
                print("✅ Serveur local détecté et opérationnel")
                return True
            else:
                print(f"⚠️ Serveur local répond mais status: {response.status_code}")
                return False
        except:
            print("❌ Serveur local non accessible")
            return False

    def print_summary(self):
        """Afficher le résumé des tests"""
        print("\n" + "=" * 60)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 60)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r['success'])
        failed_tests = total_tests - successful_tests
        
        print(f"📈 Total des tests: {total_tests}")
        print(f"✅ Tests réussis: {successful_tests}")
        print(f"❌ Tests échoués: {failed_tests}")
        print(f"📊 Taux de réussite: {(successful_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Tests échoués:")
            for result in self.results:
                if not result['success']:
                    print(f"   • {result['method']} {result['endpoint']} - {result.get('actual_status', 'ERROR')}")
        
        # Recommandations
        print(f"\n💡 RECOMMANDATIONS:")
        if successful_tests == total_tests:
            print("   ✅ Tous les tests sont passés ! Prêt pour le déploiement.")
        elif successful_tests >= total_tests * 0.8:
            print("   ⚠️ La plupart des tests passent. Vérifiez les échecs avant déploiement.")
        else:
            print("   ❌ Plusieurs tests échouent. Vérifiez la configuration avant déploiement.")

def main():
    """Fonction principale"""
    # Déterminer l'URL de test
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5000"
    
    print(f"🎯 URL de test: {base_url}")
    
    # Créer le testeur et exécuter les tests
    tester = WebPanelTester(base_url)
    
    # Test préliminaire pour serveur local
    if "localhost" in base_url or "127.0.0.1" in base_url:
        if not tester.test_local_server():
            print("\n⚠️ Serveur local non accessible. Démarrez l'application avec:")
            print("   python app.py")
            print("\nPuis relancez les tests.")
            return
    
    # Exécuter tous les tests
    tester.run_tests()
    
    # Sauvegarder les résultats
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(tester.results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Résultats sauvegardés dans 'test_results.json'")

if __name__ == "__main__":
    main()

