#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNIPER BOT BACKTESTING - Version CSV
Test de la stratégie de divergences RSI sur données historiques XAUUSD M15
Philosophie: Validation de la stratégie "Sniper" avant trading live
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
# import matplotlib.pyplot as plt  # Optionnel pour les graphiques

# =============================================================================
# CONFIGURATION IDENTIQUE AU SNIPER BOT
# =============================================================================
RISK_REWARD_RATIO_TARGET = 2.0          
RISK_PER_TRADE_PERCENT = 1.0            
MIN_DIVERGENCE_STRENGTH = 5.0           
EMA_PERIOD = 200                        
RSI_PERIOD = 14                         
LOOKBACK_PERIOD = 50                    
SWING_PERIOD = 5                        
ATR_PERIOD = 14                         
MIN_SWING_PERCENTAGE = 0.05             
MIN_TP_ATR_MULTIPLIER = 2.0             
VOLATILITY_FILTER_ENABLED = True        
MIN_ATR_VALUE = 0.50                    

# =============================================================================
# PARAMÈTRES DE BACKTESTING
# =============================================================================
INITIAL_BALANCE = 10000.0  # Balance initiale pour simulation
RISK_PER_TRADE = 100.0     # Montant risqué par trade ($)
CSV_FILE = "XAUUSD_M15.csv"

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def load_data():
    """Charge et prépare les données depuis le fichier CSV"""
    try:
        logging.info(f"📂 Chargement des données depuis {CSV_FILE}...")
        
        # Charger le CSV
        df = pd.read_csv(CSV_FILE, header=None, names=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        
        # Convertir la date
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        
        logging.info(f"✅ {len(df)} bougies chargées")
        logging.info(f"📅 Période: {df.index[0]} → {df.index[-1]}")
        logging.info(f"💰 Prix min: {df['low'].min():.2f} | Prix max: {df['high'].max():.2f}")
        
        return df
        
    except Exception as e:
        logging.error(f"❌ Erreur chargement données: {e}")
        return None

def calculate_indicators(df):
    """Calcule tous les indicateurs techniques"""
    try:
        logging.info("🔧 Calcul des indicateurs techniques...")
        
        # EMA 200 pour la tendance majeure
        df['ema200'] = df['close'].ewm(span=EMA_PERIOD).mean()
        
        # RSI pour les divergences
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/RSI_PERIOD, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/RSI_PERIOD, adjust=False).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # ATR pour mesurer la volatilité
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['atr'] = true_range.rolling(window=ATR_PERIOD).mean()
        
        # Détection des swing points
        df = detect_swing_points_advanced(df)
        
        logging.info("✅ Indicateurs calculés avec succès")
        return df
        
    except Exception as e:
        logging.error(f"❌ Erreur calcul indicateurs: {e}")
        return None

def detect_swing_points_advanced(df):
    """Détecte les points de retournement avec validation de mouvement significatif"""
    df['swing_high'] = np.nan
    df['swing_low'] = np.nan
    
    for i in range(SWING_PERIOD, len(df) - SWING_PERIOD):
        # === SWING HIGH AVANCÉ ===
        if df['high'].iloc[i] == df['high'].iloc[i-SWING_PERIOD:i+SWING_PERIOD+1].max():
            recent_low = df['low'].iloc[i-SWING_PERIOD:i].min()
            price_move_pct = ((df['high'].iloc[i] - recent_low) / recent_low) * 100
            
            if price_move_pct >= MIN_SWING_PERCENTAGE:
                df.iloc[i, df.columns.get_loc('swing_high')] = df['high'].iloc[i]
        
        # === SWING LOW AVANCÉ ===
        if df['low'].iloc[i] == df['low'].iloc[i-SWING_PERIOD:i+SWING_PERIOD+1].min():
            recent_high = df['high'].iloc[i-SWING_PERIOD:i].max()
            price_move_pct = ((recent_high - df['low'].iloc[i]) / recent_high) * 100
            
            if price_move_pct >= MIN_SWING_PERCENTAGE:
                df.iloc[i, df.columns.get_loc('swing_low')] = df['low'].iloc[i]
    
    return df

def analyze_bullish_divergence(df_window, current_idx):
    """Analyse spécifique pour divergence haussière"""
    # Trouver les swing lows récents dans la fenêtre
    swing_lows_mask = df_window['swing_low'].notna()
    swing_lows = df_window[swing_lows_mask].tail(3)
    
    if len(swing_lows) < 2:
        return None
    
    # Comparer les 2 derniers swing lows
    last_low = swing_lows.iloc[-1]
    prev_low = swing_lows.iloc[-2]
    
    price_low_1 = last_low['swing_low']
    price_low_2 = prev_low['swing_low']
    rsi_low_1 = last_low['rsi']
    rsi_low_2 = prev_low['rsi']
    
    # Condition de divergence haussière
    if price_low_1 < price_low_2 and rsi_low_1 > rsi_low_2:
        rsi_divergence = rsi_low_1 - rsi_low_2
        
        if rsi_divergence >= MIN_DIVERGENCE_STRENGTH:
            current_price = df_window['close'].iloc[-1]
            current_atr = df_window['atr'].iloc[-1]
            
            # Calcul SL et TP avec validation ATR
            stop_loss_price = price_low_1 - (current_price * 0.0005)
            risk_distance = current_price - stop_loss_price
            
            theoretical_tp = current_price + (risk_distance * RISK_REWARD_RATIO_TARGET)
            min_tp_by_atr = current_price + (current_atr * MIN_TP_ATR_MULTIPLIER)
            take_profit_price = max(theoretical_tp, min_tp_by_atr)
            
            final_risk = current_price - stop_loss_price
            final_reward = take_profit_price - current_price
            final_rr_ratio = final_reward / final_risk if final_risk > 0 else 0
            
            return {
                'signal': 'BUY',
                'entry_price': current_price,
                'sl': stop_loss_price,
                'tp': take_profit_price,
                'risk_distance': final_risk,
                'reward_distance': final_reward,
                'rr_ratio': final_rr_ratio,
                'strength': rsi_divergence,
                'entry_time': df_window.index[-1]
            }
    
    return None

def analyze_bearish_divergence(df_window, current_idx):
    """Analyse spécifique pour divergence baissière"""
    # Trouver les swing highs récents dans la fenêtre
    swing_highs_mask = df_window['swing_high'].notna()
    swing_highs = df_window[swing_highs_mask].tail(3)
    
    if len(swing_highs) < 2:
        return None
    
    # Comparer les 2 derniers swing highs
    last_high = swing_highs.iloc[-1]
    prev_high = swing_highs.iloc[-2]
    
    price_high_1 = last_high['swing_high']
    price_high_2 = prev_high['swing_high']
    rsi_high_1 = last_high['rsi']
    rsi_high_2 = prev_high['rsi']
    
    # Condition de divergence baissière
    if price_high_1 > price_high_2 and rsi_high_1 < rsi_high_2:
        rsi_divergence = rsi_high_2 - rsi_high_1
        
        if rsi_divergence >= MIN_DIVERGENCE_STRENGTH:
            current_price = df_window['close'].iloc[-1]
            current_atr = df_window['atr'].iloc[-1]
            
            # Calcul SL et TP avec validation ATR
            stop_loss_price = price_high_1 + (current_price * 0.0005)
            risk_distance = stop_loss_price - current_price
            
            theoretical_tp = current_price - (risk_distance * RISK_REWARD_RATIO_TARGET)
            min_tp_by_atr = current_price - (current_atr * MIN_TP_ATR_MULTIPLIER)
            take_profit_price = min(theoretical_tp, min_tp_by_atr)
            
            final_risk = stop_loss_price - current_price
            final_reward = current_price - take_profit_price
            final_rr_ratio = final_reward / final_risk if final_risk > 0 else 0
            
            return {
                'signal': 'SELL',
                'entry_price': current_price,
                'sl': stop_loss_price,
                'tp': take_profit_price,
                'risk_distance': final_risk,
                'reward_distance': final_reward,
                'rr_ratio': final_rr_ratio,
                'strength': rsi_divergence,
                'entry_time': df_window.index[-1]
            }
    
    return None

def run_backtest(df, start_date=None, end_date=None):
    """Exécute le backtesting sur la période spécifiée"""
    logging.info("=" * 80)
    logging.info("🎯 DÉMARRAGE DU BACKTESTING SNIPER STRATEGY")
    logging.info("=" * 80)
    
    # Filtrer les dates si spécifiées
    if start_date:
        df = df[df.index >= start_date]
    if end_date:
        df = df[df.index <= end_date]
    
    logging.info(f"📅 Période de test: {df.index[0]} → {df.index[-1]}")
    logging.info(f"📊 Nombre de bougies: {len(df)}")
    
    # Variables de simulation
    current_balance = INITIAL_BALANCE
    trades = []
    in_position = False
    position_entry = None
    
    # Métriques de performance
    total_signals = 0
    signals_filtered_by_trend = 0
    signals_filtered_by_volatility = 0
    
    # Parcourir les données pour détecter les signaux
    for i in range(250, len(df) - 1):  # Commencer après 250 bougies pour avoir les indicateurs
        current_window = df.iloc[:i+1]
        current_price = current_window['close'].iloc[-1]
        current_atr = current_window['atr'].iloc[-1]
        current_ema200 = current_window['ema200'].iloc[-1]
        
        # Filtre de volatilité
        if VOLATILITY_FILTER_ENABLED and current_atr < MIN_ATR_VALUE:
            continue
        
        # Si pas en position, chercher un signal
        if not in_position:
            recent_data = current_window.tail(LOOKBACK_PERIOD)
            signal = None
            
            # Test signal haussier (tendance haussière)
            if current_price > current_ema200:
                signal = analyze_bullish_divergence(recent_data, i)
                if signal:
                    total_signals += 1
            
            # Test signal baissier (tendance baissière)
            elif current_price < current_ema200:
                signal = analyze_bearish_divergence(recent_data, i)
                if signal:
                    total_signals += 1
            
            if signal:
                # Entrer en position
                in_position = True
                position_entry = signal.copy()
                position_entry['entry_index'] = i
        
        # Si en position, vérifier les sorties
        elif in_position:
            current_high = df.iloc[i]['high']
            current_low = df.iloc[i]['low']
            
            trade_closed = False
            exit_reason = ""
            exit_price = 0
            
            if position_entry['signal'] == 'BUY':
                # Vérifier TP
                if current_high >= position_entry['tp']:
                    exit_price = position_entry['tp']
                    exit_reason = "TP atteint"
                    trade_closed = True
                # Vérifier SL
                elif current_low <= position_entry['sl']:
                    exit_price = position_entry['sl']
                    exit_reason = "SL touché"
                    trade_closed = True
            
            elif position_entry['signal'] == 'SELL':
                # Vérifier TP
                if current_low <= position_entry['tp']:
                    exit_price = position_entry['tp']
                    exit_reason = "TP atteint"
                    trade_closed = True
                # Vérifier SL
                elif current_high >= position_entry['sl']:
                    exit_price = position_entry['sl']
                    exit_reason = "SL touché"
                    trade_closed = True
            
            if trade_closed:
                # Calculer le profit
                if position_entry['signal'] == 'BUY':
                    profit_points = exit_price - position_entry['entry_price']
                else:
                    profit_points = position_entry['entry_price'] - exit_price
                
                profit_dollars = profit_points * 100  # Approximation pour XAUUSD (100$ par point)
                
                # Ajouter le trade aux résultats
                trade_result = {
                    'entry_time': position_entry['entry_time'],
                    'exit_time': df.index[i],
                    'type': position_entry['signal'],
                    'entry_price': position_entry['entry_price'],
                    'exit_price': exit_price,
                    'sl': position_entry['sl'],
                    'tp': position_entry['tp'],
                    'profit_points': profit_points,
                    'profit_dollars': profit_dollars,
                    'exit_reason': exit_reason,
                    'strength': position_entry['strength'],
                    'rr_ratio': position_entry['rr_ratio'],
                    'duration_bars': i - position_entry['entry_index']
                }
                trades.append(trade_result)
                current_balance += profit_dollars
                
                # Reset position
                in_position = False
                position_entry = None
    
    # Analyser les résultats
    analyze_results(trades, current_balance, df)
    return trades, current_balance

def analyze_results(trades, final_balance, df):
    """Analyse et affiche les résultats du backtesting"""
    if len(trades) == 0:
        logging.info("❌ Aucun trade généré pendant la période de backtest")
        return
    
    # Métriques de base
    winning_trades = [t for t in trades if t['profit_dollars'] > 0]
    losing_trades = [t for t in trades if t['profit_dollars'] < 0]
    
    win_rate = len(winning_trades) / len(trades) * 100
    total_profit = sum(t['profit_dollars'] for t in trades)
    avg_win = np.mean([t['profit_dollars'] for t in winning_trades]) if winning_trades else 0
    avg_loss = np.mean([t['profit_dollars'] for t in losing_trades]) if losing_trades else 0
    avg_rr = np.mean([t['rr_ratio'] for t in trades])
    
    # Métriques avancées
    max_win = max([t['profit_dollars'] for t in trades])
    max_loss = min([t['profit_dollars'] for t in trades])
    avg_duration = np.mean([t['duration_bars'] for t in trades])
    
    # Calcul du drawdown maximum
    cumulative = [INITIAL_BALANCE]
    for trade in trades:
        cumulative.append(cumulative[-1] + trade['profit_dollars'])
    
    peak = INITIAL_BALANCE
    max_drawdown = 0
    for balance in cumulative:
        if balance > peak:
            peak = balance
        drawdown = (peak - balance) / peak * 100
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    # Affichage des résultats
    logging.info("=" * 80)
    logging.info("📊 RÉSULTATS DU BACKTESTING SNIPER STRATEGY")
    logging.info("=" * 80)
    
    # Performance générale
    logging.info("🎯 PERFORMANCE GÉNÉRALE")
    logging.info(f"📈 Nombre total de trades: {len(trades)}")
    logging.info(f"✅ Trades gagnants: {len(winning_trades)} ({win_rate:.1f}%)")
    logging.info(f"❌ Trades perdants: {len(losing_trades)} ({100-win_rate:.1f}%)")
    logging.info(f"💰 Profit total: {total_profit:.2f}$")
    logging.info(f"💹 Balance finale: {final_balance:.2f}$ (Initial: {INITIAL_BALANCE:.2f}$)")
    logging.info(f"📈 Rendement: {((final_balance - INITIAL_BALANCE) / INITIAL_BALANCE * 100):.2f}%")
    
    # Métriques détaillées
    logging.info("\n🔍 MÉTRIQUES DÉTAILLÉES")
    logging.info(f"💚 Gain moyen: {avg_win:.2f}$ | 🔴 Perte moyenne: {avg_loss:.2f}$")
    logging.info(f"🏆 Plus gros gain: {max_win:.2f}$ | 💥 Plus grosse perte: {max_loss:.2f}$")
    logging.info(f"⚖️ Ratio R/R moyen: 1:{avg_rr:.2f}")
    logging.info(f"⏱️ Durée moyenne trade: {avg_duration:.1f} bougies M15")
    logging.info(f"📉 Drawdown maximum: {max_drawdown:.2f}%")
    
    # Analyse par type de trade
    buy_trades = [t for t in trades if t['type'] == 'BUY']
    sell_trades = [t for t in trades if t['type'] == 'SELL']
    
    if buy_trades:
        buy_win_rate = len([t for t in buy_trades if t['profit_dollars'] > 0]) / len(buy_trades) * 100
        buy_profit = sum(t['profit_dollars'] for t in buy_trades)
        logging.info(f"\n📈 TRADES BUY: {len(buy_trades)} trades | Win Rate: {buy_win_rate:.1f}% | Profit: {buy_profit:.2f}$")
    
    if sell_trades:
        sell_win_rate = len([t for t in sell_trades if t['profit_dollars'] > 0]) / len(sell_trades) * 100
        sell_profit = sum(t['profit_dollars'] for t in sell_trades)
        logging.info(f"📉 TRADES SELL: {len(sell_trades)} trades | Win Rate: {sell_win_rate:.1f}% | Profit: {sell_profit:.2f}$")
    
    # Top 5 meilleurs et pires trades
    logging.info("\n🏆 TOP 5 MEILLEURS TRADES")
    best_trades = sorted(trades, key=lambda x: x['profit_dollars'], reverse=True)[:5]
    for i, trade in enumerate(best_trades, 1):
        logging.info(f"{i}. {trade['type']} - {trade['entry_time'].strftime('%Y-%m-%d %H:%M')} - "
                    f"Profit: {trade['profit_dollars']:.2f}$ ({trade['exit_reason']})")
    
    logging.info("\n💥 TOP 5 PIRES TRADES")
    worst_trades = sorted(trades, key=lambda x: x['profit_dollars'])[:5]
    for i, trade in enumerate(worst_trades, 1):
        logging.info(f"{i}. {trade['type']} - {trade['entry_time'].strftime('%Y-%m-%d %H:%M')} - "
                    f"Perte: {trade['profit_dollars']:.2f}$ ({trade['exit_reason']})")
    
    logging.info("=" * 80)
    
    # Évaluation finale
    if win_rate >= 50 and total_profit > 0 and max_drawdown < 20:
        logging.info("✅ VERDICT: Stratégie PROMETTEUSE - Recommandée pour trading live")
    elif win_rate >= 40 and total_profit > 0:
        logging.info("⚠️ VERDICT: Stratégie ACCEPTABLE - Trading live avec prudence")
    else:
        logging.info("❌ VERDICT: Stratégie NON RECOMMANDÉE - Ajustements nécessaires")

def main():
    """Fonction principale du backtesting"""
    print("🎯 SNIPER BOT BACKTESTING - Version CSV")
    print("=" * 50)
    
    # Charger les données
    df = load_data()
    if df is None:
        return
    
    # Calculer les indicateurs
    df = calculate_indicators(df)
    if df is None:
        return
    
    # Options de test
    print("\n📅 OPTIONS DE PÉRIODE DE TEST:")
    print("1. Toute la période disponible")
    print("2. 6 derniers mois")
    print("3. 1 dernière année")
    print("4. Période personnalisée")
    
    try:
        choice = input("\nChoisissez une option (1-4): ").strip()
        
        start_date = None
        end_date = None
        
        if choice == "2":
            end_date = df.index[-1]
            start_date = end_date - timedelta(days=180)
            logging.info(f"Test sur 6 derniers mois: {start_date} → {end_date}")
        elif choice == "3":
            end_date = df.index[-1]
            start_date = end_date - timedelta(days=365)
            logging.info(f"Test sur 1 dernière année: {start_date} → {end_date}")
        elif choice == "4":
            start_str = input("Date de début (YYYY-MM-DD): ").strip()
            end_str = input("Date de fin (YYYY-MM-DD): ").strip()
            start_date = pd.to_datetime(start_str)
            end_date = pd.to_datetime(end_str)
            logging.info(f"Test sur période personnalisée: {start_date} → {end_date}")
        else:
            logging.info("Test sur toute la période disponible")
        
        # Lancer le backtesting
        trades, final_balance = run_backtest(df, start_date, end_date)
        
        # Sauvegarder les résultats
        if trades:
            trades_df = pd.DataFrame(trades)
            trades_df.to_csv("sniper_backtest_results.csv", index=False)
            logging.info("💾 Résultats sauvegardés dans 'sniper_backtest_results.csv'")
        
    except KeyboardInterrupt:
        logging.info("🛑 Backtesting interrompu par l'utilisateur")
    except Exception as e:
        logging.error(f"❌ Erreur durant le backtesting: {e}")

if __name__ == "__main__":
    main()
