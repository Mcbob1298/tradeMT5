#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNIPER BOT ÉQUILIBRÉ - Version 4.0
Basé sur les résultats ultra-optimisés : Qualité + Quantité optimale
Objectif: 10-20 trades/an avec maintien du ratio R/R élevé
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

# =============================================================================
# CONFIGURATION ÉQUILIBRÉE - SWEET SPOT QUALITÉ/QUANTITÉ
# =============================================================================
RISK_REWARD_RATIO_TARGET = 1.8          
RISK_PER_TRADE_PERCENT = 1.0            

# === ASSOUPLISSEMENT CONTRÔLÉ DES FILTRES ===
MIN_DIVERGENCE_STRENGTH = 6.0           # ⬇️ De 8 à 6 (plus de signaux)
EMA_PERIOD_LONG = 200                   # Tendance de fond (gardé)
EMA_PERIOD_MEDIUM = 50                  # Tendance moyenne (simplifié)
EMA_PERIOD_SHORT = 20                   # Tendance courte (simplifié)
RSI_PERIOD = 14                         
LOOKBACK_PERIOD = 50                    
SWING_PERIOD = 7                        # ⬇️ De 8 à 7 (swings plus fréquents)
ATR_PERIOD = 14                         

# =============================================================================
# FILTRES ÉQUILIBRÉS (MOINS RESTRICTIFS)
# =============================================================================
# 1. FILTRE DE VOLATILITÉ ATR ASSOUPLI
ATR_VOLATILITY_FILTER = True           
ATR_LOOKBACK_PERIOD = 100               
ATR_MINIMUM_MULTIPLIER = 1.0            # ⬇️ De 1.2 à 1.0 (accepter volatilité normale)

# 2. TAKE PROFIT DYNAMIQUE PLUS ACCESSIBLE
DYNAMIC_TP_ENABLED = True               
MIN_RR_RATIO_REQUIRED = 1.3             # ⬇️ De 1.5 à 1.3 (objectifs plus réalistes)
MAX_TP_DISTANCE_ATR = 5.0               # ⬆️ De 4.0 à 5.0 (objectifs plus ambitieux)

# 3. TENDANCE SIMPLIFIÉE (COMME SUGGÉRÉ)
SIMPLIFIED_TREND_FILTER = True          # ⭐ NOUVEAU: Simplification
ONLY_EMA200_FILTER = True               # ⭐ Utiliser seulement EMA200 comme filtre principal
EMA_SECONDARY_CONFIRMATION = False      # ⭐ Désactiver la triple confirmation

# 4. FILTRE RSI MOMENTUM ASSOUPLI
RSI_MOMENTUM_FILTER = True              
RSI_OVERBOUGHT_LEVEL = 80               # ⬆️ De 75 à 80 (moins restrictif)
RSI_OVERSOLD_LEVEL = 20                 # ⬇️ De 25 à 20 (moins restrictif)

# =============================================================================
# NOUVEAU: ANALYSE DES "PRESQUE-SIGNAUX"
# =============================================================================
TRACK_NEAR_MISS_SIGNALS = True          # Tracker les signaux ratés de peu
NEAR_MISS_DIVERGENCE_THRESHOLD = 4.5    # Seuil pour "presque divergence"

# =============================================================================
# PARAMÈTRES DE BACKTESTING
# =============================================================================
INITIAL_BALANCE = 300.0  
CSV_FILE = "XAUUSD_M15.csv"

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def load_data():
    """Charge les données CSV"""
    try:
        logging.info(f"📂 Chargement des données depuis {CSV_FILE}...")
        df = pd.read_csv(CSV_FILE, header=None, names=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        logging.info(f"✅ {len(df)} bougies chargées")
        return df
    except Exception as e:
        logging.error(f"❌ Erreur chargement données: {e}")
        return None

def calculate_indicators(df):
    """Calcule les indicateurs avec configuration équilibrée"""
    try:
        logging.info("🔧 Calcul des indicateurs équilibrés...")
        
        # EMAs pour la tendance
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
        
        # ATR moyenne pour le filtre de volatilité
        df['atr_avg'] = df['atr'].rolling(window=ATR_LOOKBACK_PERIOD).mean()
        
        # Swing points équilibrés
        df = detect_swing_points_balanced(df)
        
        logging.info("✅ Indicateurs équilibrés calculés")
        return df
        
    except Exception as e:
        logging.error(f"❌ Erreur calcul indicateurs: {e}")
        return None

def detect_swing_points_balanced(df):
    """Détection équilibrée des swing points"""
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

def check_trend_condition_simplified(current_price, ema200, ema50=None, ema20=None):
    """Vérification de tendance simplifiée selon la configuration"""
    if ONLY_EMA200_FILTER:
        # Mode simplifié : seulement EMA200
        return current_price > ema200, current_price < ema200
    else:
        # Mode complet avec confirmation secondaire
        bullish_trend = (current_price > ema200 and 
                        (ema20 > ema50 > ema200 if EMA_SECONDARY_CONFIRMATION else True))
        bearish_trend = (current_price < ema200 and 
                        (ema20 < ema50 < ema200 if EMA_SECONDARY_CONFIRMATION else True))
        return bullish_trend, bearish_trend

def analyze_bullish_divergence_balanced(df_window, current_idx):
    """Analyse de divergence haussière équilibrée"""
    swing_lows_mask = df_window['swing_low'].notna()
    swing_lows = df_window[swing_lows_mask].tail(3)
    
    if len(swing_lows) < 2:
        return None, None  # Signal et near_miss
    
    last_low = swing_lows.iloc[-1]
    prev_low = swing_lows.iloc[-2]
    
    price_low_1 = last_low['swing_low']
    price_low_2 = prev_low['swing_low']
    rsi_low_1 = last_low['rsi']
    rsi_low_2 = prev_low['rsi']
    
    # Condition de divergence
    if price_low_1 < price_low_2 and rsi_low_1 > rsi_low_2:
        rsi_divergence = rsi_low_1 - rsi_low_2
        
        current_price = df_window['close'].iloc[-1]
        current_atr = df_window['atr'].iloc[-1]
        current_ema200 = df_window['ema200'].iloc[-1]
        current_ema50 = df_window['ema50'].iloc[-1]
        current_ema20 = df_window['ema20'].iloc[-1]
        current_rsi = df_window['rsi'].iloc[-1]
        
        # Filtres équilibrés
        # 1. Tendance
        bullish_trend, _ = check_trend_condition_simplified(current_price, current_ema200, current_ema50, current_ema20)
        if not bullish_trend:
            return None, None
        
        # 2. Volatilité
        if ATR_VOLATILITY_FILTER:
            atr_avg = df_window['atr_avg'].iloc[-1]
            if current_atr < (atr_avg * ATR_MINIMUM_MULTIPLIER):
                return None, None
        
        # 3. RSI
        if RSI_MOMENTUM_FILTER and current_rsi > RSI_OVERBOUGHT_LEVEL:
            return None, None
        
        # Vérifier si c'est un signal valide ou un "near miss"
        near_miss = None
        if rsi_divergence >= NEAR_MISS_DIVERGENCE_THRESHOLD and rsi_divergence < MIN_DIVERGENCE_STRENGTH:
            near_miss = {
                'type': 'BUY',
                'divergence_strength': rsi_divergence,
                'reason': 'Divergence trop faible',
                'time': df_window.index[-1]
            }
        
        if rsi_divergence >= MIN_DIVERGENCE_STRENGTH:
            # Signal valide
            stop_loss_price = price_low_1 - (current_price * 0.0005)
            risk_distance = current_price - stop_loss_price
            
            # TP dynamique plus accessible
            theoretical_tp = current_price + (risk_distance * RISK_REWARD_RATIO_TARGET)
            max_tp_by_atr = current_price + (current_atr * MAX_TP_DISTANCE_ATR)
            take_profit_price = min(theoretical_tp, max_tp_by_atr)  # Prendre le plus conservateur
            
            final_risk = current_price - stop_loss_price
            final_reward = take_profit_price - current_price
            final_rr_ratio = final_reward / final_risk if final_risk > 0 else 0
            
            if final_rr_ratio >= MIN_RR_RATIO_REQUIRED:
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
                    'volatility_ratio': current_atr / atr_avg if ATR_VOLATILITY_FILTER else 1.0
                }, near_miss
        
        return None, near_miss
    
    return None, None

def analyze_bearish_divergence_balanced(df_window, current_idx):
    """Analyse de divergence baissière équilibrée"""
    swing_highs_mask = df_window['swing_high'].notna()
    swing_highs = df_window[swing_highs_mask].tail(3)
    
    if len(swing_highs) < 2:
        return None, None
    
    last_high = swing_highs.iloc[-1]
    prev_high = swing_highs.iloc[-2]
    
    price_high_1 = last_high['swing_high']
    price_high_2 = prev_high['swing_high']
    rsi_high_1 = last_high['rsi']
    rsi_high_2 = prev_high['rsi']
    
    # Condition de divergence
    if price_high_1 > price_high_2 and rsi_high_1 < rsi_high_2:
        rsi_divergence = rsi_high_2 - rsi_high_1
        
        current_price = df_window['close'].iloc[-1]
        current_atr = df_window['atr'].iloc[-1]
        current_ema200 = df_window['ema200'].iloc[-1]
        current_ema50 = df_window['ema50'].iloc[-1]
        current_ema20 = df_window['ema20'].iloc[-1]
        current_rsi = df_window['rsi'].iloc[-1]
        
        # Filtres équilibrés
        # 1. Tendance
        _, bearish_trend = check_trend_condition_simplified(current_price, current_ema200, current_ema50, current_ema20)
        if not bearish_trend:
            return None, None
        
        # 2. Volatilité
        if ATR_VOLATILITY_FILTER:
            atr_avg = df_window['atr_avg'].iloc[-1]
            if current_atr < (atr_avg * ATR_MINIMUM_MULTIPLIER):
                return None, None
        
        # 3. RSI
        if RSI_MOMENTUM_FILTER and current_rsi < RSI_OVERSOLD_LEVEL:
            return None, None
        
        # Vérifier si c'est un signal valide ou un "near miss"
        near_miss = None
        if rsi_divergence >= NEAR_MISS_DIVERGENCE_THRESHOLD and rsi_divergence < MIN_DIVERGENCE_STRENGTH:
            near_miss = {
                'type': 'SELL',
                'divergence_strength': rsi_divergence,
                'reason': 'Divergence trop faible',
                'time': df_window.index[-1]
            }
        
        if rsi_divergence >= MIN_DIVERGENCE_STRENGTH:
            # Signal valide
            stop_loss_price = price_high_1 + (current_price * 0.0005)
            risk_distance = stop_loss_price - current_price
            
            # TP dynamique plus accessible
            theoretical_tp = current_price - (risk_distance * RISK_REWARD_RATIO_TARGET)
            max_tp_by_atr = current_price - (current_atr * MAX_TP_DISTANCE_ATR)
            take_profit_price = max(theoretical_tp, max_tp_by_atr)  # Prendre le plus conservateur
            
            final_risk = stop_loss_price - current_price
            final_reward = current_price - take_profit_price
            final_rr_ratio = final_reward / final_risk if final_risk > 0 else 0
            
            if final_rr_ratio >= MIN_RR_RATIO_REQUIRED:
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
                    'volatility_ratio': current_atr / atr_avg if ATR_VOLATILITY_FILTER else 1.0
                }, near_miss
        
        return None, near_miss
    
    return None, None

def run_balanced_backtest(df, start_date=None, end_date=None):
    """Exécute le backtesting équilibré"""
    logging.info("=" * 80)
    logging.info("🎯 BACKTESTING SNIPER ÉQUILIBRÉ v4.0")
    logging.info("=" * 80)
    
    if start_date:
        df = df[df.index >= start_date]
    if end_date:
        df = df[df.index <= end_date]
    
    logging.info(f"📅 Période: {df.index[0]} → {df.index[-1]}")
    
    # Variables de simulation
    current_balance = INITIAL_BALANCE
    trades = []
    near_miss_signals = []
    in_position = False
    position_entry = None
    
    # Compteurs de filtrage
    total_divergences_detected = 0
    filtered_by_trend = 0
    filtered_by_volatility = 0
    filtered_by_rsi = 0
    filtered_by_rr_ratio = 0
    
    # Parcours des données
    for i in range(250, len(df) - 1):
        current_window = df.iloc[:i+1]
        current_price = current_window['close'].iloc[-1]
        current_ema200 = current_window['ema200'].iloc[-1]
        
        if not in_position:
            recent_data = current_window.tail(LOOKBACK_PERIOD)
            signal = None
            near_miss = None
            
            # Test divergence haussière
            if current_price > current_ema200:
                signal, near_miss = analyze_bullish_divergence_balanced(recent_data, i)
                if signal:
                    total_divergences_detected += 1
                elif near_miss:
                    near_miss_signals.append(near_miss)
            
            # Test divergence baissière
            elif current_price < current_ema200:
                signal, near_miss = analyze_bearish_divergence_balanced(recent_data, i)
                if signal:
                    total_divergences_detected += 1
                elif near_miss:
                    near_miss_signals.append(near_miss)
            
            if signal:
                in_position = True
                position_entry = signal.copy()
                position_entry['entry_index'] = i
        
        # Gestion des sorties
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
                    'sl': position_entry['sl'],
                    'tp': position_entry['tp'],
                    'profit_points': profit_points,
                    'profit_dollars': profit_dollars,
                    'exit_reason': exit_reason,
                    'strength': position_entry['strength'],
                    'rr_ratio': position_entry['rr_ratio'],
                    'volatility_ratio': position_entry['volatility_ratio'],
                    'duration_bars': i - position_entry['entry_index']
                }
                trades.append(trade_result)
                current_balance += profit_dollars
                
                in_position = False
                position_entry = None
    
    return trades, current_balance, near_miss_signals

def analyze_balanced_results(trades, final_balance, near_miss_signals):
    """Analyse les résultats équilibrés"""
    logging.info("=" * 80)
    logging.info("📊 RÉSULTATS SNIPER ÉQUILIBRÉ v4.0")
    logging.info("=" * 80)
    
    if len(trades) == 0:
        logging.info("❌ Aucun trade généré même avec les filtres assouplis")
        return
    
    winning_trades = [t for t in trades if t['profit_dollars'] > 0]
    losing_trades = [t for t in trades if t['profit_dollars'] < 0]
    
    win_rate = len(winning_trades) / len(trades) * 100
    total_profit = sum(t['profit_dollars'] for t in trades)
    avg_win = np.mean([t['profit_dollars'] for t in winning_trades]) if winning_trades else 0
    avg_loss = np.mean([t['profit_dollars'] for t in losing_trades]) if losing_trades else 0
    avg_rr = np.mean([t['rr_ratio'] for t in trades])
    profit_factor = abs(sum(t['profit_dollars'] for t in winning_trades) / sum(t['profit_dollars'] for t in losing_trades)) if losing_trades else float('inf')
    
    # Drawdown
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
    
    logging.info("🎯 PERFORMANCE ÉQUILIBRÉE")
    logging.info(f"📈 Nombre total de trades: {len(trades)}")
    logging.info(f"✅ Trades gagnants: {len(winning_trades)} ({win_rate:.1f}%)")
    logging.info(f"❌ Trades perdants: {len(losing_trades)} ({100-win_rate:.1f}%)")
    logging.info(f"💰 Profit total: {total_profit:.2f}$")
    logging.info(f"💹 Balance finale: {final_balance:.2f}$ (Initial: {INITIAL_BALANCE:.2f}$)")
    logging.info(f"📈 Rendement: {((final_balance - INITIAL_BALANCE) / INITIAL_BALANCE * 100):.2f}%")
    
    logging.info("\n🔍 MÉTRIQUES ÉQUILIBRÉES")
    logging.info(f"💚 Gain moyen: {avg_win:.2f}$ | 🔴 Perte moyenne: {avg_loss:.2f}$")
    logging.info(f"⚖️ Ratio R/R moyen: 1:{avg_rr:.2f}")
    logging.info(f"🏆 Facteur de profit: {profit_factor:.2f}")
    logging.info(f"📉 Drawdown maximum: {max_drawdown:.2f}%")
    logging.info(f"⏱️ Fréquence: {len(trades)/4:.1f} trades/an")
    
    # Analyse des near miss
    if near_miss_signals:
        logging.info(f"\n🔍 ANALYSE DES SIGNAUX RATÉS DE PEU")
        logging.info(f"📊 Signaux 'presque validés': {len(near_miss_signals)}")
        buy_near_miss = len([s for s in near_miss_signals if s['type'] == 'BUY'])
        sell_near_miss = len([s for s in near_miss_signals if s['type'] == 'SELL'])
        logging.info(f"📈 Near miss BUY: {buy_near_miss} | 📉 Near miss SELL: {sell_near_miss}")
    
    # Comparaison avec les versions précédentes
    logging.info("\n📊 ÉVOLUTION DES VERSIONS")
    logging.info("Version 1.0 (Originale): 276 trades | 39% win | -$643 | 164% DD")
    logging.info("Version 3.0 (Ultra):     3 trades   | 33% win | +$1202 | 15% DD")
    logging.info(f"Version 4.0 (Équilibrée): {len(trades)} trades | {win_rate:.0f}% win | {total_profit:+.0f}$ | {max_drawdown:.0f}% DD")
    
    logging.info("=" * 80)
    
    # Verdict final
    trades_per_year = len(trades) / 4
    if (win_rate >= 40 and total_profit > 500 and max_drawdown < 25 and 
        trades_per_year >= 5 and trades_per_year <= 30):
        logging.info("✅ VERDICT: ÉQUILIBRE PARFAIT ATTEINT - Stratégie RECOMMANDÉE!")
        logging.info("🎯 Sweet spot trouvé: Qualité + Quantité optimales")
    elif win_rate >= 35 and total_profit > 0 and trades_per_year >= 3:
        logging.info("✅ VERDICT: BON ÉQUILIBRE - Stratégie viable pour trading live")
    else:
        logging.info("🔧 VERDICT: Ajustements supplémentaires nécessaires")

def main():
    """Fonction principale du backtesting équilibré"""
    print("🎯 SNIPER BOT ÉQUILIBRÉ v4.0")
    print("Objectif: Sweet Spot Qualité/Quantité (10-20 trades/an)")
    print("=" * 60)
    
    df = load_data()
    if df is None:
        return
    
    df = calculate_indicators(df)
    if df is None:
        return
    
    print("\n📅 OPTIONS DE PÉRIODE DE TEST:")
    print("1. Toute la période disponible (2021-2025) - RECOMMANDÉ")
    print("2. 2 dernières années (plus représentatif)")
    print("3. 1 dernière année")
    
    try:
        choice = input("\nChoisissez une option (1-3) [défaut=1]: ").strip()
        if not choice:
            choice = "1"
        
        start_date = None
        end_date = None
        
        if choice == "2":
            end_date = df.index[-1]
            start_date = end_date - timedelta(days=730)
            logging.info(f"Test sur 2 dernières années: {start_date} → {end_date}")
        elif choice == "3":
            end_date = df.index[-1]
            start_date = end_date - timedelta(days=365)
            logging.info(f"Test sur 1 dernière année: {start_date} → {end_date}")
        else:
            logging.info("Test sur TOUTE la période disponible (2021-2025)")
        
        # Lancer le backtesting équilibré
        trades, final_balance, near_miss_signals = run_balanced_backtest(df, start_date, end_date)
        
        # Analyser les résultats
        analyze_balanced_results(trades, final_balance, near_miss_signals)
        
        # Sauvegarder les résultats
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        period_suffix = "complete" if start_date is None else f"2years" if choice == "2" else "1year"
        filename = f"sniper_balanced_{period_suffix}_{timestamp}.csv"
        
        if trades:
            trades_df = pd.DataFrame(trades)
            trades_df.to_csv(filename, index=False)
            logging.info(f"💾 Résultats équilibrés sauvegardés: {filename}")
            
            # Fichier bonus avec les near miss
            if near_miss_signals:
                near_miss_df = pd.DataFrame(near_miss_signals)
                near_miss_filename = f"sniper_near_miss_{period_suffix}_{timestamp}.csv"
                near_miss_df.to_csv(near_miss_filename, index=False)
                logging.info(f"💾 Signaux 'presque validés' sauvegardés: {near_miss_filename}")
        
    except KeyboardInterrupt:
        logging.info("🛑 Backtesting interrompu par l'utilisateur")
    except Exception as e:
        logging.error(f"❌ Erreur durant le backtesting: {e}")

if __name__ == "__main__":
    main()
