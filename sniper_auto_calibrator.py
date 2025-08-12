#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNIPER BOT CALIBREUR - Version Auto-Optimization
Test automatique de différents seuils de divergence pour trouver le sweet spot
Objectif: 1-2 trades par heure avec facteur de profit > 1.10
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

# =============================================================================
# CONFIGURATION DE BASE POUR CALIBRAGE
# =============================================================================
RISK_REWARD_RATIO_TARGET = 1.8          
RISK_PER_TRADE_PERCENT = 1.0            
EMA_PERIOD_LONG = 200                   
EMA_PERIOD_MEDIUM = 50                  
EMA_PERIOD_SHORT = 20                   
RSI_PERIOD = 14                         
LOOKBACK_PERIOD = 50                    
SWING_PERIOD = 7                        
ATR_PERIOD = 14                         

# =============================================================================
# PARAMÈTRES DE CALIBRAGE AUTOMATIQUE
# =============================================================================
# Plage de test pour MIN_DIVERGENCE_STRENGTH
DIVERGENCE_TEST_RANGE = [4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0]
TARGET_TRADES_PER_YEAR = [50, 100]      # Objectif: 50-100 trades/an
MIN_PROFIT_FACTOR = 1.10                # Facteur de profit minimum acceptable
CSV_FILE = "XAUUSD_M15.csv"
INITIAL_BALANCE = 10000.0

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
        
        df = pd.read_csv(CSV_FILE, header=None, names=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        
        logging.info(f"✅ {len(df)} bougies chargées")
        logging.info(f"📅 Période: {df.index[0]} → {df.index[-1]}")
        
        return df
        
    except Exception as e:
        logging.error(f"❌ Erreur chargement données: {e}")
        return None

def calculate_indicators(df):
    """Calcule tous les indicateurs techniques"""
    try:
        # EMA pour les tendances
        df['ema200'] = df['close'].ewm(span=EMA_PERIOD_LONG).mean()
        df['ema50'] = df['close'].ewm(span=EMA_PERIOD_MEDIUM).mean()
        df['ema20'] = df['close'].ewm(span=EMA_PERIOD_SHORT).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/RSI_PERIOD, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/RSI_PERIOD, adjust=False).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # ATR
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['atr'] = true_range.rolling(window=ATR_PERIOD).mean()
        
        # Swing points
        df = detect_swing_points(df)
        
        return df
        
    except Exception as e:
        logging.error(f"❌ Erreur calcul indicateurs: {e}")
        return None

def detect_swing_points(df):
    """Détecte les swing points pour les divergences"""
    df['swing_high'] = np.nan
    df['swing_low'] = np.nan
    
    for i in range(SWING_PERIOD, len(df) - SWING_PERIOD):
        # Swing High
        if df['high'].iloc[i] == df['high'].iloc[i-SWING_PERIOD:i+SWING_PERIOD+1].max():
            df.iloc[i, df.columns.get_loc('swing_high')] = df['high'].iloc[i]
        
        # Swing Low
        if df['low'].iloc[i] == df['low'].iloc[i-SWING_PERIOD:i+SWING_PERIOD+1].min():
            df.iloc[i, df.columns.get_loc('swing_low')] = df['low'].iloc[i]
    
    return df

def analyze_bullish_divergence(df_window, current_idx, min_divergence_strength):
    """Analyse pour divergence haussière avec seuil configurable"""
    swing_lows_mask = df_window['swing_low'].notna()
    swing_lows = df_window[swing_lows_mask].tail(3)
    
    if len(swing_lows) < 2:
        return None
    
    last_low = swing_lows.iloc[-1]
    prev_low = swing_lows.iloc[-2]
    
    price_low_1 = last_low['swing_low']
    price_low_2 = prev_low['swing_low']
    rsi_low_1 = last_low['rsi']
    rsi_low_2 = prev_low['rsi']
    
    # Condition de divergence haussière
    if price_low_1 < price_low_2 and rsi_low_1 > rsi_low_2:
        rsi_divergence = rsi_low_1 - rsi_low_2
        
        if rsi_divergence >= min_divergence_strength:
            current_price = df_window['close'].iloc[-1]
            current_atr = df_window['atr'].iloc[-1]
            current_ema200 = df_window['ema200'].iloc[-1]
            
            # Filtre de tendance de base
            if current_price <= current_ema200:
                return None
            
            # Calcul SL et TP
            stop_loss_price = price_low_1 - (current_price * 0.0005)
            risk_distance = current_price - stop_loss_price
            take_profit_price = current_price + (risk_distance * RISK_REWARD_RATIO_TARGET)
            
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

def analyze_bearish_divergence(df_window, current_idx, min_divergence_strength):
    """Analyse pour divergence baissière avec seuil configurable"""
    swing_highs_mask = df_window['swing_high'].notna()
    swing_highs = df_window[swing_highs_mask].tail(3)
    
    if len(swing_highs) < 2:
        return None
    
    last_high = swing_highs.iloc[-1]
    prev_high = swing_highs.iloc[-2]
    
    price_high_1 = last_high['swing_high']
    price_high_2 = prev_high['swing_high']
    rsi_high_1 = last_high['rsi']
    rsi_high_2 = prev_high['rsi']
    
    # Condition de divergence baissière
    if price_high_1 > price_high_2 and rsi_high_1 < rsi_high_2:
        rsi_divergence = rsi_high_2 - rsi_high_1
        
        if rsi_divergence >= min_divergence_strength:
            current_price = df_window['close'].iloc[-1]
            current_atr = df_window['atr'].iloc[-1]
            current_ema200 = df_window['ema200'].iloc[-1]
            
            # Filtre de tendance de base
            if current_price >= current_ema200:
                return None
            
            # Calcul SL et TP
            stop_loss_price = price_high_1 + (current_price * 0.0005)
            risk_distance = stop_loss_price - current_price
            take_profit_price = current_price - (risk_distance * RISK_REWARD_RATIO_TARGET)
            
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

def run_single_backtest(df, min_divergence_strength, start_date=None, end_date=None):
    """Exécute un backtest avec un seuil de divergence spécifique"""
    if start_date:
        df = df[df.index >= start_date]
    if end_date:
        df = df[df.index <= end_date]
    
    # Variables de simulation
    current_balance = INITIAL_BALANCE
    trades = []
    in_position = False
    position_entry = None
    
    # Parcourir les données
    for i in range(250, len(df) - 1):
        current_window = df.iloc[:i+1]
        current_price = current_window['close'].iloc[-1]
        current_ema200 = current_window['ema200'].iloc[-1]
        
        # Si pas en position, chercher un signal
        if not in_position:
            recent_data = current_window.tail(LOOKBACK_PERIOD)
            signal = None
            
            # Test signal haussier
            if current_price > current_ema200:
                signal = analyze_bullish_divergence(recent_data, i, min_divergence_strength)
            
            # Test signal baissier
            elif current_price < current_ema200:
                signal = analyze_bearish_divergence(recent_data, i, min_divergence_strength)
            
            if signal:
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
                if current_high >= position_entry['tp']:
                    exit_price = position_entry['tp']
                    exit_reason = "TP atteint"
                    trade_closed = True
                elif current_low <= position_entry['sl']:
                    exit_price = position_entry['sl']
                    exit_reason = "SL touché"
                    trade_closed = True
            
            elif position_entry['signal'] == 'SELL':
                if current_low <= position_entry['tp']:
                    exit_price = position_entry['tp']
                    exit_reason = "TP atteint"
                    trade_closed = True
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
                
                profit_dollars = profit_points * 100
                
                trade_result = {
                    'entry_time': position_entry['entry_time'],
                    'exit_time': df.index[i],
                    'type': position_entry['signal'],
                    'entry_price': position_entry['entry_price'],
                    'exit_price': exit_price,
                    'profit_points': profit_points,
                    'profit_dollars': profit_dollars,
                    'exit_reason': exit_reason,
                    'strength': position_entry['strength'],
                    'rr_ratio': position_entry['rr_ratio'],
                    'duration_bars': i - position_entry['entry_index']
                }
                trades.append(trade_result)
                current_balance += profit_dollars
                
                in_position = False
                position_entry = None
    
    return trades, current_balance

def analyze_calibration_results(results):
    """Analyse les résultats de calibrage pour trouver le sweet spot"""
    logging.info("=" * 80)
    logging.info("📊 RÉSULTATS DU CALIBRAGE AUTOMATIQUE")
    logging.info("=" * 80)
    
    best_config = None
    best_score = 0
    
    for config in results:
        divergence = config['divergence_strength']
        trades = config['trades']
        balance = config['final_balance']
        profit = balance - INITIAL_BALANCE
        num_trades = len(trades)
        
        if num_trades > 0:
            winning_trades = [t for t in trades if t['profit_dollars'] > 0]
            win_rate = len(winning_trades) / num_trades * 100
            avg_profit = np.mean([t['profit_dollars'] for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t['profit_dollars'] for t in trades if t['profit_dollars'] < 0])
            profit_factor = abs(sum(t['profit_dollars'] for t in winning_trades) / sum(t['profit_dollars'] for t in trades if t['profit_dollars'] < 0)) if any(t['profit_dollars'] < 0 for t in trades) else float('inf')
            
            # Calcul du score composite
            frequency_score = min(num_trades / 50, 2.0)  # Max 2 points pour fréquence
            profit_score = max(profit / 1000, 0) if profit > 0 else profit / 1000  # Points pour profit
            factor_score = min(profit_factor, 2.0) if profit_factor >= 1.0 else 0  # Points pour facteur
            
            total_score = frequency_score + profit_score + factor_score
            
            config['win_rate'] = win_rate
            config['profit_factor'] = profit_factor
            config['total_score'] = total_score
            
            if total_score > best_score:
                best_score = total_score
                best_config = config
        else:
            config['win_rate'] = 0
            config['profit_factor'] = 0
            config['total_score'] = 0
        
        # Affichage des résultats
        status = "🔥" if profit > 500 and profit_factor > 1.2 else "✅" if profit > 0 else "❌"
        logging.info(f"{status} Divergence {divergence:.1f}: {num_trades} trades | Profit: {profit:.0f}$ | "
                    f"Win Rate: {config['win_rate']:.1f}% | Factor: {config['profit_factor']:.2f}")
    
    # Recommandation finale
    logging.info("=" * 80)
    if best_config:
        logging.info("🏆 CONFIGURATION OPTIMALE TROUVÉE:")
        logging.info(f"🎯 Seuil de divergence: {best_config['divergence_strength']}")
        logging.info(f"📈 Nombre de trades: {len(best_config['trades'])}")
        logging.info(f"💰 Profit total: {best_config['final_balance'] - INITIAL_BALANCE:.2f}$")
        logging.info(f"✅ Win rate: {best_config['win_rate']:.1f}%")
        logging.info(f"⚖️ Facteur de profit: {best_config['profit_factor']:.2f}")
        logging.info(f"🏅 Score total: {best_config['total_score']:.2f}")
        
        # Sauvegarder la meilleure configuration
        if best_config['trades']:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"sniper_calibrated_optimal_{timestamp}.csv"
            trades_df = pd.DataFrame(best_config['trades'])
            trades_df.to_csv(filename, index=False)
            logging.info(f"💾 Configuration optimale sauvegardée: {filename}")
    else:
        logging.info("❌ Aucune configuration profitable trouvée")
        logging.info("💡 Suggestions: Élargir la plage de test ou assouplir d'autres filtres")
    
    logging.info("=" * 80)
    return best_config

def run_auto_calibration(df):
    """Lance le calibrage automatique sur TOUTE la période disponible"""
    logging.info("🎯 DÉMARRAGE DU CALIBRAGE AUTOMATIQUE")
    logging.info(f"🔧 Test de {len(DIVERGENCE_TEST_RANGE)} configurations de divergence")
    logging.info(f"📊 Plage testée: {min(DIVERGENCE_TEST_RANGE)} → {max(DIVERGENCE_TEST_RANGE)}")
    
    # Test sur TOUTE la période disponible pour maximum de données
    start_date = None  # Début du CSV
    end_date = None    # Fin du CSV
    
    logging.info(f"📅 Période de calibrage: {df.index[0]} → {df.index[-1]} (TOUTE LA PÉRIODE)")
    logging.info(f"📊 Nombre total de bougies: {len(df)}")
    
    results = []
    
    for i, divergence_strength in enumerate(DIVERGENCE_TEST_RANGE, 1):
        logging.info(f"🔄 Test {i}/{len(DIVERGENCE_TEST_RANGE)} - Divergence {divergence_strength}...")
        
        trades, final_balance = run_single_backtest(df, divergence_strength, start_date, end_date)
        
        results.append({
            'divergence_strength': divergence_strength,
            'trades': trades,
            'final_balance': final_balance,
            'num_trades': len(trades)
        })
        
        # Affichage intermédiaire du résultat
        profit = final_balance - INITIAL_BALANCE
        logging.info(f"   → {len(trades)} trades | Profit: {profit:.0f}$")
    
    # Analyser les résultats et trouver le sweet spot
    best_config = analyze_calibration_results(results)
    
    return best_config, results

def main():
    """Fonction principale du calibreur automatique"""
    print("🎯 SNIPER BOT CALIBREUR AUTOMATIQUE")
    print("Objectif: Trouver le sweet spot qualité/quantité optimal")
    print("=" * 60)
    
    df = load_data()
    if df is None:
        return
    
    logging.info("🔧 Calcul des indicateurs pour calibrage...")
    df = calculate_indicators(df)
    if df is None:
        return
    
    logging.info("✅ Données préparées - Démarrage du calibrage")
    
    # Lancer le calibrage automatique
    best_config, all_results = run_auto_calibration(df)
    
    if best_config:
        logging.info("🎉 CALIBRAGE TERMINÉ AVEC SUCCÈS!")
        logging.info(f"💡 Utilisez MIN_DIVERGENCE_STRENGTH = {best_config['divergence_strength']} dans votre bot final")
    else:
        logging.info("⚠️ Calibrage terminé - Aucune configuration optimale trouvée")
        logging.info("🔧 Suggestions d'ajustement supplémentaires nécessaires")

if __name__ == "__main__":
    main()
