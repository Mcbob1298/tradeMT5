"""
STRATÉGIE M1 "L'HYPER-SCALPER" - Bot Ultime
Stratégie ultra-rapide pour micro-impulsions et scalping intensif
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
import threading
from datetime import datetime
from ..config.config_ultimate import M1_SCALPER_CONFIG, SYMBOL, COLORS
from ..core.risk_manager import can_open_new_trade, place_order_safely

class M1Strategy:
    def __init__(self):
        self.config = M1_SCALPER_CONFIG
        self.magic_number = self.config["MAGIC_NUMBER"]
        self.name = self.config["NAME"]
        self.color = self.config["COLOR"]
        self.emoji = self.config["EMOJI"]
        self.is_running = False
        self.last_signal_time = 0
        
    def log(self, message, level="INFO"):
        """Log avec couleur et emoji de la stratégie"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {self.color}{self.emoji} {self.name}{COLORS['RESET']}: {message}")
        
    def connect_mt5(self):
        """Connexion à MetaTrader 5"""
        if not mt5.initialize():
            self.log("❌ Échec initialisation MT5", "ERROR")
            return False
        self.log("✅ Connexion MT5 établie")
        return True
        
    def get_market_data(self, timeframe=mt5.TIMEFRAME_M1, bars=300):
        """Récupère les données de marché pour M1 (moins de barres pour vitesse)"""
        try:
            rates = mt5.copy_rates_from_pos(SYMBOL, timeframe, 0, bars)
            if rates is None or len(rates) == 0:
                self.log("⚠️ Aucune donnée de marché reçue", "WARNING")
                return None
                
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            return df
            
        except Exception as e:
            self.log(f"💥 Erreur récupération données: {e}", "ERROR")
            return None
            
    def calculate_rsi(self, data, period=14):
        """Calcul du RSI optimisé pour M1"""
        try:
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        except:
            return pd.Series([50] * len(data))
            
    def calculate_adx(self, data, period=14):
        """Calcul de l'ADX optimisé pour M1"""
        try:
            high = data['high']
            low = data['low'] 
            close = data['close']
            
            plus_dm = high.diff()
            minus_dm = low.diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm > 0] = 0
            
            tr1 = pd.DataFrame(high - low)
            tr2 = pd.DataFrame(abs(high - close.shift(1)))
            tr3 = pd.DataFrame(abs(low - close.shift(1)))
            frames = [tr1, tr2, tr3]
            tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
            
            atr = tr.rolling(period).mean()
            plus_di = 100 * (plus_dm.ewm(alpha=1/period).mean() / atr)
            minus_di = 100 * (minus_dm.ewm(alpha=1/period).mean() / atr)
            
            dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
            adx = ((dx.shift(1) * (period - 1)) + dx) / period
            adx[:period] = dx[:period].expanding().mean()
            
            return adx.fillna(0)
            
        except Exception as e:
            self.log(f"⚠️ Erreur calcul ADX: {e}", "WARNING")
            return pd.Series([15] * len(data))
            
    def calculate_ema(self, data, period):
        """Calcul de l'EMA"""
        return data['close'].ewm(span=period).mean()
        
    def detect_divergence(self, df):
        """Détection des divergences RSI/Prix selon les paramètres optimaux M1"""
        try:
            rsi = self.calculate_rsi(df)
            if len(rsi) < 30:
                return None, 0
                
            # Paramètres M1 ultra-optimisés (de votre calibrage)
            lookback = 3  # Ultra-réactif pour M1
            min_strength = self.config["MIN_DIVERGENCE_STRENGTH"]  # 2.0
            
            # Points pivots prix et RSI
            price_highs = []
            price_lows = []
            rsi_highs = []
            rsi_lows = []
            
            for i in range(lookback, len(df) - lookback):
                # Highs
                if (df['high'].iloc[i] == df['high'].iloc[i-lookback:i+lookback+1].max() and 
                    rsi.iloc[i] == rsi.iloc[i-lookback:i+lookback+1].max()):
                    price_highs.append((i, df['high'].iloc[i]))
                    rsi_highs.append((i, rsi.iloc[i]))
                    
                # Lows  
                if (df['low'].iloc[i] == df['low'].iloc[i-lookback:i+lookback+1].min() and
                    rsi.iloc[i] == rsi.iloc[i-lookback:i+lookback+1].min()):
                    price_lows.append((i, df['low'].iloc[i]))
                    rsi_lows.append((i, rsi.iloc[i]))
            
            # Vérification divergences baissières
            if len(price_highs) >= 2 and len(rsi_highs) >= 2:
                last_price_high = price_highs[-1]
                prev_price_high = price_highs[-2]
                last_rsi_high = rsi_highs[-1]
                prev_rsi_high = rsi_highs[-2]
                
                if (last_price_high[1] > prev_price_high[1] and 
                    last_rsi_high[1] < prev_rsi_high[1]):
                    strength = abs(last_rsi_high[1] - prev_rsi_high[1])
                    if strength >= min_strength:
                        return "SELL", strength
            
            # Vérification divergences haussières
            if len(price_lows) >= 2 and len(rsi_lows) >= 2:
                last_price_low = price_lows[-1]
                prev_price_low = price_lows[-2]
                last_rsi_low = rsi_lows[-1]
                prev_rsi_low = rsi_lows[-2]
                
                if (last_price_low[1] < prev_price_low[1] and 
                    last_rsi_low[1] > prev_rsi_low[1]):
                    strength = abs(last_rsi_low[1] - prev_rsi_low[1])
                    if strength >= min_strength:
                        return "BUY", strength
                        
            return None, 0
            
        except Exception as e:
            self.log(f"💥 Erreur détection divergence: {e}", "ERROR")
            return None, 0
            
    def detect_micro_momentum(self, df):
        """Détection de micro-momentum pour M1 (analyse des 5 dernières bougies)"""
        try:
            if len(df) < 5:
                return False, None
                
            recent_closes = df['close'].tail(5).values
            recent_highs = df['high'].tail(5).values
            recent_lows = df['low'].tail(5).values
            
            # Momentum haussier: 3/5 bougies vertes et prix monte
            green_candles = sum(1 for i in range(4) if recent_closes[i+1] > recent_closes[i])
            if green_candles >= 3 and recent_closes[-1] > recent_closes[0]:
                return True, "BUY"
                
            # Momentum baissier: 3/5 bougies rouges et prix baisse  
            red_candles = sum(1 for i in range(4) if recent_closes[i+1] < recent_closes[i])
            if red_candles >= 3 and recent_closes[-1] < recent_closes[0]:
                return True, "SELL"
                
            return False, None
            
        except Exception as e:
            self.log(f"⚠️ Erreur détection micro-momentum: {e}", "WARNING")
            return False, None
            
    def analyze_signal(self):
        """Analyse complète pour signal M1"""
        try:
            df = self.get_market_data()
            if df is None or len(df) < 50:
                return None
                
            # Calcul des indicateurs
            adx = self.calculate_adx(df)
            current_adx = adx.iloc[-1]
            
            # Filtre ADX pour M1 (seuil très bas pour capter micro-impulsions)
            if current_adx < self.config["ADX_THRESHOLD"]:  # 15
                return None
                
            # Détection de divergence principale
            signal, strength = self.detect_divergence(df)
            if signal is None:
                return None
                
            # Confirmation par micro-momentum
            has_momentum, momentum_direction = self.detect_micro_momentum(df)
            if not has_momentum or momentum_direction != signal:
                return None
                
            # Filtre de volatilité pour M1 - éviter les périodes mortes
            recent_range = df['high'].tail(10).max() - df['low'].tail(10).min()
            if recent_range < 0.10:  # Moins de 10 cents de range = pas assez de volatilité
                return None
                
            current_price = df['close'].iloc[-1]
            self.log(f"🚀 Signal M1 détecté: {signal} (Force: {strength:.1f}, ADX: {current_adx:.1f}, Range: {recent_range:.3f})")
            
            return {
                "action": signal,
                "strength": strength,
                "adx": current_adx,
                "price": current_price,
                "range": recent_range,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            self.log(f"💥 Erreur analyse signal: {e}", "ERROR")
            return None
            
    def calculate_position_size(self):
        """Calcul de la taille de position pour M1 (plus petite)"""
        return self.config["VOLUME"]  # 0.01
        
    def place_trade(self, signal):
        """Place un trade basé sur le signal M1"""
        try:
            if not can_open_new_trade(self.magic_number, self.name):
                return False
                
            symbol_info = mt5.symbol_info(SYMBOL)
            if symbol_info is None:
                self.log("❌ Impossible de récupérer les infos du symbole", "ERROR")
                return False
                
            current_price = signal["price"]
            volume = self.calculate_position_size()
            
            # Calcul des niveaux selon le ratio R/R optimisé M1
            if signal["action"] == "BUY":
                order_type = mt5.ORDER_TYPE_BUY
                entry_price = symbol_info.ask
                
                # SL et TP pour M1 (très serrés)
                sl_distance = 0.25  # 25 cents pour M1
                tp_distance = sl_distance * self.config["RR_RATIO"]  # 1.2
                
                sl_price = entry_price - sl_distance
                tp_price = entry_price + tp_distance
                
            else:  # SELL
                order_type = mt5.ORDER_TYPE_SELL
                entry_price = symbol_info.bid
                
                sl_distance = 0.25
                tp_distance = sl_distance * self.config["RR_RATIO"]
                
                sl_price = entry_price + sl_distance
                tp_price = entry_price - tp_distance
            
            # Préparation de la requête
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": SYMBOL,
                "volume": volume,
                "type": order_type,
                "price": entry_price,
                "sl": round(sl_price, 5),
                "tp": round(tp_price, 5),
                "magic": self.magic_number,
                "comment": f"M1_Scalper_{signal['action']}_S{signal['strength']:.1f}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Placement sécurisé
            success, result = place_order_safely(request, self.name)
            
            if success:
                self.log(f"🚀 Trade M1 placé: {signal['action']} à {entry_price:.5f} (SL: {sl_price:.5f}, TP: {tp_price:.5f})")
                self.last_signal_time = time.time()
                return True
            else:
                self.log(f"❌ Échec placement trade M1: {result}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"💥 Erreur placement trade: {e}", "ERROR")
            return False
            
    def run_strategy(self):
        """Boucle principale de la stratégie M1"""
        self.log("🚀 Démarrage de l'Hyper-Scalper M1")
        self.is_running = True
        
        while self.is_running:
            try:
                # Pour M1, on permet plus de fréquence (minimum 3 minutes entre trades)
                if time.time() - self.last_signal_time < 180:
                    time.sleep(30)
                    continue
                    
                # Analyse ultra-rapide du marché
                signal = self.analyze_signal()
                if signal:
                    self.place_trade(signal)
                    
                # Attente très courte avant la prochaine analyse (30 secondes pour M1)
                time.sleep(30)
                
            except Exception as e:
                self.log(f"💥 Erreur dans la boucle principale: {e}", "ERROR")
                time.sleep(30)
                
    def stop_strategy(self):
        """Arrête la stratégie"""
        self.is_running = False
        self.log("🛑 Hyper-Scalper M1 arrêté")

# === FONCTION D'ENTRÉE POUR LE THREADING ===
def run_m1_strategy():
    """Fonction d'entrée pour le thread M1"""
    strategy = M1Strategy()
    
    if not strategy.connect_mt5():
        return
        
    try:
        strategy.run_strategy()
    except KeyboardInterrupt:
        strategy.log("🔄 Arrêt demandé par l'utilisateur")
    except Exception as e:
        strategy.log(f"💥 Erreur fatale: {e}", "ERROR")
    finally:
        strategy.stop_strategy()
        mt5.shutdown()

if __name__ == "__main__":
    # Test en standalone
    run_m1_strategy()
