#!/usr/bin/env python3
"""Test d'import spécifique"""

print("🔍 Test d'import spécifique...")

# Test import avec inspection du namespace
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("app_module", "app.py")
app_module = importlib.util.module_from_spec(spec)

print("📋 Avant l'exécution du module...")

try:
    spec.loader.exec_module(app_module)
    print("✅ Module exécuté avec succès")
    
    print("📋 Variables dans le module:")
    for name in dir(app_module):
        if not name.startswith('_'):
            obj = getattr(app_module, name)
            print(f"  - {name}: {type(obj)}")
    
    if hasattr(app_module, 'app'):
        print(f"✅ app trouvé: {type(app_module.app)}")
    else:
        print("❌ app non trouvé")
        
    if hasattr(app_module, 'socketio'):
        print(f"✅ socketio trouvé: {type(app_module.socketio)}")
    else:
        print("❌ socketio non trouvé")
        
except Exception as e:
    print(f"❌ Erreur lors de l'exécution: {e}")
    import traceback
    traceback.print_exc()

