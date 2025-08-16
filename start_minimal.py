#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ARSENAL BOT START - Version minimaliste ultra-stable
Script de démarrage simple sans fonctionnalités complexes
"""

import os
import sys
import asyncio
import discord
from discord.ext import commands

# Setup minimal
os.environ['PYTHONUNBUFFERED'] = '1'

def main():
    """Démarrage minimal du bot"""
    print("🚀 [MINIMAL] Démarrage Arsenal Bot - Mode Minimal Stable")
    
    # Import seulement du nécessaire
    try:
        from main import client
        print("✅ [MINIMAL] Bot client importé")
        
        # Démarrage
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            print("❌ [MINIMAL] Token Discord non trouvé!")
            return 1
            
        print("🔑 [MINIMAL] Token trouvé, connexion...")
        client.run(token)
        
    except KeyboardInterrupt:
        print("🛑 [MINIMAL] Arrêt manuel du bot")
        return 0
    except Exception as e:
        print(f"❌ [MINIMAL] Erreur critique: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
