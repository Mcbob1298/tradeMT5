#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Scalping XAUUSD - Version Rapide 2s
Analyse toutes les 2 secondes avec ratio R/R favorable
"""

import MetaTrader5 as mt5
import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# Import des paramètres de configuration
try:
    from config import (RISK_REWARD_RATIO, ATR_MULTIPLIER, MIN_SL_DISTANCE, MAX_SL_DISTANCE,
                       CONFIDENCE_SCORE_REQUIRED)
except ImportError:
    # Valeurs par défaut si config.py n'est pas trouvé (SCALPING ÉQUILIBRÉ)
    RISK_REWARD_RATIO = 1.5
    ATR_MULTIPLIER = 1.5
    MIN_SL_DISTANCE = 0.10
    MAX_SL_DISTANCE = 2.00
    CONFIDENCE_SCORE_REQUIRED = 2

# Paramètres de trading intelligents
MAX_TRADES_PER_MINUTE = 5  # Maximum 5 positions par minute
RISK_PER_TRADE_PERCENT = 1.0  # 1% de risque par trade (adaptatif)

# Configuration
SYMBOL = "XAUUSD"
MAGIC_NUMBER = 123462
MIN_RR_RATIO = 1.5  # Ratio R/R cible (informatif seulement)

# Variables globales pour le suivi des trades
trade_timestamps = []  # Liste des timestamps des trades

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def get_market_data():
    """Récupération rapide des données de marché avec RSI"""
    try:
        # Données récentes (on prend plus de barres pour le RSI)
        rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M1, 0, 50)  # 50 périodes pour RSI(14) stable
        if rates is None or len(rates) < 20:  # Vérification de 20 barres min
            logging.warning("❌ Données insuffisantes")
            return None
        
        tick = mt5.symbol_info_tick(SYMBOL)
        if tick is None:
            logging.warning("❌ Pas de tick disponible")
            return None
        
        df = pd.DataFrame(rates)
        current_price = tick.bid
        
        # Log des prix en temps réel
        logging.info(f"💹 Prix: Bid={tick.bid:.2f} Ask={tick.ask:.2f} Spread={tick.ask-tick.bid:.2f}")
        
        # --- AJOUT DU CALCUL RSI ---
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        # --- FIN DE L'AJOUT ---
        
        # Calculs simples et rapides
        df['ema5'] = df['close'].ewm(span=5).mean()
        df['ema10'] = df['close'].ewm(span=10).mean()
        
        # ATR simplifié
        df['hl'] = df['high'] - df['low']
        atr = df['hl'].rolling(5).mean().iloc[-1]
        
        # Support/Résistance basiques
        recent_high = df['high'].tail(10).max()
        recent_low = df['low'].tail(10).min()
        
        # Log des niveaux techniques avec RSI
        logging.info(f"📊 EMA5={df['ema5'].iloc[-1]:.2f} | EMA10={df['ema10'].iloc[-1]:.2f} | RSI(14)={df['rsi'].iloc[-1]:.2f}")
        logging.info(f"🔺 Résistance={recent_high:.2f} | 🔻 Support={recent_low:.2f}")
        logging.info(f"⚡ Momentum={((current_price - df['close'].iloc[-5]) / df['close'].iloc[-5] * 100):.3f}% | ATR={atr:.3f}")
        
        return {
            'bid': tick.bid,
            'ask': tick.ask,
            'spread': tick.ask - tick.bid,
            'current_price': current_price,
            'ema5': df['ema5'].iloc[-1],
            'ema10': df['ema10'].iloc[-1],
            'atr': atr,
            'resistance': recent_high,
            'support': recent_low,
            'momentum': (current_price - df['close'].iloc[-5]) / df['close'].iloc[-5] * 100,
            'rsi': df['rsi'].iloc[-1]  # Retour de la valeur du RSI
        }
        
    except Exception as e:
        logging.error(f"❌ Erreur données: {e}")
        return None

def get_signal(data):
    """Génération de signal renforcée avec un score de confiance"""
    try:
        # Récupération des données
        price = data['current_price']
        ema5 = data['ema5']
        ema10 = data['ema10']
        rsi = data['rsi']
        atr = data['atr']
        resistance = data['resistance']
        support = data['support']

        # Paramètres de la stratégie (configurable via config.py)
        # CONFIDENCE_SCORE_REQUIRED est maintenant importé du fichier config

        # Log de l'analyse technique générale
        trend_status = "📈 HAUSSIER" if price > ema5 > ema10 else "📉 BAISSIER" if price < ema5 < ema10 else "↔️ NEUTRE"
        rsi_status = "🚀 FORT" if rsi > 60 else "⬇️ FAIBLE" if rsi < 40 else "� NEUTRE"
        
        logging.info(f"🎯 Analyse: {trend_status} | RSI: {rsi_status} ({rsi:.1f})")
        logging.info(f"📊 Prix: {price:.2f} | EMA5: {ema5:.2f} | EMA10: {ema10:.2f}")
        logging.info(f"📈 Support: {support:.2f} | Résistance: {resistance:.2f}")

        # --- ÉVALUATION DU SIGNAL D'ACHAT (BUY) ---
        buy_score = 0
        
        # Condition 1: Tendance (croisement EMA)
        if price > ema5 and ema5 > ema10:
            buy_score += 1
            logging.info("✅ BUY Condition 1: Tendance haussière confirmée")
        
        # Condition 2: Momentum (RSI) - Moins strict pour plus d'agressivité
        if rsi > 50:  # Retour à 50 au lieu de 52 pour plus de trades
            buy_score += 1
            logging.info("✅ BUY Condition 2: RSI confirme la force acheteuse")
            
        # Condition 3: Confirmation de la tendance (prix par rapport à EMA10)
        if price > ema10:
            buy_score += 1
            logging.info("✅ BUY Condition 3: Prix au-dessus d'EMA10")

        logging.info(f"🔍 Analyse BUY: Score de confiance = {buy_score}/{CONFIDENCE_SCORE_REQUIRED}")

        if buy_score >= CONFIDENCE_SCORE_REQUIRED:
            logging.info("✅ Conditions BUY remplies - Calcul TP/SL dynamique...")
            
            # Calcul dynamique du risque
            sl_distance_atr = atr * ATR_MULTIPLIER
            sl_distance = max(MIN_SL_DISTANCE, min(sl_distance_atr, MAX_SL_DISTANCE))
            tp_distance = sl_distance * RISK_REWARD_RATIO
            sl_price = price - sl_distance
            tp_price = price + tp_distance
            
            # Filtre de sécurité: le TP est-il réaliste par rapport à la résistance ?
            if tp_price > resistance:
                logging.warning(f"⚠️ Signal BUY ignoré: le TP ({tp_price:.2f}) est au-dessus de la résistance ({resistance:.2f})")
                return None
            
            rr_ratio_calculated = tp_distance / sl_distance
            logging.info(f"🔍 Signal BUY de haute qualité - R/R: {rr_ratio_calculated:.2f}:1")
            logging.info(f"💰 TP: +{tp_distance:.3f} | SL: -{sl_distance:.3f} (ATR + Score)")

            return {
                'signal': 'BUY',
                'entry': data['ask'],
                'sl': sl_price,
                'tp': tp_price,
                'rr_ratio': rr_ratio_calculated
            }

        # --- ÉVALUATION DU SIGNAL DE VENTE (SELL) ---
        sell_score = 0

        # Condition 1: Tendance (croisement EMA)
        if price < ema5 and ema5 < ema10:
            sell_score += 1
            logging.info("✅ SELL Condition 1: Tendance baissière confirmée")
        
        # Condition 2: Momentum (RSI) - Moins strict pour plus d'agressivité
        if rsi < 50:  # Retour à 50 au lieu de 48 pour plus de trades
            sell_score += 1
            logging.info("✅ SELL Condition 2: RSI confirme la force vendeuse")

        # Condition 3: Confirmation de la tendance (prix par rapport à EMA10)
        if price < ema10:
            sell_score += 1
            logging.info("✅ SELL Condition 3: Prix en-dessous d'EMA10")

        logging.info(f"🔍 Analyse SELL: Score de confiance = {sell_score}/{CONFIDENCE_SCORE_REQUIRED}")

        if sell_score >= CONFIDENCE_SCORE_REQUIRED:
            logging.info("✅ Conditions SELL remplies - Calcul TP/SL dynamique...")
            
            # Calcul dynamique du risque
            sl_distance_atr = atr * ATR_MULTIPLIER
            sl_distance = max(MIN_SL_DISTANCE, min(sl_distance_atr, MAX_SL_DISTANCE))
            tp_distance = sl_distance * RISK_REWARD_RATIO
            sl_price = price + sl_distance
            tp_price = price - tp_distance
            
            # Filtre de sécurité: le TP est-il réaliste par rapport au support ?
            if tp_price < support:
                logging.warning(f"⚠️ Signal SELL ignoré: le TP ({tp_price:.2f}) est en dessous du support ({support:.2f})")
                return None
            
            rr_ratio_calculated = tp_distance / sl_distance
            logging.info(f"🔍 Signal SELL de haute qualité - R/R: {rr_ratio_calculated:.2f}:1")
            logging.info(f"💰 TP: +{tp_distance:.3f} | SL: -{sl_distance:.3f} (ATR + Score)")

            return {
                'signal': 'SELL',
                'entry': data['bid'],
                'sl': sl_price,
                'tp': tp_price,
                'rr_ratio': rr_ratio_calculated
            }

        # Aucun signal de haute qualité
        logging.info("⏳ Pas de signal de haute qualité - Conditions non remplies")
        return None
        
    except Exception as e:
        logging.error(f"❌ Erreur signal: {e}")
        return None

def can_place_trade():
    """Vérifie si on peut placer un trade (max 5 par minute)"""
    global trade_timestamps
    current_time = time.time()
    
    # Nettoyer les timestamps plus anciens que 1 minute
    minute_ago = current_time - 60  # 60 secondes = 1 minute
    trade_timestamps = [ts for ts in trade_timestamps if ts > minute_ago]
    
    # Vérifier le nombre de trades dans la dernière minute
    trades_last_minute = len(trade_timestamps)
    
    if trades_last_minute >= MAX_TRADES_PER_MINUTE:
        next_allowed_trade = min(trade_timestamps) + 60
        wait_time = next_allowed_trade - current_time
        logging.warning(f"⏳ Limite de {MAX_TRADES_PER_MINUTE} trades/minute atteinte. Attente {wait_time:.0f}s")
        return False
    
    logging.info(f"✅ Trades cette minute: {trades_last_minute}/{MAX_TRADES_PER_MINUTE}")
    return True

def record_trade():
    """Enregistre le timestamp d'un trade placé"""
    global trade_timestamps
    trade_timestamps.append(time.time())

def calculate_adaptive_lot_size(sl_distance):
    """Calcul adaptatif de la taille de lot basé sur la balance et le SL"""
    try:
        account_info = mt5.account_info()
        if account_info is None:
            return 0.01  # Défaut sécurisé
        
        balance = account_info.balance
        margin_free = account_info.margin_free
        
        # Calcul du risque en $ basé sur le pourcentage de la balance
        risk_amount = balance * (RISK_PER_TRADE_PERCENT / 100)  # Conversion en décimal
        
        # Calcul du lot basé sur la distance SL réelle
        # Pour XAUUSD: 1 point = $1 pour 1 lot, donc 0.01 point = $0.01 pour 1 lot
        sl_distance_points = sl_distance * 10000  # Conversion en points (0.01 = 1 point)
        
        if sl_distance_points > 0:
            # 1 lot XAUUSD avec 1 point de mouvement = 1$ de P&L
            lot_size = risk_amount / sl_distance_points
        else:
            lot_size = 0.01  # Sécurité si SL invalide
        
        # Vérification de la marge nécessaire (estimation XAUUSD ≈ 100$ par 0.01 lot)
        estimated_margin_needed = lot_size * 10000  # Estimation conservative
        
        # Ajustement si pas assez de marge libre
        if estimated_margin_needed > margin_free * 0.7:  # Garder 30% de marge libre
            lot_size = (margin_free * 0.5) / 10000  # Utiliser max 50% de la marge libre
            logging.info(f"⚠️ Marge limitée! Lot ajusté à {lot_size:.3f}")
        
        # Arrondir au centième pour respecter les contraintes MT5 (0.01, 0.02, etc.)
        lot_size = round(lot_size, 2)
        
        # Limites min/max avec plus de flexibilité
        lot_size = max(0.01, min(1.0, lot_size))  # Entre 0.01 et 1.0 lot max
        
        # Logs informatifs
        risk_percent_actual = (lot_size * sl_distance_points / balance) * 100
        logging.info(f"💰 Balance: {balance:.2f}$ | Risque ciblé: {RISK_PER_TRADE_PERCENT}% ({risk_amount:.2f}$)")
        logging.info(f"📊 SL: {sl_distance:.3f} | Lot calculé: {lot_size:.2f} | Risque réel: {risk_percent_actual:.2f}%")
        
        return lot_size
        
    except Exception as e:
        logging.error(f"❌ Erreur calcul lot: {e}")
        return 0.01

def place_order(signal_data):
    """Placement d'ordre avec gestion intelligente du volume et limite par minute"""
    try:
        # 1. Vérification de la limite de trades par minute
        if not can_place_trade():
            return False
        
        # 2. Vérification de la marge disponible
        account_info = mt5.account_info()
        if account_info is None:
            logging.error("❌ Impossible de récupérer les informations du compte")
            return False
            
        margin_free = account_info.margin_free
        if margin_free < 300:  # Marge libre minimum réduite à 300$
            logging.warning(f"⚠️ Marge libre insuffisante: {margin_free:.2f}$ - Trade annulé")
            return False
        
        # 3. Calcul adaptatif du lot basé sur le SL
        sl_distance = abs(signal_data['entry'] - signal_data['sl'])
        lot = calculate_adaptive_lot_size(sl_distance)
        
        # 4. Préparation de la requête
        if signal_data['signal'] == 'BUY':
            order_type = mt5.ORDER_TYPE_BUY
            price = signal_data['entry']
            action = "📈 BUY"
        else:
            order_type = mt5.ORDER_TYPE_SELL
            price = signal_data['entry']
            action = "📉 SELL"
        
        # 5. Vérification des niveaux pour éviter "Invalid stops"
        symbol_info = mt5.symbol_info(SYMBOL)
        min_stop_level = symbol_info.trade_stops_level
        point = symbol_info.point
        
        # Distance minimum en points (généralement 20-30 points pour XAUUSD)
        min_distance_points = max(min_stop_level, 20)  # Au minimum 20 points
        min_distance_price = min_distance_points * point
        
        logging.info(f"🔧 Distance min requise: {min_distance_points} points ({min_distance_price:.2f})")
        
        # 6. Ajustement si nécessaire
        if signal_data['signal'] == 'BUY':
            # Pour BUY: SL doit être en dessous du prix d'au moins min_distance
            sl_distance_check = price - signal_data['sl']
            tp_distance_check = signal_data['tp'] - price
            
            if sl_distance_check < min_distance_price:
                signal_data['sl'] = price - min_distance_price
                logging.info(f"⚠️ SL ajusté: {signal_data['sl']:.2f} (distance min respectée)")
                
            if tp_distance_check < min_distance_price:
                signal_data['tp'] = price + min_distance_price
                logging.info(f"⚠️ TP ajusté: {signal_data['tp']:.2f} (distance min respectée)")
        else:
            # Pour SELL: SL doit être au dessus du prix d'au moins min_distance
            sl_distance_check = signal_data['sl'] - price
            tp_distance_check = price - signal_data['tp']
            
            if sl_distance_check < min_distance_price:
                signal_data['sl'] = price + min_distance_price
                logging.info(f"⚠️ SL ajusté: {signal_data['sl']:.2f} (distance min respectée)")
                
            if tp_distance_check < min_distance_price:
                signal_data['tp'] = price - min_distance_price
                logging.info(f"⚠️ TP ajusté: {signal_data['tp']:.2f} (distance min respectée)")
        
        # 7. Déterminer le mode de remplissage disponible
        symbol_info = mt5.symbol_info(SYMBOL)
        filling_mode = mt5.ORDER_FILLING_FOK
        
        # Vérifier les modes de remplissage supportés
        if symbol_info.filling_mode & 2:  # ORDER_FILLING_IOC
            filling_mode = mt5.ORDER_FILLING_IOC
        elif symbol_info.filling_mode & 1:  # ORDER_FILLING_FOK
            filling_mode = mt5.ORDER_FILLING_FOK
        else:
            filling_mode = mt5.ORDER_FILLING_RETURN  # Mode par défaut
        
        # 8. Création et envoi de la requête
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": lot,
            "type": order_type,
            "price": price,
            "sl": signal_data['sl'],
            "tp": signal_data['tp'],
            "magic": MAGIC_NUMBER,
            "comment": f"AdaptiveBot_RR{signal_data['rr_ratio']:.2f}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": filling_mode,
        }
        
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            # 9. Enregistrer le trade pour le compteur par minute
            record_trade()
            
            distance_sl = abs(price - signal_data['sl']) / 0.01
            distance_tp = abs(signal_data['tp'] - price) / 0.01
            
            logging.info(f"🎯 {action}: Lot adaptatif={lot} Prix={price:.2f}")
            logging.info(f"🎯 TP={signal_data['tp']:.2f} ({distance_tp:.0f}p) | SL={signal_data['sl']:.2f} ({distance_sl:.0f}p)")
            logging.info(f"📊 R/R: {signal_data['rr_ratio']:.2f}:1 | Risque: {RISK_PER_TRADE_PERCENT}%")
            logging.info(f"✅ Ordre #{result.order} exécuté avec succès !")
            return True  # Ordre exécuté avec succès
        else:
            logging.error(f"❌ Échec ordre: {result.retcode} - {result.comment}")
            return False  # Échec de l'ordre
            
    except Exception as e:
        logging.error(f"❌ Erreur placement: {e}")
        return False  # Erreur lors du placement

def check_positions():
    """Vérification des positions avec logs détaillés (nouvelle version adaptative)"""
    try:
        positions = mt5.positions_get(symbol=SYMBOL, magic=MAGIC_NUMBER)
        account_info = mt5.account_info()
        
        if account_info:
            logging.info(f"💰 Balance: {account_info.balance:.2f} | Equity: {account_info.equity:.2f}")
            logging.info(f"💹 Marge libre: {account_info.margin_free:.2f}")
        
        if positions:
            total_profit = sum([pos.profit for pos in positions])
            buy_count = len([p for p in positions if p.type == 0])
            sell_count = len([p for p in positions if p.type == 1])
            
            # Calcul du nombre de trades dans la dernière minute pour info
            current_time = time.time()
            minute_ago = current_time - 60
            recent_trades = len([ts for ts in trade_timestamps if ts > minute_ago])
            
            logging.info(f"📊 {len(positions)} position(s) ouvertes:")
            logging.info(f"   📈 BUY: {buy_count} | 📉 SELL: {sell_count}")
            logging.info(f"   💵 Profit total: {total_profit:.2f}")
            logging.info(f"   ⏱️ Trades cette minute: {recent_trades}/{MAX_TRADES_PER_MINUTE}")
            
            # Détail des positions si peu nombreuses
            if len(positions) <= 5:
                for i, pos in enumerate(positions):
                    direction = "📈 BUY" if pos.type == 0 else "📉 SELL"
                    logging.info(f"   Position {i+1}: {direction} | Volume: {pos.volume} | Profit: {pos.profit:.2f}")
            
            return len(positions)
        else:
            # Afficher quand même les trades récents même sans positions
            current_time = time.time()
            minute_ago = current_time - 60
            recent_trades = len([ts for ts in trade_timestamps if ts > minute_ago])
            
            logging.info("📊 Aucune position ouverte")
            logging.info(f"⏱️ Trades cette minute: {recent_trades}/{MAX_TRADES_PER_MINUTE}")
            return 0
            
    except Exception as e:
        logging.error(f"❌ Erreur vérification positions: {e}")
        return 0

def main():
    """Boucle principale avec gestion adaptative intelligente"""
    if not mt5.initialize():
        logging.error("❌ Échec initialisation MT5")
        return
    
    logging.info("🚀 Bot Adaptatif XAUUSD démarré !")
    logging.info("⏱️ Analyse: toutes les 1 seconde")
    logging.info(f"📊 R/R cible: {MIN_RR_RATIO}:1 (informatif)")
    logging.info("🎯 Momentum: ±0.005% (plus réactif)")
    logging.info("⚡ Délai entre trades: 1 seconde")
    logging.info(f"🧠 Gestion intelligente: MAX {MAX_TRADES_PER_MINUTE} trades/minute")
    logging.info(f"💰 Lot adaptatif: {RISK_PER_TRADE_PERCENT}% de risque par trade")
    logging.info("🛡️ Gestion risque: ATR dynamique + R/R 1.5:1")
    
    iteration = 0
    last_signal_time = 0
    
    try:
        while True:
            current_time = time.time()
            
            # Stats toutes les 60 itérations (1 minute avec analyse 1s)
            if iteration % 60 == 0:
                logging.info("="*60)
                logging.info(f"🔄 Bot Rapide - Itération {iteration} - {datetime.now().strftime('%H:%M:%S')}")
                num_pos = check_positions()
                logging.info("="*60)
            
            # Log de progression toutes les 10 itérations (20 secondes)
            elif iteration % 10 == 0:
                logging.info(f"⏱️ Analyse en cours... ({iteration} cycles)")
            
            # Analyse du marché avec logs détaillés
            logging.info(f"🔍 Cycle {iteration+1} - Analyse du marché...")
            data = get_market_data()
            if data is None:
                logging.warning("⚠️ Données indisponibles - Retry dans 0.5s")
                time.sleep(0.5)
                continue
            
            # Génération de signal avec logs détaillés
            signal = get_signal(data)
            
            # Placement si signal valide et délai respecté
            if signal:
                time_since_last = current_time - last_signal_time
                if time_since_last > 1:  # Réduit à 1 seconde
                    logging.info(f"🎯 Signal {signal['signal']} détecté - R/R: {signal['rr_ratio']:.2f}:1")
                    place_order(signal)
                    last_signal_time = current_time
                else:
                    logging.info(f"⏱️ Signal ignoré - Délai insuffisant ({time_since_last:.1f}s < 1s)")
            
            iteration += 1
            logging.info(f"💤 Pause 1s... (Prochaine analyse: {(iteration+1)})")
            time.sleep(1)  # 1 seconde entre analyses
            
    except KeyboardInterrupt:
        logging.info("🛑 Arrêt demandé")
    except Exception as e:
        logging.error(f"❌ Erreur: {e}")
    finally:
        final_positions = check_positions()
        if final_positions > 0:
            logging.info(f"⚠️ {final_positions} position(s) encore ouverte(s)")
        
        mt5.shutdown()
        logging.info("👋 Bot Rapide arrêté")

if __name__ == "__main__":
    main()
