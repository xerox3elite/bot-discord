#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test des routes API Arsenal V4 WebPanel
Ce script teste toutes les routes API pour identifier les erreurs 404/502
"""

import requests
import json
from colorama import init, Fore, Style
import time

# Initialiser colorama pour les couleurs dans le terminal
init()

# Configuration
BASE_URL = "http://localhost:5000"
TIMEOUT = 10

def print_colored(message, color=Fore.WHITE):
    """Affiche un message en couleur"""
    print(f"{color}{message}{Style.RESET_ALL}")

def test_endpoint(endpoint, method='GET', data=None):
    """Test un endpoint API"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        print_colored(f"\n🔄 Testing {method} {endpoint}...", Fore.CYAN)
        
        if method == 'GET':
            response = requests.get(url, timeout=TIMEOUT)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=TIMEOUT)
        else:
            print_colored(f"❌ Méthode {method} non supportée", Fore.RED)
            return False
        
        # Affichage du résultat
        status_color = Fore.GREEN if response.status_code < 400 else Fore.RED
        print_colored(f"Status: {response.status_code} {response.reason}", status_color)
        
        # Affichage du contenu si c'est du JSON
        try:
            content = response.json()
            print(json.dumps(content, indent=2, ensure_ascii=False))
        except:
            print(f"Response (text): {response.text[:200]}...")
        
        return response.status_code < 400
        
    except requests.exceptions.ConnectionError:
        print_colored("❌ Erreur de connexion - Le serveur n'est pas démarré", Fore.RED)
        return False
    except requests.exceptions.Timeout:
        print_colored("⏰ Timeout - Le serveur met trop de temps à répondre", Fore.YELLOW)
        return False
    except Exception as e:
        print_colored(f"❌ Erreur: {str(e)}", Fore.RED)
        return False

def main():
    """Fonction principale de test"""
    print_colored("🧪 TEST DES ROUTES API - ARSENAL V4 WEBPANEL", Fore.MAGENTA)
    print_colored("=" * 60, Fore.MAGENTA)
    
    # Routes à tester
    routes = [
        # Routes de base
        ("/api/test", "GET"),
        ("/api/info", "GET"),
        ("/api/health", "GET"),
        ("/api/status", "GET"),
        ("/api/version", "GET"),
        
        # Routes utilisateur (nécessitent authentification)
        ("/api/user/info", "GET"),
        ("/api/user/profile", "GET"),
        ("/api/user/settings", "GET"),
        ("/api/user/activity", "GET"),
        ("/api/user/security", "GET"),
        ("/api/user/dashboard", "GET"),
        ("/api/user/permissions", "GET"),
        
        # Routes statistiques
        ("/api/stats", "GET"),
        ("/api/stats/dashboard", "GET"),
        ("/api/stats/general", "GET"),
        ("/api/stats/real", "GET"),
        
        # Routes bot
        ("/api/bot/status", "GET"),
        ("/api/bot/performance", "GET"),
        ("/api/bot/detailed", "GET"),
        
        # Routes serveurs
        ("/api/servers/list", "GET"),
        ("/api/servers/detailed", "GET"),
        ("/api/servers/123/config", "GET"),
        
        # Routes activité
        ("/api/activity/feed", "GET"),
        ("/api/activity/recent", "GET"),
        
        # Routes économie
        ("/api/economy/overview", "GET"),
        ("/api/economy/servers", "GET"),
        
        # Routes musique
        ("/api/music/status", "GET"),
        ("/api/music/queue", "GET"),
        
        # Routes administration
        ("/api/guilds", "GET"),
        ("/api/channels", "GET"),
        ("/api/performance", "GET"),
        
        # Tests d'endpoints inexistants (doivent retourner 501 avec la route fallback)
        ("/api/nonexistent", "GET"),
        ("/api/fake/route", "GET"),
        ("/api/missing/endpoint", "GET"),
    ]
    
    # Variables de comptage
    total_tests = len(routes)
    success_count = 0
    failed_count = 0
    
    # Test de connexion au serveur
    print_colored("\n🔌 Vérification de la connexion au serveur...", Fore.YELLOW)
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print_colored("✅ Serveur accessible", Fore.GREEN)
    except:
        print_colored("❌ Serveur non accessible - Démarrez le serveur Flask d'abord", Fore.RED)
        print_colored("Commande: python app.py", Fore.CYAN)
        return
    
    # Test de chaque route
    for endpoint, method in routes:
        success = test_endpoint(endpoint, method)
        if success:
            success_count += 1
        else:
            failed_count += 1
        
        time.sleep(0.5)  # Pause entre les tests
    
    # Résumé
    print_colored("\n" + "=" * 60, Fore.MAGENTA)
    print_colored("📊 RÉSUMÉ DES TESTS", Fore.MAGENTA)
    print_colored(f"Total: {total_tests}", Fore.WHITE)
    print_colored(f"Succès: {success_count}", Fore.GREEN)
    print_colored(f"Échecs: {failed_count}", Fore.RED)
    print_colored(f"Taux de réussite: {(success_count/total_tests)*100:.1f}%", Fore.CYAN)
    
    if failed_count == 0:
        print_colored("\n🎉 Tous les tests sont passés ! Les erreurs 404/502 semblent être résolues.", Fore.GREEN)
    else:
        print_colored(f"\n⚠️  {failed_count} tests ont échoué. Vérifiez les routes défaillantes.", Fore.YELLOW)

if __name__ == "__main__":
    main()

