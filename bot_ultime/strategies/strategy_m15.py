"""
STRATÉGIE M15 "LE STRATÈGE" - Bot Ultime
Stratégie patiente et sélective pour les mouvements de fond
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
import time
import threading
from datetime import datetime
from ..config.config_ultimate import M15_SNIPER_CONFIG, SYMBOL, COLORS
from ..core.risk_manager import can_open_new_trade, place_order_safely

class M15Strategy:
    def __init__(self):
        self.config = M15_SNIPER_CONFIG
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
        
    def get_market_data(self, timeframe=mt5.TIMEFRAME_M15, bars=500):
        """Récupère les données de marché pour M15"""
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
        """Calcul du RSI"""
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
        """Calcul de l'ADX"""
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
            return pd.Series([20] * len(data))
            
    def calculate_ema(self, data, period):
        """Calcul de l'EMA"""
        return data['close'].ewm(span=period).mean()
        
    def detect_divergence(self, df):
        """Détection des divergences RSI/Prix selon les paramètres optimaux M15"""
        try:
            rsi = self.calculate_rsi(df)
            if len(rsi) < 50:
                return None, 0
                
            # Paramètres M15 optimisés
            lookback = 10  # Plus large pour M15
            min_strength = self.config["MIN_DIVERGENCE_STRENGTH"]
            
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
            
    def analyze_signal(self):
        """Analyse complète pour signal M15"""
        try:
            df = self.get_market_data()
            if df is None or len(df) < 100:
                return None
                
            # Calcul des indicateurs
            adx = self.calculate_adx(df)
            current_adx = adx.iloc[-1]
            
            # Filtre ADX - Éviter les marchés sans tendance
            if current_adx < self.config["ADX_THRESHOLD"]:
                return None
                
            # Détection de divergence
            signal, strength = self.detect_divergence(df)
            if signal is None:
                return None
                
            # Filtre EMA pour confirmation de tendance
            ema_50 = self.calculate_ema(df, 50)
            ema_200 = self.calculate_ema(df, 200)
            current_price = df['close'].iloc[-1]
            
            trend_confirmation = False
            if signal == "BUY" and current_price > ema_50.iloc[-1] > ema_200.iloc[-1]:
                trend_confirmation = True
            elif signal == "SELL" and current_price < ema_50.iloc[-1] < ema_200.iloc[-1]:
                trend_confirmation = True
                
            if not trend_confirmation:
                self.log(f"⚠️ Signal {signal} sans confirmation de tendance EMA")
                return None
                
            self.log(f"🎯 Signal détecté: {signal} (Force: {strength:.1f}, ADX: {current_adx:.1f})")
            
            return {
                "action": signal,
                "strength": strength,
                "adx": current_adx,
                "price": current_price,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            self.log(f"💥 Erreur analyse signal: {e}", "ERROR")
            return None
            
    def calculate_position_size(self):
        """Calcul de la taille de position pour M15"""
        return self.config["VOLUME"]
        
    def place_trade(self, signal):
        """Place un trade basé sur le signal"""
        try:
            if not can_open_new_trade(self.magic_number, self.name):
                return False
                
            symbol_info = mt5.symbol_info(SYMBOL)
            if symbol_info is None:
                self.log("❌ Impossible de récupérer les infos du symbole", "ERROR")
                return False
                
            current_price = signal["price"]
            volume = self.calculate_position_size()
            
            # Calcul des niveaux selon le ratio R/R optimisé M15
            if signal["action"] == "BUY":
                order_type = mt5.ORDER_TYPE_BUY
                entry_price = symbol_info.ask
                
                # SL et TP pour M15 (plus larges)
                sl_distance = 0.8  # 80 cents pour M15
                tp_distance = sl_distance * self.config["RR_RATIO"]
                
                sl_price = entry_price - sl_distance
                tp_price = entry_price + tp_distance
                
            else:  # SELL
                order_type = mt5.ORDER_TYPE_SELL
                entry_price = symbol_info.bid
                
                sl_distance = 0.8
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
                "comment": f"M15_Sniper_{signal['action']}_S{signal['strength']:.1f}",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Placement sécurisé
            success, result = place_order_safely(request, self.name)
            
            if success:
                self.log(f"✅ Trade placé: {signal['action']} à {entry_price:.5f} (SL: {sl_price:.5f}, TP: {tp_price:.5f})")
                self.last_signal_time = time.time()
                return True
            else:
                self.log(f"❌ Échec placement trade: {result}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"💥 Erreur placement trade: {e}", "ERROR")
            return False
            
    def run_strategy(self):
        """Boucle principale de la stratégie M15"""
        self.log("🚀 Démarrage de la stratégie M15")
        self.is_running = True
        
        while self.is_running:
            try:
                # Éviter les signaux trop fréquents (minimum 30 minutes entre trades)
                if time.time() - self.last_signal_time < 1800:
                    time.sleep(60)
                    continue
                    
                # Analyse du marché
                signal = self.analyze_signal()
                if signal:
                    self.place_trade(signal)
                    
                # Attente avant la prochaine analyse (5 minutes pour M15)
                time.sleep(300)
                
            except Exception as e:
                self.log(f"💥 Erreur dans la boucle principale: {e}", "ERROR")
                time.sleep(60)
                
    def stop_strategy(self):
        """Arrête la stratégie"""
        self.is_running = False
        self.log("🛑 Stratégie M15 arrêtée")

# === FONCTION D'ENTRÉE POUR LE THREADING ===
def run_m15_strategy():
    """Fonction d'entrée pour le thread M15"""
    strategy = M15Strategy()
    
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
    run_m15_strategy()
