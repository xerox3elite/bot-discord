#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test de configuration Arsenal V4 WebPanel
"""

import os
import sys

print("🔍 DIAGNOSTIC ARSENAL V4 WEBPANEL")
print("=" * 50)

# 1. Vérifier la structure des fichiers
print("📁 Structure des fichiers:")
webpanel_path = os.path.dirname(__file__)
required_files = [
    "backend/advanced_server.py",
    "frontend/index.html", 
    "login.html",
    "requirements.txt"
]

for file in required_files:
    file_path = os.path.join(webpanel_path, file)
    status = "✅ OK" if os.path.exists(file_path) else "❌ MANQUANT"
    print(f"   {file}: {status}")

print()

# 2. Vérifier les variables d'environnement
print("🔐 Variables d'environnement:")
env_vars = [
    "DISCORD_CLIENT_ID",
    "DISCORD_CLIENT_SECRET", 
    "DISCORD_REDIRECT_URI"
]

for var in env_vars:
    value = os.environ.get(var, "NON_DEFINI")
    if var == "DISCORD_CLIENT_SECRET" and value != "NON_DEFINI":
        value = "Défini (masqué)"
    print(f"   {var}: {value}")

print()

# 3. Test d'import des modules
print("📦 Modules Python:")
modules_to_test = [
    "flask",
    "flask_cors", 
    "requests",
    "sqlite3"
]

for module in modules_to_test:
    try:
        __import__(module)
        print(f"   {module}: ✅ OK")
    except ImportError:
        print(f"   {module}: ❌ MANQUANT")

print()

# 4. Vérifier la base de données
print("💾 Base de données:")
db_path = os.path.join(webpanel_path, "arsenal_v4.db")
db_status = "✅ OK" if os.path.exists(db_path) else "⚠️ Sera créée au démarrage"
print(f"   arsenal_v4.db: {db_status}")

print()

# 5. Configuration recommandée pour Render
print("🚀 Configuration Render recommandée:")
print("   Build Command: pip install -r requirements.txt")
print("   Start Command: cd backend && gunicorn --bind 0.0.0.0:$PORT advanced_server:app --workers 1 --timeout 120")
print("   Root Directory: Arsenal_bot/Arsenal_V4/webpanel")

print()

# 6. URLs de test après déploiement
app_name = input("🌐 Nom de ton app Render (optionnel): ").strip()
if app_name:
    print(f"🔗 URLs de test:")
    print(f"   https://{app_name}.onrender.com/")
    print(f"   https://{app_name}.onrender.com/login")
    print(f"   https://{app_name}.onrender.com/debug")
    print(f"   https://{app_name}.onrender.com/auth/login")

print()
print("✅ Diagnostic terminé !")
print("💡 Utilise /debug après déploiement pour plus d'infos")

