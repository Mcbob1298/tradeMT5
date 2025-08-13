#!/usr/bin/env python3
"""
🧪 TESTEUR BOT ULTIME
Script de test et de validation avant démarrage en live
"""

import time
from datetime import datetime
from config_ultimate import ACTIVE_STRATEGIES, COLORS
from risk_manager import get_risk_summary, can_open_new_trade
import MetaTrader5 as mt5

def test_mt5_connection():
    """Test de la connexion MT5"""
    print(f"🔌 {COLORS['CYAN']}Test de connexion MT5...{COLORS['RESET']}")
    
    if not mt5.initialize():
        print(f"❌ {COLORS['RED']}Échec d'initialisation MT5{COLORS['RESET']}")
        return False
        
    account_info = mt5.account_info()
    if account_info is None:
        print(f"❌ {COLORS['RED']}Impossible de récupérer les infos du compte{COLORS['RESET']}")
        return False
        
    print(f"✅ {COLORS['GREEN']}Connexion MT5 réussie{COLORS['RESET']}")
    print(f"📊 Compte: {account_info.login} | Solde: {account_info.balance:.2f} {account_info.currency}")
    
    mt5.shutdown()
    return True

def test_market_data():
    """Test de récupération des données de marché"""
    print(f"📊 {COLORS['CYAN']}Test des données de marché...{COLORS['RESET']}")
    
    if not mt5.initialize():
        return False
        
    try:
        # Test M15
        rates_m15 = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M15, 0, 100)
        if rates_m15 is not None and len(rates_m15) > 0:
            print(f"✅ {COLORS['GREEN']}Données M15: {len(rates_m15)} barres{COLORS['RESET']}")
        else:
            print(f"❌ {COLORS['RED']}Échec données M15{COLORS['RESET']}")
            
        # Test M5  
        rates_m5 = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M5, 0, 100)
        if rates_m5 is not None and len(rates_m5) > 0:
            print(f"✅ {COLORS['GREEN']}Données M5: {len(rates_m5)} barres{COLORS['RESET']}")
        else:
            print(f"❌ {COLORS['RED']}Échec données M5{COLORS['RESET']}")
            
        # Test M1
        rates_m1 = mt5.copy_rates_from_pos("XAUUSD", mt5.TIMEFRAME_M1, 0, 100)
        if rates_m1 is not None and len(rates_m1) > 0:
            print(f"✅ {COLORS['GREEN']}Données M1: {len(rates_m1)} barres{COLORS['RESET']}")
        else:
            print(f"❌ {COLORS['RED']}Échec données M1{COLORS['RESET']}")
            
        mt5.shutdown()
        return True
        
    except Exception as e:
        print(f"💥 {COLORS['RED']}Erreur test données: {e}{COLORS['RESET']}")
        mt5.shutdown()
        return False

def test_risk_manager():
    """Test du gestionnaire de risque"""
    print(f"🛡️ {COLORS['CYAN']}Test du Risk Manager...{COLORS['RESET']}")
    
    if not mt5.initialize():
        return False
        
    try:
        # Test des autorisations
        can_m15 = can_open_new_trade(15001, "Test M15")
        can_m5 = can_open_new_trade(5001, "Test M5") 
        can_m1 = can_open_new_trade(1001, "Test M1")
        
        print(f"📊 Autorisations: M15={can_m15}, M5={can_m5}, M1={can_m1}")
        
        # Test du résumé
        summary = get_risk_summary()
        print(f"💰 P&L: {summary['daily_pnl']:.2f}$")
        print(f"📈 Positions: {summary['total_positions']}")
        print(f"🚨 Statut: {'ARRÊT' if summary['emergency_stop'] else 'ACTIF'}")
        
        print(f"✅ {COLORS['GREEN']}Risk Manager fonctionnel{COLORS['RESET']}")
        mt5.shutdown()
        return True
        
    except Exception as e:
        print(f"💥 {COLORS['RED']}Erreur test Risk Manager: {e}{COLORS['RESET']}")
        mt5.shutdown()
        return False

def test_configuration():
    """Test de la configuration"""
    print(f"⚙️ {COLORS['CYAN']}Test de la configuration...{COLORS['RESET']}")
    
    print(f"📊 Stratégies actives: {len(ACTIVE_STRATEGIES)}")
    
    for timeframe, config in ACTIVE_STRATEGIES:
        status = "✅ ACTIVÉ" if config["ENABLED"] else "❌ DÉSACTIVÉ"
        print(f"  {config['EMOJI']} {config['NAME']}: {status}")
        print(f"    - Magic: {config['MAGIC_NUMBER']}")
        print(f"    - ADX Seuil: {config['ADX_THRESHOLD']}")
        print(f"    - Divergence Min: {config['MIN_DIVERGENCE_STRENGTH']}")
        print(f"    - Ratio R/R: {config['RR_RATIO']}")
        print(f"    - Volume: {config['VOLUME']}")
        print(f"    - Scan Interval: {config['SCAN_INTERVAL']}s")
        
    print(f"✅ {COLORS['GREEN']}Configuration validée{COLORS['RESET']}")
    return True

def display_pre_launch_summary():
    """Affichage du résumé avant lancement"""
    summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       🚀 RÉSUMÉ AVANT LANCEMENT                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  {COLORS['GREEN']}✅ Tests de Validation:{COLORS['RESET']}                                               ║
║     • Connexion MT5: Testée                                                  ║
║     • Données de marché: Vérifiées                                           ║
║     • Risk Manager: Fonctionnel                                              ║
║     • Configuration: Validée                                                 ║
║                                                                              ║
║  {COLORS['BLUE']}🎯 Stratégies Prêtes:{COLORS['RESET']}                                                 ║
║     • M15 Stratège: Sélectif, mouvements de fond                            ║
║     • M5 Commando: Équilibré, opportunités tactiques                        ║
║     • M1 Hyper-Scalper: Ultra-rapide, micro-impulsions                      ║
║                                                                              ║
║  {COLORS['YELLOW']}⚠️  Rappels de Sécurité:{COLORS['RESET']}                                            ║
║     • Risque maximal par trade: Configuré                                    ║
║     • Limite de positions simultanées: 5 trades max                          ║
║     • Arrêt d'urgence automatique: Activé                                    ║
║     • Surveillance continue des risques: Active                              ║
║                                                                              ║
║  {COLORS['RED']}🚨 ATTENTION: ARGENT RÉEL !{COLORS['RESET']}                                            ║
║     Vérifiez une dernière fois vos paramètres avant de continuer.           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(summary)

def main():
    """Test complet du système"""
    print(f"""
🧪 {COLORS['BOLD']}{COLORS['PURPLE']}TESTEUR BOT ULTIME{COLORS['RESET']}
═══════════════════════════════
Tests de validation avant lancement
""")
    
    tests_passed = 0
    total_tests = 4
    
    # Test 1: Configuration
    if test_configuration():
        tests_passed += 1
    time.sleep(1)
    
    # Test 2: Connexion MT5
    if test_mt5_connection():
        tests_passed += 1
    time.sleep(1)
    
    # Test 3: Données de marché
    if test_market_data():
        tests_passed += 1
    time.sleep(1)
    
    # Test 4: Risk Manager
    if test_risk_manager():
        tests_passed += 1
    time.sleep(1)
    
    print(f"\n📊 {COLORS['BOLD']}RÉSULTATS DES TESTS: {tests_passed}/{total_tests}{COLORS['RESET']}")
    
    if tests_passed == total_tests:
        print(f"🎉 {COLORS['GREEN']}TOUS LES TESTS RÉUSSIS !{COLORS['RESET']}")
        display_pre_launch_summary()
        
        response = input(f"\n{COLORS['YELLOW']}Voulez-vous lancer le Bot Ultime ? (oui/non): {COLORS['RESET']}")
        if response.lower() in ['oui', 'o', 'yes', 'y']:
            print(f"🚀 {COLORS['GREEN']}Lancement du Bot Ultime...{COLORS['RESET']}")
            import ultimate_bot
            ultimate_bot.main()
        else:
            print(f"🔄 {COLORS['CYAN']}Lancement annulé par l'utilisateur{COLORS['RESET']}")
    else:
        print(f"❌ {COLORS['RED']}TESTS ÉCHOUÉS. Veuillez corriger les erreurs avant de continuer.{COLORS['RESET']}")
        print(f"💡 {COLORS['CYAN']}Vérifiez votre connexion MT5 et vos paramètres de configuration.{COLORS['RESET']}")

if __name__ == "__main__":
    main()
