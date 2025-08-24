#!/usr/bin/env python3
"""Test rapide pour vérifier que le frontend se charge correctement"""

import os
import sys

# Définir les variables d'environnement pour le test
os.environ['DISCORD_CLIENT_ID'] = 'test'
os.environ['DISCORD_CLIENT_SECRET'] = 'test'
os.environ['DISCORD_REDIRECT_URI'] = 'test'

try:
    from app import app
    print("✅ Backend chargé avec succès")
    
    # Tester l'accès au frontend
    with app.test_client() as client:
        response = client.get('/')
        print(f"📊 Status code: {response.status_code}")
        print(f"📄 Content type: {response.content_type}")
        print(f"📏 Taille réponse: {len(response.data)} bytes")
        print(f"🔍 Contient 'Arsenal V4': {'Arsenal V4' in response.data.decode('utf-8', errors='ignore')}")
        
        if response.status_code == 200:
            print("✅ Frontend accessible et fonctionnel")
        else:
            print("❌ Problème d'accès au frontend")
            
        # Tester les routes d'authentification  
        auth_response = client.get('/api/auth/user')
        print(f"🔐 Route /api/auth/user: {auth_response.status_code}")
        
        discord_response = client.get('/auth/discord')
        print(f"🔐 Route /auth/discord: {discord_response.status_code}")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    print(f"📍 Type d'erreur: {type(e).__name__}")

