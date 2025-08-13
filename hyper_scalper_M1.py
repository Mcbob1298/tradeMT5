#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HYPER-SCALPER M1 - Version Ultra Haute Fréquence avec Filtre ADX
Calibrage automatique optimisé pour le timeframe M1 (1 minute)
OBJECTIF: Scalping ultra-rapide avec micro-profits haute fréquence
Philosophie: Quantité over qualité - Capitaliser sur les micro-impulsions
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

# =============================================================================
# CONFIGURATION DE BASE POUR CALIBRAGE M1 HYPER-SCALPER
# =============================================================================
RISK_REWARD_RATIO_TARGET = 1.3             # RR très conservateur pour M1
RISK_PER_TRADE_PERCENT = 1.0            
EMA_PERIOD_LONG = 200                   
EMA_PERIOD_MEDIUM = 50                  
EMA_PERIOD_SHORT = 20                   
RSI_PERIOD = 14                         
LOOKBACK_PERIOD = 50                    
SWING_PERIOD = 3                        # Très réduit pour M1 (ultra-réactif)
ATR_PERIOD = 14                         
ADX_PERIOD = 14                         

# =============================================================================
# PARAMÈTRES DE CALIBRAGE AUTOMATIQUE POUR M1 HYPER-SCALPER
# =============================================================================
# Plage de test pour MIN_DIVERGENCE_STRENGTH (ajustée pour M1 bruyant)
DIVERGENCE_TEST_RANGE = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

# Filtre ADX - Régime de marché (ajusté pour micro-impulsions M1)
ADX_TEST_RANGE = [15, 17, 19, 21, 23, 25, 27, 30]  # Très bas pour capter micro-tendances

# Ratio Risk/Reward - Test (très conservateur pour M1)
RR_TEST_RANGE = [1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8]  # Ratios serrés pour M1

TARGET_TRADES_PER_DAY = [10, 50]        # Objectif ambitieux pour M1
MIN_PROFIT_FACTOR = 1.10                # Seuil très bas mais réaliste pour M1
CSV_FILE = "XAUUSD_M1.csv"             # Fichier de données M1
INITIAL_BALANCE = 300.0

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def load_data():
    """Charge et prépare les données M1 depuis le fichier CSV"""
    try:
        logging.info(f"📂 Chargement des données M1 HYPER-SCALPER depuis {CSV_FILE}...")
        
        df = pd.read_csv(CSV_FILE, header=None, names=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        
        logging.info(f"✅ {len(df)} bougies M1 chargées")
        logging.info(f"📅 Période: {df.index[0]} → {df.index[-1]}")
        
        # Calcul approximatif du nombre de jours
        total_days = (df.index[-1] - df.index[0]).days
        logging.info(f"📊 Approximativement {total_days} jours de données ultra-haute fréquence")
        
        return df
        
    except Exception as e:
        logging.error(f"❌ Erreur chargement données M1: {e}")
        return None

def calculate_adx(df):
    """
    Calcule l'ADX (Average Directional Index) pour mesurer la force de tendance
    Optimisé pour M1: détection de micro-impulsions très courtes
    """
    # Calcul des mouvements directionnels
    df['high_diff'] = df['high'].diff()
    df['low_diff'] = df['low'].diff()
    
    # Plus DM et Moins DM
    df['plus_dm'] = np.where((df['high_diff'] > df['low_diff']) & (df['high_diff'] > 0), df['high_diff'], 0)
    df['minus_dm'] = np.where((df['low_diff'] > df['high_diff']) & (df['low_diff'] > 0), df['low_diff'], 0)
    
    # True Range
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # Moyennes mobiles exponentielles
    alpha = 1.0 / ADX_PERIOD
    
    # ATR lissé
    df['atr_smooth'] = true_range.ewm(alpha=alpha, adjust=False).mean()
    
    # Plus DI et Minus DI
    plus_dm_smooth = df['plus_dm'].ewm(alpha=alpha, adjust=False).mean()
    minus_dm_smooth = df['minus_dm'].ewm(alpha=alpha, adjust=False).mean()
    
    df['plus_di'] = 100 * (plus_dm_smooth / df['atr_smooth'])
    df['minus_di'] = 100 * (minus_dm_smooth / df['atr_smooth'])
    
    # DX (Directional Movement Index)
    df['dx'] = 100 * np.abs(df['plus_di'] - df['minus_di']) / (df['plus_di'] + df['minus_di'])
    df['dx'] = df['dx'].fillna(0)
    
    # ADX (moyenne mobile de DX)
    df['adx'] = df['dx'].ewm(alpha=alpha, adjust=False).mean()
    
    # Nettoyer les colonnes temporaires
    df.drop(['high_diff', 'low_diff', 'plus_dm', 'minus_dm', 'atr_smooth'], axis=1, inplace=True)
    
    return df

def calculate_indicators(df):
    """Calcule tous les indicateurs techniques optimisés pour M1"""
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
        
        # ADX - Indicateur de force de tendance
        df = calculate_adx(df)
        
        # Swing points (ajustés pour M1 ultra-réactif)
        df = detect_swing_points(df)
        
        return df
        
    except Exception as e:
        logging.error(f"❌ Erreur calcul indicateurs: {e}")
        return None

def detect_swing_points(df):
    """Détecte les swing points optimisés pour M1 (ultra-réactifs)"""
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

def analyze_bullish_divergence(df_window, current_idx, min_divergence_strength, min_adx_value, rr_ratio):
    """Analyse pour divergence haussière M1 avec filtres ultra-légers"""
    
    # FILTRE ADX - Détection de micro-impulsion
    current_adx = df_window['adx'].iloc[-1]
    if pd.isna(current_adx) or current_adx < min_adx_value:
        return None  # Même en M1, on évite les marchés complètement plats
    
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
            
            # Filtre de tendance très léger pour M1
            if current_price <= current_ema200:
                return None
            
            # Calcul SL et TP avec RR ratio très serré pour M1
            stop_loss_price = price_low_1 - (current_price * 0.0003)  # SL plus serré pour M1
            risk_distance = current_price - stop_loss_price
            take_profit_price = current_price + (risk_distance * rr_ratio)
            
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
                'entry_time': df_window.index[-1],
                'adx': current_adx
            }
    
    return None

def analyze_bearish_divergence(df_window, current_idx, min_divergence_strength, min_adx_value, rr_ratio):
    """Analyse pour divergence baissière M1 avec filtres ultra-légers"""
    
    # FILTRE ADX - Détection de micro-impulsion
    current_adx = df_window['adx'].iloc[-1]
    if pd.isna(current_adx) or current_adx < min_adx_value:
        return None  # Même en M1, on évite les marchés complètement plats
    
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
            
            # Filtre de tendance très léger pour M1
            if current_price >= current_ema200:
                return None
            
            # Calcul SL et TP avec RR ratio très serré pour M1
            stop_loss_price = price_high_1 + (current_price * 0.0003)  # SL plus serré pour M1
            risk_distance = stop_loss_price - current_price
            take_profit_price = current_price - (risk_distance * rr_ratio)
            
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
                'entry_time': df_window.index[-1],
                'adx': current_adx
            }
    
    return None

def run_single_backtest(df, min_divergence_strength, min_adx_value, rr_ratio, start_date=None, end_date=None):
    """Exécute un backtest M1 ultra-haute fréquence avec paramètres configurables"""
    if start_date:
        df = df[df.index >= start_date]
    if end_date:
        df = df[df.index <= end_date]
    
    # Variables de simulation
    current_balance = INITIAL_BALANCE
    trades = []
    in_position = False
    position_entry = None
    
    # Parcourir les données (ajusté pour M1 ultra-rapide)
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
                signal = analyze_bullish_divergence(recent_data, i, min_divergence_strength, min_adx_value, rr_ratio)
            
            # Test signal baissier
            elif current_price < current_ema200:
                signal = analyze_bearish_divergence(recent_data, i, min_divergence_strength, min_adx_value, rr_ratio)
            
            if signal:
                in_position = True
                position_entry = signal.copy()
                position_entry['entry_index'] = i
        
        # Si en position, vérifier les sorties (très rapide en M1)
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
                    'duration_bars': i - position_entry['entry_index'],
                    'adx': position_entry.get('adx', 0)
                }
                trades.append(trade_result)
                current_balance += profit_dollars
                
                in_position = False
                position_entry = None
    
    return trades, current_balance

def run_hyper_scalper_m1_calibration(df):
    """Lance le calibrage complet pour M1 HYPER-SCALPER avec tous les paramètres"""
    logging.info("🚀 DÉMARRAGE DU CALIBRAGE HYPER-SCALPER M1")
    logging.info(f"⚡ Test de {len(DIVERGENCE_TEST_RANGE)} seuils de divergence")
    logging.info(f"🌊 Test de {len(ADX_TEST_RANGE)} seuils ADX (micro-impulsions)")
    logging.info(f"⚖️ Test de {len(RR_TEST_RANGE)} ratios R/R (serrés pour M1)")
    
    total_tests = len(DIVERGENCE_TEST_RANGE) * len(ADX_TEST_RANGE) * len(RR_TEST_RANGE)
    logging.info(f"🎯 Total: {total_tests} configurations HYPER-SCALPER à tester")
    
    results = []
    test_count = 0
    
    for divergence in DIVERGENCE_TEST_RANGE:
        for adx_threshold in ADX_TEST_RANGE:
            for rr_ratio in RR_TEST_RANGE:
                test_count += 1
                logging.info(f"⚡ Test {test_count}/{total_tests} - "
                           f"Div: {divergence}, ADX: {adx_threshold}, RR: {rr_ratio}...")
                
                trades, final_balance = run_single_backtest(df, divergence, adx_threshold, rr_ratio)
                profit = final_balance - INITIAL_BALANCE
                
                config = {
                    'divergence_strength': divergence,
                    'adx_threshold': adx_threshold,
                    'rr_ratio': rr_ratio,
                    'trades': trades,
                    'final_balance': final_balance,
                    'profit': profit,
                    'num_trades': len(trades)
                }
                
                if len(trades) > 0:
                    winning_trades = [t for t in trades if t['profit_dollars'] > 0]
                    config['win_rate'] = len(winning_trades) / len(trades) * 100
                    
                    total_wins = sum(t['profit_dollars'] for t in winning_trades)
                    total_losses = abs(sum(t['profit_dollars'] for t in trades if t['profit_dollars'] < 0))
                    config['profit_factor'] = total_wins / total_losses if total_losses > 0 else float('inf')
                    
                    # Score composite pour M1 HYPER-SCALPER
                    frequency_score = min(len(trades) / 200, 3.0)  # Bonus élevé pour ultra-haute fréquence
                    profit_score = max(profit / 300, 0) if profit > 0 else profit / 300
                    factor_score = min(config['profit_factor'], 2.0) if config['profit_factor'] >= 1.10 else 0
                    
                    config['total_score'] = frequency_score + profit_score + factor_score
                else:
                    config['win_rate'] = 0
                    config['profit_factor'] = 0
                    config['total_score'] = 0
                
                results.append(config)
                
                # Affichage rapide du résultat
                logging.info(f"   → {len(trades)} trades | {profit:.0f}$ | "
                           f"WR: {config['win_rate']:.1f}% | PF: {config['profit_factor']:.2f}")
    
    # Analyser et trouver la meilleure configuration
    best_config = max(results, key=lambda x: x['total_score'])
    
    logging.info("=" * 80)
    logging.info("🏆 MEILLEURE CONFIGURATION HYPER-SCALPER M1 TROUVÉE:")
    logging.info(f"⚡ Seuil de divergence: {best_config['divergence_strength']}")
    logging.info(f"🌊 Seuil ADX: {best_config['adx_threshold']}")
    logging.info(f"⚖️ Ratio R/R: {best_config['rr_ratio']}")
    logging.info(f"📈 Nombre de trades: {best_config['num_trades']}")
    logging.info(f"💰 Profit total: {best_config['profit']:.2f}$")
    logging.info(f"✅ Win rate: {best_config['win_rate']:.1f}%")
    logging.info(f"⚖️ Facteur de profit: {best_config['profit_factor']:.2f}")
    logging.info(f"🏅 Score total: {best_config['total_score']:.2f}")
    
    # Calculer la fréquence approximative
    if best_config['trades']:
        total_days = (df.index[-1] - df.index[0]).days
        trades_per_day = best_config['num_trades'] / total_days if total_days > 0 else 0
        trades_per_hour = trades_per_day / 24
        logging.info(f"🚀 Fréquence: ~{trades_per_hour:.2f} trades/heure (HYPER-SCALPING!)")
    
    # Sauvegarder la meilleure configuration
    if best_config['trades']:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"hyper_scalper_M1_optimal_{timestamp}.csv"
        trades_df = pd.DataFrame(best_config['trades'])
        trades_df.to_csv(filename, index=False)
        logging.info(f"💾 Configuration optimale HYPER-SCALPER M1 sauvegardée: {filename}")
    
    logging.info("=" * 80)
    return best_config, results

def main():
    """Fonction principale du HYPER-SCALPER M1"""
    print("🚀 HYPER-SCALPER M1 - CALIBREUR ULTRA HAUTE FRÉQUENCE")
    print("Objectif: Scalping ultra-rapide avec micro-profits")
    print("⚡ Triple calibrage: Divergence + ADX + Risk/Reward (serrés)")
    print("🎯 Cible: Plusieurs trades par heure")
    print("=" * 60)
    
    df = load_data()
    if df is None:
        return
    
    logging.info("🔧 Calcul des indicateurs optimisés pour M1 HYPER-SCALPING...")
    df = calculate_indicators(df)
    if df is None:
        return
    
    logging.info("✅ Données M1 préparées - Démarrage du calibrage HYPER-SCALPER")
    
    # Lancer le calibrage complet M1
    best_config, all_results = run_hyper_scalper_m1_calibration(df)
    
    if best_config and best_config['total_score'] > 0:
        logging.info("🎉 CALIBRAGE HYPER-SCALPER M1 TERMINÉ AVEC SUCCÈS!")
        logging.info("💡 Configuration optimale trouvée pour ultra-haute fréquence")
    else:
        logging.info("⚠️ Calibrage M1 terminé - Environnement très challengeant")
        logging.info("🔧 Le M1 est le timeframe le plus difficile - résultats attendus")

if __name__ == "__main__":
    main()
