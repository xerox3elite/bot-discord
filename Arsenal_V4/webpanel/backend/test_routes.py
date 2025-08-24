#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test des routes Flask - Diagnostic
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Définir les variables d'environnement nécessaires pour le test
os.environ['DISCORD_CLIENT_ID'] = '1346646498040877076'
os.environ['DISCORD_CLIENT_SECRET'] = 'test_secret_local'
os.environ['DISCORD_REDIRECT_URI'] = 'http://localhost:5000/auth/callback'

try:
    from app import app
    
    print("🔍 DIAGNOSTIC DES ROUTES FLASK")
    print("=" * 50)
    
    # Lister toutes les routes enregistrées
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'rule': rule.rule,
            'methods': list(rule.methods),
            'endpoint': rule.endpoint
        })
    
    # Trier par URL
    routes.sort(key=lambda x: x['rule'])
    
    print(f"📊 Nombre total de routes: {len(routes)}")
    print()
    
    # Routes problématiques à vérifier
    problematic_routes = [
        '/api/auth/user',
        '/auth/discord',
        '/NSS',
        '/huntroyale/demo',
        '/api/huntroyale/hunters'
    ]
    
    print("🎯 ROUTES PROBLÉMATIQUES:")
    print("-" * 30)
    
    for prob_route in problematic_routes:
        found = False
        for route in routes:
            if route['rule'] == prob_route:
                print(f"✅ {prob_route} -> {route['endpoint']} {route['methods']}")
                found = True
                break
        if not found:
            print(f"❌ {prob_route} -> INTROUVABLE")
    
    print()
    print("📋 TOUTES LES ROUTES:")
    print("-" * 30)
    
    for route in routes:
        if 'GET' in route['methods'] or 'POST' in route['methods']:
            methods_str = ', '.join([m for m in route['methods'] if m not in ['HEAD', 'OPTIONS']])
            print(f"{route['rule']:<40} -> {route['endpoint']:<30} [{methods_str}]")

except Exception as e:
    print(f"❌ ERREUR LORS DU CHARGEMENT DE L'APP: {e}")
    import traceback
    traceback.print_exc()

