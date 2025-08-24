#!/usr/bin/env python3
"""Version minimale pour tester"""

print("🔍 Test minimal...")

# Test 1: Importer seulement les modules de base
from flask import Flask
from flask_socketio import SocketIO

print("✅ Imports de base OK")

# Test 2: Créer l'app
app = Flask(__name__)
print(f"✅ App créée: {type(app)}")

# Test 3: Créer SocketIO
socketio = SocketIO(app)
print(f"✅ SocketIO créé: {type(socketio)}")

# Test 4: Route simple
@app.route('/test')
def test():
    return "Test OK"

print("✅ Route définie")

print("🎉 Test minimal réussi !")
print(f"Variables définies: app={type(app)}, socketio={type(socketio)}")

