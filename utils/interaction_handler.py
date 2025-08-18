#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🛡️ Arsenal Interaction Handler - Gestion Anti-Timeout
Système de protection contre les timeouts Discord
"""

import discord
import asyncio
import logging
from functools import wraps
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)

class InteractionTimeoutHandler:
    """Gestionnaire des timeouts d'interaction Discord"""
    
    @staticmethod
    async def safe_respond(interaction: discord.Interaction, content: Optional[str] = None, embed: Optional[discord.Embed] = None, ephemeral: bool = True):
        """
        Réponse sécurisée qui gère les timeouts automatiquement
        """
        try:
            # Vérifier si l'interaction n'est pas déjà expirée
            if interaction.response.is_done():
                # Interaction déjà répondue, utiliser followup
                return await interaction.followup.send(content=content, embed=embed, ephemeral=ephemeral)
            else:
                # Première réponse
                return await interaction.response.send_message(content=content, embed=embed, ephemeral=ephemeral)
                
        except discord.errors.NotFound:
            # Interaction expirée (404 Unknown interaction)
            logger.warning(f"Interaction expirée pour {interaction.user.display_name} ({interaction.command.name if interaction.command else 'Unknown'})")
            return None
            
        except discord.errors.InteractionResponded:
            # Interaction déjà répondue, utiliser edit
            try:
                return await interaction.edit_original_response(content=content, embed=embed)
            except Exception as e:
                logger.error(f"Erreur edit_original_response: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur dans safe_respond: {e}")
            return None
    
    @staticmethod  
    async def safe_edit(interaction: discord.Interaction, content: Optional[str] = None, embed: Optional[discord.Embed] = None):
        """
        Édition sécurisée de la réponse originale
        """
        try:
            return await interaction.edit_original_response(content=content, embed=embed)
        except discord.errors.NotFound:
            logger.warning(f"Impossible d'éditer - Interaction expirée pour {interaction.user.display_name}")
            return None
        except Exception as e:
            logger.error(f"Erreur dans safe_edit: {e}")
            return None

def timeout_protection(loading_message: str = "⏳ Traitement en cours..."):
    """
    Décorateur pour protéger les commandes contre les timeouts
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Identifier l'objet interaction dans les arguments
            interaction = None
            for arg in args:
                if isinstance(arg, discord.Interaction):
                    interaction = arg
                    break
            
            if not interaction:
                # Pas d'interaction trouvée, exécuter normalement
                return await func(*args, **kwargs)
            
            # Réponse immédiate pour éviter le timeout
            handler = InteractionTimeoutHandler()
            response = await handler.safe_respond(interaction, content=loading_message, ephemeral=True)
            
            if response is None:
                # Interaction déjà expirée, impossible de continuer
                logger.error(f"Interaction expirée avant même la réponse initiale - Commande: {interaction.command.name if interaction.command else 'Unknown'}")
                return None
            
            try:
                # Exécuter la fonction originale (sans la réponse initiale)
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                # Erreur dans l'exécution, envoyer un message d'erreur
                await handler.safe_edit(interaction, content=f"❌ Erreur lors de l'exécution: {str(e)[:100]}...")
                logger.error(f"Erreur dans commande protégée {interaction.command.name if interaction.command else 'Unknown'}: {e}")
                return None
                
        return wrapper
    return decorator

# Alias pour facilité d'utilisation
safe_interaction = timeout_protection
