"""
RISK MANAGER - Gestionnaire de Risque Global pour le Bot Ultime
Contrôle la prise de risque globale de toutes les stratégies combinées
"""

import threading
import MetaTrader5 as mt5
import time
from datetime import datetime, date
from ..config.config_ultimate import (
    MAX_TOTAL_TRADES, SYMBOL, MAX_DAILY_LOSS, MAX_DAILY_PROFIT, 
    M15_SNIPER_CONFIG, M5_COMMANDO_CONFIG, M1_SCALPER_CONFIG, COLORS
)

# === VERROUS DE SÉCURITÉ ===
# Le "Lock" empêche les threads de se marcher sur les pieds
mt5_lock = threading.Lock()
risk_lock = threading.Lock()

# === STATISTIQUES GLOBALES ===
class RiskStats:
    def __init__(self):
        self.daily_pnl = 0.0
        self.total_trades_today = 0
        self.last_reset_date = date.today()
        self.trades_by_strategy = {15001: 0, 5001: 0, 1001: 0}  # Magic numbers
        self.emergency_stop = False
        
    def reset_daily_stats(self):
        """Remet à zéro les stats quotidiennes"""
        current_date = date.today()
        if current_date != self.last_reset_date:
            print(f"🔄 {COLORS['YELLOW']}Reset des statistiques quotidiennes{COLORS['RESET']}")
            self.daily_pnl = 0.0
            self.total_trades_today = 0
            self.trades_by_strategy = {15001: 0, 5001: 0, 1001: 0}
            self.last_reset_date = current_date
            self.emergency_stop = False

# Instance globale des statistiques
risk_stats = RiskStats()

def update_daily_pnl():
    """Met à jour le P&L quotidien en analysant les positions fermées"""
    with mt5_lock:
        try:
            today = datetime.now().date()
            # Récupérer les deals d'aujourd'hui
            deals = mt5.history_deals_get(
                datetime.combine(today, datetime.min.time()),
                datetime.now()
            )
            
            if deals is not None:
                daily_profit = sum(deal.profit for deal in deals if deal.symbol == SYMBOL)
                risk_stats.daily_pnl = daily_profit
                return daily_profit
            return 0.0
        except Exception as e:
            print(f"⚠️ Erreur update P&L: {e}")
            return 0.0

def can_open_new_trade(magic_number, strategy_name):
    """
    Vérifie si une nouvelle position peut être ouverte
    
    Args:
        magic_number: Numéro magique de la stratégie
        strategy_name: Nom de la stratégie pour les logs
    
    Returns:
        bool: True si le trade peut être ouvert
    """
    with risk_lock:
        # Reset quotidien si nécessaire
        risk_stats.reset_daily_stats()
        
        # Vérification arrêt d'urgence
        if risk_stats.emergency_stop:
            print(f"🚨 {COLORS['RED']}ARRÊT D'URGENCE ACTIF - Tous trades bloqués{COLORS['RESET']}")
            return False
        
        # Mise à jour du P&L quotidien
        current_pnl = update_daily_pnl()
        
        # Vérification perte maximale quotidienne
        if current_pnl <= MAX_DAILY_LOSS:
            print(f"🚨 {COLORS['RED']}LIMITE DE PERTE QUOTIDIENNE ATTEINTE: {current_pnl:.2f}$ ≤ {MAX_DAILY_LOSS}${COLORS['RESET']}")
            risk_stats.emergency_stop = True
            return False
            
        # Vérification profit maximal quotidien (protection des gains)
        if current_pnl >= MAX_DAILY_PROFIT:
            print(f"🎯 {COLORS['GREEN']}OBJECTIF QUOTIDIEN ATTEINT: {current_pnl:.2f}$ ≥ {MAX_DAILY_PROFIT}$ - Arrêt préventif{COLORS['RESET']}")
            risk_stats.emergency_stop = True
            return False
    
    # Vérification nombre total de positions
    with mt5_lock:
        positions = mt5.positions_get(symbol=SYMBOL)
        if positions is None:
            print(f"⚠️ {COLORS['YELLOW']}Erreur lecture positions MT5{COLORS['RESET']}")
            return False
        
        current_positions = len(positions)
        if current_positions >= MAX_TOTAL_TRADES:
            print(f"⚠️ {COLORS['YELLOW']}{strategy_name}: Limite de {MAX_TOTAL_TRADES} trades atteinte ({current_positions}){COLORS['RESET']}")
            return False
    
    # Vérification spécifique par stratégie (éviter le spam)
    strategy_positions = len([p for p in positions if p.magic == magic_number])
    if strategy_positions >= 2:  # Maximum 2 positions par stratégie
        print(f"⚠️ {COLORS['YELLOW']}{strategy_name}: Maximum 2 positions par stratégie atteint{COLORS['RESET']}")
        return False
    
    print(f"✅ {COLORS['GREEN']}{strategy_name}: Autorisation de trade accordée (P&L: {current_pnl:.2f}$, Positions: {current_positions}){COLORS['RESET']}")
    return True

def place_order_safely(request, strategy_name):
    """
    Place un ordre en utilisant le verrou de sécurité
    
    Args:
        request: Dictionnaire de requête MT5
        strategy_name: Nom de la stratégie
    
    Returns:
        tuple: (success, result)
    """
    with mt5_lock:
        try:
            result = mt5.order_send(request)
            if result is None:
                print(f"❌ {COLORS['RED']}{strategy_name}: Échec ordre - Résultat None{COLORS['RESET']}")
                return False, None
                
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                # Mise à jour des statistiques
                with risk_lock:
                    risk_stats.total_trades_today += 1
                    risk_stats.trades_by_strategy[request['magic']] += 1
                
                print(f"✅ {COLORS['GREEN']}{strategy_name}: Ordre exécuté - Ticket #{result.order}{COLORS['RESET']}")
                return True, result
            else:
                print(f"❌ {COLORS['RED']}{strategy_name}: Ordre rejeté - Code: {result.retcode}{COLORS['RESET']}")
                return False, result
                
        except Exception as e:
            print(f"💥 {COLORS['RED']}{strategy_name}: Exception lors du placement - {e}{COLORS['RESET']}")
            return False, None

def get_risk_summary():
    """Retourne un résumé des risques actuels"""
    with risk_lock:
        risk_stats.reset_daily_stats()
        current_pnl = update_daily_pnl()
        
        with mt5_lock:
            positions = mt5.positions_get(symbol=SYMBOL)
            pos_count = len(positions) if positions else 0
            
            # Comptage par stratégie
            m15_pos = len([p for p in (positions or []) if p.magic == 15001])
            m5_pos = len([p for p in (positions or []) if p.magic == 5001])
            m1_pos = len([p for p in (positions or []) if p.magic == 1001])
    
    return {
        "daily_pnl": current_pnl,
        "total_positions": pos_count,
        "total_trades_today": risk_stats.total_trades_today,
        "emergency_stop": risk_stats.emergency_stop,
        "positions_by_strategy": {
            "M15": m15_pos,
            "M5": m5_pos, 
            "M1": m1_pos
        },
        "risk_level": "HIGH" if pos_count >= MAX_TOTAL_TRADES * 0.8 else "NORMAL"
    }

def emergency_close_all():
    """Ferme toutes les positions en cas d'urgence"""
    print(f"🚨 {COLORS['RED']}FERMETURE D'URGENCE DE TOUTES LES POSITIONS{COLORS['RESET']}")
    
    with mt5_lock:
        positions = mt5.positions_get(symbol=SYMBOL)
        if positions is None:
            return
            
        for position in positions:
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": mt5.ORDER_TYPE_SELL if position.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
                "position": position.ticket,
                "magic": position.magic,
                "comment": "EMERGENCY_CLOSE"
            }
            
            result = mt5.order_send(close_request)
            if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                print(f"✅ Position #{position.ticket} fermée")
            else:
                print(f"❌ Échec fermeture position #{position.ticket}")
    
    risk_stats.emergency_stop = True

def reset_emergency_stop():
    """Réinitialise l'arrêt d'urgence (à utiliser avec précaution)"""
    with risk_lock:
        risk_stats.emergency_stop = False
        print(f"🔄 {COLORS['GREEN']}Arrêt d'urgence réinitialisé{COLORS['RESET']}")

# === SURVEILLANCE CONTINUE ===
def risk_monitor():
    """Thread de surveillance continue des risques"""
    while True:
        try:
            summary = get_risk_summary()
            
            # Log périodique (toutes les 5 minutes)
            if int(time.time()) % 300 == 0:
                print(f"""
📊 {COLORS['CYAN']}RAPPORT RISQUE{COLORS['RESET']}
💰 P&L Quotidien: {summary['daily_pnl']:.2f}$
📈 Positions: {summary['total_positions']}/{MAX_TOTAL_TRADES}
🎯 Trades Jour: {summary['total_trades_today']}
⚡ M15: {summary['positions_by_strategy']['M15']} | M5: {summary['positions_by_strategy']['M5']} | M1: {summary['positions_by_strategy']['M1']}
🚨 Statut: {'ARRÊT' if summary['emergency_stop'] else 'ACTIF'}
""")
            
            time.sleep(10)  # Vérification toutes les 10 secondes
            
        except Exception as e:
            print(f"⚠️ Erreur surveillance risque: {e}")
            time.sleep(30)

if __name__ == "__main__":
    # Test du risk manager
    print("🧪 Test du Risk Manager")
    if not mt5.initialize():
        print("❌ Échec initialisation MT5")
    else:
        summary = get_risk_summary()
        print(f"Résumé: {summary}")
        mt5.shutdown()
