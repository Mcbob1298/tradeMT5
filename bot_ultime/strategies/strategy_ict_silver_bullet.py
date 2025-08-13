#!/usr/bin/env python3
"""
🏅 STRATÉGIE ICT SILVER BULLET - BOT ULTIME
Intégration de la stratégie ICT Silver Bullet optimisée dans le Bot Ultime
Configuration finale pragmatique validée

Spécialisé XAUUSD uniquement - Configurations gagnantes
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import logging
from datetime import datetime, time
import threading
from typing import Dict, List, Optional, Tuple

class ICTSilverBulletStrategy:
    def __init__(self, symbol='XAUUSD', timeframe='M5'):
        self.symbol = symbol
        self.timeframe = timeframe
        self.is_active = True
        
        # Configurations gagnantes pragmatiques
        self.configs = {
            'XAUUSD_M1': {
                'version': 'PRAGMATIC_M1',
                'confidence_threshold': 0.70,
                'fvg_min_pips': 3.5,
                'lookback_period': 20,
                'max_daily_trades': 3,
                'preferred_sessions': ['london_session', 'ny_am_session']
            },
            'XAUUSD_M5': {
                'version': 'VALIDATED_PERFECT',
                'confidence_threshold': 0.60,
                'fvg_min_pips': 3.0,
                'lookback_period': 15,
                'max_daily_trades': 5,
                'preferred_sessions': ['london_session', 'ny_am_session']
            },
            'XAUUSD_M15': {
                'version': 'PRAGMATIC_M15',
                'confidence_threshold': 0.70,
                'fvg_min_pips': 4.0,
                'lookback_period': 12,
                'max_daily_trades': 2,
                'preferred_sessions': ['london_session']
            }
        }
        
        self.config = self.configs.get(f'{symbol}_{timeframe}', self.configs['XAUUSD_M5'])
        
        # Sessions de trading
        self.sessions = {
            'london_session': (time(7, 0), time(10, 0)),
            'ny_am_session': (time(13, 30), time(17, 0)),
            'ny_pm_session': (time(20, 0), time(22, 0))
        }
        
        # Risk management
        self.pip_value = 0.01
        self.risk_per_trade = 0.02  # 2%
        self.reward_risk_ratio = 2.0
        self.stop_loss_pips = 30
        
        # Daily tracking
        self.daily_trades = 0
        self.last_trade_date = None
        self.current_position = None
        
        # Timeframe mapping pour MT5
        self.tf_mapping = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15
        }
        
        logging.info(f"🏅 ICT Silver Bullet Strategy initialized: {symbol}_{timeframe}")
        logging.info(f"📊 Config: {self.config['version']} | Conf≥{self.config['confidence_threshold']} | Max Daily: {self.config['max_daily_trades']}")
    
    def is_valid_session(self) -> bool:
        """Vérifier si nous sommes dans une session valide"""
        current_time = datetime.now().time()
        preferred_sessions = self.config.get('preferred_sessions', [])
        
        if not preferred_sessions:
            return True
        
        for session_name, (start_time, end_time) in self.sessions.items():
            if start_time <= current_time <= end_time:
                return session_name in preferred_sessions
        
        return False
    
    def check_daily_limit(self) -> bool:
        """Vérifier la limite quotidienne"""
        current_date = datetime.now().date()
        
        if self.last_trade_date != current_date:
            self.daily_trades = 0
            self.last_trade_date = current_date
        
        max_daily = self.config.get('max_daily_trades', 5)
        return self.daily_trades < max_daily
    
    def get_market_data(self, bars: int = 100) -> Optional[pd.DataFrame]:
        """Récupérer les données de marché"""
        try:
            timeframe = self.tf_mapping[self.timeframe]
            rates = mt5.copy_rates_from_pos(self.symbol, timeframe, 0, bars)
            
            if rates is None or len(rates) == 0:
                return None
            
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'tick_volume': 'Volume'}, inplace=True)
            df.set_index('time', inplace=True)
            
            return df
            
        except Exception as e:
            logging.error(f"❌ Erreur récupération données: {e}")
            return None
    
    def detect_fvg(self, df: pd.DataFrame, current_idx: int) -> List[Dict]:
        """Détection des Fair Value Gaps"""
        if current_idx < 3:
            return []
        
        fvgs = []
        min_gap_size = self.config['fvg_min_pips'] * self.pip_value
        strength_threshold = self.config['confidence_threshold']
        
        # Analyse des 3 dernières bougies
        for i in range(max(1, current_idx - 25), current_idx - 2):
            candle1 = df.iloc[i]
            candle2 = df.iloc[i + 1]
            candle3 = df.iloc[i + 2]
            
            # Bullish FVG
            if (candle1['High'] < candle3['Low']):
                gap_size = candle3['Low'] - candle1['High']
                if gap_size >= min_gap_size:
                    momentum = abs(candle2['Close'] - candle2['Open']) / candle2['Open']
                    volume_factor = 1.0
                    
                    if 'Volume' in df.columns:
                        avg_volume = df['Volume'].iloc[max(0, i-10):i+3].mean()
                        volume_factor = min(candle2['Volume'] / avg_volume, 2.0)
                    
                    strength = min((gap_size / min_gap_size) * 0.4 + volume_factor * 0.3 + momentum * 100 * 0.3, 1.0)
                    
                    if strength >= strength_threshold:
                        fvgs.append({
                            'type': 'bullish',
                            'high': candle3['Low'],
                            'low': candle1['High'],
                            'strength': strength,
                            'age': current_idx - (i + 1)
                        })
            
            # Bearish FVG
            if (candle1['Low'] > candle3['High']):
                gap_size = candle1['Low'] - candle3['High']
                if gap_size >= min_gap_size:
                    momentum = abs(candle2['Close'] - candle2['Open']) / candle2['Open']
                    volume_factor = 1.0
                    
                    if 'Volume' in df.columns:
                        avg_volume = df['Volume'].iloc[max(0, i-10):i+3].mean()
                        volume_factor = min(candle2['Volume'] / avg_volume, 2.0)
                    
                    strength = min((gap_size / min_gap_size) * 0.4 + volume_factor * 0.3 + momentum * 100 * 0.3, 1.0)
                    
                    if strength >= strength_threshold:
                        fvgs.append({
                            'type': 'bearish',
                            'high': candle1['Low'],
                            'low': candle3['High'],
                            'strength': strength,
                            'age': current_idx - (i + 1)
                        })
        
        return fvgs
    
    def detect_liquidity_levels(self, df: pd.DataFrame, current_idx: int) -> List[Dict]:
        """Détection des niveaux de liquidité"""
        lookback = self.config['lookback_period']
        
        if current_idx < lookback:
            return []
        
        window = df.iloc[current_idx - lookback:current_idx + 1]
        levels = []
        
        highs = window['High'].values
        lows = window['Low'].values
        
        if len(highs) >= 5:
            # Trouver les niveaux significatifs
            num_levels = 2
            top_indices = np.argpartition(highs, -num_levels)[-num_levels:]
            bottom_indices = np.argpartition(lows, num_levels)[:num_levels]
            
            # Buy-Side Liquidity (BSL)
            for idx in top_indices:
                level_value = highs[idx]
                tolerance = np.std(highs) * 0.1
                touches = np.sum(np.abs(highs - level_value) <= tolerance)
                strength = min(touches / 2.5, 1.0)
                
                if strength >= 0.6:
                    levels.append({
                        'type': 'BSL',
                        'level': level_value,
                        'strength': strength
                    })
            
            # Sell-Side Liquidity (SSL)
            for idx in bottom_indices:
                level_value = lows[idx]
                tolerance = np.std(lows) * 0.1
                touches = np.sum(np.abs(lows - level_value) <= tolerance)
                strength = min(touches / 2.5, 1.0)
                
                if strength >= 0.6:
                    levels.append({
                        'type': 'SSL',
                        'level': level_value,
                        'strength': strength
                    })
        
        return levels
    
    def check_liquidity_sweep(self, df: pd.DataFrame, current_idx: int, levels: List[Dict]) -> Optional[Dict]:
        """Vérification des sweeps de liquidité"""
        if not levels or current_idx < 2:
            return None
        
        current_candle = df.iloc[current_idx]
        prev_candle = df.iloc[current_idx - 1]
        
        for level in levels:
            sweep_tolerance = 2 * self.pip_value
            
            if level['type'] == 'BSL':
                # Check BSL sweep (bearish signal)
                if (current_candle['High'] > level['level'] + sweep_tolerance and
                    prev_candle['High'] <= level['level'] + sweep_tolerance):
                    
                    # Validation avec rejet
                    wick_confirm = (current_candle['High'] - current_candle['Close']) >= \
                                 (current_candle['High'] - current_candle['Low']) * 0.4
                    
                    if wick_confirm:
                        return {
                            'type': 'BSL_SWEPT',
                            'level': level['level'],
                            'strength': level['strength'],
                            'entry_type': 'SELL'
                        }
            
            elif level['type'] == 'SSL':
                # Check SSL sweep (bullish signal)
                if (current_candle['Low'] < level['level'] - sweep_tolerance and
                    prev_candle['Low'] >= level['level'] - sweep_tolerance):
                    
                    # Validation avec rejet
                    wick_confirm = (current_candle['Close'] - current_candle['Low']) >= \
                                 (current_candle['High'] - current_candle['Low']) * 0.4
                    
                    if wick_confirm:
                        return {
                            'type': 'SSL_SWEPT',
                            'level': level['level'],
                            'strength': level['strength'],
                            'entry_type': 'BUY'
                        }
        
        return None
    
    def check_entry_signal(self, df: pd.DataFrame) -> Optional[Dict]:
        """Vérification du signal d'entrée complet"""
        current_idx = len(df) - 1
        
        # 1. Vérifications préliminaires
        if not self.is_valid_session():
            return None
        
        if not self.check_daily_limit():
            return None
        
        if self.current_position is not None:
            return None
        
        # 2. Détection FVG
        fvgs = self.detect_fvg(df, current_idx)
        if not fvgs:
            return None
        
        # 3. Détection niveaux de liquidité
        levels = self.detect_liquidity_levels(df, current_idx)
        if not levels:
            return None
        
        # 4. Vérification sweep
        sweep = self.check_liquidity_sweep(df, current_idx, levels)
        if not sweep:
            return None
        
        # 5. Alignement FVG-Sweep
        current_price = df.iloc[current_idx]['Close']
        
        for fvg in fvgs:
            alignment_score = 0.0
            
            if sweep['entry_type'] == 'SELL' and fvg['type'] == 'bearish':
                price_alignment = min(abs(sweep['level'] - fvg['high']) / fvg['high'], 0.02) / 0.02
                alignment_score = (1 - price_alignment) * 0.6 + fvg['strength'] * 0.4
                
            elif sweep['entry_type'] == 'BUY' and fvg['type'] == 'bullish':
                price_alignment = min(abs(sweep['level'] - fvg['low']) / fvg['low'], 0.02) / 0.02
                alignment_score = (1 - price_alignment) * 0.6 + fvg['strength'] * 0.4
            
            if alignment_score >= self.config['confidence_threshold']:
                return {
                    'entry_type': sweep['entry_type'],
                    'entry_price': current_price,
                    'confidence': alignment_score,
                    'fvg': fvg,
                    'sweep': sweep,
                    'timestamp': df.index[current_idx]
                }
        
        return None
    
    def calculate_position_size(self, entry_price: float) -> Tuple[float, float, float]:
        """Calcul de la taille de position et niveaux"""
        # Récupérer le solde du compte
        account_info = mt5.account_info()
        if account_info is None:
            balance = 1000.0  # Fallback
        else:
            balance = account_info.balance
        
        risk_amount = balance * self.risk_per_trade
        stop_distance = self.stop_loss_pips * self.pip_value
        
        # Calcul de la taille de position
        symbol_info = mt5.symbol_info(self.symbol)
        if symbol_info is None:
            return 0.01, stop_distance, stop_distance * self.reward_risk_ratio
        
        contract_size = symbol_info.trade_contract_size
        pip_value_calc = self.pip_value * contract_size
        
        position_size = risk_amount / (stop_distance * contract_size)
        position_size = max(0.01, min(position_size, 1.0))  # Limites
        
        take_profit_distance = stop_distance * self.reward_risk_ratio
        
        return position_size, stop_distance, take_profit_distance
    
    def open_position(self, signal: Dict) -> bool:
        """Ouvrir une position"""
        try:
            entry_price = signal['entry_price']
            position_size, sl_distance, tp_distance = self.calculate_position_size(entry_price)
            
            if signal['entry_type'] == 'SELL':
                order_type = mt5.ORDER_TYPE_SELL
                stop_loss = entry_price + sl_distance
                take_profit = entry_price - tp_distance
            else:  # BUY
                order_type = mt5.ORDER_TYPE_BUY
                stop_loss = entry_price - sl_distance
                take_profit = entry_price + tp_distance
            
            # Préparer la requête
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": position_size,
                "type": order_type,
                "price": entry_price,
                "sl": stop_loss,
                "tp": take_profit,
                "deviation": 20,
                "magic": 20250813,
                "comment": f"ICT_SB_{self.timeframe}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Envoyer l'ordre
            result = mt5.order_send(request)
            
            if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                self.current_position = {
                    'ticket': result.order,
                    'entry_type': signal['entry_type'],
                    'entry_price': entry_price,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'volume': position_size,
                    'confidence': signal['confidence'],
                    'timestamp': datetime.now()
                }
                
                self.daily_trades += 1
                
                logging.info(f"🏅 ICT SILVER BULLET ENTRY: {signal['entry_type']} {self.symbol} @ {entry_price:.5f}")
                logging.info(f"📊 Volume: {position_size:.2f} | Conf: {signal['confidence']:.2f} | SL: {stop_loss:.5f} | TP: {take_profit:.5f}")
                
                return True
            else:
                logging.error(f"❌ Échec ouverture position: {result}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Erreur ouverture position: {e}")
            return False
    
    def check_position_status(self) -> bool:
        """Vérifier le statut de la position actuelle"""
        if self.current_position is None:
            return True
        
        try:
            positions = mt5.positions_get(symbol=self.symbol)
            
            # Si aucune position ouverte, la position a été fermée
            if positions is None or len(positions) == 0:
                logging.info(f"💰 Position fermée: {self.current_position['entry_type']} {self.symbol}")
                self.current_position = None
                return True
            
            # Vérifier si notre position spécifique existe
            for pos in positions:
                if pos.ticket == self.current_position['ticket']:
                    return False  # Position encore ouverte
            
            # Notre position n'existe plus
            logging.info(f"💰 Position fermée: {self.current_position['entry_type']} {self.symbol}")
            self.current_position = None
            return True
            
        except Exception as e:
            logging.error(f"❌ Erreur vérification position: {e}")
            return True
    
    def run_strategy(self):
        """Boucle principale de la stratégie"""
        logging.info(f"🏅 ICT Silver Bullet Strategy démarrée: {self.symbol}_{self.timeframe}")
        
        while self.is_active:
            try:
                # Vérifier le statut des positions
                self.check_position_status()
                
                # Récupérer les données de marché
                df = self.get_market_data(150)
                if df is None:
                    time.sleep(5)
                    continue
                
                # Vérifier les signaux d'entrée
                signal = self.check_entry_signal(df)
                
                if signal:
                    logging.info(f"🎯 Signal détecté: {signal['entry_type']} {self.symbol} (Conf: {signal['confidence']:.2f})")
                    success = self.open_position(signal)
                    
                    if success:
                        logging.info(f"✅ Position ouverte avec succès")
                    else:
                        logging.error(f"❌ Échec ouverture position")
                
                # Attente adaptative selon le timeframe
                if self.timeframe == 'M1':
                    time.sleep(10)  # 10 secondes pour M1
                elif self.timeframe == 'M5':
                    time.sleep(30)  # 30 secondes pour M5
                else:  # M15
                    time.sleep(60)  # 1 minute pour M15
                
            except Exception as e:
                logging.error(f"❌ Erreur dans la boucle stratégie: {e}")
                time.sleep(30)
        
        logging.info(f"🛑 ICT Silver Bullet Strategy arrêtée: {self.symbol}_{self.timeframe}")
    
    def stop_strategy(self):
        """Arrêter la stratégie"""
        self.is_active = False
        logging.info(f"🛑 Arrêt demandé pour ICT Silver Bullet: {self.symbol}_{self.timeframe}")

def run_ict_silver_bullet_strategy(symbol='XAUUSD', timeframe='M5'):
    """Fonction d'exécution de la stratégie ICT Silver Bullet"""
    strategy = ICTSilverBulletStrategy(symbol, timeframe)
    strategy.run_strategy()
    return strategy
