#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SNIPER BOT ULTRA-OPTIMISÉ - Version 3.0
Intégration des améliorations basées sur l'analyse de l'equity curve
Focus: Filtre de volatilité ATR, TP dynamique, double confirmation de tendance
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta

# =============================================================================
# CONFIGURATION ULTRA-OPTIMISÉE BASÉE SUR L'ANALYSE DE L'EQUITY CURVE
# =============================================================================
RISK_REWARD_RATIO_TARGET = 1.8          # ⬇️ Réduction de 2.0 à 1.8 (plus réaliste)
RISK_PER_TRADE_PERCENT = 1.0            
MIN_DIVERGENCE_STRENGTH = 8.0           # ⬆️ Augmenté pour plus de sélectivité
EMA_PERIOD_LONG = 200                   # Tendance de fond
EMA_PERIOD_MEDIUM = 50                  # ⭐ NOUVEAU: Tendance moyenne
EMA_PERIOD_SHORT = 20                   # ⭐ NOUVEAU: Tendance courte
RSI_PERIOD = 14                         
LOOKBACK_PERIOD = 50                    
SWING_PERIOD = 8                        # ⬆️ Augmenté pour des swings plus significatifs
ATR_PERIOD = 14                         

# =============================================================================
# ⭐ NOUVEAUX FILTRES ULTRA-SÉLECTIFS
# =============================================================================
# 1. FILTRE DE VOLATILITÉ ATR DYNAMIQUE
ATR_VOLATILITY_FILTER = True           
ATR_LOOKBACK_PERIOD = 100               # Période pour calculer l'ATR moyen
ATR_MINIMUM_MULTIPLIER = 1.2            # ATR actuel doit être > 1.2x ATR moyen

# 2. TAKE PROFIT DYNAMIQUE BASÉ SUR LES NIVEAUX
DYNAMIC_TP_ENABLED = True               
MIN_RR_RATIO_REQUIRED = 1.5             # Ratio minimum requis pour prendre le trade
MAX_TP_DISTANCE_ATR = 4.0               # TP maximum = 4x ATR (éviter les objectifs irréalistes)

# 3. TRIPLE CONFIRMATION DE TENDANCE
TRIPLE_TREND_FILTER = True              
MIN_TREND_ALIGNMENT_DISTANCE = 0.3      # Distance minimum entre EMAs en % du prix

# 4. FILTRE DE MOMENTUM RSI
RSI_MOMENTUM_FILTER = True              
RSI_OVERBOUGHT_LEVEL = 75               # Plus restrictif que 70
RSI_OVERSOLD_LEVEL = 25                 # Plus restrictif que 30

# =============================================================================
# PARAMÈTRES DE BACKTESTING
# =============================================================================
INITIAL_BALANCE = 10000.0  
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
    """Calcule tous les indicateurs avec triple EMA et ATR dynamique"""
    try:
        logging.info("🔧 Calcul des indicateurs ultra-optimisés...")
        
        # TRIPLE EMA pour confirmation de tendance
        df['ema200'] = df['close'].ewm(span=EMA_PERIOD_LONG).mean()
        df['ema50'] = df['close'].ewm(span=EMA_PERIOD_MEDIUM).mean()
        df['ema20'] = df['close'].ewm(span=EMA_PERIOD_SHORT).mean()
        
        # RSI pour les divergences
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/RSI_PERIOD, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/RSI_PERIOD, adjust=False).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # ATR pour la volatilité
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df['atr'] = true_range.rolling(window=ATR_PERIOD).mean()
        
        # ATR moyen pour le filtre de volatilité
        df['atr_mean'] = df['atr'].rolling(window=ATR_LOOKBACK_PERIOD).mean()
        df['atr_ratio'] = df['atr'] / df['atr_mean']
        
        # Détection des swing points pour TP dynamique
        df = detect_swing_points_for_tp(df)
        
        # Confirmation de tendance triple
        df['trend_alignment'] = calculate_trend_alignment(df)
        
        logging.info("✅ Indicateurs ultra-optimisés calculés")
        return df
        
    except Exception as e:
        logging.error(f"❌ Erreur calcul indicateurs: {e}")
        return None

def calculate_trend_alignment(df):
    """Calcule l'alignement des trois EMAs pour confirmation de tendance"""
    # Pour un signal haussier: EMA20 > EMA50 > EMA200
    # Pour un signal baissier: EMA20 < EMA50 < EMA200
    
    bullish_alignment = (df['ema20'] > df['ema50']) & (df['ema50'] > df['ema200'])
    bearish_alignment = (df['ema20'] < df['ema50']) & (df['ema50'] < df['ema200'])
    
    # Calculer la "force" de l'alignement (distance entre EMAs)
    ema_spread_pct = abs(df['ema20'] - df['ema200']) / df['close'] * 100
    
    alignment = np.where(bullish_alignment, 1, np.where(bearish_alignment, -1, 0))
    
    return pd.Series(alignment, index=df.index)

def detect_swing_points_for_tp(df):
    """Détecte les swing points pour calculer des TP dynamiques réalistes"""
    df['swing_high'] = np.nan
    df['swing_low'] = np.nan
    df['support_level'] = np.nan
    df['resistance_level'] = np.nan
    
    for i in range(SWING_PERIOD * 2, len(df) - SWING_PERIOD):
        # Swing High: plus haut local
        if df['high'].iloc[i] == df['high'].iloc[i-SWING_PERIOD:i+SWING_PERIOD+1].max():
            df.iloc[i, df.columns.get_loc('swing_high')] = df['high'].iloc[i]
        
        # Swing Low: plus bas local
        if df['low'].iloc[i] == df['low'].iloc[i-SWING_PERIOD:i+SWING_PERIOD+1].min():
            df.iloc[i, df.columns.get_loc('swing_low')] = df['low'].iloc[i]
        
        # Calculer les niveaux de support/résistance les plus proches
        current_price = df['close'].iloc[i]
        
        # Résistance = premier swing high au-dessus du prix actuel
        recent_highs = df['swing_high'].iloc[max(0, i-100):i].dropna()
        resistance_candidates = recent_highs[recent_highs > current_price]
        if len(resistance_candidates) > 0:
            df.iloc[i, df.columns.get_loc('resistance_level')] = resistance_candidates.iloc[-1]
        
        # Support = premier swing low en-dessous du prix actuel
        recent_lows = df['swing_low'].iloc[max(0, i-100):i].dropna()
        support_candidates = recent_lows[recent_lows < current_price]
        if len(support_candidates) > 0:
            df.iloc[i, df.columns.get_loc('support_level')] = support_candidates.iloc[-1]
    
    return df

def check_volatility_filter(df_window):
    """Vérifie si la volatilité actuelle est suffisante pour trader"""
    if not ATR_VOLATILITY_FILTER:
        return True, "Filtre désactivé"
    
    current_atr = df_window['atr'].iloc[-1]
    mean_atr = df_window['atr_mean'].iloc[-1]
    atr_ratio = df_window['atr_ratio'].iloc[-1]
    
    if pd.isna(atr_ratio) or atr_ratio < ATR_MINIMUM_MULTIPLIER:
        return False, f"ATR insuffisant: {atr_ratio:.2f} < {ATR_MINIMUM_MULTIPLIER}"
    
    return True, f"ATR OK: {atr_ratio:.2f}x moyenne"

def check_triple_trend_filter(df_window, signal_type):
    """Vérifie l'alignement triple des EMAs selon le type de signal"""
    if not TRIPLE_TREND_FILTER:
        return True, "Filtre désactivé"
    
    current_price = df_window['close'].iloc[-1]
    ema20 = df_window['ema20'].iloc[-1]
    ema50 = df_window['ema50'].iloc[-1] 
    ema200 = df_window['ema200'].iloc[-1]
    trend_alignment = df_window['trend_alignment'].iloc[-1]
    
    # Distance entre EMAs en % du prix
    ema_spread_pct = abs(ema20 - ema200) / current_price * 100
    
    if signal_type == 'BUY':
        # Pour un achat: prix > EMA20 > EMA50 > EMA200
        conditions_met = (
            current_price > ema20 and
            ema20 > ema50 and
            ema50 > ema200 and
            ema_spread_pct >= MIN_TREND_ALIGNMENT_DISTANCE
        )
        
        if not conditions_met:
            return False, f"Tendance haussière insuffisante. Spread: {ema_spread_pct:.2f}%"
        
        return True, f"Triple tendance haussière confirmée. Spread: {ema_spread_pct:.2f}%"
    
    elif signal_type == 'SELL':
        # Pour une vente: prix < EMA20 < EMA50 < EMA200
        conditions_met = (
            current_price < ema20 and
            ema20 < ema50 and
            ema50 < ema200 and
            ema_spread_pct >= MIN_TREND_ALIGNMENT_DISTANCE
        )
        
        if not conditions_met:
            return False, f"Tendance baissière insuffisante. Spread: {ema_spread_pct:.2f}%"
        
        return True, f"Triple tendance baissière confirmée. Spread: {ema_spread_pct:.2f}%"
    
    return False, "Type de signal invalide"

def calculate_dynamic_tp(df_window, signal_type, entry_price, sl_price):
    """Calcule un TP dynamique basé sur les niveaux de support/résistance"""
    if not DYNAMIC_TP_ENABLED:
        # TP fixe basé sur le ratio
        risk_distance = abs(entry_price - sl_price)
        if signal_type == 'BUY':
            return entry_price + (risk_distance * RISK_REWARD_RATIO_TARGET)
        else:
            return entry_price - (risk_distance * RISK_REWARD_RATIO_TARGET)
    
    current_atr = df_window['atr'].iloc[-1]
    max_tp_distance = current_atr * MAX_TP_DISTANCE_ATR
    
    if signal_type == 'BUY':
        # Chercher le niveau de résistance le plus proche
        resistance = df_window['resistance_level'].iloc[-1]
        
        if pd.notna(resistance) and resistance > entry_price:
            # Vérifier que la distance n'est pas excessive
            tp_distance = resistance - entry_price
            if tp_distance <= max_tp_distance:
                # Vérifier que le ratio R/R est acceptable
                risk_distance = entry_price - sl_price
                rr_ratio = tp_distance / risk_distance if risk_distance > 0 else 0
                
                if rr_ratio >= MIN_RR_RATIO_REQUIRED:
                    return resistance - (current_atr * 0.1)  # Légèrement avant la résistance
        
        # Fallback: TP basé sur le ratio fixe mais limité par l'ATR
        risk_distance = entry_price - sl_price
        theoretical_tp = entry_price + (risk_distance * RISK_REWARD_RATIO_TARGET)
        max_allowed_tp = entry_price + max_tp_distance
        
        return min(theoretical_tp, max_allowed_tp)
    
    else:  # SELL
        # Chercher le niveau de support le plus proche
        support = df_window['support_level'].iloc[-1]
        
        if pd.notna(support) and support < entry_price:
            # Vérifier que la distance n'est pas excessive
            tp_distance = entry_price - support
            if tp_distance <= max_tp_distance:
                # Vérifier que le ratio R/R est acceptable
                risk_distance = sl_price - entry_price
                rr_ratio = tp_distance / risk_distance if risk_distance > 0 else 0
                
                if rr_ratio >= MIN_RR_RATIO_REQUIRED:
                    return support + (current_atr * 0.1)  # Légèrement après le support
        
        # Fallback: TP basé sur le ratio fixe mais limité par l'ATR
        risk_distance = sl_price - entry_price
        theoretical_tp = entry_price - (risk_distance * RISK_REWARD_RATIO_TARGET)
        min_allowed_tp = entry_price - max_tp_distance
        
        return max(theoretical_tp, min_allowed_tp)

def analyze_bullish_divergence_ultra(df_window, current_idx):
    """Analyse ultra-optimisée pour divergence haussière"""
    # 1. FILTRE DE VOLATILITÉ
    volatility_ok, volatility_msg = check_volatility_filter(df_window)
    if not volatility_ok:
        return None
    
    # 2. FILTRE DE TENDANCE TRIPLE
    trend_ok, trend_msg = check_triple_trend_filter(df_window, 'BUY')
    if not trend_ok:
        return None
    
    # 3. RECHERCHE DE DIVERGENCE
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
    
    # Condition de divergence haussière renforcée
    if price_low_1 < price_low_2 and rsi_low_1 > rsi_low_2:
        rsi_divergence = rsi_low_1 - rsi_low_2
        
        if rsi_divergence >= MIN_DIVERGENCE_STRENGTH:
            current_price = df_window['close'].iloc[-1]
            current_rsi = df_window['rsi'].iloc[-1]
            
            # 4. FILTRE RSI MOMENTUM
            if RSI_MOMENTUM_FILTER and current_rsi > RSI_OVERBOUGHT_LEVEL:
                return None
            
            # 5. CALCUL DES NIVEAUX
            stop_loss_price = price_low_1 - (current_price * 0.0005)
            take_profit_price = calculate_dynamic_tp(df_window, 'BUY', current_price, stop_loss_price)
            
            # 6. VÉRIFICATION DU RATIO R/R FINAL
            risk_distance = current_price - stop_loss_price
            reward_distance = take_profit_price - current_price
            final_rr_ratio = reward_distance / risk_distance if risk_distance > 0 else 0
            
            if final_rr_ratio < MIN_RR_RATIO_REQUIRED:
                return None
            
            return {
                'signal': 'BUY',
                'entry_price': current_price,
                'sl': stop_loss_price,
                'tp': take_profit_price,
                'risk_distance': risk_distance,
                'reward_distance': reward_distance,
                'rr_ratio': final_rr_ratio,
                'strength': rsi_divergence,
                'volatility_msg': volatility_msg,
                'trend_msg': trend_msg,
                'entry_time': df_window.index[-1]
            }
    
    return None

def analyze_bearish_divergence_ultra(df_window, current_idx):
    """Analyse ultra-optimisée pour divergence baissière"""
    # 1. FILTRE DE VOLATILITÉ
    volatility_ok, volatility_msg = check_volatility_filter(df_window)
    if not volatility_ok:
        return None
    
    # 2. FILTRE DE TENDANCE TRIPLE
    trend_ok, trend_msg = check_triple_trend_filter(df_window, 'SELL')
    if not trend_ok:
        return None
    
    # 3. RECHERCHE DE DIVERGENCE
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
    
    # Condition de divergence baissière renforcée
    if price_high_1 > price_high_2 and rsi_high_1 < rsi_high_2:
        rsi_divergence = rsi_high_2 - rsi_high_1
        
        if rsi_divergence >= MIN_DIVERGENCE_STRENGTH:
            current_price = df_window['close'].iloc[-1]
            current_rsi = df_window['rsi'].iloc[-1]
            
            # 4. FILTRE RSI MOMENTUM
            if RSI_MOMENTUM_FILTER and current_rsi < RSI_OVERSOLD_LEVEL:
                return None
            
            # 5. CALCUL DES NIVEAUX
            stop_loss_price = price_high_1 + (current_price * 0.0005)
            take_profit_price = calculate_dynamic_tp(df_window, 'SELL', current_price, stop_loss_price)
            
            # 6. VÉRIFICATION DU RATIO R/R FINAL
            risk_distance = stop_loss_price - current_price
            reward_distance = current_price - take_profit_price
            final_rr_ratio = reward_distance / risk_distance if risk_distance > 0 else 0
            
            if final_rr_ratio < MIN_RR_RATIO_REQUIRED:
                return None
            
            return {
                'signal': 'SELL',
                'entry_price': current_price,
                'sl': stop_loss_price,
                'tp': take_profit_price,
                'risk_distance': risk_distance,
                'reward_distance': reward_distance,
                'rr_ratio': final_rr_ratio,
                'strength': rsi_divergence,
                'volatility_msg': volatility_msg,
                'trend_msg': trend_msg,
                'entry_time': df_window.index[-1]
            }
    
    return None

def run_ultra_backtest(df, start_date=None, end_date=None):
    """Exécute le backtesting avec tous les filtres ultra-optimisés"""
    logging.info("=" * 80)
    logging.info("🎯 BACKTESTING SNIPER ULTRA-OPTIMISÉ v3.0")
    logging.info("=" * 80)
    
    if start_date:
        df = df[df.index >= start_date]
    if end_date:
        df = df[df.index <= end_date]
    
    logging.info(f"📅 Période de test: {df.index[0]} → {df.index[-1]}")
    
    # Variables de simulation
    current_balance = INITIAL_BALANCE
    trades = []
    in_position = False
    position_entry = None
    
    # Statistiques des filtres
    filter_stats = {
        'signals_detected': 0,
        'filtered_volatility': 0,
        'filtered_trend': 0,
        'filtered_rsi': 0,
        'filtered_rr': 0,
        'trades_executed': 0
    }
    
    # Parcourir les données
    for i in range(300, len(df) - 1):  # Plus de données initiales pour les EMAs
        current_window = df.iloc[:i+1]
        current_price = current_window['close'].iloc[-1]
        
        # Si pas en position, chercher un signal
        if not in_position:
            recent_data = current_window.tail(LOOKBACK_PERIOD)
            signal = None
            
            # Test signal haussier
            signal = analyze_bullish_divergence_ultra(recent_data, i)
            if not signal:
                # Test signal baissier
                signal = analyze_bearish_divergence_ultra(recent_data, i)
            
            if signal:
                filter_stats['trades_executed'] += 1
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
                    'sl': position_entry['sl'],
                    'tp': position_entry['tp'],
                    'profit_points': profit_points,
                    'profit_dollars': profit_dollars,
                    'exit_reason': exit_reason,
                    'strength': position_entry['strength'],
                    'rr_ratio': position_entry['rr_ratio'],
                    'volatility_msg': position_entry['volatility_msg'],
                    'trend_msg': position_entry['trend_msg'],
                    'duration_bars': i - position_entry['entry_index']
                }
                trades.append(trade_result)
                current_balance += profit_dollars
                
                in_position = False
                position_entry = None
    
    # Analyser les résultats
    analyze_ultra_results(trades, current_balance, filter_stats)
    return trades, current_balance

def analyze_ultra_results(trades, final_balance, filter_stats):
    """Analyse ultra-détaillée des résultats"""
    if len(trades) == 0:
        logging.info("❌ Aucun trade généré avec les filtres ultra-sélectifs")
        return
    
    winning_trades = [t for t in trades if t['profit_dollars'] > 0]
    losing_trades = [t for t in trades if t['profit_dollars'] < 0]
    
    win_rate = len(winning_trades) / len(trades) * 100
    total_profit = sum(t['profit_dollars'] for t in trades)
    avg_win = np.mean([t['profit_dollars'] for t in winning_trades]) if winning_trades else 0
    avg_loss = np.mean([t['profit_dollars'] for t in losing_trades]) if losing_trades else 0
    avg_rr = np.mean([t['rr_ratio'] for t in trades])
    
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
    
    # Facteur de profit
    total_wins = sum(t['profit_dollars'] for t in winning_trades) if winning_trades else 0
    total_losses = abs(sum(t['profit_dollars'] for t in losing_trades)) if losing_trades else 1
    profit_factor = total_wins / total_losses if total_losses > 0 else 0
    
    # Affichage des résultats ultra-optimisés
    logging.info("=" * 80)
    logging.info("📊 RÉSULTATS SNIPER ULTRA-OPTIMISÉ v3.0")
    logging.info("=" * 80)
    
    logging.info("🎯 PERFORMANCE ULTRA-SÉLECTIVE")
    logging.info(f"📈 Nombre total de trades: {len(trades)}")
    logging.info(f"✅ Trades gagnants: {len(winning_trades)} ({win_rate:.1f}%)")
    logging.info(f"❌ Trades perdants: {len(losing_trades)} ({100-win_rate:.1f}%)")
    logging.info(f"💰 Profit total: {total_profit:.2f}$")
    logging.info(f"💹 Balance finale: {final_balance:.2f}$ (Initial: {INITIAL_BALANCE:.2f}$)")
    logging.info(f"📈 Rendement: {((final_balance - INITIAL_BALANCE) / INITIAL_BALANCE * 100):.2f}%")
    
    logging.info("\n🔍 MÉTRIQUES ULTRA-OPTIMISÉES")
    logging.info(f"💚 Gain moyen: {avg_win:.2f}$ | 🔴 Perte moyenne: {avg_loss:.2f}$")
    logging.info(f"⚖️ Ratio R/R moyen: 1:{avg_rr:.2f}")
    logging.info(f"🏆 Facteur de profit: {profit_factor:.2f}")
    logging.info(f"📉 Drawdown maximum: {max_drawdown:.2f}%")
    
    # Comparaison avec les versions précédentes
    logging.info("\n📊 ÉVOLUTION DES PERFORMANCES")
    logging.info("Version 1.0 (Originale):")
    logging.info("  - Trades: 276 | Win Rate: 39.1% | Profit: -$643 | Drawdown: 164%")
    logging.info(f"Version 3.0 (Ultra-optimisée):")
    logging.info(f"  - Trades: {len(trades)} | Win Rate: {win_rate:.1f}% | Profit: {total_profit:.2f}$ | Drawdown: {max_drawdown:.1f}%")
    
    # Amélioration en %
    improvement_trades = ((len(trades) - 276) / 276 * 100) if len(trades) != 276 else 0
    improvement_winrate = win_rate - 39.1
    improvement_profit = total_profit - (-643.13)
    improvement_drawdown = max_drawdown - 164.23
    
    logging.info(f"\n🚀 AMÉLIORATIONS:")
    logging.info(f"📉 Réduction trades: {improvement_trades:.1f}% (qualité > quantité)")
    logging.info(f"✅ Amélioration win rate: +{improvement_winrate:.1f}%")
    logging.info(f"💰 Amélioration profit: +{improvement_profit:.2f}$")
    logging.info(f"📉 Réduction drawdown: {improvement_drawdown:.1f}%")
    
    logging.info("=" * 80)
    
    # Verdict final ultra-optimisé
    if win_rate >= 55 and total_profit > 500 and max_drawdown < 15:
        logging.info("✅ VERDICT: Stratégie ULTRA-OPTIMISÉE - EXCELLENTE pour trading live!")
    elif win_rate >= 50 and total_profit > 0 and max_drawdown < 25:
        logging.info("✅ VERDICT: Stratégie OPTIMISÉE - RECOMMANDÉE pour trading live")
    elif win_rate >= 45 and total_profit > 0:
        logging.info("⚠️ VERDICT: Stratégie AMÉLIORÉE - Trading live avec prudence")
    else:
        logging.info("🔧 VERDICT: Optimisation en cours - Ajustements supplémentaires requis")

def main():
    """Fonction principale du backtesting ultra-optimisé"""
    print("🎯 SNIPER BOT ULTRA-OPTIMISÉ v3.0")
    print("Filtres: ATR Dynamique + Triple EMA + TP Dynamique + RSI Momentum")
    print("=" * 70)
    
    df = load_data()
    if df is None:
        return
    
    df = calculate_indicators(df)
    if df is None:
        return
    
    # Test sur la dernière année pour validation
    end_date = df.index[-1]
    start_date = end_date - timedelta(days=365)
    logging.info(f"Test ultra-optimisé sur 1 dernière année: {start_date} → {end_date}")
    
    # Lancer le backtesting ultra-optimisé
    trades, final_balance = run_ultra_backtest(df, start_date, end_date)
    
    # Sauvegarder les résultats
    if trades:
        trades_df = pd.DataFrame(trades)
        trades_df.to_csv("sniper_backtest_ultra_optimized.csv", index=False)
        logging.info("💾 Résultats ultra-optimisés sauvegardés dans 'sniper_backtest_ultra_optimized.csv'")

if __name__ == "__main__":
    main()
