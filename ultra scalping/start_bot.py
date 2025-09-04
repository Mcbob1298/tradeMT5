#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de lancement du bot ultra scalping avec reset automatique
================================================================

Usage:
- python start_bot.py         # Lancement normal
- python start_bot.py --reset # Lancement avec reset forcé de la balance
"""

import sys
import os

# Ajout du répertoire actuel au path pour l'import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import des modules nécessaires
import MetaTrader5 as mt5
import io
from ultra_scalping_bot import UltraScalpingBot, safe_log

def main():
    """Fonction principale de lancement"""
    
    # Vérification des arguments
    force_reset = '--reset' in sys.argv
    
    if force_reset:
        safe_log("🔄 Lancement avec RESET FORCÉ de la balance de référence")
    else:
        safe_log("🚀 Lancement normal du bot ultra scalping")
    
    try:
        # Création et lancement du bot avec option de reset
        bot = UltraScalpingBot(
            config_name='YOLO',
            force_daily_reset=force_reset
        )
        
        # Lancement du bot
        bot.start_ultra_scalping()
        
    except KeyboardInterrupt:
        safe_log("⏹️ Arrêt du bot demandé par l'utilisateur")
    except Exception as e:
        safe_log(f"❌ Erreur fatale: {e}")
        import traceback
        safe_log(f"📋 Traceback: {traceback.format_exc()}")
    finally:
        # Nettoyage MT5
        mt5.shutdown()
        safe_log("👋 MT5 fermé - Bot arrêté")

if __name__ == "__main__":
    main()
