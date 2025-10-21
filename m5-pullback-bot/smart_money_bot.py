"""
🎯 SMART MONEY BOT - CONCEPTS ICT/SMC
=====================================

Ce bot utilise les concepts Smart Money (ICT) au lieu des indicateurs techniques classiques:
- Structure de marché (Swing Highs/Lows)
- Break of Structure (BOS) et Change of Character (CHoCH)
- Fair Value Gaps (FVG / Imbalances)
- Order Blocks (OB)
- Multi-timeframe: H1 pour structure, M5 pour entrée

Auteur: Trading Bot v2.0 - Smart Money Edition
Date: 21 octobre 2025
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import sys
import os  # 🆕 Pour gestion des fichiers log

# =============================================================================
# CONFIGURATION GLOBALE
# =============================================================================

# Connexion MT5
MT5_LOGIN = 18491073
MT5_PASSWORD = "mr^WV%U8"
MT5_SERVER = "VantageInternational-Live 4"

# Symbole et paramètres
SYMBOL = "XAUUSD"
TIMEFRAME_HTF = mt5.TIMEFRAME_H1  # Higher TimeFrame - Structure/Tendance
TIMEFRAME_LTF = mt5.TIMEFRAME_M5  # Lower TimeFrame - Entrée précise

# Paramètres Structure
SWING_LOOKBACK = 2  # Nombre de bougies de chaque côté pour valider un swing point
MIN_STRUCTURE_POINTS = 5  # Minimum de swing points pour analyser la tendance

# Paramètres FVG
MIN_FVG_SIZE = 5.0  # Taille minimum d'un FVG en points (0.5 = 5 pips pour XAUUSD)
MAX_FVG_AGE = 20  # Nombre max de bougies depuis la création d'un FVG

# Paramètres Order Block
MIN_OB_MOVE = 10.0  # Mouvement minimum après l'OB en points (1.0 = 10 pips)
MAX_OB_AGE = 15  # Nombre max de bougies depuis la création d'un OB

# Paramètres de Trading
ENABLE_REAL_TRADING = True  # False = Mode simulation
MAX_RISK_PERCENT = 2.0  # Risque maximum par trade (% de l'equity)
MIN_RR_RATIO = 2.0  # Ratio Risk/Reward minimum requis

# 🎯 OPTIMISATION #5: Mode d'exécution des trades
USE_PENDING_ORDERS = True  # True = BUY_LIMIT/SELL_LIMIT, False = Market Orders
CANCEL_ORDERS_ON_CHOCH = True  # Annuler ordres limites si CHoCH détecté

# Sécurité
DAILY_LOSS_LIMIT_PERCENT = 5.0  # Arrêt si perte > 5% du capital journalier
MAX_DAILY_TRADES = 10  # Nombre maximum de trades par jour

# 🆕 OPTIMISATION #8: Killzones (Plages horaires interdites)
ENABLE_KILLZONES = True  # Activer/désactiver les killzones
# Pas de nouveaux trades:
# - Chaque jour de 23h à 00h (minuit) - Fermeture marchés
# - Week-end: Vendredi 23h → Lundi 00h
DAILY_BLACKOUT_START = 23  # 23h
DAILY_BLACKOUT_END = 0     # 00h (minuit)

# =============================================================================
# 🆕 OPTIMISATION #6: GESTION DES LOGS DANS UN FICHIER
# =============================================================================

LOG_FILE_HANDLE = None
CURRENT_LOG_DATE = None

def safe_log(message):
    """
    Log avec timestamp, écrit dans la console ET dans un fichier journalier.
    
    Crée automatiquement le dossier logs/ et un fichier par jour:
    - logs/smc_bot_2025-10-21.log
    - logs/smc_bot_2025-10-22.log
    - etc.
    """
    global LOG_FILE_HANDLE, CURRENT_LOG_DATE
    
    try:
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Vérifier s'il faut ouvrir un nouveau fichier (changement de jour ou premier lancement)
        if today_str != CURRENT_LOG_DATE or LOG_FILE_HANDLE is None:
            if LOG_FILE_HANDLE is not None:
                LOG_FILE_HANDLE.close()
            
            # Créer le dossier 'logs' s'il n'existe pas
            log_dir = "logs"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Ouvrir le nouveau fichier log du jour
            log_path = os.path.join(log_dir, f"smc_bot_{today_str}.log")
            LOG_FILE_HANDLE = open(log_path, 'a', encoding='utf-8')
            CURRENT_LOG_DATE = today_str
        
        # Formater et écrire le message
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] {message}"
        
        # Écrire dans la console
        print(log_message, flush=True)
        sys.stdout.flush()
        
        # Écrire dans le fichier
        if LOG_FILE_HANDLE is not None:
            LOG_FILE_HANDLE.write(log_message + '\n')
            LOG_FILE_HANDLE.flush()
            
    except Exception as e:
        # En cas d'erreur de log, on ne veut pas crasher le bot
        print(f"[ERREUR LOGGING] {e}")

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def connect_mt5():
    """Connexion à MetaTrader 5"""
    if not mt5.initialize():
        safe_log(f"❌ Échec initialisation MT5: {mt5.last_error()}")
        return False
    
    if not mt5.login(MT5_LOGIN, MT5_PASSWORD, MT5_SERVER):
        safe_log(f"❌ Échec connexion MT5: {mt5.last_error()}")
        mt5.shutdown()
        return False
    
    account_info = mt5.account_info()
    if account_info:
        safe_log(f"✅ Connecté à MT5 - Compte: {account_info.login}")
        safe_log(f"💰 Balance: {account_info.balance:.2f}€ | Equity: {account_info.equity:.2f}€")
        return True
    
    return False

def is_in_killzone():
    """
    🆕 OPTIMISATION #8: Vérifie si on est dans une killzone (plage horaire interdite).
    
    Killzones:
    - Chaque jour: 23h00 → 00h00 (minuit)
    - Week-end: Vendredi 23h00 → Lundi 00h00
    
    Returns:
        bool: True si dans une killzone (pas de nouveaux trades), False sinon
    """
    if not ENABLE_KILLZONES:
        return False
    
    now = datetime.now()
    current_hour = now.hour
    current_weekday = now.weekday()  # 0=Lundi, 4=Vendredi, 5=Samedi, 6=Dimanche
    
    # 1. Vérifier si c'est le week-end (Samedi ou Dimanche)
    if current_weekday in [5, 6]:  # Samedi ou Dimanche
        return True
    
    # 2. Vérifier si c'est Vendredi soir après 23h
    if current_weekday == 4 and current_hour >= DAILY_BLACKOUT_START:  # Vendredi >= 23h
        return True
    
    # 3. Vérifier si c'est Lundi avant minuit (début de semaine)
    if current_weekday == 0 and current_hour < DAILY_BLACKOUT_END:  # Lundi < 00h (impossible car 00h = minuit)
        return True
    
    # 4. Vérifier blackout quotidien (23h-00h chaque jour)
    if current_hour >= DAILY_BLACKOUT_START:  # >= 23h
        return True
    
    return False

# =============================================================================
# CLASSE SMART MONEY BOT
# =============================================================================

class SmartMoneyBot:
    def __init__(self):
        self.symbol = SYMBOL
        self.htf = TIMEFRAME_HTF
        self.ltf = TIMEFRAME_LTF
        
        # État du bot
        self.is_running = False
        self.start_balance = 0.0
        self.daily_trades_count = 0
        self.open_positions = []
        
        # Cache de données
        self.htf_data = None
        self.ltf_data = None
        self.swing_highs = []
        self.swing_lows = []
        self.current_trend = "NEUTRAL"
        self.last_bos = None
        self.last_choch = None  # Change of Character
        self.poi_zones = []  # Points of Interest (FVG + OB)
        
        # 🔧 OPTIMISATION: Cache pour éviter la ré-analyse H1 toutes les 30s
        self.last_htf_candle_time = None  # Timestamp de la dernière bougie H1 analysée
        self.htf_analysis_cache = None    # Résultat de l'analyse H1
        self.bos_confirmed_in_past = False  # True si un BOS a eu lieu dans la tendance actuelle
        
        # 🎯 OPTIMISATION #4: Confirmation LTF (M5 CHoCH)
        self.monitoring_ltf_confirmation = False  # True quand prix touche POI H1
        self.ltf_entry_zone = None  # POI en cours de surveillance
        self.ltf_confirmation_type = None  # 'BULLISH' ou 'BEARISH' attendu
        
        # 🆕 OPTIMISATION #7: Trailing Stop Loss Progressif
        # Dictionnaire pour gérer les positions ouvertes
        # Format: {ticket: {'initial_sl': 123.45, 'current_trail_level': 0.5, 'entry_price': 123.00}}
        self.open_trades_manager = {}
        
        safe_log("🎯 Smart Money Bot initialisé")
    
    # =========================================================================
    # 1. IDENTIFICATION DE LA STRUCTURE (SWING POINTS)
    # =========================================================================
    
    def find_swing_points(self, rates_df, lookback=SWING_LOOKBACK):
        """
        Identifie les Swing Highs et Swing Lows.
        
        Un Swing High = une bougie dont le High est le plus haut 
        sur une fenêtre de (lookback*2+1) bougies centrée sur elle.
        
        Un Swing Low = une bougie dont le Low est le plus bas
        sur une fenêtre de (lookback*2+1) bougies centrée sur elle.
        
        Args:
            rates_df: DataFrame pandas avec colonnes ['time', 'open', 'high', 'low', 'close']
            lookback: Nombre de bougies de chaque côté pour validation
            
        Returns:
            tuple: (swing_highs_df, swing_lows_df) avec index, time, price
        """
        if len(rates_df) < lookback * 2 + 1:
            safe_log(f"⚠️ Pas assez de données pour swing points (besoin {lookback*2+1}, reçu {len(rates_df)})")
            return pd.DataFrame(), pd.DataFrame()
        
        # Rolling window pour trouver les extremums locaux
        window_size = lookback * 2 + 1
        
        # Swing High: le high est le maximum sur la fenêtre centrée
        rates_df['is_swing_high'] = (
            rates_df['high'].rolling(window=window_size, center=True).max() == rates_df['high']
        )
        
        # Swing Low: le low est le minimum sur la fenêtre centrée
        rates_df['is_swing_low'] = (
            rates_df['low'].rolling(window=window_size, center=True).min() == rates_df['low']
        )
        
        # Filtrer les swing points confirmés (pas ceux en formation)
        # On exclut les dernières 'lookback' bougies car elles ne sont pas confirmées
        confirmed_data = rates_df.iloc[:-lookback] if len(rates_df) > lookback else rates_df
        
        swing_highs = confirmed_data[confirmed_data['is_swing_high'] == True][['time', 'high']].copy()
        swing_highs.rename(columns={'high': 'price'}, inplace=True)
        
        swing_lows = confirmed_data[confirmed_data['is_swing_low'] == True][['time', 'low']].copy()
        swing_lows.rename(columns={'low': 'price'}, inplace=True)
        
        safe_log(f"📊 Structure trouvée: {len(swing_highs)} Swing Highs, {len(swing_lows)} Swing Lows")
        
        # 🆕 Logs détaillés des derniers swing points
        if len(swing_highs) >= 3:
            last_3_highs = swing_highs.tail(3)['price'].tolist()
            safe_log(f"   📈 Derniers Swing Highs: {last_3_highs[0]:.2f} → {last_3_highs[1]:.2f} → {last_3_highs[2]:.2f}")
        if len(swing_lows) >= 3:
            last_3_lows = swing_lows.tail(3)['price'].tolist()
            safe_log(f"   📉 Derniers Swing Lows: {last_3_lows[0]:.2f} → {last_3_lows[1]:.2f} → {last_3_lows[2]:.2f}")
        
        return swing_highs, swing_lows
    
    # =========================================================================
    # 2. DÉFINITION DE LA TENDANCE (BOS / CHoCH)
    # =========================================================================
    
    def detect_trend_and_bos(self, swing_highs, swing_lows):
        """
        Détermine la tendance en analysant la structure des swing points.
        
        BULLISH: Higher Highs (HH) + Higher Lows (HL)
        BEARISH: Lower Highs (LH) + Lower Lows (LL)
        
        BOS (Break of Structure): Cassure du dernier swing confirmant la tendance
        CHoCH (Change of Character): Cassure inverse signalant un possible retournement
        
        Returns:
            dict: {
                'trend': 'BULLISH'|'BEARISH'|'NEUTRAL',
                'bos_detected': bool,
                'bos_level': float,
                'choch_detected': bool,
                'choch_level': float
            }
        """
        if len(swing_highs) < 3 or len(swing_lows) < 3:
            safe_log("⚠️ Pas assez de swing points pour déterminer la tendance")
            return {
                'trend': 'NEUTRAL',
                'bos_detected': False,
                'bos_level': None,
                'choch_detected': False,
                'choch_level': None
            }
        
        # Prendre les 3 derniers swing points de chaque type
        recent_highs = swing_highs.tail(3)['price'].tolist()
        recent_lows = swing_lows.tail(3)['price'].tolist()
        
        # Analyse de la tendance
        # BULLISH: HH (Higher Highs) + HL (Higher Lows)
        hh_condition = recent_highs[-1] > recent_highs[-2] and recent_highs[-2] > recent_highs[-3]
        hl_condition = recent_lows[-1] > recent_lows[-2] and recent_lows[-2] > recent_lows[-3]
        
        # BEARISH: LH (Lower Highs) + LL (Lower Lows)
        lh_condition = recent_highs[-1] < recent_highs[-2] and recent_highs[-2] < recent_highs[-3]
        ll_condition = recent_lows[-1] < recent_lows[-2] and recent_lows[-2] < recent_lows[-3]
        
        trend = "NEUTRAL"
        if hh_condition and hl_condition:
            trend = "BULLISH"
            safe_log(f"📈 TENDANCE BULLISH détectée - HH: {recent_highs[-1]:.2f}, HL: {recent_lows[-1]:.2f}")
        elif lh_condition and ll_condition:
            trend = "BEARISH"
            safe_log(f"📉 TENDANCE BEARISH détectée - LH: {recent_highs[-1]:.2f}, LL: {recent_lows[-1]:.2f}")
        else:
            safe_log(f"➡️ Tendance NEUTRAL (structure mixte)")
            # 🆕 Diagnostic détaillé du NEUTRAL
            safe_log(f"   🔍 Analyse Higher Highs: {recent_highs[-3]:.2f} → {recent_highs[-2]:.2f} → {recent_highs[-1]:.2f}")
            safe_log(f"      {'✅' if hh_condition else '❌'} Condition HH: {recent_highs[-1]:.2f} > {recent_highs[-2]:.2f} AND {recent_highs[-2]:.2f} > {recent_highs[-3]:.2f}")
            safe_log(f"   🔍 Analyse Higher Lows: {recent_lows[-3]:.2f} → {recent_lows[-2]:.2f} → {recent_lows[-1]:.2f}")
            safe_log(f"      {'✅' if hl_condition else '❌'} Condition HL: {recent_lows[-1]:.2f} > {recent_lows[-2]:.2f} AND {recent_lows[-2]:.2f} > {recent_lows[-3]:.2f}")
            safe_log(f"   🔍 Analyse Lower Highs: {recent_highs[-3]:.2f} → {recent_highs[-2]:.2f} → {recent_highs[-1]:.2f}")
            safe_log(f"      {'✅' if lh_condition else '❌'} Condition LH: {recent_highs[-1]:.2f} < {recent_highs[-2]:.2f} AND {recent_highs[-2]:.2f} < {recent_highs[-3]:.2f}")
            safe_log(f"   🔍 Analyse Lower Lows: {recent_lows[-3]:.2f} → {recent_lows[-2]:.2f} → {recent_lows[-1]:.2f}")
            safe_log(f"      {'✅' if ll_condition else '❌'} Condition LL: {recent_lows[-1]:.2f} < {recent_lows[-2]:.2f} AND {recent_lows[-2]:.2f} < {recent_lows[-3]:.2f}")
            safe_log(f"   💡 Pour sortir du NEUTRAL, il faut:")
            safe_log(f"      🐂 BULLISH: HH + HL (tous les highs ET lows doivent monter)")
            safe_log(f"      🐻 BEARISH: LH + LL (tous les highs ET lows doivent descendre)")
        
        # Détection BOS (cassure de structure confirmant la tendance)
        bos_detected = False
        bos_level = None
        
        if trend == "BULLISH" and len(recent_highs) >= 2:
            # BOS Bullish = prix casse le dernier Swing High
            bos_level = recent_highs[-2]  # Avant-dernier SH
            bos_detected = recent_highs[-1] > bos_level
            if bos_detected:
                safe_log(f"🔥 BOS BULLISH confirmé - Cassure de {bos_level:.2f}")
        
        elif trend == "BEARISH" and len(recent_lows) >= 2:
            # BOS Bearish = prix casse le dernier Swing Low
            bos_level = recent_lows[-2]  # Avant-dernier SL
            bos_detected = recent_lows[-1] < bos_level
            if bos_detected:
                safe_log(f"🔥 BOS BEARISH confirmé - Cassure de {bos_level:.2f}")
        
        # 🔧 NOUVEAU: Détection CHoCH (Change of Character)
        choch_detected = False
        choch_level = None
        
        if trend == "BULLISH" and len(recent_lows) >= 2:
            # CHoCH en tendance BULLISH = prix casse le dernier Swing Low (mouvement opposé)
            choch_level = recent_lows[-2]
            # Si le prix actuel est sous le dernier SL, c'est un CHoCH
            current_price = self.htf_data.iloc[-1]['close']
            choch_detected = current_price < choch_level
            if choch_detected:
                safe_log(f"⚠️ CHoCH BULLISH→BEARISH détecté - Prix {current_price:.2f} < SL {choch_level:.2f}")
                safe_log(f"   💡 Possible retournement de tendance en cours!")
        
        elif trend == "BEARISH" and len(recent_highs) >= 2:
            # CHoCH en tendance BEARISH = prix casse le dernier Swing High (mouvement opposé)
            choch_level = recent_highs[-2]
            current_price = self.htf_data.iloc[-1]['close']
            choch_detected = current_price > choch_level
            if choch_detected:
                safe_log(f"⚠️ CHoCH BEARISH→BULLISH détecté - Prix {current_price:.2f} > SH {choch_level:.2f}")
                safe_log(f"   💡 Possible retournement de tendance en cours!")
        
        return {
            'trend': trend,
            'bos_detected': bos_detected,
            'bos_level': bos_level,
            'choch_detected': choch_detected,
            'choch_level': choch_level
        }
    
    # =========================================================================
    # 3. IDENTIFICATION DES ZONES D'INTÉRÊT (FVG / IMBALANCES)
    # =========================================================================
    
    def find_fvgs(self, rates_df):
        """
        Trouve les Fair Value Gaps (Imbalances).
        
        Un FVG est un schéma de 3 bougies où les mèches ne se chevauchent pas.
        
        FVG BULLISH (zone d'achat):
        - Bougie 3 low > Bougie 1 high (gap entre les deux)
        - Bougie 2 est une forte bougie haussière
        
        FVG BEARISH (zone de vente):
        - Bougie 3 high < Bougie 1 low (gap entre les deux)
        - Bougie 2 est une forte bougie baissière
        
        Returns:
            list: Liste de dict avec {type, top, bottom, candle_index, time, size}
        """
        if len(rates_df) < 3:
            return []
        
        fvgs = []
        
        for i in range(len(rates_df) - 2):
            candle1 = rates_df.iloc[i]
            candle2 = rates_df.iloc[i + 1]
            candle3 = rates_df.iloc[i + 2]
            
            # FVG BULLISH (zone d'achat potentielle)
            if candle3['low'] > candle1['high']:
                # Vérifier que la bougie 2 est haussière
                if candle2['close'] > candle2['open']:
                    gap_size = candle3['low'] - candle1['high']
                    
                    # Filtrer les FVG trop petits
                    if gap_size >= MIN_FVG_SIZE * 0.01:  # Conversion points -> price
                        fvg = {
                            'type': 'BULLISH',
                            'top': candle3['low'],
                            'bottom': candle1['high'],
                            'candle_index': i + 1,
                            'time': pd.to_datetime(candle2['time'], unit='s'),
                            'size': gap_size,
                            'age': len(rates_df) - (i + 2)  # Âge en nombre de bougies
                        }
                        
                        # Filtrer les FVG trop vieux
                        if fvg['age'] <= MAX_FVG_AGE:
                            fvgs.append(fvg)
            
            # FVG BEARISH (zone de vente potentielle)
            elif candle3['high'] < candle1['low']:
                # Vérifier que la bougie 2 est baissière
                if candle2['close'] < candle2['open']:
                    gap_size = candle1['low'] - candle3['high']
                    
                    if gap_size >= MIN_FVG_SIZE * 0.01:
                        fvg = {
                            'type': 'BEARISH',
                            'top': candle1['low'],
                            'bottom': candle3['high'],
                            'candle_index': i + 1,
                            'time': pd.to_datetime(candle2['time'], unit='s'),
                            'size': gap_size,
                            'age': len(rates_df) - (i + 2)
                        }
                        
                        if fvg['age'] <= MAX_FVG_AGE:
                            fvgs.append(fvg)
        
        if fvgs:
            safe_log(f"🎯 {len(fvgs)} FVG trouvés ({sum(1 for f in fvgs if f['type']=='BULLISH')} BULL, {sum(1 for f in fvgs if f['type']=='BEARISH')} BEAR)")
        
        return fvgs
    
    # =========================================================================
    # 4. IDENTIFICATION DES ORDER BLOCKS
    # =========================================================================
    
    def find_order_blocks(self, rates_df, trend):
        """
        Trouve les Order Blocks (zones de retournement institutionnel).
        
        OB BULLISH:
        - Dernière bougie baissière (close < open)
        - Avant un fort mouvement haussier
        - Le mouvement doit faire au moins MIN_OB_MOVE points
        
        OB BEARISH:
        - Dernière bougie haussière (close > open)
        - Avant un fort mouvement baissier
        
        Returns:
            list: Liste de dict avec {type, top, bottom, candle_index, time}
        """
        if len(rates_df) < 5:
            return []
        
        order_blocks = []
        
        for i in range(len(rates_df) - 3):
            current_candle = rates_df.iloc[i]
            
            # Analyser les 3 bougies suivantes pour détecter un "fort mouvement"
            next_3_candles = rates_df.iloc[i+1:i+4]
            
            # OB BULLISH (si tendance est BULLISH)
            if trend == "BULLISH":
                # Bougie actuelle est baissière
                if current_candle['close'] < current_candle['open']:
                    # Mesurer le mouvement haussier qui suit
                    move_start = current_candle['low']
                    move_end = next_3_candles['high'].max()
                    move_size = move_end - move_start
                    
                    # Si le mouvement est assez fort
                    if move_size >= MIN_OB_MOVE * 0.01:
                        ob = {
                            'type': 'BULLISH',
                            'top': current_candle['high'],
                            'bottom': current_candle['low'],
                            'candle_index': i,
                            'time': pd.to_datetime(current_candle['time'], unit='s'),
                            'move_size': move_size,
                            'age': len(rates_df) - (i + 1)
                        }
                        
                        if ob['age'] <= MAX_OB_AGE:
                            order_blocks.append(ob)
            
            # OB BEARISH (si tendance est BEARISH)
            elif trend == "BEARISH":
                # Bougie actuelle est haussière
                if current_candle['close'] > current_candle['open']:
                    move_start = current_candle['high']
                    move_end = next_3_candles['low'].min()
                    move_size = move_start - move_end
                    
                    if move_size >= MIN_OB_MOVE * 0.01:
                        ob = {
                            'type': 'BEARISH',
                            'top': current_candle['high'],
                            'bottom': current_candle['low'],
                            'candle_index': i,
                            'time': pd.to_datetime(current_candle['time'], unit='s'),
                            'move_size': move_size,
                            'age': len(rates_df) - (i + 1)
                        }
                        
                        if ob['age'] <= MAX_OB_AGE:
                            order_blocks.append(ob)
        
        if order_blocks:
            safe_log(f"📦 {len(order_blocks)} Order Blocks trouvés ({sum(1 for ob in order_blocks if ob['type']=='BULLISH')} BULL, {sum(1 for ob in order_blocks if ob['type']=='BEARISH')} BEAR)")
        
        return order_blocks
    
    # =========================================================================
    # 5. LOGIQUE DE TRADE MULTI-TIMEFRAME
    # =========================================================================
    
    def analyze_htf_structure(self):
        """
        Analyse la structure sur le Higher TimeFrame (H1).
        
        🔧 OPTIMISATION: Utilise un cache pour ne ré-analyser que si nouvelle bougie H1.
        
        Détermine:
        1. La tendance (BULLISH/BEARISH/NEUTRAL)
        2. Les swing points récents
        3. Si un BOS vient d'avoir lieu
        4. Si un CHoCH (retournement) est détecté
        """
        # Récupérer les données H1
        rates = mt5.copy_rates_from_pos(self.symbol, self.htf, 0, 100)
        if rates is None or len(rates) == 0:
            safe_log("❌ Erreur récupération données HTF")
            return None
        
        # Vérifier si c'est une nouvelle bougie H1
        current_htf_time = rates[-1]['time']
        
        if self.last_htf_candle_time == current_htf_time and self.htf_analysis_cache is not None:
            # ✅ Même bougie H1 → Utiliser le cache
            safe_log(f"💾 Cache H1 utilisé (même bougie depuis {datetime.fromtimestamp(current_htf_time).strftime('%H:%M')})")
            
            # 🆕 Afficher un résumé visuel de la situation actuelle
            cache = self.htf_analysis_cache
            current_price = rates[-1]['close']
            
            safe_log(f"┌─────────────────────────────────────────────────────────┐")
            safe_log(f"│ 📊 ÉTAT DU MARCHÉ (H1)                                  │")
            safe_log(f"├─────────────────────────────────────────────────────────┤")
            safe_log(f"│ 💰 Prix: {current_price:.2f}                                     │")
            safe_log(f"│ 📈 Tendance: {cache['trend']:<45}│")
            safe_log(f"│ 🔥 BOS: {'✅ Confirmé' if cache['bos_detected'] else '❌ Absent':<50}│")
            safe_log(f"│ ⚠️  CHoCH: {'⚠️  Détecté (retournement possible)' if cache['choch_detected'] else '✅ Non':<45}│")
            safe_log(f"│ 🎯 POI actifs: {len(self.poi_zones):<42}│")
            safe_log(f"│ 🔍 Monitoring LTF: {'✅ Actif (attente CHoCH M5)' if self.monitoring_ltf_confirmation else '❌ Inactif':<37}│")
            safe_log(f"└─────────────────────────────────────────────────────────┘")
            
            return self.htf_analysis_cache
        
        # 🔄 Nouvelle bougie H1 → Ré-analyser
        safe_log(f"\n{'='*60}")
        safe_log(f"📊 NOUVELLE BOUGIE H1 - ANALYSE STRUCTURE DU MARCHÉ")
        safe_log(f"{'='*60}")
        
        # Conversion en DataFrame
        self.htf_data = pd.DataFrame(rates)
        
        # 1. Trouver les swing points
        swing_highs, swing_lows = self.find_swing_points(self.htf_data)
        self.swing_highs = swing_highs
        self.swing_lows = swing_lows
        
        # 2. Déterminer la tendance et détecter BOS/CHoCH
        trend_info = self.detect_trend_and_bos(swing_highs, swing_lows)
        self.current_trend = trend_info['trend']
        
        # 3. Mettre à jour l'historique BOS
        if trend_info['bos_detected']:
            self.last_bos = trend_info['bos_level']
            self.bos_confirmed_in_past = True
            safe_log(f"🔥 BOS CONFIRMÉ - La tendance {self.current_trend} est validée")
        
        # 4. Détecter CHoCH (retournement)
        if trend_info['choch_detected']:
            self.last_choch = trend_info['choch_level']
            self.bos_confirmed_in_past = False  # Reset: nouvelle tendance potentielle
            safe_log(f"⚠️ CHoCH DÉTECTÉ - Possible retournement de tendance!")
        
        # Sauvegarder dans le cache
        self.last_htf_candle_time = current_htf_time
        self.htf_analysis_cache = trend_info
        
        safe_log(f"{'='*60}\n")
        
        return trend_info
    
    def find_poi_zones(self):
        """
        Identifie les Points of Interest (POI) pour entrée.
        
        Combine:
        - Fair Value Gaps (FVG)
        - Order Blocks (OB)
        
        Filtre selon la tendance actuelle.
        """
        if self.htf_data is None or self.current_trend == "NEUTRAL":
            return []
        
        safe_log(f"\n📍 RECHERCHE ZONES D'INTÉRÊT (POI)...")
        
        all_poi = []
        
        # Trouver les FVG
        fvgs = self.find_fvgs(self.htf_data)
        for fvg in fvgs:
            # Ne garder que les FVG alignés avec la tendance
            if fvg['type'] == self.current_trend:
                fvg['poi_type'] = 'FVG'
                all_poi.append(fvg)
        
        # Trouver les Order Blocks
        obs = self.find_order_blocks(self.htf_data, self.current_trend)
        for ob in obs:
            if ob['type'] == self.current_trend:
                ob['poi_type'] = 'OB'
                all_poi.append(ob)
        
        # Trier par âge (les plus récents en premier)
        all_poi.sort(key=lambda x: x['age'])
        
        self.poi_zones = all_poi
        
        if all_poi:
            safe_log(f"✅ {len(all_poi)} POI valides trouvés:")
            for i, poi in enumerate(all_poi[:3], 1):  # Afficher les 3 premiers
                safe_log(f"   {i}. {poi['poi_type']} {poi['type']}: {poi['bottom']:.2f} - {poi['top']:.2f} (âge: {poi['age']} bougies)")
            
            # 🆕 Afficher le prix actuel par rapport aux POI
            if self.htf_data is not None and len(self.htf_data) > 0:
                current_price = self.htf_data.iloc[-1]['close']
                safe_log(f"   💰 Prix actuel H1: {current_price:.2f}")
                
                # Trouver le POI le plus proche
                closest_poi = None
                min_distance = float('inf')
                
                for poi in all_poi[:3]:
                    poi_center = (poi['top'] + poi['bottom']) / 2
                    distance = abs(current_price - poi_center)
                    
                    if distance < min_distance:
                        min_distance = distance
                        closest_poi = poi
                
                if closest_poi:
                    poi_center = (closest_poi['top'] + closest_poi['bottom']) / 2
                    direction = "au-dessus" if current_price > poi_center else "en-dessous"
                    safe_log(f"   📍 POI le plus proche: {closest_poi['poi_type']} à {poi_center:.2f} ({direction}, écart: {abs(current_price - poi_center):.2f})")
                    
                    if closest_poi['bottom'] <= current_price <= closest_poi['top']:
                        safe_log(f"   🎯 PRIX DANS LA ZONE POI!")
                    else:
                        safe_log(f"   ⏳ Attente que le prix entre dans une zone POI...")
        else:
            safe_log(f"⚠️ Aucun POI trouvé aligné avec la tendance {self.current_trend}")
            safe_log(f"   💡 Les POI sont créés après un BOS (Fair Value Gaps + Order Blocks)")
            safe_log(f"   🔍 Recherche automatique à chaque nouveau BOS détecté")
        
        return all_poi
    
    def check_ltf_entry(self):
        """
        Vérifie sur le Lower TimeFrame (M5) si le prix entre dans une zone POI.
        
        🎯 OPTIMISATION #4: Au lieu d'entrer immédiatement, active le monitoring
        pour attendre une confirmation LTF (CHoCH M5).
        
        Returns:
            dict: Signal de trade ou None (si confirmation LTF activée, retourne None)
        """
        if not self.poi_zones:
            return None
        
        # Récupérer le prix actuel sur M5
        rates = mt5.copy_rates_from_pos(self.symbol, self.ltf, 0, 5)
        if rates is None or len(rates) == 0:
            return None
        
        current_price = rates[-1]['close']
        
        # Vérifier si le prix touche une zone POI
        for poi in self.poi_zones:
            # BULLISH: le prix doit toucher le haut de la zone (retracement)
            if poi['type'] == 'BULLISH':
                if poi['bottom'] <= current_price <= poi['top']:
                    safe_log(f"\n🎯 PRIX DANS ZONE POI H1!")
                    safe_log(f"   Prix {current_price:.2f} dans zone {poi['poi_type']} BULLISH")
                    safe_log(f"   Zone: {poi['bottom']:.2f} - {poi['top']:.2f}")
                    
                    # 🎯 NOUVELLE LOGIQUE: Activer monitoring LTF au lieu d'entrer
                    if not self.monitoring_ltf_confirmation:
                        self.monitoring_ltf_confirmation = True
                        self.ltf_entry_zone = poi
                        self.ltf_confirmation_type = 'BULLISH'
                        safe_log(f"🔍 ACTIVATION MONITORING LTF - Attente CHoCH M5 BULLISH...")
                    
                    return None  # Pas de signal immédiat
            
            # BEARISH: le prix doit toucher le bas de la zone
            elif poi['type'] == 'BEARISH':
                if poi['bottom'] <= current_price <= poi['top']:
                    safe_log(f"\n🎯 PRIX DANS ZONE POI H1!")
                    safe_log(f"   Prix {current_price:.2f} dans zone {poi['poi_type']} BEARISH")
                    safe_log(f"   Zone: {poi['bottom']:.2f} - {poi['top']:.2f}")
                    
                    # 🎯 NOUVELLE LOGIQUE: Activer monitoring LTF
                    if not self.monitoring_ltf_confirmation:
                        self.monitoring_ltf_confirmation = True
                        self.ltf_entry_zone = poi
                        self.ltf_confirmation_type = 'BEARISH'
                        safe_log(f"🔍 ACTIVATION MONITORING LTF - Attente CHoCH M5 BEARISH...")
                    
                    return None  # Pas de signal immédiat
        
        return None
    
    def analyze_ltf_for_confirmation(self):
        """
        🎯 OPTIMISATION #4: Analyse M5 pour détecter CHoCH de confirmation.
        
        Scénario BULLISH:
        1. Prix H1 entre dans POI BULLISH (zone de demande)
        2. Structure M5 est baissière (retracement)
        3. On attend que M5 casse son dernier Swing High M5 (CHoCH BULLISH)
        4. ALORS on achète le pullback sur FVG/OB M5
        
        Returns:
            dict: Signal de trade confirmé ou None
        """
        if not self.monitoring_ltf_confirmation or self.ltf_entry_zone is None:
            return None
        
        # Récupérer données M5 (50 bougies pour détecter structure)
        rates = mt5.copy_rates_from_pos(self.symbol, self.ltf, 0, 50)
        if rates is None or len(rates) < 20:
            return None
        
        ltf_df = pd.DataFrame(rates)
        current_price = ltf_df.iloc[-1]['close']
        
        # Vérifier que le prix est toujours dans la zone H1
        poi = self.ltf_entry_zone
        if not (poi['bottom'] <= current_price <= poi['top']):
            # Prix sorti de la zone avant confirmation
            safe_log(f"⚠️ Prix sorti de la zone POI H1 avant confirmation - Reset monitoring")
            self.monitoring_ltf_confirmation = False
            self.ltf_entry_zone = None
            return None
        
        # Trouver les swing points M5 (lookback=2)
        ltf_swing_highs, ltf_swing_lows = self.find_swing_points(ltf_df, lookback=2)
        
        if len(ltf_swing_highs) < 2 or len(ltf_swing_lows) < 2:
            return None  # Pas assez de structure
        
        # Détecter CHoCH M5
        choch_detected = False
        
        if self.ltf_confirmation_type == 'BULLISH':
            # CHoCH BULLISH = prix casse le dernier Swing High M5
            # (La structure M5 était baissière, maintenant elle devient haussière)
            last_sh_m5 = ltf_swing_highs.iloc[-1]['price']
            prev_sh_m5 = ltf_swing_highs.iloc[-2]['price']
            
            # Prix doit casser le dernier SH M5
            if current_price > last_sh_m5:
                choch_detected = True
                safe_log(f"\n✅ CHoCH M5 BULLISH DÉTECTÉ!")
                safe_log(f"   Prix {current_price:.2f} > Swing High M5 {last_sh_m5:.2f}")
                safe_log(f"   🎯 CONFIRMATION VALIDE - Entrée BUY autorisée!")
        
        elif self.ltf_confirmation_type == 'BEARISH':
            # CHoCH BEARISH = prix casse le dernier Swing Low M5
            last_sl_m5 = ltf_swing_lows.iloc[-1]['price']
            prev_sl_m5 = ltf_swing_lows.iloc[-2]['price']
            
            # Prix doit casser le dernier SL M5
            if current_price < last_sl_m5:
                choch_detected = True
                safe_log(f"\n✅ CHoCH M5 BEARISH DÉTECTÉ!")
                safe_log(f"   Prix {current_price:.2f} < Swing Low M5 {last_sl_m5:.2f}")
                safe_log(f"   🎯 CONFIRMATION VALIDE - Entrée SELL autorisée!")
        
        # Si CHoCH M5 détecté, créer le signal
        if choch_detected:
            # Reset monitoring
            self.monitoring_ltf_confirmation = False
            
            # Créer signal de trade
            if self.ltf_confirmation_type == 'BULLISH':
                signal = {
                    'type': 'BUY',
                    'entry_price': current_price,
                    'sl_price': poi['bottom'] - 0.50,  # SL sous la zone H1
                    'tp_price': self.swing_highs.iloc[-1]['price'] if len(self.swing_highs) > 0 else current_price + 10.0,
                    'poi': poi,
                    'reason': f"{poi['poi_type']} BULLISH + CHoCH M5 confirmé"
                }
            else:  # BEARISH
                signal = {
                    'type': 'SELL',
                    'entry_price': current_price,
                    'sl_price': poi['top'] + 0.50,  # SL au-dessus de la zone H1
                    'tp_price': self.swing_lows.iloc[-1]['price'] if len(self.swing_lows) > 0 else current_price - 10.0,
                    'poi': poi,
                    'reason': f"{poi['poi_type']} BEARISH + CHoCH M5 confirmé"
                }
            
            self.ltf_entry_zone = None
            return signal
        
        return None  # Attente CHoCH M5
    
    # =========================================================================
    # 6. GESTION DES ORDRES LIMITES (PENDING ORDERS)
    # =========================================================================
    
    def place_pending_orders(self):
        """
        🎯 OPTIMISATION #5: Place des ordres limites sur les POI H1.
        
        Au lieu d'attendre que le prix touche la zone pour entrer au marché,
        on place des ordres BUY_LIMIT / SELL_LIMIT directement sur les zones POI.
        
        Avantages:
        - Prix d'entrée garanti (pas de slippage)
        - Ratio R/R exact
        - Trading "passif" - le marché vient à nous
        """
        if not self.poi_zones:
            return
        
        if not ENABLE_REAL_TRADING:
            safe_log("🎮 MODE SIMULATION - Ordres limites non placés")
            return
        
        safe_log(f"\n📝 PLACEMENT D'ORDRES LIMITES SUR {len(self.poi_zones)} POI...")
        
        for poi in self.poi_zones[:3]:  # Limiter aux 3 meilleurs POI
            # Déterminer le prix d'entrée selon le type
            if poi['type'] == 'BULLISH':
                # BUY_LIMIT: On veut acheter au HAUT de la zone (meilleur prix)
                entry_price = poi['top']
                sl_price = poi['bottom'] - 0.50
                
                # TP = dernier Swing High H1
                if len(self.swing_highs) > 0:
                    tp_price = self.swing_highs.iloc[-1]['price']
                else:
                    tp_price = entry_price + 10.0
                
                order_type = mt5.ORDER_TYPE_BUY_LIMIT
                order_type_str = "BUY_LIMIT"
                
            else:  # BEARISH
                # SELL_LIMIT: On veut vendre au BAS de la zone (meilleur prix)
                entry_price = poi['bottom']
                sl_price = poi['top'] + 0.50
                
                # TP = dernier Swing Low H1
                if len(self.swing_lows) > 0:
                    tp_price = self.swing_lows.iloc[-1]['price']
                else:
                    tp_price = entry_price - 10.0
                
                order_type = mt5.ORDER_TYPE_SELL_LIMIT
                order_type_str = "SELL_LIMIT"
            
            # Vérifier R/R
            sl_distance = abs(entry_price - sl_price)
            tp_distance = abs(tp_price - entry_price)
            rr_ratio = tp_distance / sl_distance if sl_distance > 0 else 0
            
            if rr_ratio < MIN_RR_RATIO:
                safe_log(f"   ⚠️ {order_type_str} sur {poi['poi_type']} ignoré - R/R {rr_ratio:.2f} < {MIN_RR_RATIO}")
                continue
            
            # Calculer le lot
            account_info = mt5.account_info()
            if not account_info:
                continue
            
            risk_amount = account_info.equity * (MAX_RISK_PERCENT / 100)
            lot_size = risk_amount / (sl_distance * 100)
            lot_size = max(0.01, min(lot_size, 1.0))
            lot_size = round(lot_size, 2)
            
            # Préparer l'ordre limite
            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "symbol": self.symbol,
                "volume": lot_size,
                "type": order_type,
                "price": entry_price,
                "sl": sl_price,
                "tp": tp_price,
                "deviation": 20,
                "magic": 234567,
                "comment": f"SMC_Limit_{poi['poi_type']}",
                "type_time": mt5.ORDER_TIME_GTC,  # Good Till Cancelled
                "type_filling": mt5.ORDER_FILLING_RETURN,
            }
            
            # Envoyer l'ordre
            result = mt5.order_send(request)
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                safe_log(f"   ✅ {order_type_str} placé - Entry: {entry_price:.2f}, SL: {sl_price:.2f}, TP: {tp_price:.2f}")
                safe_log(f"      📊 Lot: {lot_size}, R/R: 1:{rr_ratio:.2f}, Ticket: {result.order}")
                
                # 🆕 OPTIMISATION #7: Enregistrer l'ordre dans le manager
                # Il sera converti en position plus tard lors de l'exécution
                self.open_trades_manager[result.order] = {
                    'initial_sl': sl_price,
                    'current_trail_level': 0,
                    'entry_price': entry_price
                }
                
            else:
                safe_log(f"   ❌ Erreur placement {order_type_str}: {result.retcode} - {result.comment}")
    
    def cancel_old_pending_orders(self):
        """
        Annule les ordres limites non exécutés qui ne sont plus valides.
        
        Un ordre devient invalide si:
        - La tendance H1 a changé (CHoCH)
        - Le POI est trop ancien
        - Un nouveau BOS a créé de nouveaux POI plus pertinents
        """
        # Récupérer tous les ordres en attente
        orders = mt5.orders_get(symbol=self.symbol)
        if orders is None or len(orders) == 0:
            return
        
        safe_log(f"\n🧹 Vérification {len(orders)} ordres en attente...")
        
        for order in orders:
            # Vérifier si l'ordre a notre magic number
            if order.magic != 234567:
                continue
            
            # Annuler l'ordre si CHoCH détecté ou si tendance NEUTRAL
            if self.current_trend == "NEUTRAL" or not self.bos_confirmed_in_past:
                safe_log(f"   🗑️ Annulation ordre {order.ticket} (tendance invalidée)")
                
                cancel_request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order": order.ticket,
                }
                
                result = mt5.order_send(cancel_request)
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    safe_log(f"      ✅ Ordre {order.ticket} annulé")
                else:
                    safe_log(f"      ❌ Erreur annulation: {result.comment}")
    
    # =========================================================================
    # 7. GESTION DES POSITIONS OUVERTES (TRAILING STOP PROGRESSIF)
    # =========================================================================
    
    def manage_open_positions(self):
        """
        🆕 OPTIMISATION #7: Gère les positions ouvertes avec un Trailing Stop progressif
        basé sur les paliers de R:R (Risk/Reward).
        
        Logique intelligente:
        - 1.5R atteint → SL déplacé à +0.5R (profit garanti, trade "payé")
        - 2.5R atteint → SL déplacé à +1.5R (verrouille 1.5R de profit)
        - 3.5R atteint → SL déplacé à +2.5R
        - 5.0R atteint → SL déplacé à +4.0R
        
        Le trade garde toujours ~1R de "marge de manœuvre" pour respirer.
        """
        
        # 🎯 PALIERS DE TRAILING (configurable)
        # Clé = R:R atteint, Valeur = R:R à sécuriser
        TRAIL_MILESTONES = {
            1.5: 0.5,   # Quand +1.5R atteint → SL à +0.5R
            2.5: 1.5,   # Quand +2.5R atteint → SL à +1.5R
            3.5: 2.5,   # Quand +3.5R atteint → SL à +2.5R
            5.0: 4.0,   # Quand +5.0R atteint → SL à +4.0R
            7.0: 6.0    # Quand +7.0R atteint → SL à +6.0R (bonus si grosse tendance)
        }
        
        try:
            positions = mt5.positions_get(symbol=self.symbol)
            if positions is None or len(positions) == 0:
                # S'il n'y a pas de positions, nettoyer le manager au cas où
                self.open_trades_manager = {k: v for k, v in self.open_trades_manager.items() if not isinstance(k, int)}
                return

            tick_info = mt5.symbol_info_tick(self.symbol)
            if tick_info is None:
                return

            current_tickets_in_mt5 = set()

            for position in positions:
                ticket = position.ticket
                current_tickets_in_mt5.add(ticket)

                # 1. Vérifier si le trade est dans notre manager
                if ticket not in self.open_trades_manager:
                    # Le trade a été pris (probablement un ordre limite exécuté)
                    # ou le bot a redémarré. Tentons de le récupérer.
                    
                    # Chercher dans l'historique des ordres
                    order_info = mt5.history_orders_get(ticket=ticket)
                    if order_info and len(order_info) > 0:
                        # On suppose que l'ordre limite a été exécuté
                        original_order = order_info[0]
                        
                        # Vérifier si l'ordre original est dans le manager
                        if original_order.ticket in self.open_trades_manager:
                            trade_info = self.open_trades_manager[original_order.ticket]
                            trade_info['entry_price'] = position.price_open  # MAJ avec prix réel
                            self.open_trades_manager[ticket] = trade_info
                            del self.open_trades_manager[original_order.ticket]
                            safe_log(f"🔄 Ordre limite {original_order.ticket} devenu position {ticket}. TSL activé.")
                        else:
                            # Trade inconnu, on l'ajoute avec son SL actuel
                            safe_log(f"🆕 Nouveau trade {ticket} détecté (non managé). Ajout au TSL.")
                            self.open_trades_manager[ticket] = {
                                'initial_sl': position.sl,
                                'current_trail_level': 0,
                                'entry_price': position.price_open
                            }
                    else:
                        # Impossible de retrouver l'ordre, on l'ajoute quand même
                        self.open_trades_manager[ticket] = {
                            'initial_sl': position.sl,
                            'current_trail_level': 0,
                            'entry_price': position.price_open
                        }

                # 2. Récupérer les infos du trade
                trade_info = self.open_trades_manager[ticket]
                initial_sl = trade_info['initial_sl']
                entry_price = trade_info['entry_price']
                current_trail_level = trade_info['current_trail_level']

                # 3. Calculer le R:R actuel
                risk_distance_R = abs(entry_price - initial_sl)
                if risk_distance_R == 0:
                    continue  # Division par zéro

                if position.type == mt5.POSITION_TYPE_BUY:
                    current_price = tick_info.bid
                    current_profit_distance = current_price - entry_price
                else:  # SELL
                    current_price = tick_info.ask
                    current_profit_distance = entry_price - current_price

                current_R_multiple = current_profit_distance / risk_distance_R

                # 4. Trouver le meilleur palier de trailing atteint
                best_trail_level = current_trail_level  # Par défaut, on garde l'actuel
                for R_milestone, R_secure_level in TRAIL_MILESTONES.items():
                    if current_R_multiple >= R_milestone and R_secure_level > current_trail_level:
                        best_trail_level = R_secure_level
                
                # 5. Si un nouveau palier est atteint, déplacer le SL
                if best_trail_level > current_trail_level:
                    if position.type == mt5.POSITION_TYPE_BUY:
                        new_sl_price = entry_price + (risk_distance_R * best_trail_level)
                    else:  # SELL
                        new_sl_price = entry_price - (risk_distance_R * best_trail_level)
                    
                    new_sl_price = round(new_sl_price, 2)
                    
                    # Vérifier qu'on ne déplace pas le SL *devant* le prix
                    if (position.type == mt5.POSITION_TYPE_BUY and new_sl_price >= current_price) or \
                       (position.type == mt5.POSITION_TYPE_SELL and new_sl_price <= current_price):
                        continue  # Ne pas déplacer le SL pour fermer le trade

                    safe_log(f"\n🔒 TRAILING STOP PROGRESSIF - Ticket {ticket}")
                    safe_log(f"   📊 R:R actuel: {current_R_multiple:.2f}R (palier {best_trail_level}R atteint)")
                    safe_log(f"   💰 Entry: {entry_price:.2f}, Prix actuel: {current_price:.2f}")
                    safe_log(f"   🛡️ SL actuel: {position.sl:.2f} → Nouveau SL: {new_sl_price:.2f}")
                    
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "position": ticket,
                        "sl": new_sl_price,
                        "tp": position.tp,
                    }
                    
                    result = mt5.order_send(request)
                    if result.retcode == mt5.TRADE_RETCODE_DONE:
                        safe_log(f"   ✅ SL déplacé avec succès - Profit {best_trail_level}R sécurisé!")
                        self.open_trades_manager[ticket]['current_trail_level'] = best_trail_level
                    else:
                        safe_log(f"   ❌ Erreur Trailing Stop: {result.retcode} - {result.comment}")

            # 6. Nettoyer les positions fermées du manager
            closed_tickets = set(self.open_trades_manager.keys()) - current_tickets_in_mt5
            for ticket in closed_tickets:
                # Ne supprimer que les positions (pas les ordres limites en attente)
                if ticket in self.open_trades_manager:
                    del self.open_trades_manager[ticket]
                    safe_log(f"🧹 Position {ticket} fermée, retirée du TSL Manager.")

        except Exception as e:
            safe_log(f"❌ Erreur dans manage_open_positions: {e}")
            import traceback
            safe_log(f"   Traceback: {traceback.format_exc()}")
    
    # =========================================================================
    # 8. EXÉCUTION DES TRADES (MODE MARKET - Alternative)
    # =========================================================================
    
    def execute_trade(self, signal):
        """
        Exécute un trade Market basé sur le signal.
        
        ⚠️ Cette fonction est utilisée uniquement si USE_PENDING_ORDERS = False
        Pour les ordres limites, voir place_pending_orders()
        
        Args:
            signal: dict avec type, entry_price, sl_price, tp_price, reason
        """
        if not ENABLE_REAL_TRADING:
            safe_log("🎮 MODE SIMULATION - Trade non exécuté")
            return False
        
        # Calcul du lot adapté au risque
        sl_distance = abs(signal['entry_price'] - signal['sl_price'])
        tp_distance = abs(signal['tp_price'] - signal['entry_price'])
        rr_ratio = tp_distance / sl_distance if sl_distance > 0 else 0
        
        # Vérifier le ratio R/R minimum
        if rr_ratio < MIN_RR_RATIO:
            safe_log(f"❌ Trade rejeté - Ratio R/R {rr_ratio:.2f} < {MIN_RR_RATIO}")
            return False
        
        # Calculer le lot basé sur le risque
        account_info = mt5.account_info()
        if not account_info:
            return False
        
        risk_amount = account_info.equity * (MAX_RISK_PERCENT / 100)
        lot_size = risk_amount / (sl_distance * 100)  # Conversion approximative pour XAUUSD
        lot_size = max(0.01, min(lot_size, 1.0))  # Limiter entre 0.01 et 1.0
        lot_size = round(lot_size, 2)
        
        safe_log(f"\n🚀 EXÉCUTION TRADE {signal['type']}")
        safe_log(f"   💰 Entry: {signal['entry_price']:.2f}")
        safe_log(f"   🛡️ SL: {signal['sl_price']:.2f} (distance: {sl_distance:.2f})")
        safe_log(f"   🎯 TP: {signal['tp_price']:.2f} (distance: {tp_distance:.2f})")
        safe_log(f"   ⚖️ Ratio R/R: 1:{rr_ratio:.2f}")
        safe_log(f"   📊 Lot: {lot_size}")
        safe_log(f"   💸 Risque: {risk_amount:.2f}€ ({MAX_RISK_PERCENT}%)")
        
        # Préparer l'ordre
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY if signal['type'] == 'BUY' else mt5.ORDER_TYPE_SELL,
            "price": signal['entry_price'],
            "sl": signal['sl_price'],
            "tp": signal['tp_price'],
            "deviation": 20,
            "magic": 234567,
            "comment": f"SMC_{signal['reason']}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        # Envoyer l'ordre
        result = mt5.order_send(request)
        
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            safe_log(f"✅ Trade exécuté avec succès - Ticket: {result.order}")
            self.daily_trades_count += 1
            
            # 🆕 OPTIMISATION #7: Enregistrer le trade dans le manager pour le trailing
            self.open_trades_manager[result.order] = {
                'initial_sl': signal['sl_price'],
                'current_trail_level': 0,  # Niveau de R:R sécurisé (0 = entrée)
                'entry_price': signal['entry_price']
            }
            safe_log(f"📋 Trade {result.order} enregistré dans le TSL Manager")
            
            return True
        else:
            safe_log(f"❌ Erreur exécution trade: {result.retcode} - {result.comment}")
            return False
    
    # =========================================================================
    # 7. BOUCLE PRINCIPALE
    # =========================================================================
    
    def run(self):
        """Boucle principale du bot"""
        safe_log("\n" + "="*60)
        safe_log("🚀 DÉMARRAGE SMART MONEY BOT")
        safe_log("="*60)
        
        if not connect_mt5():
            return
        
        account_info = mt5.account_info()
        self.start_balance = account_info.equity
        self.is_running = True
        
        safe_log(f"💰 Capital de départ: {self.start_balance:.2f}€")
        safe_log(f"📊 Timeframes: HTF={self.htf}, LTF={self.ltf}")
        safe_log(f"🎯 Symbole: {self.symbol}")
        safe_log(f"⚙️ Mode Trading: {'ORDRES LIMITES (BUY_LIMIT/SELL_LIMIT)' if USE_PENDING_ORDERS else 'ORDRES MARKET avec Confirmation LTF'}")
        safe_log(f"🎮 Simulation: {'OUI - Trades non exécutés' if not ENABLE_REAL_TRADING else 'NON - Trading Réel Activé'}")
        safe_log("\n")
        
        try:
            while self.is_running:
                # 🆕 OPTIMISATION #7: Gérer les positions ouvertes (TSL)
                # On le fait avant l'analyse pour être réactif
                self.manage_open_positions()
                
                # 1. Analyser la structure HTF (cache intelligent: uniquement sur nouvelle bougie H1)
                trend_info = self.analyze_htf_structure()
                
                # 🆕 OPTIMISATION #8: Vérifier si on est dans une killzone
                if is_in_killzone():
                    now = datetime.now()
                    day_name = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"][now.weekday()]
                    safe_log(f"🚫 KILLZONE ACTIVE - {day_name} {now.hour}h{now.minute:02d}")
                    safe_log(f"   💤 Pas de nouveaux trades (23h-00h en semaine, week-end complet)")
                    safe_log(f"   ℹ️ Le TSL reste actif sur les positions existantes")
                    safe_log(f"\n⏸️ Pause 30 secondes...\n")
                    time.sleep(30)
                    continue  # Passer à l'itération suivante sans chercher de trades
                
                if trend_info and trend_info['trend'] != "NEUTRAL":
                    # 🔧 OPTIMISATION: Vérifier CHoCH avant de chercher des trades
                    if trend_info['choch_detected']:
                        safe_log("⚠️ CHoCH détecté - ARRÊT des trades dans la direction actuelle")
                        safe_log("   💡 Attente de confirmation de la nouvelle tendance...")
                        # Reset le flag BOS car la tendance pourrait changer
                        self.bos_confirmed_in_past = False
                        
                        # 🎯 OPTIMISATION #5: Annuler ordres limites si CHoCH
                        if USE_PENDING_ORDERS and CANCEL_ORDERS_ON_CHOCH:
                            self.cancel_old_pending_orders()
                    
                    # 🔧 OPTIMISATION: Trade si tendance confirmée (pas besoin de BOS à chaque cycle)
                    # Un BOS doit avoir eu lieu DANS LE PASSÉ pour valider la tendance
                    elif self.bos_confirmed_in_past or trend_info['bos_detected']:
                        safe_log(f"✅ Tendance {trend_info['trend']} confirmée - Recherche de zones d'entrée...")
                        
                        # 2. Chercher les POI (uniquement si nouvelle analyse HTF ou pas encore fait)
                        if not self.poi_zones or trend_info['bos_detected']:
                            self.find_poi_zones()
                            
                            # 🎯 OPTIMISATION #5: Placer ordres limites sur POI
                            if USE_PENDING_ORDERS:
                                self.place_pending_orders()
                        
                        # 3. Vérifier les entrées sur LTF (Mode Market uniquement)
                        if not USE_PENDING_ORDERS:
                            signal = None
                            
                            # 🎯 OPTIMISATION #4: Si monitoring LTF actif, analyser pour confirmation
                            if self.monitoring_ltf_confirmation:
                                safe_log("🔍 Monitoring LTF actif - Analyse CHoCH M5...")
                                signal = self.analyze_ltf_for_confirmation()
                            else:
                                # Surveillance normale: chercher si prix touche POI H1
                                self.check_ltf_entry()  # Active le monitoring si zone touchée
                            
                            # 4. Exécuter le trade Market si signal confirmé
                            if signal:
                                self.execute_trade(signal)
                    else:
                        safe_log("⏳ Attente d'un BOS pour confirmer la tendance...")
                        safe_log(f"   💡 La tendance {trend_info['trend']} est détectée mais pas encore confirmée")
                        safe_log(f"   🎯 Un Break of Structure (BOS) est requis avant de trader")
                else:
                    safe_log("➡️ Marché NEUTRAL - Pas de setup valide")
                    safe_log(f"   💡 Le bot attend un marché directionnel clair (BULLISH ou BEARISH)")
                    safe_log(f"   🛡️ Protection contre le surtrading en range/consolidation")
                
                # Pause avant la prochaine analyse (M5 surveillance continue)
                safe_log(f"\n⏸️ Pause 30 secondes...\n")
                time.sleep(30)
                
        except KeyboardInterrupt:
            safe_log("\n⚠️ Arrêt demandé par l'utilisateur")
        finally:
            self.is_running = False
            mt5.shutdown()
            
            # 🆕 OPTIMISATION #6: Fermer proprement le fichier log
            global LOG_FILE_HANDLE
            if LOG_FILE_HANDLE is not None:
                safe_log("📝 Fermeture du fichier log...")
                LOG_FILE_HANDLE.close()
                LOG_FILE_HANDLE = None
            
            safe_log("🛑 Bot arrêté")

# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

if __name__ == "__main__":
    bot = SmartMoneyBot()
    bot.run()
