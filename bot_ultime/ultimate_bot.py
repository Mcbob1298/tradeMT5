#!/usr/bin/env python3
"""
🤖 BOT ULTIME - SYSTÈME MULTI-STRATÉGIES
Architecture multi-threading pour trading algorithmique institutionnel

Ce bot combine 3 stratégies spécialisées :
- M15 "Le Stratège" : Mouvements de fond, sélectif
- M5 "Le Commando" : Opportunités tactiques, équilibré  
- M1 "L'Hyper-Scalper" : Micro-impulsions, ultra-rapide

Auteur: Assistant IA & Mathias Cassonnet
Date: Août 2025
Version: 1.0
"""

import threading
import time
import signal
import sys
import MetaTrader5 as mt5
from datetime import datetime
import logging

# Configuration et modules  
from .config.config_ultimate import (
    ACTIVE_STRATEGIES, COLORS, MT5_LOGIN, MT5_PASSWORD, MT5_SERVER,
    M15_SNIPER_CONFIG, M5_COMMANDO_CONFIG, M1_SCALPER_CONFIG
)
from .core.risk_manager import risk_monitor, get_risk_summary, emergency_close_all

# Stratégies
from .strategies.strategy_m15 import run_m15_strategy
from .strategies.strategy_m5 import run_m5_strategy  
from .strategies.strategy_m1 import run_m1_strategy

class UltimateBot:
    def __init__(self):
        self.name = "🤖 BOT ULTIME"
        self.version = "1.0"
        self.start_time = datetime.now()
        self.is_running = False
        self.strategy_threads = []
        self.risk_thread = None
        
        # Configuration des logs
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler('ultimate_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def print_banner(self):
        """Affichage du banner de démarrage"""
        banner = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            🤖 BOT ULTIME v{self.version}                              ║
║                     SYSTÈME MULTI-STRATÉGIES INSTITUTIONNEL                  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🎯 {COLORS['BLUE']}M15 "LE STRATÈGE"{COLORS['RESET']}     │  Mouvements de fond, sélectif         ║
║  ⚡ {COLORS['GREEN']}M5 "LE COMMANDO"{COLORS['RESET']}     │  Opportunités tactiques, équilibré    ║
║  🚀 {COLORS['RED']}M1 "HYPER-SCALPER"{COLORS['RESET']}   │  Micro-impulsions, ultra-rapide       ║
║                                                                              ║
║  💾 Risk Manager Global  │  Contrôle unifié des risques                     ║
║  🧵 Multi-Threading      │  Exécution parallèle optimisée                   ║
║  📊 Monitoring Temps Réel│  Surveillance continue des performances          ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  {COLORS['YELLOW']}⚠️  ATTENTION: Ce bot utilise de l'argent réel !{COLORS['RESET']}                        ║
║  {COLORS['YELLOW']}⚠️  Assurez-vous que vos paramètres sont corrects !{COLORS['RESET']}                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        print(banner)
        
    def connect_mt5(self):
        """Connexion principale à MetaTrader 5"""
        print(f"🔌 {COLORS['CYAN']}Connexion à MetaTrader 5...{COLORS['RESET']}")
        
        if not mt5.initialize():
            print(f"❌ {COLORS['RED']}Échec d'initialisation MT5{COLORS['RESET']}")
            return False
            
        # Tentative de connexion au compte
        authorized = mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER)
        if not authorized:
            print(f"❌ {COLORS['RED']}Échec de connexion au compte {MT5_LOGIN}{COLORS['RESET']}")
            error = mt5.last_error()
            print(f"Code d'erreur: {error}")
            mt5.shutdown()
            return False
            
        # Vérification des informations du compte
        account_info = mt5.account_info()
        if account_info is None:
            print(f"❌ {COLORS['RED']}Impossible de récupérer les informations du compte{COLORS['RESET']}")
            return False
            
        print(f"✅ {COLORS['GREEN']}Connexion réussie !{COLORS['RESET']}")
        print(f"📊 Compte: {account_info.login} | Solde: {account_info.balance:.2f} {account_info.currency}")
        print(f"🏢 Courtier: {account_info.company} | Serveur: {account_info.server}")
        
        return True
        
    def start_risk_monitor(self):
        """Démarre le thread de surveillance des risques"""
        print(f"🛡️ {COLORS['YELLOW']}Démarrage du Risk Manager...{COLORS['RESET']}")
        self.risk_thread = threading.Thread(target=risk_monitor, name="RiskMonitor", daemon=True)
        self.risk_thread.start()
        print(f"✅ {COLORS['GREEN']}Risk Manager actif{COLORS['RESET']}")
        
    def start_strategies(self):
        """Lance toutes les stratégies actives dans des threads séparés"""
        print(f"🚀 {COLORS['PURPLE']}Lancement des stratégies...{COLORS['RESET']}")
        
        strategy_functions = {
            "M15": run_m15_strategy,
            "M5": run_m5_strategy,
            "M1": run_m1_strategy
        }
        
        for timeframe, config in ACTIVE_STRATEGIES:
            if config["ENABLED"]:
                strategy_func = strategy_functions[timeframe]
                thread = threading.Thread(
                    target=strategy_func, 
                    name=f"{config['NAME']}", 
                    daemon=True
                )
                thread.start()
                self.strategy_threads.append(thread)
                
                print(f"✅ {config['COLOR']}{config['EMOJI']} {config['NAME']}{COLORS['RESET']} - Thread démarré")
                time.sleep(2)  # Espacement pour éviter la surcharge
                
        print(f"🎯 {COLORS['BOLD']}{len(self.strategy_threads)} stratégies actives{COLORS['RESET']}")
        
    def display_status(self):
        """Affiche le statut du bot et des performances"""
        uptime = datetime.now() - self.start_time
        risk_summary = get_risk_summary()
        
        status = f"""
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🤖 BOT ULTIME - STATUT EN TEMPS RÉEL                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│ ⏰ Uptime: {str(uptime).split('.')[0]}                                       │
│ 💰 P&L Quotidien: {risk_summary['daily_pnl']:.2f}$                          │
│ 📊 Positions Actives: {risk_summary['total_positions']}/5                   │
│ 🎯 Trades Aujourd'hui: {risk_summary['total_trades_today']}                 │
│                                                                              │
│ 📈 Répartition par Stratégie:                                               │
│   🎯 M15 Stratège: {risk_summary['positions_by_strategy']['M15']} positions │
│   ⚡ M5 Commando: {risk_summary['positions_by_strategy']['M5']} positions    │
│   🚀 M1 Scalper: {risk_summary['positions_by_strategy']['M1']} positions    │
│                                                                              │
│ 🚨 Statut: {"🔴 ARRÊT D'URGENCE" if risk_summary['emergency_stop'] else "🟢 OPÉRATIONNEL"} │
│ ⚖️ Niveau Risque: {risk_summary['risk_level']}                              │
└─────────────────────────────────────────────────────────────────────────────┘
"""
        print(status)
        
    def signal_handler(self, signum, frame):
        """Gestionnaire pour arrêt propre (Ctrl+C)"""
        print(f"\n🔄 {COLORS['YELLOW']}Signal d'arrêt reçu...{COLORS['RESET']}")
        self.stop()
        
    def stop(self):
        """Arrêt propre du bot"""
        print(f"🛑 {COLORS['RED']}Arrêt du Bot Ultime...{COLORS['RESET']}")
        self.is_running = False
        
        # Attendre que les threads se terminent
        for thread in self.strategy_threads:
            if thread.is_alive():
                print(f"⏳ Attente de l'arrêt de {thread.name}...")
                thread.join(timeout=10)
                
        # Fermer MT5
        mt5.shutdown()
        print(f"✅ {COLORS['GREEN']}Bot Ultime arrêté proprement{COLORS['RESET']}")
        
    def run(self):
        """Boucle principale du Bot Ultime"""
        try:
            # Affichage du banner
            self.print_banner()
            
            # Connexion MT5
            if not self.connect_mt5():
                print(f"💥 {COLORS['RED']}Impossible de se connecter à MT5. Arrêt.{COLORS['RESET']}")
                return
                
            # Configuration du signal d'arrêt
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
            
            # Démarrage du Risk Manager
            self.start_risk_monitor()
            time.sleep(2)
            
            # Démarrage des stratégies
            self.start_strategies()
            time.sleep(5)
            
            print(f"🎉 {COLORS['BOLD']}{COLORS['GREEN']}BOT ULTIME OPÉRATIONNEL !{COLORS['RESET']}")
            print(f"💡 {COLORS['CYAN']}Appuyez sur Ctrl+C pour arrêter proprement{COLORS['RESET']}")
            
            self.is_running = True
            status_counter = 0
            
            # Boucle de supervision
            while self.is_running:
                time.sleep(10)
                
                # Affichage du statut toutes les 30 itérations (5 minutes)
                status_counter += 1
                if status_counter >= 30:
                    self.display_status()
                    status_counter = 0
                    
                # Vérifier si les threads sont toujours vivants
                dead_threads = [t for t in self.strategy_threads if not t.is_alive()]
                if dead_threads:
                    for thread in dead_threads:
                        self.logger.warning(f"Thread {thread.name} s'est arrêté de manière inattendue")
                        
        except KeyboardInterrupt:
            print(f"\n🔄 {COLORS['YELLOW']}Interruption clavier détectée{COLORS['RESET']}")
            self.stop()
        except Exception as e:
            self.logger.error(f"Erreur fatale dans le Bot Ultime: {e}")
            print(f"💥 {COLORS['RED']}Erreur fatale: {e}{COLORS['RESET']}")
            self.stop()
        finally:
            sys.exit(0)

def main():
    """Point d'entrée principal"""
    bot = UltimateBot()
    bot.run()

if __name__ == "__main__":
    main()
