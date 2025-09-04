# -*- coding: utf-8 -*-
"""
SCRIPT DE CORRECTION DU COMPTEUR SL
===================================
Utilise ce script pour diagnostiquer et corriger le compteur de SL bugué
"""

import sys
import os

# Ajouter le chemin du dossier parent pour importer le bot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ultra_scalping_bot import UltraScalpingBot

def main():
    print("🔧 SCRIPT DE CORRECTION DU COMPTEUR SL")
    print("="*50)
    
    try:
        # Initialisation du bot
        bot = UltraScalpingBot('YOLO')
        
        print("\n1️⃣ DIAGNOSTIC AVANT CORRECTION:")
        bot.debug_sl_detection()
        
        print("\n2️⃣ RESET FORCÉ DU COMPTEUR:")
        bot.force_reset_sl_counter()
        
        print("\n3️⃣ DIAGNOSTIC APRÈS CORRECTION:")
        bot.debug_sl_detection()
        
        print("\n✅ CORRECTION TERMINÉE!")
        print("Le compteur SL devrait maintenant afficher 0/10")
        print("Relancez votre bot principal.")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        print(f"📋 Détails: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
