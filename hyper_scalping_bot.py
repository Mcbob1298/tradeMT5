#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot Hyper-Scalping XAUUSD - Gains de quelques centimes
Stratégie ultra-agressive avec TP/SL fixes
"""

import MetaTrader5 as mt5
import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# Import des paramètres de configuration Hyper-Scalping
try:
    from config import (FIXED_TP_DOLLARS, SL_MULTIPLIER, FIXED_LOT_SIZE,
                       CONFIDENCE_SCORE_REQUIRED, MAX_TRADES_PER_MINUTE)
except ImportError:
    # Valeurs par défaut Hyper-Scalping
    FIXED_TP_DOLLARS = 0.10
    SL_MULTIPLIER = 10.0
    FIXED_LOT_SIZE = 0.01
    CONFIDENCE_SCORE_REQUIRED = 1
    MAX_TRADES_PER_MINUTE = 999

# Paramètres MT5
from config import MT5_LOGIN, MT5_PASSWORD, MT5_SERVER, SYMBOL, MAGIC_NUMBER, ANALYSIS_INTERVAL

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Variables globales pour la gestion des trades
trade_timestamps = []

# Variables pour le comptage statistique des trades (fenêtre glissante 1 minute)
buy_timestamps = []  # Liste des timestamps des trades BUY
sell_timestamps = []  # Liste des timestamps des trades SELL
WINDOW_DURATION = 60  # Fenêtre de temps pour compter les trades (1 minute)

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
    logging.info(f"💰 Balance: {account_info.balance} | Serveur: {account_info.server}")
    return True

def get_data():
    """Récupération et calcul des données techniques"""
    try:
        rates = mt5.copy_rates_from_pos(SYMBOL, mt5.TIMEFRAME_M1, 0, 100)
        if rates is None or len(rates) < 50:
            logging.error("❌ Données insuffisantes")
            return None
        
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        
        # Calcul des indicateurs techniques
        df['ema5'] = df['close'].ewm(span=5).mean()
        df['ema10'] = df['close'].ewm(span=10).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Prix actuels
        tick_info = mt5.symbol_info_tick(SYMBOL)
        if tick_info is None:
            logging.error("❌ Impossible de récupérer les prix actuels")
            return None
        
        return {
            'ask': tick_info.ask,
            'bid': tick_info.bid,
            'current_price': (tick_info.ask + tick_info.bid) / 2,
            'ema5': df['ema5'].iloc[-1],
            'ema10': df['ema10'].iloc[-1],
            'rsi': df['rsi'].iloc[-1],
            'spread': tick_info.ask - tick_info.bid
        }
        
    except Exception as e:
        logging.error(f"❌ Erreur données: {e}")
        return None

def get_signal(data):
    """Génération de signal pour Hyper-Scalping avec TP/SL fixes."""
    try:
        price = data['current_price']
        ema5 = data['ema5']
        ema10 = data['ema10']
        rsi = data['rsi']

        # Log de l'analyse technique générale
        trend_status = "📈 HAUSSIER" if price > ema5 > ema10 else "📉 BAISSIER" if price < ema5 < ema10 else "↔️ NEUTRE"
        rsi_status = "🚀 FORT" if rsi > 60 else "⬇️ FAIBLE" if rsi < 40 else "📊 NEUTRE"
        
        logging.info(f"🎯 Analyse: {trend_status} | RSI: {rsi_status} ({rsi:.1f})")
        logging.info(f"📊 Prix: {price:.2f} | EMA5: {ema5:.2f} | EMA10: {ema10:.2f}")

        # --- ÉVALUATION DU SIGNAL D'ACHAT (BUY) ---
        buy_score = 0
        if price > ema5 and ema5 > ema10: 
            buy_score += 1
            logging.info("✅ BUY Condition 1: Tendance haussière")
        if rsi > 50: 
            buy_score += 1
            logging.info("✅ BUY Condition 2: RSI > 50")
        if price > ema10: 
            buy_score += 1
            logging.info("✅ BUY Condition 3: Prix > EMA10")

        logging.info(f"🔍 Analyse BUY: Score = {buy_score}/{CONFIDENCE_SCORE_REQUIRED}")

        # --- ÉVALUATION DU SIGNAL DE VENTE (SELL) ---
        sell_score = 0
        if price < ema5 and ema5 < ema10: 
            sell_score += 1
            logging.info("✅ SELL Condition 1: Tendance baissière")
        if rsi < 50: 
            sell_score += 1
            logging.info("✅ SELL Condition 2: RSI < 50")
        if price < ema10: 
            sell_score += 1
            logging.info("✅ SELL Condition 3: Prix < EMA10")

        logging.info(f"🔍 Analyse SELL: Score = {sell_score}/{CONFIDENCE_SCORE_REQUIRED}")

        # Génération du signal avec TP/SL fixes
        if buy_score >= CONFIDENCE_SCORE_REQUIRED:
            tp_price = data['ask'] + FIXED_TP_DOLLARS  # Direct: 0.30 points
            sl_price = data['ask'] - (FIXED_TP_DOLLARS * SL_MULTIPLIER)  # Direct: 3.00 points
            
            logging.info("✅ Signal BUY détecté. Calcul TP/SL fixe...")
            logging.info(f"💰 TP: +${FIXED_TP_DOLLARS:.2f} | SL: -${FIXED_TP_DOLLARS * SL_MULTIPLIER:.2f} | R/R: 1:{SL_MULTIPLIER}")
            
            return {
                'signal': 'BUY',
                'entry': data['ask'],
                'tp': tp_price,
                'sl': sl_price,
                'rr_ratio': 1.0 / SL_MULTIPLIER
            }
            
        elif sell_score >= CONFIDENCE_SCORE_REQUIRED:
            tp_price = data['bid'] - FIXED_TP_DOLLARS  # Direct: 0.30 points
            sl_price = data['bid'] + (FIXED_TP_DOLLARS * SL_MULTIPLIER)  # Direct: 3.00 points
            
            logging.info("✅ Signal SELL détecté. Calcul TP/SL fixe...")
            logging.info(f"💰 TP: +${FIXED_TP_DOLLARS:.2f} | SL: -${FIXED_TP_DOLLARS * SL_MULTIPLIER:.2f} | R/R: 1:{SL_MULTIPLIER}")
            
            return {
                'signal': 'SELL',
                'entry': data['bid'],
                'tp': tp_price,
                'sl': sl_price,
                'rr_ratio': 1.0 / SL_MULTIPLIER
            }
        
        return None
        
    except Exception as e:
        logging.error(f"❌ Erreur génération signal: {e}")
        return None

def can_place_trade():
    """Vérification de la limite de trades par minute"""
    global trade_timestamps
    
    current_time = time.time()
    minute_ago = current_time - 60
    
    # Nettoyer les timestamps anciens
    trade_timestamps = [ts for ts in trade_timestamps if ts > minute_ago]
    
    if len(trade_timestamps) >= MAX_TRADES_PER_MINUTE:
        logging.warning(f"⚠️ Limite atteinte: {len(trade_timestamps)}/{MAX_TRADES_PER_MINUTE} trades/minute")
        return False
    
    return True

def record_trade():
    """Enregistre le timestamp d'un trade placé"""
    global trade_timestamps
    trade_timestamps.append(time.time())

def clean_old_timestamps():
    """Nettoie les timestamps plus anciens que la fenêtre de temps"""
    global buy_timestamps, sell_timestamps
    
    current_time = time.time()
    cutoff_time = current_time - WINDOW_DURATION
    
    # Garder seulement les timestamps dans la fenêtre de 1 minute
    buy_timestamps = [ts for ts in buy_timestamps if ts > cutoff_time]
    sell_timestamps = [ts for ts in sell_timestamps if ts > cutoff_time]

def check_and_update_trade_count(signal_type):
    """Enregistre le trade sans limitation (protection d'overtrading désactivée)"""
    global buy_timestamps, sell_timestamps
    
    current_time = time.time()
    
    # Nettoyer les anciens timestamps
    clean_old_timestamps()
    
    if signal_type == 'BUY':
        # Ajouter le nouveau trade sans vérification
        buy_timestamps.append(current_time)
        logging.info(f"📊 BUY dans la dernière minute: {len(buy_timestamps)}/∞")
        
    elif signal_type == 'SELL':
        # Ajouter le nouveau trade sans vérification
        sell_timestamps.append(current_time)
        logging.info(f"📊 SELL dans la dernière minute: {len(sell_timestamps)}/∞")
    
    return True

def place_order(signal_data):
    """Placement d'ordre simple avec lot fixe pour Hyper-Scalping."""
    try:
        # 1. Vérification de la limite de trades par minute
        if not can_place_trade():
            return False

        # 2. Vérification et gestion intelligente de la marge
        if not check_margin_and_manage_positions():
            return False

        # 3. Utilisation du lot fixe défini dans la config
        lot = FIXED_LOT_SIZE

        # 4. Préparation de la requête
        if signal_data['signal'] == 'BUY':
            order_type = mt5.ORDER_TYPE_BUY
            price = signal_data['entry']
            action = "📈 BUY"
        else:
            order_type = mt5.ORDER_TYPE_SELL
            price = signal_data['entry']
            action = "📉 SELL"

        # 5. Vérification des niveaux SL/TP (distance minimum MT5)
        min_distance = 0.20  # Distance minimum en points pour XAUUSD
        sl_distance = abs(signal_data['entry'] - signal_data['sl'])
        tp_distance = abs(signal_data['tp'] - signal_data['entry'])
        
        if sl_distance < min_distance or tp_distance < min_distance:
            logging.warning(f"⚠️ Distance SL/TP trop faible: SL={sl_distance:.3f} TP={tp_distance:.3f}")
            logging.info(f"🔧 Distance min requise: {min_distance} points")
            return False

        # 6. Préparation de la requête d'ordre
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": SYMBOL,
            "volume": lot,
            "type": order_type,
            "price": price,
            "sl": signal_data['sl'],
            "tp": signal_data['tp'],
            "magic": MAGIC_NUMBER,
            "comment": f"HyperScalp_TP{FIXED_TP_DOLLARS:.2f}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,  # IOC est souvent meilleur pour le scalping
        }
        
        # 7. Envoi de l'ordre
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            logging.info(f"🎯 {action}: Lot FIXE={lot} Prix={price:.2f}")
            logging.info(f"✅ Ordre #{result.order} exécuté avec succès !")
            record_trade()  # Enregistrer le trade pour la limite par minute
            check_and_update_trade_count(signal_data['signal'])  # Enregistrer le trade sans limitation
            return True
        else:
            logging.error(f"❌ Échec ordre: {result.retcode} - {result.comment}")
            return False
            
    except Exception as e:
        logging.error(f"❌ Erreur placement: {e}")
        return False

def check_positions():
    """Vérification et gestion des positions ouvertes"""
    try:
        positions = mt5.positions_get(symbol=SYMBOL)
        if positions is None:
            return
        
        if len(positions) > 0:
            total_profit = 0
            for pos in positions:
                profit = pos.profit
                profit_percent = (profit / pos.volume) if pos.volume > 0 else 0
                type_name = "BUY" if pos.type == 0 else "SELL"
                total_profit += profit
                logging.info(f"💼 Position {pos.ticket}: {type_name} {pos.volume} lots | P&L: {profit:.2f}$ ({profit_percent:.2f}%)")
            logging.info(f"💰 P&L total positions: {total_profit:.2f}$")
        else:
            logging.info("📊 Aucune position ouverte")
            
    except Exception as e:
        logging.error(f"❌ Erreur vérification positions: {e}")

def check_margin_and_manage_positions():
    """Vérification de la marge et gestion des positions si nécessaire"""
    try:
        account_info = mt5.account_info()
        if account_info is None:
            return False
            
        margin_free = account_info.margin_free
        symbol_info = mt5.symbol_info(SYMBOL)
        
        if symbol_info is None:
            logging.error("❌ Impossible de récupérer les infos du symbole")
            return False
        
        # Calcul de la marge requise pour un trade
        margin_required = FIXED_LOT_SIZE * symbol_info.margin_initial
        
        logging.info(f"💰 Balance: {account_info.balance:.2f} | Equity: {account_info.equity:.2f} | Marge libre: {margin_free:.2f}")
        logging.info(f"🏦 Marge requise pour trade: {margin_required:.2f}")
        
        # Si marge insuffisante
        if margin_free < margin_required * 2:  # Sécurité x2
            logging.warning(f"⚠️ Marge insuffisante! Libre: {margin_free:.2f} | Requise: {margin_required:.2f}")
            
            # Essayer de fermer les positions perdantes
            positions = mt5.positions_get(symbol=SYMBOL)
            if positions:
                for pos in positions:
                    if pos.profit < -1.0:  # Position perdante de plus de 1$
                        close_request = {
                            "action": mt5.TRADE_ACTION_DEAL,
                            "symbol": SYMBOL,
                            "volume": pos.volume,
                            "type": mt5.ORDER_TYPE_SELL if pos.type == 0 else mt5.ORDER_TYPE_BUY,
                            "position": pos.ticket,
                            "magic": MAGIC_NUMBER,
                        }
                        result = mt5.order_send(close_request)
                        if result.retcode == mt5.TRADE_RETCODE_DONE:
                            logging.info(f"🔄 Position perdante #{pos.ticket} fermée: {pos.profit:.2f}$")
                        break  # Fermer une seule position à la fois
            
            return False
        
        return True
        
    except Exception as e:
        logging.error(f"❌ Erreur vérification marge: {e}")
        return False

def main():
    """Fonction principale du bot Hyper-Scalping"""
    logging.info("🔪 BOT HYPER-SCALPING XAUUSD DÉMARRÉ !")
    logging.info(f"💰 TP Fixe: ${FIXED_TP_DOLLARS:.2f} | SL Multiplier: {SL_MULTIPLIER}x | Lot: {FIXED_LOT_SIZE}")
    logging.info(f"⚡ Agressivité: {CONFIDENCE_SCORE_REQUIRED}/3 | Max trades/min: {MAX_TRADES_PER_MINUTE}")
    logging.info("⚠️ ATTENTION: Stratégie à HAUT RISQUE - Gains minuscules mais fréquents")
    logging.info("=" * 80)
    
    if not initialize_mt5():
        return
    
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            
            # Affichage du statut toutes les minutes
            if cycle_count % 60 == 1:  # Toutes les 60 secondes environ
                account_info = mt5.account_info()
                if account_info:
                    logging.info("=" * 60)
                    logging.info(f"📊 STATUT - Cycle #{cycle_count}")
                    logging.info(f"💰 Balance: {account_info.balance:.2f} | Equity: {account_info.equity:.2f}")
                    logging.info(f"💹 Marge libre: {account_info.margin_free:.2f}")
                    check_positions()
                    minute_ago = time.time() - 60
                    recent_trades = [ts for ts in trade_timestamps if ts > minute_ago]
                    clean_old_timestamps()
                    logging.info(f"⏱️ Trades cette minute: {len(recent_trades)}/{MAX_TRADES_PER_MINUTE}")
                    logging.info(f"📊 BUY dernière minute: {len(buy_timestamps)}/∞ | SELL dernière minute: {len(sell_timestamps)}/∞")
                    logging.info("=" * 60)
            
            # Analyse technique et signaux
            logging.info(f"🔍 Cycle {cycle_count} - Analyse du marché...")
            data = get_data()
            
            if data is None:
                logging.warning("⚠️ Données indisponibles, attente...")
                time.sleep(ANALYSIS_INTERVAL)
                continue
            
            # Log des données de marché
            logging.info(f"💹 Prix: Bid={data['bid']:.2f} Ask={data['ask']:.2f} Spread={data['spread']:.2f}")
            
            # Génération et traitement du signal
            signal = get_signal(data)
            
            if signal:
                logging.info(f"🎯 Signal {signal['signal']} détecté - R/R: {signal['rr_ratio']:.2f}:1")
                success = place_order(signal)
                if success:
                    logging.info("✅ Trade placé avec succès !")
                else:
                    logging.warning("❌ Échec du placement de trade")
            else:
                logging.info("⏳ Pas de signal - Attente du prochain cycle")
            
            logging.info(f"💤 Pause {ANALYSIS_INTERVAL}s... (Prochaine analyse: {cycle_count + 1})")
            time.sleep(ANALYSIS_INTERVAL)
            
    except KeyboardInterrupt:
        logging.info("🛑 Arrêt demandé")
    except Exception as e:
        logging.error(f"❌ Erreur critique: {e}")
    finally:
        # Affichage du résumé final
        account_info = mt5.account_info()
        if account_info:
            logging.info("=" * 60)
            logging.info("📊 RÉSUMÉ FINAL")
            logging.info(f"💰 Balance: {account_info.balance:.2f} | Equity: {account_info.equity:.2f}")
            logging.info(f"💹 Marge libre: {account_info.margin_free:.2f}")
            check_positions()
            logging.info(f"⏱️ Total trades placés: {len(trade_timestamps)}")
            logging.info("=" * 60)
        
        logging.info("👋 Bot Hyper-Scalping arrêté")
        mt5.shutdown()

if __name__ == "__main__":
    main()
