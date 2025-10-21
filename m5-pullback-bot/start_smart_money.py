"""
Script de démarrage pour le Smart Money Bot
"""

import sys
import os

# Ajouter le chemin du bot au PYTHONPATH
sys.path.insert(0, os.path.dirname(__file__))

from smart_money_bot import SmartMoneyBot

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 SMART MONEY BOT - ICT/SMC Concepts")
    print("="*60)
    print("\nFonctionnalités:")
    print("  📊 Structure de marché (Swing Highs/Lows)")
    print("  🔥 Break of Structure (BOS)")
    print("  🎯 Fair Value Gaps (FVG)")
    print("  📦 Order Blocks (OB)")
    print("  ⏰ Multi-timeframe (H1 + M5)")
    print("\n" + "="*60 + "\n")
    
    bot = SmartMoneyBot()
    bot.run()
