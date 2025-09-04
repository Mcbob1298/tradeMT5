# -*- coding: utf-8 -*-
"""
Script de correction de la balance de référence
===============================================
Corrige le problème de balance de référence incorrecte
"""

import MetaTrader5 as mt5
from datetime import datetime
import sys
import io

# Configuration UTF-8 pour Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configuration MT5
MT5_LOGIN = 5039554492
MT5_PASSWORD = "L-V3AbDk"    
MT5_SERVER = "MetaQuotes-Demo"

def safe_log(message):
    """Log avec timestamp"""
    try:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {message}", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"[LOG ERROR] {e}", flush=True)

def connect_mt5():
    """Connexion à MT5"""
    if not mt5.initialize():
        safe_log("❌ Échec initialisation MT5")
        return False
    
    if not mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
        safe_log(f"❌ Échec connexion compte {MT5_LOGIN}")
        safe_log(f"Erreur: {mt5.last_error()}")
        mt5.shutdown()
        return False
    
    safe_log("✅ MT5 connecté")
    return True

def show_current_balance_info():
    """Affiche les informations actuelles de balance"""
    safe_log("📊 INFORMATIONS BALANCE ACTUELLES:")
    
    account_info = mt5.account_info()
    if account_info:
        safe_log(f"   💰 Balance actuelle: {account_info.balance:.2f}€")
        safe_log(f"   📊 Équité: {account_info.equity:.2f}€")
        safe_log(f"   📈 Profit flottant: {account_info.equity - account_info.balance:.2f}€")
        safe_log(f"   📉 Marge utilisée: {account_info.margin:.2f}€")
        safe_log(f"   💡 Marge libre: {account_info.margin_free:.2f}€")
        
        # Calcul suggéré pour corriger
        suggested_reference = account_info.balance
        safe_log(f"")
        safe_log(f"💡 SUGGESTION DE CORRECTION:")
        safe_log(f"   🎯 Nouvelle balance de référence: {suggested_reference:.2f}€")
        safe_log(f"   🛡️ Nouveau seuil -5%: {suggested_reference * 0.05:.2f}€")
        safe_log(f"   📉 Balance critique: {suggested_reference * 0.95:.2f}€")
        
        return suggested_reference
    else:
        safe_log("❌ Impossible de récupérer les infos balance")
        return None

def main():
    safe_log("🔧 SCRIPT DE CORRECTION BALANCE DE RÉFÉRENCE")
    safe_log("=" * 50)
    
    if not connect_mt5():
        return
    
    try:
        # Affichage des infos actuelles
        suggested_reference = show_current_balance_info()
        
        if suggested_reference:
            safe_log("")
            safe_log("🎯 PROCHAINES ÉTAPES:")
            safe_log("   1️⃣ Arrêter le bot si il tourne")
            safe_log("   2️⃣ Redémarrer le bot (il prendra automatiquement la nouvelle balance)")
            safe_log("   3️⃣ OU utiliser la fonction force_daily_reset_now() dans le bot")
            safe_log("")
            safe_log("💡 Le système se remettra automatiquement à zéro chaque jour maintenant")
        
    except Exception as e:
        safe_log(f"❌ Erreur: {e}")
    
    finally:
        mt5.shutdown()
        safe_log("✅ Script terminé")

if __name__ == "__main__":
    main()
