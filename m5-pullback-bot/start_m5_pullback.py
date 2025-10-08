#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de lancement du bot M5 Pullback en mode ARGENT RÉEL
==========================================================

🚨 ATTENTION: Lance le bot avec de l'ARGENT RÉEL !
Risque de pertes financières importantes.

🎯 Stratégie: M5 Pullback sur Tendance
- EMA 200 + EMA 50 + RSI + ATR
- TP/SL adaptatifs selon volatilité
- Ratio Risque/Rendement 1:2
"""

import sys
import os

# Ajout du répertoire actuel au path pour l'import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import des modules nécessaires
import MetaTrader5 as mt5
from m5_pullback_bot import M5PullbackBot

def main():
    """Fonction principale de lancement"""
    
    print("🚨 ULTRA SCALPING BOT - MODE ARGENT RÉEL 🚨")
    print("=" * 50)
    print("⚠️ Ce bot utilise de l'ARGENT RÉEL pour trader")
    print("📉 Risque de pertes financières importantes")
    print("🛡️ Sécurités: Seuil -5%, Max 5 positions, Fréquence adaptative")
    print()
    
    try:
        # Création et lancement du bot
        bot = M5PullbackBot(config_name='BALANCED')
        
        print("Appuyez sur Ctrl+C pour arreter le bot")
        print("-" * 50)
        
        # Lancement du bot
        bot.start_trading_loop()
        
    except KeyboardInterrupt:
        print("\n⏸️ Arret du bot demande par l'utilisateur")
        print("💰 Vérifiez vos positions ouvertes sur MT5")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        print(f"Details: {traceback.format_exc()}")
    finally:
        # Nettoyage MT5
        if mt5.terminal_info():
            mt5.shutdown()
        print("🛑 Bot arrete")

if __name__ == "__main__":
    main()
