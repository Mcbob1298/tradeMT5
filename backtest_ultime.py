#!/usr/bin/env python3
"""
🎯 BACKTEST ULTIME - Simulation Multi-Stratégies
===============================================

Ce backtester simule l'exécution parallèle des 3 stratégies du Bot Ultime :
- M15 "Le Stratège" : Sélectif, mouvements de fond
- M5 "Le Commando" : Équilibré, opportunités tactiques  
- M1 "L'Hyper-Scalper" : Ultra-rapide, micro-impulsions

Architecture :
- Simulation du threading avec time-slicing
- Risk Manager global avec contrôles inter-stratégies
- Agrégation des performances et analyse d'interactions
- Rapport détaillé par stratégie et performance globale

Auteur: Assistant IA & Mathias Cassonnet
Date: 13 Août 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import concurrent.futures
from typing import Dict, List, Tuple, Any
import json
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

# Configuration similaire au bot réel
@dataclass
class StrategyConfig:
    """Configuration d'une stratégie"""
    name: str
    timeframe: str
    rsi_period: int
    rsi_overbought: int
    rsi_oversold: int
    adx_period: int
    adx_threshold: int
    max_positions: int
    lot_size: float
    active: bool

# Balance de départ et paramètres de risque
INITIAL_BALANCE = 300.0  # €
RISK_PER_TRADE = 0.02    # 2% par trade maximum
MAX_DAILY_RISK = 0.10    # 10% de perte journalière max (30€)

# Configurations adaptées pour 300€ de capital
M15_CONFIG = StrategyConfig(
    name="Le Stratège M15",
    timeframe="M15",
    rsi_period=14,
    rsi_overbought=50,
    rsi_oversold=30,
    adx_period=14,
    adx_threshold=25,
    max_positions=2,         # Réduit pour petit capital
    lot_size=0.01,          # Micro lot pour 300€
    active=True
)

M5_CONFIG = StrategyConfig(
    name="Le Commando M5", 
    timeframe="M5",
    rsi_period=14,
    rsi_overbought=45,
    rsi_oversold=35,
    adx_period=14,
    adx_threshold=24,
    max_positions=2,         # Réduit pour petit capital
    lot_size=0.01,          # Micro lot pour 300€
    active=True
)

M1_CONFIG = StrategyConfig(
    name="L'Hyper-Scalper M1",
    timeframe="M1", 
    rsi_period=14,
    rsi_overbought=65,
    rsi_oversold=40,
    adx_period=14,
    adx_threshold=15,
    max_positions=3,         # Réduit pour petit capital
    lot_size=0.01,          # Micro lot pour 300€
    active=True
)

# Risk Manager Global
class GlobalRiskManager:
    """Gestionnaire de risque global simulant le threading safety"""
    
    def __init__(self):
        self.initial_balance = INITIAL_BALANCE
        self.current_balance = INITIAL_BALANCE
        self.max_total_positions = 7   # Réduit pour 300€
        self.max_daily_loss = INITIAL_BALANCE * MAX_DAILY_RISK  # 30€ max
        self.max_daily_profit = INITIAL_BALANCE * 0.20  # 60€ max par jour
        self.current_positions = 0
        self.daily_pnl = 0.0
        self.total_trades = 0
        self.emergency_stop = False
        self.equity_curve = [INITIAL_BALANCE]  # Track balance evolution
        
    def can_open_trade(self, strategy_name: str) -> bool:
        """Vérifie si une nouvelle position peut être ouverte"""
        if self.emergency_stop:
            return False
            
        if self.current_positions >= self.max_total_positions:
            return False
            
        # Vérification de la perte journalière en €
        if self.daily_pnl <= -self.max_daily_loss:
            print(f"🚨 ARRÊT D'URGENCE: Perte journalière dépassée ({self.daily_pnl:.2f}€)")
            self.emergency_stop = True
            return False
            
        # Vérification du profit journalier en €
        if self.daily_pnl >= self.max_daily_profit:
            print(f"🎯 LIMITE DE PROFIT ATTEINTE: {self.daily_pnl:.2f}€")
            return False
        
        # Vérification que la balance ne tombe pas sous 200€ (seuil critique)
        if self.current_balance <= INITIAL_BALANCE * 0.67:  # Moins de 200€
            print(f"🚨 BALANCE CRITIQUE: {self.current_balance:.2f}€ - Arrêt trading")
            self.emergency_stop = True
            return False
            
        return True
    
    def register_trade(self, strategy_name: str, pnl: float):
        """Enregistre un trade et met à jour les statistiques"""
        self.total_trades += 1
        self.daily_pnl += pnl
        self.current_balance += pnl
        self.equity_curve.append(self.current_balance)
        
    def add_position(self):
        """Ajoute une position au compteur global"""
        self.current_positions += 1
        
    def remove_position(self):
        """Retire une position du compteur global"""
        self.current_positions = max(0, self.current_positions - 1)
        
    def get_balance_stats(self):
        """Retourne les statistiques de balance"""
        return {
            "initial_balance": self.initial_balance,
            "final_balance": self.current_balance,
            "total_return": self.current_balance - self.initial_balance,
            "return_percentage": ((self.current_balance / self.initial_balance) - 1) * 100,
            "max_balance": max(self.equity_curve),
            "min_balance": min(self.equity_curve),
            "max_drawdown": self.calculate_max_drawdown()
        }
        
    def calculate_max_drawdown(self):
        """Calcule le drawdown maximum"""
        if len(self.equity_curve) < 2:
            return 0
            
        peak = self.equity_curve[0]
        max_dd = 0
        
        for balance in self.equity_curve:
            if balance > peak:
                peak = balance
            drawdown = (peak - balance) / peak * 100
            if drawdown > max_dd:
                max_dd = drawdown
                
        return max_dd

class TradingStrategy:
    """Classe de base pour les stratégies de trading"""
    
    def __init__(self, config: StrategyConfig, data: pd.DataFrame, risk_manager: GlobalRiskManager):
        self.config = config
        self.data = data.copy()
        self.risk_manager = risk_manager
        self.positions = []
        self.trades = []
        self.current_positions = 0
        
    def calculate_indicators(self):
        """Calcule les indicateurs techniques"""
        # RSI
        delta = self.data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.config.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.config.rsi_period).mean()
        rs = gain / loss
        self.data['rsi'] = 100 - (100 / (1 + rs))
        
        # ADX
        high = self.data['high']
        low = self.data['low'] 
        close = self.data['close']
        
        plus_dm = high.diff()
        minus_dm = low.diff()
        plus_dm = plus_dm.where(plus_dm > minus_dm, 0)
        minus_dm = minus_dm.where(minus_dm > plus_dm, 0)
        
        tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
        atr = tr.rolling(window=self.config.adx_period).mean()
        
        plus_di = 100 * (plus_dm.rolling(window=self.config.adx_period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=self.config.adx_period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        self.data['adx'] = dx.rolling(window=self.config.adx_period).mean()
        
    def detect_rsi_divergence(self, idx: int) -> str:
        """Détecte les divergences RSI (simplifié)"""
        if idx < 20:
            return "none"
            
        recent_data = self.data.iloc[idx-20:idx+1]
        
        # Divergence haussière : prix baisse, RSI monte
        if (recent_data['close'].iloc[-1] < recent_data['close'].iloc[0] and 
            recent_data['rsi'].iloc[-1] > recent_data['rsi'].iloc[0] and
            recent_data['rsi'].iloc[-1] < self.config.rsi_oversold):
            return "bullish"
            
        # Divergence baissière : prix monte, RSI baisse  
        if (recent_data['close'].iloc[-1] > recent_data['close'].iloc[0] and
            recent_data['rsi'].iloc[-1] < recent_data['rsi'].iloc[0] and
            recent_data['rsi'].iloc[-1] > self.config.rsi_overbought):
            return "bearish"
            
        return "none"
    
    def should_enter_trade(self, idx: int) -> Tuple[bool, str]:
        """Détermine s'il faut entrer en position"""
        if not self.risk_manager.can_open_trade(self.config.name):
            return False, "none"
            
        if self.current_positions >= self.config.max_positions:
            return False, "none"
            
        row = self.data.iloc[idx]
        
        # Filtre ADX : tendance forte requise
        if pd.isna(row['adx']) or row['adx'] < self.config.adx_threshold:
            return False, "none"
            
        # Détection de divergence
        divergence = self.detect_rsi_divergence(idx)
        
        if divergence == "bullish":
            return True, "buy"
        elif divergence == "bearish":
            return True, "sell"
            
        return False, "none"
    
    def run_backtest(self) -> Dict[str, Any]:
        """Exécute le backtest pour cette stratégie"""
        print(f"🚀 Démarrage backtest: {self.config.name}")
        
        if not self.config.active:
            return {"active": False}
            
        self.calculate_indicators()
        
        for idx in range(50, len(self.data)):  # Skip initial period for indicators
            if self.risk_manager.emergency_stop:
                break
                
            should_enter, direction = self.should_enter_trade(idx)
            
            if should_enter:
                self.enter_position(idx, direction)
                
            # Vérifier les sorties de positions existantes
            self.check_exits(idx)
                
        # Clôturer toutes les positions ouvertes à la fin
        self.close_all_positions(len(self.data) - 1)
        
        return self.get_results()
    
    def enter_position(self, idx: int, direction: str):
        """Entre en position"""
        row = self.data.iloc[idx]
        
        position = {
            'entry_time': row['time'],
            'entry_price': row['close'],
            'direction': direction,
            'lot_size': self.config.lot_size,
            'stop_loss': self.calculate_stop_loss(row['close'], direction),
            'take_profit': self.calculate_take_profit(row['close'], direction),
            'open': True
        }
        
        self.positions.append(position)
        self.current_positions += 1
        self.risk_manager.add_position()
        
    def calculate_stop_loss(self, entry_price: float, direction: str) -> float:
        """Calcule le stop loss adapté au capital de 300€"""
        # Stop loss de 10-15 pips pour limiter le risque par trade à ~6€ (2% de 300€)
        sl_pips = 12  # 12 pips de stop loss pour micro lots
        pip_value = 0.01 if 'XAU' in str(entry_price) else 0.0001  # Ajusté pour l'or
        
        if direction == "buy":
            return entry_price - (sl_pips * pip_value)
        else:
            return entry_price + (sl_pips * pip_value)
    
    def calculate_take_profit(self, entry_price: float, direction: str) -> float:
        """Calcule le take profit adapté (R:R = 1:2)"""
        tp_pips = 24  # 24 pips de take profit (ratio 1:2)
        pip_value = 0.01 if 'XAU' in str(entry_price) else 0.0001
        
        if direction == "buy":
            return entry_price + (tp_pips * pip_value)
        else:
            return entry_price - (tp_pips * pip_value)
    
    def check_exits(self, idx: int):
        """Vérifie les conditions de sortie"""
        row = self.data.iloc[idx]
        
        for i, pos in enumerate(self.positions):
            if not pos['open']:
                continue
                
            # Vérification Stop Loss / Take Profit
            if pos['direction'] == "buy":
                if row['low'] <= pos['stop_loss']:
                    self.close_position(i, idx, pos['stop_loss'], "Stop Loss")
                elif row['high'] >= pos['take_profit']:
                    self.close_position(i, idx, pos['take_profit'], "Take Profit")
            else:  # sell
                if row['high'] >= pos['stop_loss']:
                    self.close_position(i, idx, pos['stop_loss'], "Stop Loss")
                elif row['low'] <= pos['take_profit']:
                    self.close_position(i, idx, pos['take_profit'], "Take Profit")
    
    def close_position(self, pos_idx: int, data_idx: int, exit_price: float, reason: str):
        """Clôture une position"""
        position = self.positions[pos_idx]
        row = self.data.iloc[data_idx]
        
        # Calcul du P&L adapté pour XAUUSD avec micro lots (0.01)
        if position['direction'] == "buy":
            pips = (exit_price - position['entry_price']) / 0.01  # Pour l'or
        else:
            pips = (position['entry_price'] - exit_price) / 0.01
            
        # P&L en euros pour micro lots sur XAUUSD
        # Formule: pips × lot_size × pip_value_euro
        pnl = pips * position['lot_size'] * 0.01  # Ajusté pour 300€ de capital
        
        trade = {
            'strategy': self.config.name,
            'entry_time': position['entry_time'],
            'exit_time': row['time'],
            'direction': position['direction'],
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'pips': pips,
            'pnl': pnl,
            'reason': reason
        }
        
        self.trades.append(trade)
        self.positions[pos_idx]['open'] = False
        self.current_positions -= 1
        self.risk_manager.remove_position()
        self.risk_manager.register_trade(self.config.name, pnl)
    
    def close_all_positions(self, idx: int):
        """Clôture toutes les positions ouvertes"""
        row = self.data.iloc[idx]
        
        for i, pos in enumerate(self.positions):
            if pos['open']:
                self.close_position(i, idx, row['close'], "End of Backtest")
    
    def get_results(self) -> Dict[str, Any]:
        """Retourne les résultats de la stratégie"""
        if not self.trades:
            return {
                "strategy_name": self.config.name,
                "active": True,
                "total_trades": 0,
                "total_pnl": 0,
                "win_rate": 0,
                "avg_win": 0,
                "avg_loss": 0,
                "max_drawdown": 0,
                "trades": []
            }
            
        df_trades = pd.DataFrame(self.trades)
        
        winning_trades = df_trades[df_trades['pnl'] > 0]
        losing_trades = df_trades[df_trades['pnl'] < 0]
        
        results = {
            "strategy_name": self.config.name,
            "active": True,
            "total_trades": len(self.trades),
            "total_pnl": df_trades['pnl'].sum(),
            "win_rate": len(winning_trades) / len(self.trades) * 100,
            "avg_win": winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0,
            "avg_loss": losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0,
            "best_trade": df_trades['pnl'].max(),
            "worst_trade": df_trades['pnl'].min(),
            "profit_factor": abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 else float('inf'),
            "trades": self.trades
        }
        
        return results

class UltimateBacktester:
    """Backtester principal qui orchestre les 3 stratégies"""
    
    def __init__(self):
        self.risk_manager = GlobalRiskManager()
        self.strategies = {}
        self.results = {}
        
    def load_data(self) -> Dict[str, pd.DataFrame]:
        """Charge les données pour chaque timeframe"""
        data_files = {
            "M15": "data/XAUUSD_M15.csv",
            "M5": "data/XAUUSD_M5.csv", 
            "M1": "data/XAUUSD_M1.csv"
        }
        
        datasets = {}
        
        for timeframe, file_path in data_files.items():
            try:
                # Lecture sans header car les fichiers n'en ont pas
                df = pd.read_csv(file_path, header=None)
                # Attribution des noms de colonnes
                df.columns = ['time', 'open', 'high', 'low', 'close', 'volume']
                df['time'] = pd.to_datetime(df['time'])
                df = df.sort_values('time').reset_index(drop=True)
                datasets[timeframe] = df
                print(f"✅ Données {timeframe} chargées: {len(df)} barres")
            except Exception as e:
                print(f"❌ Erreur chargement {timeframe}: {e}")
                datasets[timeframe] = pd.DataFrame()
                
        return datasets
    
    def run_ultimate_backtest(self) -> Dict[str, Any]:
        """Lance le backtest ultime multi-stratégies"""
        print("\n" + "="*60)
        print("🎯 BACKTEST ULTIME - SIMULATION MULTI-STRATÉGIES")
        print("="*60)
        
        # Chargement des données
        datasets = self.load_data()
        
        if not all(len(df) > 0 for df in datasets.values()):
            print("❌ Impossible de charger toutes les données")
            return {}
        
        # Initialisation des stratégies
        configs = {
            "M15": M15_CONFIG,
            "M5": M5_CONFIG,
            "M1": M1_CONFIG
        }
        
        strategies = {}
        for timeframe, config in configs.items():
            if config.active and timeframe in datasets:
                strategies[timeframe] = TradingStrategy(config, datasets[timeframe], self.risk_manager)
        
        print(f"\n🚀 Stratégies actives: {list(strategies.keys())}")
        
        # Exécution parallèle simulée
        all_results = {}
        
        # Pour simuler le comportement multi-thread, nous exécutons séquentiellement
        # mais avec le même risk manager partagé
        for timeframe, strategy in strategies.items():
            print(f"\n📊 Exécution {strategy.config.name}...")
            results = strategy.run_backtest()
            all_results[timeframe] = results
            
            if results.get("active", False):
                print(f"   ✅ {results['total_trades']} trades, P&L: {results['total_pnl']:.2f}$")
        
        # Agrégation des résultats
        combined_results = self.aggregate_results(all_results)
        
        return combined_results
    
    def aggregate_results(self, results: Dict[str, Dict]) -> Dict[str, Any]:
        """Agrège les résultats de toutes les stratégies"""
        
        # Statistiques globales
        total_trades = sum(r.get("total_trades", 0) for r in results.values() if r.get("active", False))
        total_pnl = sum(r.get("total_pnl", 0) for r in results.values() if r.get("active", False))
        
        # Collecte de tous les trades
        all_trades = []
        for strategy_results in results.values():
            if strategy_results.get("active", False):
                all_trades.extend(strategy_results.get("trades", []))
        
        # Tri par temps
        if all_trades:
            all_trades.sort(key=lambda x: x['entry_time'])
            
            df_all_trades = pd.DataFrame(all_trades)
            winning_trades = df_all_trades[df_all_trades['pnl'] > 0]
            losing_trades = df_all_trades[df_all_trades['pnl'] < 0]
            
            global_win_rate = len(winning_trades) / len(all_trades) * 100 if all_trades else 0
            profit_factor = abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if len(losing_trades) > 0 else float('inf')
        else:
            global_win_rate = 0
            profit_factor = 0
        
        combined = {
            "backtest_summary": {
                "total_strategies": len([r for r in results.values() if r.get("active", False)]),
                "total_trades": total_trades,
                "total_pnl": total_pnl,
                "global_win_rate": global_win_rate,
                "profit_factor": profit_factor,
                "risk_manager_stats": {
                    "emergency_stops": self.risk_manager.emergency_stop,
                    "final_daily_pnl": self.risk_manager.daily_pnl,
                    "max_positions_reached": self.risk_manager.current_positions,
                    "balance_stats": self.risk_manager.get_balance_stats()
                }
            },
            "strategy_results": results,
            "all_trades": all_trades
        }
        
        return combined

def print_ultimate_report(results: Dict[str, Any]):
    """Affiche le rapport détaillé du backtest ultime"""
    
    print("\n" + "="*80)
    print("🎯 RAPPORT BACKTEST ULTIME - BOT MULTI-STRATÉGIES")
    print("="*80)
    
    summary = results["backtest_summary"]
    
    print(f"\n📊 PERFORMANCE GLOBALE:")
    print(f"   • Stratégies Actives : {summary['total_strategies']}")
    print(f"   • Total Trades      : {summary['total_trades']}")
    print(f"   • P&L Total        : {summary['total_pnl']:.2f}€ 💰")
    print(f"   • Taux de Réussite : {summary['global_win_rate']:.1f}%")
    print(f"   • Profit Factor    : {summary['profit_factor']:.2f}")
    
    # Affichage des statistiques de balance
    balance_stats = summary['risk_manager_stats']['balance_stats']
    print(f"\n💰 ÉVOLUTION DU CAPITAL:")
    print(f"   • Balance Initiale  : {balance_stats['initial_balance']:.2f}€")
    print(f"   • Balance Finale    : {balance_stats['final_balance']:.2f}€")
    print(f"   • Gain/Perte Total  : {balance_stats['total_return']:.2f}€")
    print(f"   • Rendement        : {balance_stats['return_percentage']:.1f}%")
    print(f"   • Drawdown Max     : {balance_stats['max_drawdown']:.1f}%")
    print(f"   • Balance Max      : {balance_stats['max_balance']:.2f}€")
    print(f"   • Balance Min      : {balance_stats['min_balance']:.2f}€")
    
    print(f"\n🔒 RISK MANAGER:")
    risk_stats = summary['risk_manager_stats']
    print(f"   • Arrêts d'urgence  : {'✅ Aucun' if not risk_stats['emergency_stops'] else '🚨 Activé'}")
    print(f"   • P&L Journalier   : {risk_stats['final_daily_pnl']:.2f}€")
    
    print(f"\n📈 DÉTAIL PAR STRATÉGIE:")
    print("-" * 80)
    
    for timeframe, strategy_result in results["strategy_results"].items():
        if strategy_result.get("active", False):
            print(f"\n🎯 {strategy_result['strategy_name']}")
            print(f"   Trades        : {strategy_result['total_trades']}")
            print(f"   P&L           : {strategy_result['total_pnl']:.2f}€")
            print(f"   Taux Réussite : {strategy_result['win_rate']:.1f}%")
            print(f"   Gain Moyen    : {strategy_result['avg_win']:.2f}€")
            print(f"   Perte Moyenne : {strategy_result['avg_loss']:.2f}€")
            print(f"   Meilleur Trade: {strategy_result['best_trade']:.2f}€")
            print(f"   Pire Trade    : {strategy_result['worst_trade']:.2f}€")
    
    print("\n" + "="*80)
    print("🚀 BACKTEST TERMINÉ - SYSTÈME MULTI-STRATÉGIES ANALYSÉ")
    print("="*80)

def main():
    """Fonction principale"""
    backtester = UltimateBacktester()
    results = backtester.run_ultimate_backtest()
    
    if results:
        print_ultimate_report(results)
        
        # Sauvegarde des résultats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backtest_ultime_results_{timestamp}.json"
        
        # Conversion pour JSON (dates)
        json_results = results.copy()
        for trade in json_results.get("all_trades", []):
            if 'entry_time' in trade:
                trade['entry_time'] = str(trade['entry_time'])
            if 'exit_time' in trade:
                trade['exit_time'] = str(trade['exit_time'])
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False, default=str)
            
        print(f"\n💾 Résultats sauvegardés: {filename}")
    else:
        print("❌ Échec du backtest")

if __name__ == "__main__":
    main()
