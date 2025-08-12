#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sniper Bot XAUUSD - Stratégie de Haute Conviction
Trading M15 avec divergences RSI et confluence EMA200
Philosophie: Peu de trades, mais ultra-précis et très rentables
"""

import MetaTrader5 as mt5
import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# Import des paramètres de connexion
from config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, MAGIC_NUMBER, SYMBOL

# =============================================================================
# CONFIGURATION SNIPER BOT
# =============================================================================
TIMEFRAME = mt5.TIMEFRAME_M15           # Analyse sur 15 minutes pour plus de qualité
RISK_REWARD_RATIO_TARGET = 2.0          # Viser 2€ de gain pour 1€ de risque
RISK_PER_TRADE_PERCENT = 1.0            # Risquer 1% du capital par trade
MIN_DIVERGENCE_STRENGTH = 5.0           # Force minimum de divergence RSI
EMA_PERIOD = 200                        # EMA pour déterminer la tendance majeure
RSI_PERIOD = 14                         # Période RSI pour divergences
LOOKBACK_PERIOD = 50                    # Nombre de bougies à analyser pour divergences
SWING_PERIOD = 5                        # Période pour détecter les swings high/low

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def initialize_mt5():
    """Initialisation de la connexion MT5"""
    if not mt5.initialize():
        logging.error("❌ Échec de l'initialisation MT5")
        return False
    
    if not mt5.login(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER):
        logging.error(f"❌ Échec de la connexion MT5: {mt5.last_error()}")
        mt5.shutdown()
        return False
    
    account_info = mt5.account_info()
    if account_info is None:
        logging.error("❌ Impossible de récupérer les informations du compte")
        return False
    
    logging.info(f"✅ Connexion réussie - Compte: {account_info.login}")
    logging.info(f"💰 Balance: {account_info.balance:.2f} | Serveur: {account_info.server}")
    return True

def get_market_data_M15():
    """Récupère les données et calcule les indicateurs sur M15"""
    try:
        rates = mt5.copy_rates_from_pos(SYMBOL, TIMEFRAME, 0, 300)
        if rates is None or len(rates) < 250:
            logging.warning("❌ Données M15 insuffisantes pour l'analyse")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # === INDICATEURS CLÉS ===
        # EMA 200 pour la tendance majeure
        df['ema200'] = df['close'].ewm(span=EMA_PERIOD).mean()
        
        # RSI pour les divergences
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/RSI_PERIOD, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/RSI_PERIOD, adjust=False).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Détection des swing points (plus hauts et plus bas locaux)
        df = detect_swing_points(df)
        
        # Prix actuel pour référence
        tick_info = mt5.symbol_info_tick(SYMBOL)
        current_price = tick_info.ask if tick_info else df['close'].iloc[-1]
        
        return df, current_price
        
    except Exception as e:
        logging.error(f"❌ Erreur récupération données M15: {e}")
        return None, None

def detect_swing_points(df):
    """Détecte les points de retournement (swing highs et swing lows)"""
    df['swing_high'] = np.nan
    df['swing_low'] = np.nan
    
    for i in range(SWING_PERIOD, len(df) - SWING_PERIOD):
        # Swing High: point le plus haut sur la période
        if df['high'].iloc[i] == df['high'].iloc[i-SWING_PERIOD:i+SWING_PERIOD+1].max():
            df.loc[df.index[i], 'swing_high'] = df['high'].iloc[i]
        
        # Swing Low: point le plus bas sur la période  
        if df['low'].iloc[i] == df['low'].iloc[i-SWING_PERIOD:i+SWING_PERIOD+1].min():
            df.loc[df.index[i], 'swing_low'] = df['low'].iloc[i]
    
    return df

def find_divergence_signal(df, current_price):
    """
    Recherche une divergence RSI en confluence avec la tendance EMA200
    Retourne un signal de haute conviction ou None
    """
    try:
        # Données récentes pour l'analyse
        recent_data = df.tail(LOOKBACK_PERIOD).copy()
        
        # === FILTRE DE TENDANCE MAJEURE ===
        last_ema200 = recent_data['ema200'].iloc[-1]
        trend_direction = "HAUSSIER" if current_price > last_ema200 else "BAISSIER"
        
        logging.info(f"📊 Analyse M15 - Prix: {current_price:.2f} | EMA200: {last_ema200:.2f}")
        logging.info(f"📈 Tendance majeure: {trend_direction}")
        
        # === 1. RECHERCHE DIVERGENCE HAUSSIÈRE (SIGNAL D'ACHAT) ===
        if current_price > last_ema200:  # Tendance haussière confirmée
            bullish_signal = analyze_bullish_divergence(recent_data, current_price)
            if bullish_signal:
                return bullish_signal
        
        # === 2. RECHERCHE DIVERGENCE BAISSIÈRE (SIGNAL DE VENTE) ===
        elif current_price < last_ema200:  # Tendance baissière confirmée
            bearish_signal = analyze_bearish_divergence(recent_data, current_price)
            if bearish_signal:
                return bearish_signal
        
        # Aucun signal de haute conviction trouvé
        return None
        
    except Exception as e:
        logging.error(f"❌ Erreur analyse divergence: {e}")
        return None

def analyze_bullish_divergence(df, current_price):
    """Analyse spécifique pour divergence haussière"""
    # Trouver les swing lows récents
    swing_lows = df[df['swing_low'].notna()].tail(3)  # 3 derniers plus bas
    
    if len(swing_lows) < 2:
        return None
    
    # Comparer les 2 derniers swing lows
    last_low = swing_lows.iloc[-1]
    prev_low = swing_lows.iloc[-2]
    
    price_low_1 = last_low['swing_low']
    price_low_2 = prev_low['swing_low']
    rsi_low_1 = last_low['rsi']
    rsi_low_2 = prev_low['rsi']
    
    # Condition de divergence haussière:
    # Prix fait un plus bas MAIS RSI fait un plus bas PLUS HAUT
    if price_low_1 < price_low_2 and rsi_low_1 > rsi_low_2:
        
        # Calculer la force de la divergence
        price_divergence = ((price_low_2 - price_low_1) / price_low_2) * 100
        rsi_divergence = rsi_low_1 - rsi_low_2
        
        if rsi_divergence >= MIN_DIVERGENCE_STRENGTH:
            logging.info("🎯✅ DIVERGENCE HAUSSIÈRE DE HAUTE QUALITÉ DÉTECTÉE!")
            logging.info(f"📉 Prix: {price_low_2:.2f} → {price_low_1:.2f} ({price_divergence:.2f}%)")
            logging.info(f"📈 RSI: {rsi_low_2:.1f} → {rsi_low_1:.1f} (+{rsi_divergence:.1f})")
            
            # Calcul du Stop Loss et Take Profit
            stop_loss_price = price_low_1 - (current_price * 0.0005)  # SL sous le dernier plus bas
            risk_distance = current_price - stop_loss_price
            take_profit_price = current_price + (risk_distance * RISK_REWARD_RATIO_TARGET)
            
            return {
                'signal': 'BUY',
                'entry_price': current_price,
                'sl': stop_loss_price,
                'tp': take_profit_price,
                'risk_distance': risk_distance,
                'reward_distance': risk_distance * RISK_REWARD_RATIO_TARGET,
                'rr_ratio': RISK_REWARD_RATIO_TARGET,
                'reason': f'Divergence Haussière RSI +{rsi_divergence:.1f} points',
                'strength': rsi_divergence
            }
    
    return None

def analyze_bearish_divergence(df, current_price):
    """Analyse spécifique pour divergence baissière"""
    # Trouver les swing highs récents
    swing_highs = df[df['swing_high'].notna()].tail(3)  # 3 derniers plus hauts
    
    if len(swing_highs) < 2:
        return None
    
    # Comparer les 2 derniers swing highs
    last_high = swing_highs.iloc[-1]
    prev_high = swing_highs.iloc[-2]
    
    price_high_1 = last_high['swing_high']
    price_high_2 = prev_high['swing_high']
    rsi_high_1 = last_high['rsi']
    rsi_high_2 = prev_high['rsi']
    
    # Condition de divergence baissière:
    # Prix fait un plus haut MAIS RSI fait un plus haut PLUS BAS
    if price_high_1 > price_high_2 and rsi_high_1 < rsi_high_2:
        
        # Calculer la force de la divergence
        price_divergence = ((price_high_1 - price_high_2) / price_high_2) * 100
        rsi_divergence = rsi_high_2 - rsi_high_1
        
        if rsi_divergence >= MIN_DIVERGENCE_STRENGTH:
            logging.info("🎯✅ DIVERGENCE BAISSIÈRE DE HAUTE QUALITÉ DÉTECTÉE!")
            logging.info(f"📈 Prix: {price_high_2:.2f} → {price_high_1:.2f} (+{price_divergence:.2f}%)")
            logging.info(f"📉 RSI: {rsi_high_2:.1f} → {rsi_high_1:.1f} (-{rsi_divergence:.1f})")
            
            # Calcul du Stop Loss et Take Profit
            stop_loss_price = price_high_1 + (current_price * 0.0005)  # SL au-dessus du dernier plus haut
            risk_distance = stop_loss_price - current_price
            take_profit_price = current_price - (risk_distance * RISK_REWARD_RATIO_TARGET)
            
            return {
                'signal': 'SELL',
                'entry_price': current_price,
                'sl': stop_loss_price,
                'tp': take_profit_price,
                'risk_distance': risk_distance,
                'reward_distance': risk_distance * RISK_REWARD_RATIO_TARGET,
                'rr_ratio': RISK_REWARD_RATIO_TARGET,
                'reason': f'Divergence Baissière RSI -{rsi_divergence:.1f} points',
                'strength': rsi_divergence
            }
    
    return None

def calculate_lot_size(signal_data):
    """Calcule la taille du lot basée sur le % de risque du capital"""
    try:
        account_info = mt5.account_info()
        if account_info is None:
            return 0.01  # Lot de sécurité
        
        balance = account_info.balance
        risk_amount = balance * (RISK_PER_TRADE_PERCENT / 100.0)
        risk_distance = signal_data['risk_distance']
        
        # Calcul théorique du lot
        symbol_info = mt5.symbol_info(SYMBOL)
        if symbol_info is None:
            return 0.01
        
        contract_size = symbol_info.trade_contract_size
        tick_value = symbol_info.trade_tick_value
        tick_size = symbol_info.trade_tick_size
        
        # Calcul: taille_lot = montant_risque / (distance_risque * valeur_par_point)
        value_per_point = (tick_value / tick_size)
        calculated_lot = risk_amount / (risk_distance * value_per_point)
        
        # Arrondir au volume minimum acceptable
        min_volume = symbol_info.volume_min
        max_volume = symbol_info.volume_max
        volume_step = symbol_info.volume_step
        
        # Arrondir selon le step
        lot_size = round(calculated_lot / volume_step) * volume_step
        lot_size = max(min_volume, min(lot_size, max_volume))
        
        logging.info(f"💰 Calcul lot: Balance={balance:.2f} | Risque={risk_amount:.2f} | Distance={risk_distance:.4f}")
        logging.info(f"📊 Lot calculé: {calculated_lot:.3f} → Lot final: {lot_size:.3f}")
        
        return lot_size
        
    except Exception as e:
        logging.error(f"❌ Erreur calcul lot: {e}")
        return 0.01  # Lot de sécurité

def place_sniper_order(signal_data):
    """Place un ordre de haute conviction avec gestion précise du risque"""
    try:
        # Calcul de la taille du lot adaptée au risque
        lot_size = calculate_lot_size(signal_data)
        
        # Préparer la requête d'ordre
        if signal_data['signal'] == 'BUY':
            order_type = mt5.ORDER_TYPE_BUY
            price = signal_data['entry_price']
            action_emoji = "📈"
        else:
            order_type = mt5.ORDER_TYPE_SELL
            price = signal_data['entry_price']
            action_emoji = "📉"
        
        # Vérifier les distances minimum MT5
        symbol_info = mt5.symbol_info(SYMBOL)
        stops_level = symbol_info.stops_level * symbol_info.point
        
        sl_distance = abs(price - signal_data['sl'])
        tp_distance = abs(signal_data['tp'] - price)
        
        if sl_distance < stops_level or tp_distance < stops_level:
            logging.warning(f"⚠️ Distances SL/TP trop faibles pour MT5: SL={sl_distance:.4f} TP={tp_distance:.4f}")
            logging.warning(f"🔧 Minimum requis: {stops_level:.4f}")
            return False
        
        # Construire la requête
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": lot_size,
            "type": order_type,
            "price": price,
            "sl": signal_data['sl'],
            "tp": signal_data['tp'],
            "magic": MAGIC_NUMBER,
            "comment": f"Sniper_{signal_data['reason'][:20]}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Exécuter l'ordre
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logging.info("=" * 80)
            logging.info(f"🎯 {action_emoji} ORDRE SNIPER EXÉCUTÉ AVEC SUCCÈS!")
            logging.info(f"📋 Ticket: #{result.order}")
            logging.info(f"💰 Lot: {lot_size} | Prix: {price:.2f}")
            logging.info(f"🛡️ SL: {signal_data['sl']:.2f} | 🎯 TP: {signal_data['tp']:.2f}")
            logging.info(f"⚖️ Ratio R/R: 1:{signal_data['rr_ratio']:.1f}")
            logging.info(f"🔍 Raison: {signal_data['reason']}")
            logging.info(f"💸 Risque: {signal_data['risk_distance']:.4f} | Gain potentiel: {signal_data['reward_distance']:.4f}")
            logging.info("=" * 80)
            return True
        else:
            logging.error(f"❌ Échec ordre sniper: {result.retcode} - {result.comment}")
            return False
            
    except Exception as e:
        logging.error(f"❌ Erreur placement ordre sniper: {e}")
        return False

def check_open_positions():
    """Vérifie et affiche les positions ouvertes"""
    try:
        positions = mt5.positions_get(symbol=SYMBOL)
        if positions is None or len(positions) == 0:
            return 0
        
        total_profit = 0
        for pos in positions:
            profit = pos.profit
            type_name = "BUY" if pos.type == 0 else "SELL"
            total_profit += profit
            
            # Calculer le potentiel de gain restant
            if pos.tp > 0:
                if pos.type == 0:  # BUY
                    remaining_gain = pos.tp - mt5.symbol_info_tick(SYMBOL).bid
                else:  # SELL
                    remaining_gain = mt5.symbol_info_tick(SYMBOL).ask - pos.tp
                remaining_gain *= pos.volume * 100  # Approximation pour XAUUSD
            else:
                remaining_gain = 0
            
            logging.info(f"💼 Position #{pos.ticket}: {type_name} {pos.volume} lots")
            logging.info(f"   💰 P&L actuel: {profit:.2f}$ | Gain potentiel restant: {remaining_gain:.2f}$")
        
        logging.info(f"📊 P&L total positions: {total_profit:.2f}$")
        return len(positions)
        
    except Exception as e:
        logging.error(f"❌ Erreur vérification positions: {e}")
        return 0

def main():
    """Boucle principale du Sniper Bot"""
    logging.info("🎯 SNIPER BOT XAUUSD DÉMARRÉ!")
    logging.info("🎯 Philosophie: Patience et Précision - Qualité > Quantité")
    logging.info(f"📊 Analyse: M15 | RR Target: 1:{RISK_REWARD_RATIO_TARGET} | Risque: {RISK_PER_TRADE_PERCENT}%")
    logging.info("⏳ En attente d'un signal de HAUTE CONVICTION...")
    logging.info("=" * 80)
    
    if not initialize_mt5():
        return
    
    cycle_count = 0
    last_signal_time = 0
    
    try:
        while True:
            cycle_count += 1
            
            # Affichage du statut toutes les 10 minutes
            if cycle_count % 40 == 1:  # 40 cycles de 15s = 10 minutes
                account_info = mt5.account_info()
                if account_info:
                    logging.info("=" * 60)
                    logging.info(f"📊 STATUT SNIPER - Cycle #{cycle_count}")
                    logging.info(f"💰 Balance: {account_info.balance:.2f} | Equity: {account_info.equity:.2f}")
                    logging.info(f"💹 Marge libre: {account_info.margin_free:.2f}")
                    
                    positions_count = check_open_positions()
                    if positions_count == 0:
                        logging.info("🎯 Aucune position - En mode CHASSE au signal parfait")
                    
                    logging.info("=" * 60)
            
            # Analyse des données M15
            data_result = get_market_data_M15()
            if data_result[0] is None:
                logging.warning("⚠️ Données indisponibles, nouvelle tentative dans 15s...")
                time.sleep(15)
                continue
            
            df, current_price = data_result
            
            # Recherche de signal de divergence
            signal = find_divergence_signal(df, current_price)
            
            if signal:
                # Éviter les signaux répétitifs (minimum 30 minutes entre signaux)
                current_time = time.time()
                if current_time - last_signal_time < 1800:  # 30 minutes
                    time_remaining = int((1800 - (current_time - last_signal_time)) / 60)
                    logging.info(f"⏱️ Signal détecté mais cooldown actif - Attendre {time_remaining} minutes")
                else:
                    # Vérifier qu'il n'y a pas déjà une position ouverte
                    existing_positions = mt5.positions_get(symbol=SYMBOL)
                    if existing_positions and len(existing_positions) > 0:
                        logging.info("⚠️ Position déjà ouverte - Signal ignoré")
                    else:
                        # Exécuter le trade de haute conviction
                        success = place_sniper_order(signal)
                        if success:
                            last_signal_time = current_time
                            logging.info("✅ Trade Sniper placé - Patience pour le prochain signal...")
                        else:
                            logging.warning("❌ Échec placement trade sniper")
            else:
                if cycle_count % 20 == 0:  # Log toutes les 5 minutes
                    logging.info("🔍 Analyse en cours... Aucun signal de haute conviction détecté")
            
            # Attendre 15 secondes avant la prochaine analyse
            time.sleep(15)
            
    except KeyboardInterrupt:
        logging.info("🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        logging.error(f"❌ Erreur critique: {e}")
    finally:
        # Affichage du résumé final
        account_info = mt5.account_info()
        if account_info:
            logging.info("=" * 60)
            logging.info("📊 RÉSUMÉ FINAL SNIPER BOT")
            logging.info(f"💰 Balance: {account_info.balance:.2f} | Equity: {account_info.equity:.2f}")
            logging.info(f"💹 Marge libre: {account_info.margin_free:.2f}")
            check_open_positions()
            logging.info("=" * 60)
        
        logging.info("🎯 Sniper Bot arrêté - Merci pour votre patience et discipline!")
        mt5.shutdown()

if __name__ == "__main__":
    main()
