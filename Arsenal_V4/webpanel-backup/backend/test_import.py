#!/usr/bin/env python3
"""Test script pour diagnostiquer le problème d'import"""

print("🔍 Test d'import du module app.py...")

try:
    print("1. Tentative d'import du module...")
    import app
    print("✅ Module app importé avec succès")
    
    print("2. Vérification de la variable 'app'...")
    if hasattr(app, 'app'):
        print(f"✅ Variable 'app' trouvée: {type(app.app)}")
    else:
        print("❌ Variable 'app' NOT FOUND")
        print("Variables disponibles dans le module:")
        for attr in dir(app):
            if not attr.startswith('_'):
                print(f"  - {attr}: {type(getattr(app, attr))}")
    
    print("3. Vérification de la variable 'socketio'...")
    if hasattr(app, 'socketio'):
        print(f"✅ Variable 'socketio' trouvée: {type(app.socketio)}")
    else:
        print("❌ Variable 'socketio' NOT FOUND")

except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
except Exception as e:
    print(f"❌ Erreur inattendue: {e}")
    import traceback
    traceback.print_exc()

