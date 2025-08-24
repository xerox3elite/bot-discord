#!/usr/bin/env python3
"""Test progressif des imports"""

print("🔍 Test progressif des imports...")

try:
    print("1. Test import Flask...")
    from flask import Flask, request, jsonify, session, send_from_directory, redirect
    print("✅ Flask importé")
    
    print("2. Test import Flask-CORS...")
    from flask_cors import CORS
    print("✅ Flask-CORS importé")
    
    print("3. Test import Flask-SocketIO...")
    from flask_socketio import SocketIO, emit, join_room
    print("✅ Flask-SocketIO importé")
    
    print("4. Test imports standards...")
    import os, sys, json, sqlite3, threading, time, random
    print("✅ Imports standards OK")
    
    print("5. Test import psutil...")
    import psutil
    print("✅ psutil importé")
    
    print("6. Test import requests...")
    import requests
    print("✅ requests importé")
    
    print("7. Test imports secrets et urllib...")
    import secrets, urllib.parse
    print("✅ secrets et urllib importés")
    
    print("8. Test import datetime...")
    from datetime import datetime, timedelta
    print("✅ datetime importé")
    
    print("9. Création de l'app Flask...")
    app = Flask(__name__)
    print(f"✅ App Flask créée: {type(app)}")
    
    print("10. Configuration CORS...")
    CORS(app, supports_credentials=True)
    print("✅ CORS configuré")
    
    print("11. Configuration SocketIO...")
    socketio = SocketIO(app, cors_allowed_origins="*")
    print(f"✅ SocketIO configuré: {type(socketio)}")
    
    print("🎉 Tous les imports et configurations réussis !")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

