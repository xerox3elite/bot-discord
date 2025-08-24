import asyncio
import sys
import os
from core.logger import log

async def start_terminal(client):
    """Terminal désactivé en production pour éviter EOFError"""
    # Toujours désactiver en production
    log.info("[TERMINAL] Terminal désactivé - Mode production")
    return

