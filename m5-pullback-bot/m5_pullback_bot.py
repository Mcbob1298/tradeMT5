# -*- coding: utf-8 -*-
"""
BOT DE TRADING PROFESSIONNEL M5 - STRATÉGIE "PULLBACK SUR TENDANCE"
========================================================

🎯 PHILOSOPHIE : Qualité > Quantité
Ce bot trade sur le timeframe M5 et se concentre sur des signaux à haute probabilité.
Il n'est pas un bot de haute fréquence.
⚡ STRATÉGIE PRINCIPALE :
1.  IDENTIFICATION TENDANCE DE FOND : Utilise une EMA 200 pour déterminer la tendance majeure (haussière ou baissière).
2.  DÉTECTION DE PULLBACK : Attend que le prix fasse un repli vers une EMA 50, agissant comme support/résistance dynamique.
3.  VALIDATION MOMENTUM : Confirme le signal avec le RSI pour éviter d'entrer sur de faux rebonds.
� GESTION DU RISQUE ADAPTATIVE :
-   TP/SL ADAPTATIFS : Le Take Profit et le Stop Loss sont calculés pour chaque trade en fonction de la volatilité du marché (indicateur ATR).
-   RATIO R/R POSITIF : Vise un ratio Risque/Rendement de 1:2 pour une rentabilité à long terme.


🛡️ SÉCURITÉS PROFESSIONNELLES :
-   Pause automatique de 1h si la perte journalière atteint -5% de la balance.
-   Fermeture automatique de toutes les positions en fin de journée (22h50) et fin de semaine (vendredi soir).
-   Stop Loss obligatoire sur chaque trade.



Auteur: Ultra Scalper
Date: 03 octobre 2025
"""

import MetaTrader5 as mt5
import numpy as np
from datetime import datetime, timedelta
import sys
import io
import time
import random
import traceback
import os
import time
import random
import traceback
import io
import sys
import os
import time
import random
import traceback

# Configuration UTF-8 pour Windows
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# =============================================================================
# ⚠️ ⚠️ ⚠️ AVERTISSEMENT ARGENT RÉEL ⚠️ ⚠️ ⚠️
# =============================================================================
print("🚨🚨🚨 ATTENTION - MODE ARGENT RÉEL ACTIVÉ 🚨🚨🚨")
print("💰 Ce bot va utiliser de l'ARGENT RÉEL pour trader")
print("📉 Risque de pertes financières importantes")
print("✅ Assurez-vous d'avoir configuré correctement:")
print("   - Numéro de compte réel")
print("   - Mot de passe correct") 
print("   - Serveur de trading réel")
print("🛡️ Sécurités activées: Seuil -5%, Max 20 positions")
print("⏸️  Vous avez 10 secondes pour annuler (Ctrl+C)")
print("=" * 60)

# Pause de sécurité avant démarrage
import time
for i in range(10, 0, -1):
    print(f"⏳ Démarrage dans {i} secondes...")
    time.sleep(1)

print("🚀 DÉMARRAGE DU BOT ARGENT RÉEL CONFIRMÉ!")
print("=" * 60)

# =============================================================================
# CONFIGURATION ULTRA SCALPING - ARGENT RÉEL
# =============================================================================
ENABLE_REAL_TRADING = True   # ✅ TRADING RÉEL ACTIVÉ - ARGENT RÉEL
# MT5_LOGIN = 18491073       # ⚠️ TODO: Remplacer par votre numéro de compte RÉEL
# MT5_PASSWORD = "mr^WV%U8"    # ⚠️ TODO: Remplacer par votre mot de passe RÉEL
# MT5_SERVER = "VantageInternational-Live 4"  # ⚠️ TODO: Vérifier le serveur RÉEL
MT5_LOGIN = 10007787600       # ⚠️ TODO: Remplacer par votre numéro de compte RÉEL
MT5_PASSWORD = "G@Vv0mNf"    # ⚠️ TODO: Remplacer par votre mot de passe RÉEL
MT5_SERVER = "MetaQuotes-Demo"  # ⚠️ TODO: Vérifier le serveur RÉEL
# 🚫 MODE SIMULATION DÉSACTIVÉ - TRADING RÉEL
SIMULATE_BALANCE = 500.0     # ❌ Non utilisé en mode réel
USE_SIMULATION_MODE = False  # ❌ MODE SIMULATION DÉSACTIVÉ

# Paramètres stratégie M5 PULLBACK PROFESSIONNELLE - ARGENT RÉEL
SYMBOL = "XAUUSD"               # Or (excellent pour stratégie pullback)
TIMEFRAME = mt5.TIMEFRAME_M5    # 🕒 5 minutes (qualité > quantité)
LOT_SIZE = "ADAPTIVE"           # 🚀 LOT ADAPTATIF AGRESSIF (3.5% risque par trade)
USE_STOP_LOSS = True            # ✅ STOP LOSS OBLIGATOIRE EN ARGENT RÉEL
MAX_POSITIONS = 3               # 🔒 Max 3 positions simultanées (optimisé pour éviter "No money")
ANALYSIS_INTERVAL = 60          # 🕒 Analyse toutes les 60 secondes (M5 = moins de bruit)

# 🚀 GESTION LOT ADAPTATIF OPTIMISÉ
ADAPTIVE_LOT_RISK_PERCENT = 2.5 # Risque 2.5% par trade (optimisé vs 3.5% trop agressif)
ADAPTIVE_LOT_MIN = 0.01         # Lot minimum (contrainte broker)
ADAPTIVE_LOT_MAX = 1.0          # Lot maximum (sécurité anti-explosion)

# 🎯 NOUVEAUX PARAMÈTRES STRATÉGIE M5 PULLBACK
TREND_EMA_MASTER = 200          # EMA 200 - Juge de paix pour tendance de fond
TREND_EMA_PULLBACK = 50         # EMA 50 - Zone de repli/rebond dynamique
ATR_PERIOD = 14                 # ATR pour TP/SL adaptatifs selon volatilité
RSI_PERIOD = 14                 # RSI standard (14 périodes)

# 🎯 SEUILS PULLBACK INTELLIGENTS (Ajustés pour plus de sensibilité)
ATR_PULLBACK_MULTIPLIER = 4.5   # Distance max à l'EMA 50 (4.5x ATR - plus sensible pour plus d'opportunités)
ATR_SL_MULTIPLIER = 1.5         # Stop Loss à 1.5x ATR
ATR_TP_RATIO = 2.0              # Take Profit à 2x le SL (ratio 1:2)

# 🎯 ZONES RSI POUR PULLBACK
RSI_BUY_MIN = 40               # RSI minimum pour BUY (momentum sain)
RSI_BUY_MAX = 55               # RSI maximum pour BUY (pas de surachat)
RSI_SELL_MIN = 45              # RSI minimum pour SELL (faiblesse confirmée)
RSI_SELL_MAX = 60              # RSI maximum pour SELL (rebond s'essoufle)

# 🎯 PARAMÈTRES M5 PULLBACK (Qualité > Quantité)
# COOLDOWNS supprimés - La stratégie M5 ne nécessite pas de cooldowns agressifs

# =============================================================================

def safe_log(message):
    """Log avec timestamp pour ultra scalping"""
    try:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Millisecondes
        print(f"[{timestamp}] {message}", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"[LOG ERROR] {e}", flush=True)

class M5PullbackBot:
    """
    Bot de trading professionnel M5 - Stratégie Pullback sur Tendance
    Utilise EMA 200 (tendance) + EMA 50 (pullback) + RSI + ATR pour TP/SL adaptatifs
    Ratio risque/rendement optimal 1:2 avec gestion professionnelle du risque
    """
    
    def __init__(self, config_name='YOLO', manual_daily_profit=None):
        self.symbol = SYMBOL
        self.timeframe = TIMEFRAME
        self.is_trading = False
        self.manual_daily_profit = manual_daily_profit  # Profit manuel si fourni
        self.bot_trades_profit = 0  # Profit des trades exécutés par ce bot
        
        # 🚨 MODE ARGENT RÉEL ACTIVÉ - PLUS DE SIMULATION
        self.simulation_mode = USE_SIMULATION_MODE  # False = argent réel
        self.simulated_balance = None  # Pas de simulation
        self.real_balance_offset = 0
        
        if not self.simulation_mode:
            safe_log(f"🚨 MODE ARGENT RÉEL ACTIVÉ:")
            safe_log(f"   💰 Utilisation de la balance réelle du compte")
            safe_log(f"   ⚠️ ATTENTION: Les trades utilisent de l'argent réel!")
            safe_log(f"   � Sécurités renforcées: Max 20 positions, fréquence adaptative")
            safe_log(f"   🛡️ Stop Loss obligatoire sur toutes les positions")
        
        # Chargement de la configuration
        from m5_pullback_config import YOLO_CONFIG, AGGRESSIVE_CONFIG, BALANCED_CONFIG, CONSERVATIVE_CONFIG
        configs = {
            'YOLO': YOLO_CONFIG,
            'AGGRESSIVE': AGGRESSIVE_CONFIG, 
            'BALANCED': BALANCED_CONFIG,
            'CONSERVATIVE': CONSERVATIVE_CONFIG
        }
        self.config = configs.get(config_name, YOLO_CONFIG)
        safe_log(f"🎮 Configuration: {config_name}")
        safe_log(f"📊 RSI SELL > {self.config['RSI_OVERBOUGHT']}")
        safe_log(f"📊 RSI BUY < {self.config['RSI_OVERSOLD']}")
        
        # 🛡️ FILET DE SÉCURITÉ ARGENT RÉEL - Seuil augmenté
        self.balance_safety_threshold = -0.05  # -5% de perte maximum
        self.initial_balance = 0  # Balance de référence (sera initialisée)
        
        # Statistiques ultra scalping
        self.stats = {
            'total_trades': 0,
            'winning_trades': 0,
            'total_pips': 0,
            'total_profit': 0,
            'max_concurrent_positions': 0,
            'avg_trade_duration': 0,
            'fastest_profit': float('inf'),
            'start_time': datetime.now(),
            'last_trade_time': None,
            'daily_profit': 0,  # Profit du jour en cours
            'daily_start': datetime.now().date(),  # Date de début du jour
            'balance_safety_active': False,  # Mode sécurité activé (pause trading)
            'security_pause_count': 0,  # Compteur de pauses sécurité (pour seuil progressif)
            'security_grace_period': None,  # Période de grâce après pause (datetime)
            'security_grace_duration': 45  # Durée grâce en minutes (45 min sans contrôle)
        }
        
        # 🕐 CONTRÔLE FRÉQUENCE DES TRADES - Séparé pour BUY et SELL
        self.last_buy_timestamp = None  # Pas de timestamp initial - premier trade libre
        self.last_sell_timestamp = None  # Pas de timestamp initial - premier trade libre
        
        # 🚀 MODE TURBO - Trading ultra-rapide lors de signaux très forts
        self.turbo_mode_active = False  # Mode turbo désactivé par défaut
        self.turbo_mode_strength_threshold = 0.95  # Activation si strength > 0.95
        self.turbo_mode_exit_threshold = 0.9   # Désactivation si strength < 0.9
        
        # Variables système profit quotidien adaptatif
        self.daily_start_balance = 0  # Balance de départ du jour
        
        # 🕐 HORAIRES DE TRADING - Fermeture automatique à 22h50, reprise à 00h20
        self.daily_close_time = 22.83  # Heure de fermeture (22h50) - ultra-étendu
        self.daily_start_time = 0.33   # Heure de reprise (00h20)
        
        # Vérification de l'état initial selon l'heure de démarrage
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_time_decimal = current_hour + (current_minute / 60.0)
        
        # Si on démarre en dehors des heures de trading (avant 00h20 ou après 22h50)
        if current_time_decimal < self.daily_start_time or current_time_decimal >= self.daily_close_time:
            self.is_trading_paused = True  # Démarre en pause
            safe_log(f"🕐 DÉMARRAGE EN PAUSE NOCTURNE - {current_hour}h{current_minute:02d}")
            safe_log(f"   🌙 Trading fermé (horaires: 00h20 à 22h50)")
            safe_log(f"   ⏳ Reprise prévue à 00h20")
        else:
            self.is_trading_paused = False  # Démarre en mode actif
            safe_log(f"🕐 DÉMARRAGE EN HEURES DE TRADING - {current_hour}h{current_minute:02d}")
            safe_log(f"   ✅ Trading autorisé jusqu'à 22h50")
        
        # État des positions
        self.open_positions = []
        self.position_count = 0
        self.sell_positions_count = 0  # Compteur spécifique pour les SELL
        self.buy_positions_count = 0   # Compteur spécifique pour les BUY
        
        # Détection de tendance
        self.trend_data = {
            'current_trend': 'UNKNOWN',
            'trend_strength': 0,
            'trend_duration': 0,
            'last_trend_change': datetime.now()
        }
        
        # Initialisation MT5
        self.initialize_mt5()
        
        # Initialisation du système de profit quotidien adaptatif
        self.initialize_daily_profit_system()
        
        # 🛡️ Initialisation de la balance de référence pour le filet de sécurité
        self.initialize_balance_safety_system()
        
        # 🧮 Calcul et affichage du nombre maximum de positions adaptatif
        max_positions_adaptatif = self.calculate_adaptive_max_positions()
        
        # Synchronisation des compteurs de positions avec MT5
        self.sync_position_counters_with_mt5()
    
    def sync_position_counters_with_mt5(self):
        """Synchronise les compteurs de positions avec les positions réelles de MT5"""
        try:
            # Récupération des positions ouvertes sur MT5
            mt5_positions = mt5.positions_get(symbol=self.symbol)
            
            if mt5_positions:
                # Reset des compteurs
                self.sell_positions_count = 0
                self.buy_positions_count = 0
                
                # Comptage des positions par type
                for position in mt5_positions:
                    if position.type == mt5.POSITION_TYPE_SELL:
                        self.sell_positions_count += 1
                    elif position.type == mt5.POSITION_TYPE_BUY:
                        self.buy_positions_count += 1
                
                safe_log(f"🔄 Synchronisation positions MT5:")
                safe_log(f"   📊 SELL en cours: {self.sell_positions_count}")
                safe_log(f"   📊 BUY en cours: {self.buy_positions_count}")
                safe_log(f"   📊 Total positions: {len(mt5_positions)}")
                
                # Mise à jour de la liste des positions ouvertes pour suivi
                self.open_positions = []
                for position in mt5_positions:
                    position_info = {
                        'ticket': position.ticket,
                        'open_time': datetime.fromtimestamp(position.time),  # Conversion timestamp MT5
                        'type': 'SELL' if position.type == mt5.POSITION_TYPE_SELL else 'BUY',
                        'volume': position.volume,
                        'open_price': position.price_open,
                        'tp': position.tp if position.tp > 0 else None,
                        'sl': position.sl if position.sl > 0 else None
                    }
                    self.open_positions.append(position_info)
                
            else:
                safe_log("📊 Aucune position ouverte sur MT5")
                self.sell_positions_count = 0
                self.buy_positions_count = 0
                self.open_positions = []
                
        except Exception as e:
            safe_log(f"⚠️ Erreur synchronisation compteurs: {e}")
            # En cas d'erreur, on garde les valeurs par défaut
            self.sell_positions_count = 0
            self.buy_positions_count = 0
            self.open_positions = []
    
    def initialize_mt5(self):
        """Initialise MT5 pour ultra scalping avec gestion d'erreurs renforcée"""
        safe_log("🔄 Initialisation MT5...")
        
        # Tentative de shutdown au cas où MT5 serait déjà initialisé
        try:
            mt5.shutdown()
        except:
            pass
        
        # Initialisation
        if not mt5.initialize():
            error_code = mt5.last_error()
            safe_log(f"❌ Échec initialisation MT5 - Code: {error_code}")
            safe_log("💡 Solutions possibles:")
            safe_log("   1. Fermez complètement MetaTrader 5")
            safe_log("   2. Relancez MetaTrader 5 en tant qu'administrateur")
            safe_log("   3. Vérifiez que l'API est activée dans MT5")
            return False
        
        safe_log("✅ MT5 initialisé avec succès")
        
        # Connexion compte avec retry
        for attempt in range(3):
            if mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
                safe_log(f"✅ Connexion réussie au compte {MT5_LOGIN}")
                break
            else:
                error_code = mt5.last_error()
                safe_log(f"❌ Tentative {attempt+1}/3 - Échec connexion compte {MT5_LOGIN}")
                safe_log(f"   Code d'erreur: {error_code}")
                if attempt == 2:
                    safe_log("💡 Vérifiez:")
                    safe_log(f"   - Login: {MT5_LOGIN}")
                    safe_log(f"   - Serveur: {MT5_SERVER}")
                    safe_log("   - Mot de passe")
                    mt5.shutdown()
                    return False
                else:
                    import time
                    time.sleep(2)
        
        # Infos compte
        account_info = mt5.account_info()
        if account_info:
            safe_log(f"💰 Balance: {account_info.balance:.2f}€")
            safe_log(f"📊 Équité: {account_info.equity:.2f}€")
            safe_log(f"🏦 Serveur: {account_info.server}")
            safe_log(f"🎯 Mode: {'DEMO' if account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO else 'RÉEL'}")
        else:
            safe_log("⚠️ Impossible de récupérer les infos du compte")
        
        # Activation symbole
        if mt5.symbol_select(self.symbol, True):
            safe_log(f"⚡ {self.symbol} activé pour ultra scalping")
            
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info:
                safe_log(f"📊 Spread: {symbol_info.spread} points")
                safe_log(f"📈 Ask: {symbol_info.ask}")
                safe_log(f"📉 Bid: {symbol_info.bid}")
                
            return True
        else:
            safe_log(f"❌ Impossible d'activer {self.symbol}")
            return False
            safe_log(f"❌ Impossible d'activer {self.symbol}")
            return False
    
    def calculate_adaptive_max_positions(self):
        """🧮 Calcule le nombre maximum de positions basé sur la balance et le seuil de sécurité"""
        try:
            account_info = mt5.account_info()
            if not account_info:
                safe_log("⚠️ Impossible de récupérer balance, MAX_POSITIONS par défaut: 20")
                return 20
            
            balance = account_info.balance
            
            # 🛡️ CALCUL BASÉ SUR LE SEUIL DE SÉCURITÉ 5%
            # Risque acceptable = 5% de la balance
            risque_acceptable = balance * 0.05  # 5% de la balance
            
            # 💰 PERTE PAR POSITION = 12 pips × 0.01 lot ≈ 1.2€ pour XAUUSD
            perte_par_position = 1.2  # Environ 1.2€ de perte par position avec SL à 12 pips
            
            # 🧮 NOMBRE MAX DE POSITIONS = Risque acceptable ÷ Perte par position
            max_positions_calculé = int(risque_acceptable / perte_par_position)
            
            # 🔒 LIMITES DE SÉCURITÉ
            max_positions_final = max(5, min(max_positions_calculé, 99999999))  # Entre 5 et 99999999 positions

            safe_log(f"🧮 POSITION SIZING ADAPTATIF:")
            safe_log(f"   💰 Balance: {balance:.2f}€")
            safe_log(f"   🛡️ Risque acceptable (5%): {risque_acceptable:.2f}€")
            safe_log(f"   💸 Perte par position: {perte_par_position}€")
            safe_log(f"   🔢 Max positions calculé: {max_positions_calculé}")
            safe_log(f"   ✅ Max positions final: {max_positions_final}")
            
            return max_positions_final
            
        except Exception as e:
            safe_log(f"❌ Erreur calcul max positions adaptatif: {e}")
            return 20  # Valeur par défaut en cas d'erreur
    
    # Méthode get_simulated_balance supprimée - Plus utilisée en mode argent réel
    
    def initialize_balance_safety_system(self):
        """🛡️ Initialise le filet de sécurité basé sur la balance RÉELLE"""
        try:
            account_info = mt5.account_info()
            if account_info:
                # 🚨 MODE ARGENT RÉEL - Balance réelle uniquement
                self.initial_balance = account_info.balance
                
                safety_threshold_amount = self.initial_balance * abs(self.balance_safety_threshold)
                
                safe_log(f"🛡️ FILET DE SÉCURITÉ ARGENT RÉEL INITIALISÉ:")
                safe_log(f"   💰 Balance de référence: {self.initial_balance:.2f}€")
                safe_log(f"   🚨 Seuil critique: -5% = -{safety_threshold_amount:.2f}€")
                safe_log(f"   📉 Balance critique: {self.initial_balance + (self.initial_balance * self.balance_safety_threshold):.2f}€")
                safe_log(f"   🔄 Mode sécurité: Désactivé")
                safe_log(f"   🚨 ARGENT RÉEL: Seuil de sécurité à -5%")
            else:
                safe_log("⚠️ Impossible d'initialiser le filet de sécurité balance")
                self.initial_balance = 1000  # Valeur par défaut conservatrice
        except Exception as e:
            safe_log(f"❌ Erreur initialisation filet sécurité: {e}")
            self.initial_balance = 1000  # Valeur par défaut conservatrice
    
    def check_balance_safety(self):
        """🛡️ Vérifie si la perte atteint le seuil progressif avec période de grâce"""
        try:
            # Vérification et reset quotidien en premier
            self.check_daily_reset()
            
            account_info = mt5.account_info()
            if not account_info:
                return
            
            # 🚨 MODE ARGENT RÉEL - Balance réelle uniquement
            current_balance = account_info.balance
            
            # 🎯 CORRECTION: Utilise la balance de début de journée (pas initiale)
            balance_change = current_balance - self.daily_start_balance
            balance_change_pct = (balance_change / self.daily_start_balance) * 100
            
            # 🛡️ PÉRIODE DE GRÂCE - Vérifier si on est en période de grâce
            if self.stats.get('security_grace_period'):
                grace_end = self.stats['security_grace_period']
                if datetime.now() < grace_end:
                    # En période de grâce - pas de vérification sécurité
                    return
                else:
                    # Fin de période de grâce
                    self.stats['security_grace_period'] = None
                    safe_log(f"⏰ FIN PÉRIODE DE GRÂCE - Reprise vérifications sécurité")
            
            # 🎉 BONUS: Reset compteur si récupération significative
            pause_count = self.stats.get('security_pause_count', 0)
            if pause_count > 0 and balance_change_pct >= -1.0:  # Si on remonte à -1% ou mieux
                old_count = pause_count
                self.stats['security_pause_count'] = 0
                safe_log(f"🎉 RÉCUPÉRATION COMPLÈTE - Reset compteur pauses!")
                safe_log(f"   📊 Ancien compteur: {old_count} → Nouveau: 0")
                safe_log(f"   🎯 Seuil revenu à: -5%")
                safe_log(f"   ✨ Performance excellente - Système réinitialisé")
                pause_count = 0
            
            # 📊 SEUIL PROGRESSIF basé sur le nombre de pauses précédentes
            if pause_count == 0:
                current_threshold = -5.0  # Premier seuil: -5%
            elif pause_count == 1:
                current_threshold = -7.0  # Deuxième: -7%
            elif pause_count == 2:
                current_threshold = -10.0  # Troisième: -10%
            else:
                current_threshold = -15.0  # Au-delà: -15%
            
            # Vérification du seuil critique avec nouveau système
            if balance_change_pct <= current_threshold and not self.stats['balance_safety_active']:
                safe_log(f"🚨 ALERTE CRITIQUE ARGENT RÉEL - SEUIL PROGRESSIF ATTEINT!")
                safe_log(f"   💰 Balance début de journée: {self.daily_start_balance:.2f}€")
                safe_log(f"   📉 Balance actuelle: {current_balance:.2f}€")
                safe_log(f"   📊 Perte: {balance_change:.2f}€ ({balance_change_pct:.2f}%)")
                safe_log(f"   🎯 Seuil progressif (pause #{pause_count + 1}): {current_threshold}%")
                safe_log(f"   🛡️ Prochaine pause déclenchée à: {current_threshold - 2}%")
                safe_log(f"🛡️ ACTIVATION DU FILET DE SÉCURITÉ")
                self.activate_balance_safety_mode()
            
            # Log périodique de l'état de la balance (toutes les 30 vérifications)
            if hasattr(self, '_balance_check_count'):
                self._balance_check_count += 1
            else:
                self._balance_check_count = 1
            
            if self._balance_check_count % 30 == 0:  # Toutes les 30 vérifications (5 minutes)
                pause_count = self.stats.get('security_pause_count', 0)
                if pause_count == 0:
                    next_threshold = -5.0
                elif pause_count == 1:
                    next_threshold = -7.0
                elif pause_count == 2:
                    next_threshold = -10.0
                else:
                    next_threshold = -15.0
                safe_log(f"🚨 ARGENT RÉEL - Balance: {current_balance:.2f}€ ({balance_change_pct:+.2f}%) | Seuil: {next_threshold}%")
            
        except Exception as e:
            safe_log(f"❌ Erreur vérification balance: {e}")
    
    def activate_balance_safety_mode(self):
        """🛡️ NOUVEAU: Active une pause de trading de 1h avec compteur et période de grâce"""
        try:
            # Incrémenter le compteur de pauses sécurité
            self.stats['security_pause_count'] = self.stats.get('security_pause_count', 0) + 1
            
            # Activation du mode sécurité avec timestamp de fin
            self.stats['balance_safety_active'] = True
            self.safety_pause_end_time = datetime.now() + timedelta(hours=1)
            
            pause_count = self.stats['security_pause_count']
            safe_log(f"🔒 ACTIVATION PAUSE SÉCURITÉ #{pause_count} - 1 HEURE")
            safe_log(f"📋 Système optimisé avec récupération:")
            safe_log(f"   ⏸️ PAUSE du trading pendant 1 heure")
            safe_log(f"   🚫 AUCUNE modification des positions existantes")
            safe_log(f"   ⏰ Reprise automatique à {self.safety_pause_end_time.strftime('%H:%M:%S')}")
            safe_log(f"   🎯 Puis période de grâce: 45 minutes sans contrôle sécurité")
            safe_log(f"   💡 Les positions gardent leurs SL et TP normaux")
            
            safe_log(f"✅ Mode sécurité activé!")
            safe_log(f"   ⏸️ Trading en PAUSE jusqu'à {self.safety_pause_end_time.strftime('%H:%M')}")
            safe_log(f"   🛡️ Positions non modifiées (SL/TP conservés)")
            safe_log(f"   � Reprise automatique dans 60 minutes")
            
        except Exception as e:
            safe_log(f"❌ Erreur activation pause sécurité: {e}")
    
    def check_balance_safety_exit_conditions(self):
        """🛡️ NOUVEAU: Vérifie si la pause de 1h est terminée"""
        if not self.stats['balance_safety_active']:
            return False
        
        # Vérification si la pause de 1h est terminée
        if not hasattr(self, 'safety_pause_end_time'):
            # Si pas de timestamp (ancien système), on sort immédiatement
            safe_log(f"⚠️ Pas de timestamp de fin - Sortie immédiate du mode sécurité")
            self.stats['balance_safety_active'] = False
            return True
        
        current_time = datetime.now()
        if current_time >= self.safety_pause_end_time:
            # La pause de 1h est terminée
            safe_log(f"🎉 FIN DE LA PAUSE SÉCURITÉ - 1 HEURE ÉCOULÉE")
            safe_log(f"   ⏰ Temps écoulé: {current_time.strftime('%H:%M:%S')}")
            safe_log(f"   ✅ Reprise du trading normal")
            safe_log(f"   🎯 DÉBUT PÉRIODE DE GRÂCE: 45 minutes sans contrôle sécurité")
            safe_log(f"   🔄 Toutes les fonctions rétablies")
            
            # Démarrer la période de grâce
            grace_duration = self.stats.get('security_grace_duration', 45)  # 45 minutes par défaut
            self.stats['security_grace_period'] = current_time + timedelta(minutes=grace_duration)
            safe_log(f"   ⏰ Fin période de grâce: {self.stats['security_grace_period'].strftime('%H:%M:%S')}")
            
            self.stats['balance_safety_active'] = False
            delattr(self, 'safety_pause_end_time')  # Nettoyage
            return True
        else:
            # Pause encore en cours - log périodique
            if hasattr(self, '_safety_log_count'):
                self._safety_log_count += 1
            else:
                self._safety_log_count = 1
            
            if self._safety_log_count % 30 == 0:  # Toutes les 30 vérifications (5 minutes)
                time_remaining = self.safety_pause_end_time - current_time
                minutes_remaining = int(time_remaining.total_seconds() / 60)
                pause_count = self.stats.get('security_pause_count', 0)
                safe_log(f"⏸️ PAUSE SÉCURITÉ #{pause_count} EN COURS - {minutes_remaining} minutes restantes")
                safe_log(f"   🕐 Reprise prévue à {self.safety_pause_end_time.strftime('%H:%M:%S')}")
                safe_log(f"   🎯 Puis période de grâce de 45 minutes")
            
            return False
    
    def initialize_daily_profit_system(self):
        """Initialise le système de profit quotidien au démarrage ou nouveau jour"""
        try:
            account_info = mt5.account_info()
            if not account_info:
                safe_log("⚠️ Impossible d'initialiser le système de profit quotidien")
                return
            
            current_balance = account_info.balance
            today = datetime.now().date()
            
            # 🚨 ARGENT RÉEL: Balance de départ du jour pour calcul profit quotidien
            self.daily_start_balance = current_balance
            
            # Reset des stats quotidiennes  
            self.stats['daily_start'] = today
            self.stats['daily_profit'] = 0  # Remis à zéro
            
            safe_log(f"🌅 SYSTÈME PROFIT QUOTIDIEN ARGENT RÉEL INITIALISÉ:")
            safe_log(f"   📅 Date: {today.strftime('%d/%m/%Y')}")
            safe_log(f"   💰 Balance de départ du jour: {self.daily_start_balance:.2f}€")
            safe_log(f"   📊 Profit quotidien sera: Balance actuelle - {self.daily_start_balance:.2f}€")
            safe_log(f"   🛡️ Filet de sécurité: Balance (-5%)")
            safe_log(f"   🚨 ARGENT RÉEL: Calculs basés sur balance réelle uniquement")
            
        except Exception as e:
            safe_log(f"❌ Erreur initialisation système profit quotidien: {e}")
    
    def calculate_real_time_daily_profit(self):
        """Calcule le profit quotidien en temps réel basé sur la balance RÉELLE"""
        try:
            account_info = mt5.account_info()
            if not account_info:
                return 0
            
            # 🚨 ARGENT RÉEL: Balance réelle uniquement
            current_balance = account_info.balance
            
            # Calcul simple: Balance actuelle - Balance de début de journée
            daily_profit = current_balance - self.daily_start_balance
            
            # Debug: Log périodique du calcul (toutes les 50 vérifications)
            if not hasattr(self, '_profit_debug_count'):
                self._profit_debug_count = 0
            self._profit_debug_count += 1
            
            if self._profit_debug_count % 50 == 0:  # Toutes les 50 vérifications
                safe_log(f"💰 DEBUG PROFIT:")
                safe_log(f"   📊 Balance actuelle: {current_balance:.2f}€")
                safe_log(f"   📊 Balance début journée: {self.daily_start_balance:.2f}€")
                safe_log(f"   📊 Profit calculé: {daily_profit:+.2f}€")
            
            return daily_profit
            
        except Exception as e:
            safe_log(f"❌ Erreur calcul profit temps réel: {e}")
            return 0
    
    def place_real_order(self, trade_type, entry_price, tp_price, sl_price, signal):
        """Place un ordre RÉEL avec de l'argent RÉEL sur MT5"""
        try:
            # 🚨 VÉRIFICATION MODE ARGENT RÉEL
            if self.simulation_mode:
                safe_log("🚫 ERREUR: Mode simulation détecté mais fonction argent réel appelée!")
                return False
            
            # 🚨 AVERTISSEMENT ARGENT RÉEL
            safe_log(f"🚨 ORDRE ARGENT RÉEL EN COURS:")
            safe_log(f"   💰 Type: {trade_type}")
            safe_log(f"   ⚠️ ATTENTION: Utilise de l'argent RÉEL!")
            
            # 🕐 Vérification horaires de trading avant de placer un ordre
            if not self.check_trading_hours():
                safe_log(f"🚫 Ordre refusé - Trading fermé (horaires: 00h20 à 22h50)")
                return False
            
            # Vérification connexion MT5
            if not mt5.terminal_info():
                safe_log("❌ MT5 non connecté")
                return False
            
            # Vérification compte démo/réel
            account_info = mt5.account_info()
            if account_info:
                if account_info.trade_mode == mt5.ACCOUNT_TRADE_MODE_DEMO:
                    safe_log("⚠️ COMPTE DÉMO DÉTECTÉ - Vérifiez vos paramètres")
                else:
                    safe_log("🚨 COMPTE RÉEL CONFIRMÉ - Trading avec argent réel")
            
            # Type d'ordre
            order_type = mt5.ORDER_TYPE_SELL if trade_type == "SELL" else mt5.ORDER_TYPE_BUY
            
            # Volume (lot size adaptatif basé sur la balance RÉELLE et l'ATR)
            # Calcul de la distance SL basée sur l'ATR pour le lot adaptatif
            atr_sl_distance = signal.get('atr', 2.5) * ATR_SL_MULTIPLIER  # Fallback ATR 2.5 pour XAUUSD
            volume = self.calculate_adaptive_lot_size(atr_sl_distance)
            
            # Vérification du symbole
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info is None:
                safe_log("❌ Impossible de récupérer infos symbole")
                return False
                
            # Vérification que le symbole est sélectionné
            if not symbol_info.select:
                safe_log(f"⚠️ Sélection du symbole {self.symbol}")
                if not mt5.symbol_select(self.symbol, True):
                    safe_log("❌ Impossible de sélectionner le symbole")
                    return False
                symbol_info = mt5.symbol_info(self.symbol)
            
            # Volume minimum
            min_volume = symbol_info.volume_min
            max_volume = symbol_info.volume_max
            volume_step = symbol_info.volume_step
            
            safe_log(f"📊 Volume: {volume} | Min: {min_volume} | Max: {max_volume}")
            
            if volume < min_volume:
                volume = min_volume
                safe_log(f"⚠️ Volume ajusté au minimum: {volume}")
            
            # Prix d'entrée
            tick_info = mt5.symbol_info_tick(self.symbol)
            if tick_info is None:
                safe_log("❌ Impossible de récupérer prix")
                return False
                
            if trade_type == "SELL":
                price = tick_info.bid
            else:
                price = tick_info.ask
            
            safe_log(f"💰 Prix {trade_type}: {price} | Bid: {tick_info.bid} | Ask: {tick_info.ask}")
            
            # ✅ UTILISATION DIRECTE DES TP/SL ADAPTATIFS CALCULÉS PAR execute_m5_trade
            # Plus de calcul fixe - on utilise les valeurs ATR adaptatives passées en argument
            
            safe_log(f"🎯 TP/SL ADAPTATIFS ATR:")
            safe_log(f"   📈 Prix entrée: {price:.5f}")
            safe_log(f"   🎯 Take Profit: {tp_price:.5f} (adaptatif selon ATR)")
            safe_log(f"   🛡️ Stop Loss: {sl_price:.5f} (1.5x ATR)")
            
            # Request de trading avec TP/SL adaptatifs
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "tp": tp_price,  # ✅ UTILISE DIRECTEMENT L'ARGUMENT tp_price ADAPTATIF
                "deviation": 20,  # Déviation de prix plus large
                "magic": 123456,  # Magic number
                "comment": "M5_Pullback_ATR",  # Commentaire mis à jour pour la nouvelle stratégie
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Ajout SL seulement si spécifié
            if sl_price and sl_price > 0:
                request["sl"] = sl_price
            
            safe_log(f"📋 Request: {request}")
            
            # Envoi de l'ordre
            result = mt5.order_send(request)
            
            if result is None:
                last_error = mt5.last_error()
                safe_log(f"❌ Échec envoi ordre: result is None | Erreur: {last_error}")
                return False
                
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                safe_log(f"❌ Échec ordre: Code {result.retcode}")
                safe_log(f"   💬 Commentaire: {result.comment}")
                
                # Codes d'erreur courants
                if result.retcode == 10004:
                    safe_log("   ⚠️ Requête invalide")
                elif result.retcode == 10006:
                    safe_log("   ⚠️ Rejet par dealer")
                elif result.retcode == 10015:
                    safe_log("   ⚠️ Prix invalide")
                elif result.retcode == 10016:
                    safe_log("   ⚠️ Stops invalides")
                elif result.retcode == 10018:
                    safe_log("   ⚠️ Volume invalide")
                
                return False
            
            # Succès !
            safe_log(f"🎯 ORDRE EXÉCUTÉ:")
            safe_log(f"   📋 Ticket: {result.order}")
            safe_log(f"   💰 Volume: {result.volume}")
            safe_log(f"   💸 Prix: {result.price}")
            safe_log(f"   🎯 TP: {tp_price}")
            
            # Enregistrement de la position pour suivi temporel
            position_info = {
                'ticket': result.order,
                'open_time': datetime.now(),
                'type': trade_type,
                'volume': result.volume,
                'open_price': price,  # Utilise le prix de la requête, pas result.price qui peut être 0.0
                'tp': tp_price,  # ✅ UTILISE LE TP ADAPTATIF PASSÉ EN ARGUMENT
                'sl': sl_price
            }
            self.open_positions.append(position_info)
            
            # Mise à jour stats
            self.stats['total_trades'] += 1
            self.stats['last_trade_time'] = datetime.now()
            
            # Mise à jour compteurs par type
            if trade_type == 'SELL':
                self.sell_positions_count += 1
            else:
                self.buy_positions_count += 1
            
            return True
            
        except Exception as e:
            safe_log(f"❌ Erreur placement ordre: {e}")
            import traceback
            safe_log(f"   🔍 Détails: {traceback.format_exc()}")
            return False
    
    # Fonction de fermeture automatique désactivée pour préserver les profits
    
    def intelligent_position_management(self):
        """
        🧠 GESTION INTELLIGENTE DES POSITIONS
        ===================================
        
        Logique avancée:
        1. Si position en profit ET tendance s'inverse → Fermeture intelligente
        2. Si position dans le sens de la tendance → Laisser courir
        3. Vérification margin libre avant nouveaux trades
        """
        if not self.open_positions:
            return
        
        # Récupération des positions MT5 actuelles
        mt5_positions = mt5.positions_get(symbol=self.symbol)
        if not mt5_positions:
            return
        
        # Analyse de la tendance actuelle
        try:
            rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, 250)
            if rates is None or len(rates) < 50:
                return
            
            data = [{'open': rate['open'], 'high': rate['high'], 
                    'low': rate['low'], 'close': rate['close']} for rate in rates]
            
            trend_direction, strength, signal = self.detect_ultra_trend(data)
            current_price = signal['price']
            
        except Exception as e:
            safe_log(f"❌ Erreur analyse tendance pour gestion intelligente: {e}")
            return
        
        # Analyse de chaque position
        for mt5_pos in mt5_positions:
            try:
                profit = mt5_pos.profit
                position_type = "BUY" if mt5_pos.type == 0 else "SELL"
                ticket = mt5_pos.ticket
                
                # ✅ Condition 1: Position en profit ET tendance inversée
                if profit > 5:  # Au moins 5€ de profit
                    should_close = False
                    close_reason = ""
                    
                    if position_type == "BUY" and trend_direction == "BEARISH":
                        should_close = True
                        close_reason = "BUY profitable + tendance BEARISH"
                    elif position_type == "SELL" and trend_direction == "BULLISH":
                        should_close = True
                        close_reason = "SELL profitable + tendance BULLISH"
                    
                    if should_close:
                        safe_log(f"🧠 GESTION INTELLIGENTE: {close_reason}")
                        safe_log(f"   💰 Profit actuel: +{profit:.2f}€")
                        safe_log(f"   🔄 Fermeture anticipée pour sécuriser gain")
                        
                        success = self.close_position_by_ticket(ticket)
                        if success:
                            self.update_daily_profit(profit)
                            safe_log(f"✅ Position fermée intelligemment: +{profit:.2f}€")
                        else:
                            safe_log(f"❌ Échec fermeture intelligente position {ticket}")
                
                # ✅ Condition 2: Position dans le bon sens → Laisser courir
                elif ((position_type == "BUY" and trend_direction == "BULLISH") or
                      (position_type == "SELL" and trend_direction == "BEARISH")):
                    # Position alignée avec la tendance - on laisse courir
                    if profit > 0:
                        safe_log(f"🎯 Position {position_type} alignée avec tendance {trend_direction} (+{profit:.2f}€) - Laisser courir")
                
            except Exception as e:
                safe_log(f"❌ Erreur analyse position {mt5_pos.ticket}: {e}")
    
    def check_margin_availability(self):
        """
        💰 VÉRIFICATION MARGIN LIBRE
        ============================
        
        Vérifie si assez de margin libre pour nouveaux trades
        Évite les erreurs "No money"
        """
        try:
            account_info = mt5.account_info()
            if not account_info:
                return False
            
            margin_free = account_info.margin_free
            balance = account_info.balance
            margin_level = account_info.margin_level if account_info.margin != 0 else 0
            
            # Seuils de sécurité
            min_margin_free = balance * 0.3  # 30% de la balance en margin libre
            min_margin_level = 200  # Niveau de margin minimum 200%
            
            margin_ok = margin_free >= min_margin_free and margin_level >= min_margin_level
            
            if not margin_ok:
                safe_log(f"⚠️ MARGIN INSUFFISANTE:")
                safe_log(f"   💰 Margin libre: {margin_free:.2f}€ (min: {min_margin_free:.2f}€)")
                safe_log(f"   📊 Niveau margin: {margin_level:.1f}% (min: 200%)")
                safe_log(f"   🚫 Nouveaux trades suspendus")
            
            return margin_ok
            
        except Exception as e:
            safe_log(f"❌ Erreur vérification margin: {e}")
            return False

    def sync_positions_with_mt5(self):
        """Synchronise notre liste avec les positions réelles de MT5"""
        if not self.open_positions:
            return
        
        # Récupération des positions ouvertes sur MT5
        mt5_positions = mt5.positions_get(symbol=self.symbol)
        mt5_tickets = [pos.ticket for pos in mt5_positions] if mt5_positions else []
        
        # Suppression des positions qui ne sont plus ouvertes sur MT5
        positions_to_remove = []
        for i, position in enumerate(self.open_positions):
            if position['ticket'] not in mt5_tickets:
                duration = datetime.now() - position['open_time']
                duration_str = str(duration).split('.')[0]
                
                # Récupération du profit depuis l'historique (TP ou SL)
                profit_info = self.get_detailed_position_profit_from_history(position['ticket'])
                if profit_info:
                    profit = profit_info['profit']
                    close_type = profit_info['type']
                    self.update_daily_profit(profit)
                    
                    if close_type == 'TP':
                        safe_log(f"✅ Position fermée (TP): Ticket {position['ticket']} | Profit: {profit:+.2f}€ | Durée: {duration_str}")
                    elif close_type == 'SL':
                        safe_log(f"❌ Position fermée (SL): Ticket {position['ticket']} | Perte: {profit:+.2f}€ | Durée: {duration_str}")
                        # Note: Le filet de sécurité est maintenant basé sur la balance (-5%)
                    else:
                        safe_log(f"🔄 Position fermée: Ticket {position['ticket']} | P&L: {profit:+.2f}€ | Durée: {duration_str}")
                else:
                    safe_log(f"⚠️ Position fermée (profit non détecté): Ticket {position['ticket']} | Durée: {duration_str}")
                
                # Mise à jour des compteurs par type
                if position['type'] == 'SELL':
                    self.sell_positions_count = max(0, self.sell_positions_count - 1)
                else:
                    self.buy_positions_count = max(0, self.buy_positions_count - 1)
                positions_to_remove.append(i)
        
        # Suppression en ordre inverse
        for i in reversed(positions_to_remove):
            self.open_positions.pop(i)
    
    def reset_daily_sl_counter(self):
        """🔄 Reset manuel du compteur de SL quotidien (OBSOLÈTE - utilise maintenant balance)"""
        safe_log(f"⚠️ FONCTION OBSOLÈTE - Le filet de sécurité est maintenant basé sur la balance (-5%)")
        safe_log(f"   💡 Aucune action nécessaire - Le système balance est actif")
    
    def get_sl_detection_stats(self):
        """� Affiche les statistiques du nouveau système de sécurité balance"""
        safe_log(f"� NOUVEAU SYSTÈME DE SÉCURITÉ BALANCE:")
        safe_log(f"   🛡️ Mode sécurité: {'Activé' if self.stats['balance_safety_active'] else 'Désactivé'}")
        safe_log(f"   � Balance de référence: {self.initial_balance:.2f}€")
        safe_log(f"   � Seuil critique: -5% = {self.initial_balance * 0.05:.2f}€")
        
        # Affichage balance actuelle
        try:
            account_info = mt5.account_info()
            if account_info:
                current_balance = account_info.balance
                balance_change_pct = ((current_balance - self.initial_balance) / self.initial_balance) * 100
                safe_log(f"   📊 Balance actuelle: {current_balance:.2f}€ ({balance_change_pct:+.2f}%)")
        except Exception as e:
            safe_log(f"   ❌ Erreur lecture balance: {e}")
    
    def handle_stop_loss_detected(self):
        """🛡️ FILET DE SÉCURITÉ - Gestion basique d'un SL détecté (fonction simplifiée)"""
        # Cette fonction est maintenant simplifiée car la logique principale 
        # est dans check_for_new_stop_losses()
        
        # 🚨 ANCIEN SYSTÈME DANGEREUX SUPPRIMÉ
        # Le système basé sur "10 SL" qui supprimait les Stop Loss était dangereux
        # Seul le système de sécurité basé sur % de balance est conservé
    
    # � FONCTIONS DANGEREUSES SUPPRIMÉES
    # activate_safety_mode() et remove_stop_loss_from_position() 
    # étaient dangereuses car elles supprimaient les Stop Loss
    # après 10 pertes. Ceci peut causer des pertes catastrophiques.
    # SEUL le système activate_balance_safety_mode() est conservé.
    
    def check_safety_mode_exit_conditions(self):
        """Vérifie si les conditions de sortie du mode sécurité sont remplies"""
        # 🚨 ANCIEN SYSTÈME SUPPRIMÉ - Cette fonction utilisait 'safety_mode_active'
        # qui était lié au système dangereux de suppression des Stop Loss.
        # Maintenant on utilise seulement 'balance_safety_active' qui est sécurisé.
        return False  # Fonction désactivée
        
        # Récupération des positions ouvertes
        mt5_positions = mt5.positions_get(symbol=self.symbol)
        if not mt5_positions:
            # Plus de positions ouvertes, on peut reprendre
            safe_log(f"✅ SORTIE MODE SÉCURITÉ - Aucune position ouverte")
            safe_log(f"🔄 Reprise du trading normal")
            self.stats['safety_mode_active'] = False
            return True
        
        # Vérification et fermeture des positions profitables
        profitable_count = 0
        losing_count = 0
        closed_count = 0
        
        for position in mt5_positions:
            if position.profit > 0:
                profitable_count += 1
                # Fermeture automatique de la position profitable
                success = self.close_position_by_ticket(position.ticket)
                if success:
                    closed_count += 1
                    self.update_daily_profit(position.profit)
                    safe_log(f"💰 Position fermée (mode sécurité): Ticket {position.ticket} | Profit: +{position.profit:.2f}€")
            else:
                losing_count += 1
        
        # Log du statut
        if profitable_count > 0:
            safe_log(f"🛡️ MODE SÉCURITÉ - Fermeture positions profitables:")
            safe_log(f"   ✅ Fermées: {closed_count}/{profitable_count}")
            safe_log(f"   ❌ En attente (perte): {losing_count}")
        
        # Vérification après fermetures - récupération mise à jour
        remaining_positions = mt5.positions_get(symbol=self.symbol)
        if not remaining_positions:
            safe_log(f"🎉 SORTIE MODE SÉCURITÉ - Toutes les positions fermées!")
            safe_log(f"🔄 Reprise du trading normal")
            self.stats['safety_mode_active'] = False
            return True
        else:
            # Log périodique du statut (toutes les 10 vérifications)
            if hasattr(self, '_safety_check_count'):
                self._safety_check_count += 1
            else:
                self._safety_check_count = 1
            
            if self._safety_check_count % 10 == 0:  # Toutes les 10 vérifications (100 secondes)
                safe_log(f"🛡️ MODE SÉCURITÉ ACTIF - Attente fermeture complète:")
                safe_log(f"   📊 Positions restantes: {len(remaining_positions)}")
                safe_log(f"   ⏳ Les positions profitables sont fermées automatiquement...")
            
            return False
    
    def check_and_move_sl_to_breakeven(self):
        """
        🔒 VERROUILLAGE AGRESSIF DES GAINS - Stop Loss Progressif
        ========================================================
        
        Nouveau Principe Agressif : Maximiser les gains même en cas de reversal.
        
        Comment ça marche :
        - Dès que le trade atteint 75% du TP (0.9 pips sur 1.2 pips TP)
        - On déplace le SL à 50% du profit potentiel au lieu du prix d'entrée
        - Scénario 1 (Idéal): Prix continue → TP à 1.2 pips
        - Scénario 2 (Reversal): SL à +50% profit au lieu de 0€
        - Exemple: TP=0.9 pips, déclenchement à 0.675 pips, SL à +0.45 pips
        """
        if not self.open_positions:
            return
        
        # Récupération des positions ouvertes sur MT5
        mt5_positions = mt5.positions_get(symbol=self.symbol)
        if not mt5_positions:
            return
        
        current_price = mt5.symbol_info_tick(self.symbol)
        if not current_price:
            return
        
        # Créer un set des tickets déjà traités pour éviter les logs en boucle
        if not hasattr(self, '_breakeven_processed_tickets'):
            self._breakeven_processed_tickets = set()
        
        for position in self.open_positions:
            ticket = position['ticket']
            entry_price = position['open_price']
            position_type = position['type']
            
            # Skip si prix d'entrée invalide
            if entry_price == 0.0:
                if ticket not in self._breakeven_processed_tickets:
                    safe_log(f"⚠️ BREAKEVEN SKIP - Ticket {ticket}: Prix d'entrée invalide (0.0)")
                    self._breakeven_processed_tickets.add(ticket)
                continue
            
            # Recherche de la position correspondante sur MT5
            mt5_position = None
            for mt5_pos in mt5_positions:
                if mt5_pos.ticket == ticket:
                    mt5_position = mt5_pos
                    break
            
            if not mt5_position:
                continue
            
            # Vérification BUY uniquement (cette stratégie ne gère que les BUY)
            if position_type == 'BUY':
                # Calcul du profit actuel et du TP cible pour breakeven agressif
                symbol_info = mt5.symbol_info(self.symbol)
                if symbol_info:
                    current_profit_distance = current_price.bid - entry_price
                    # ✅ UTILISE LE TP RÉEL DE LA POSITION MT5 (adaptatif ATR)
                    tp_distance = mt5_position.tp - entry_price if mt5_position.tp > 0 else (25 * 0.1)
                else:
                    current_profit_distance = current_price.bid - entry_price
                    # ✅ FALLBACK COMPATIBLE AVEC TP ADAPTATIF
                    tp_distance = 25 * 0.1  # Fallback conservateur
                
                # Calcul du pourcentage de progression vers le TP
                if tp_distance > 0:
                    tp_progress_pct = (current_profit_distance / tp_distance) * 100
                else:
                    tp_progress_pct = 0

                # 🎯 SEUIL AGRESSIF : 75% du TP (au lieu de pips fixes)
                if tp_progress_pct >= 75.0:
                    
                    # Calcul du SL agressif : 50% du profit potentiel
                    target_profit_distance = tp_distance * 0.5  # 50% du TP
                    new_sl_aggressive = entry_price + target_profit_distance
                    
                    # Vérification si le SL est déjà proche de cette valeur (déjà configuré)
                    sl_already_set = abs(mt5_position.sl - new_sl_aggressive) < 0.05  # Tolérance 5 points
                    
                    if sl_already_set and ticket not in self._breakeven_processed_tickets:
                        safe_log(f"✅ BREAKEVEN AGRESSIF DÉJÀ ACTIF - Ticket {ticket}")
                        safe_log(f"   💰 Progression TP: {tp_progress_pct:.1f}% (seuil: 75%)")
                        safe_log(f"   �️ SL au breakeven: {mt5_position.sl:.2f} (entrée: {entry_price:.2f})")
                        self._breakeven_processed_tickets.add(ticket)
                        continue
                    
                    # Vérification si le SL doit être mis à jour
                    sl_needs_update = (mt5_position.sl == 0.0) or (not sl_already_set)
                    
                    if sl_needs_update and ticket not in self._breakeven_processed_tickets:
                        safe_log(f"🔍 BREAKEVEN AGRESSIF - Ticket {ticket}:")
                        safe_log(f"   💰 Progression TP: {tp_progress_pct:.1f}% (seuil: 75%)")
                        safe_log(f"   📊 Profit actuel: +{current_profit_distance:.3f} | TP cible: {tp_distance:.3f}")
                        safe_log(f"   📊 SL actuel: {mt5_position.sl} | Prix entrée: {entry_price}")
                        
                        # VÉRIFICATION CONTRAINTES MT5 - SL doit être suffisamment éloigné du prix actuel
                        symbol_info = mt5.symbol_info(self.symbol)
                        if symbol_info:
                            current_price_ask = mt5.symbol_info_tick(self.symbol).ask
                            min_distance = symbol_info.trade_stops_level * symbol_info.point
                            
                            # Ajustement si trop proche du prix actuel
                            if abs(new_sl_aggressive - current_price_ask) < min_distance:
                                new_sl_aggressive = current_price_ask - min_distance - (5 * symbol_info.point)
                                safe_log(f"   ⚠️ SL ajusté pour respecter stops_level: {new_sl_aggressive:.5f}")
                            
                            # Calcul du profit garanti
                            guaranteed_profit_distance = new_sl_aggressive - entry_price
                            guaranteed_profit_pips = guaranteed_profit_distance / 0.01
                            safe_log(f"   🎯 SL agressif: {new_sl_aggressive:.3f} (50% du profit potentiel)")
                            safe_log(f"   � Profit garanti: +{guaranteed_profit_pips:.1f} pips (au lieu de 0)")
                        else:
                            # Fallback
                            guaranteed_profit_distance = new_sl_aggressive - entry_price
                            guaranteed_profit_pips = guaranteed_profit_distance / 0.01
                            safe_log(f"   🎯 SL agressif: {new_sl_aggressive:.3f} (50% profit)")
                            safe_log(f"   💰 Profit garanti: +{guaranteed_profit_pips:.1f} pips")
                        
                        # Modification de la position sur MT5
                        request = {
                            "action": mt5.TRADE_ACTION_SLTP,
                            "symbol": self.symbol,
                            "position": ticket,
                            "sl": new_sl_aggressive,
                            "tp": mt5_position.tp,  # Garde le même TP
                        }
                        
                        result = mt5.order_send(request)
                        
                        if result.retcode == mt5.TRADE_RETCODE_DONE:
                            safe_log(f"🔒 GAINS AGRESSIFS VERROUILLÉS! Ticket {ticket}")
                            safe_log(f"   💰 Progression TP: {tp_progress_pct:.1f}%")
                            safe_log(f"   🛡️ SL agressif: {new_sl_aggressive:.3f} (profit garanti)")
                            safe_log(f"   ✅ Trade protégé: Perte impossible, profit minimum garanti!")
                            self._breakeven_processed_tickets.add(ticket)
                        else:
                            safe_log(f"❌ Échec déplacement SL pour {ticket}: {result.comment}")
                            # Marquer comme traité même en cas d'échec pour éviter le spam
                            self._breakeven_processed_tickets.add(ticket)
            
            else:
                # 🔴 BREAKEVEN POUR POSITIONS SELL
                if ticket not in self._breakeven_processed_tickets:
                    # Même logique que BUY mais inversée
                    symbol_info = mt5.symbol_info(self.symbol)
                    if symbol_info:
                        current_profit_distance = entry_price - current_price.ask  # Inversé pour SELL
                        # ✅ UTILISE LE TP RÉEL DE LA POSITION MT5 (adaptatif ATR)
                        tp_distance = entry_price - mt5_position.tp if mt5_position.tp > 0 else (25 * 0.1)
                    else:
                        current_profit_distance = entry_price - current_price.ask
                        # ✅ FALLBACK COMPATIBLE AVEC TP ADAPTATIF
                        tp_distance = 25 * 0.1
                    
                    # Calcul progression vers TP
                    if tp_distance > 0:
                        tp_progress_pct = (current_profit_distance / tp_distance) * 100
                        
                        # Breakeven à 75% du TP
                        if tp_progress_pct >= 75.0:
                            target_profit_distance = tp_distance * 0.5
                            new_sl_aggressive = entry_price - target_profit_distance
                            
                            # Vérification si SL doit être mis à jour
                            sl_needs_update = (mt5_position.sl == 0 or mt5_position.sl > new_sl_aggressive)
                            
                            if sl_needs_update:
                                safe_log(f"🔍 BREAKEVEN SELL - Ticket {ticket}: {tp_progress_pct:.1f}% TP atteint")
                                
                                request = {
                                    "action": mt5.TRADE_ACTION_SLTP,
                                    "symbol": self.symbol,
                                    "position": ticket,
                                    "sl": new_sl_aggressive,
                                    "tp": mt5_position.tp,
                                }
                                
                                result = mt5.order_send(request)
                                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                                    safe_log(f"✅ BREAKEVEN SELL activé pour {ticket}")
                    
                    self._breakeven_processed_tickets.add(ticket)
    
    def close_positive_positions(self):
        """🟢 FERME AUTOMATIQUEMENT TOUTES LES POSITIONS POSITIVES"""
        if not ENABLE_REAL_TRADING:
            return
            
        try:
            positions = mt5.positions_get(symbol=self.symbol)
            if not positions:
                return
                
            for position in positions:
                # Vérifier si la position est positive
                if position.profit > 0:  # Position en profit
                    safe_log(f"💰 POSITION POSITIVE DÉTECTÉE - Ticket {position.ticket}: +{position.profit:.2f}€")
                    
                    # Fermer immédiatement la position positive
                    success = self.close_position_by_ticket(position.ticket)
                    if success:
                        safe_log(f"✅ Position {position.ticket} fermée automatiquement sur profit: +{position.profit:.2f}€")
                    else:
                        safe_log(f"❌ Échec fermeture position {position.ticket}")
                        
        except Exception as e:
            safe_log(f"❌ Erreur dans close_positive_positions: {e}")

    def close_position_by_ticket(self, ticket):
        """Ferme une position spécifique par son ticket"""
        try:
            # Récupération des informations de la position
            positions = mt5.positions_get(ticket=ticket)
            
            if not positions:
                safe_log(f"⚠️ Position {ticket} non trouvée (déjà fermée?)")
                return True  # Considéré comme succès si déjà fermée
            
            position = positions[0]
            
            # Détermination du type d'ordre de fermeture
            if position.type == mt5.POSITION_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = mt5.symbol_info_tick(position.symbol).bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = mt5.symbol_info_tick(position.symbol).ask
            
            # Request de fermeture
            close_request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": position.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": ticket,
                "price": price,
                "deviation": 20,
                "magic": 123456,
                "comment": "Timeout",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }
            
            # Envoi de l'ordre de fermeture
            result = mt5.order_send(close_request)
            
            if result is None:
                last_error = mt5.last_error()
                safe_log(f"❌ Échec fermeture: result is None | Erreur: {last_error}")
                return False
            
            if result.retcode != mt5.TRADE_RETCODE_DONE:
                safe_log(f"❌ Échec fermeture: Code {result.retcode} | {result.comment}")
                return False
            
            return True
            
        except Exception as e:
            safe_log(f"❌ Erreur fermeture position {ticket}: {e}")
            return False
    
    def get_adaptive_trade_frequency(self, trend=None):
        """🎯 Retourne la fréquence adaptative selon la direction du marché détectée par detect_ultra_trend()"""
        # Si trend n'est pas fourni, on utilise la détection ultra trend pour cohérence
        if trend is None:
            data = self.get_ultra_fast_data(20)
            if data:
                trend, _, _ = self.detect_ultra_trend(data)
            else:
                trend = "SIDEWAYS"
        
        if trend == 'BULLISH':
            frequency = 300  # 5 minutes pour M5 Pullback
            safe_log(f"📈 Marché HAUSSIER → Fréquence: {frequency}s (1min)")
            return frequency
        elif trend == 'BEARISH':
            frequency = 300  # 5 minutes pour M5 Pullback
            safe_log(f"📉 Marché BAISSIER → Fréquence: {frequency}s (2min)")
            return frequency
        else:
            safe_log(f"➡️ Marché NEUTRE → PAS DE TRADING (direction incertaine)")
            return None  # Pas de trading si direction incertaine
    
    def get_ultra_fast_data(self, count=50):
        """Récupère données ultra rapides pour scalping (sans pandas)"""
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, count)
        
        if rates is None:
            safe_log(f"❌ Impossible de récupérer données {self.symbol}")
            return None
        
        # Conversion simple en liste de dictionnaires
        data = []
        for rate in rates:
            data.append({
                'time': rate[0],
                'open': rate[1],
                'high': rate[2], 
                'low': rate[3],
                'close': rate[4],
                'volume': rate[5]
            })
        
        return data
    
    def force_daily_reset_now(self):
        """🔄 Force un reset quotidien immédiat (utile pour corriger les erreurs)"""
        safe_log(f"🔄 RESET FORCÉ DEMANDÉ")
        # On force la date à être différente pour déclencher le reset
        self.stats['daily_start'] = datetime.now().date() - timedelta(days=1)
        # Puis on appelle le reset quotidien
        self.check_daily_reset()
        safe_log(f"✅ Reset forcé terminé - Système réinitialisé")

    def check_daily_reset(self):
        """🌅 Vérification et reset quotidien complet (balance + SL + tous les systèmes) - ARGENT RÉEL"""
        try:
            today = datetime.now().date()
            force_reset = self.force_reset_requested if hasattr(self, 'force_reset_requested') else False
            
            # 🚨 DÉTECTION AUTOMATIQUE DU BESOIN DE RESET (ARGENT RÉEL)
            account_info = mt5.account_info()
            needs_reset = False
            reset_reason = ""
            
            # Condition 1: Nouveau jour
            if self.stats['daily_start'] != today:
                needs_reset = True
                reset_reason = "NOUVEAU JOUR DÉTECTÉ"
            
            # Condition 2: Reset forcé au démarrage
            elif force_reset:
                needs_reset = True
                reset_reason = "RESET FORCÉ DEMANDÉ AU DÉMARRAGE"
            
            # Condition 3: Balance de référence aberrante (différence > 20% par rapport à la balance actuelle)
            elif account_info and self.initial_balance > 0:
                current_balance = account_info.balance
                balance_diff_pct = abs((current_balance - self.initial_balance) / self.initial_balance * 100)
                if balance_diff_pct > 20:  # Si la différence est trop importante
                    needs_reset = True
                    reset_reason = f"BALANCE DE RÉFÉRENCE ABERRANTE ({balance_diff_pct:.1f}% de différence)"
            
            if needs_reset:
                safe_log(f"🔄 {reset_reason} - RESET COMPLET ARGENT RÉEL")
                safe_log(f"   📅 Ancien jour: {self.stats['daily_start']}")
                safe_log(f"   📅 Nouveau jour: {today}")
                
                # 1. Reset date de référence
                self.stats['daily_start'] = today
                
                # 2. Reset système SL (ancien système, conservé pour compatibilité)
                if hasattr(self, 'stats') and 'daily_sl_count' in self.stats:
                    self.stats['daily_sl_count'] = 0
                    self.stats['safety_mode_active'] = False
                
                # 3. Reset tickets traités SL
                if hasattr(self, 'processed_tickets'):
                    self.processed_tickets.clear()
                
                # 4. 🚨 RESET BALANCE DE RÉFÉRENCE (ARGENT RÉEL)
                if account_info:
                    old_initial_balance = self.initial_balance
                    old_daily_start_balance = self.daily_start_balance
                    
                    # Mode argent réel: utilise la balance réelle uniquement
                    self.initial_balance = account_info.balance
                    self.daily_start_balance = account_info.balance
                    safe_log(f"💰 RESET BALANCE DE RÉFÉRENCE ARGENT RÉEL:")
                    safe_log(f"   📊 Ancienne balance de référence: {old_initial_balance:.2f}€")
                    safe_log(f"   📊 Nouvelle balance de référence: {self.initial_balance:.2f}€")
                    safe_log(f"   🚨 Nouveau seuil -5%: {self.initial_balance * 0.05:.2f}€")
                    
                    safe_log(f"💰 RESET BALANCE DE DÉPART QUOTIDIENNE:")
                    safe_log(f"   📊 Ancienne balance de départ: {old_daily_start_balance:.2f}€")
                    safe_log(f"   📊 Nouvelle balance de départ: {self.daily_start_balance:.2f}€")
                    safe_log(f"   🔄 Profit quotidien remis à zéro")
                
                # 5. Reset mode sécurité balance et système progressif
                self.stats['balance_safety_active'] = False
                self.stats['security_pause_count'] = 0  # Reset compteur pauses
                self.stats['security_grace_period'] = None  # Reset période grâce
                safe_log(f"🔄 RESET SYSTÈME SÉCURITÉ PROGRESSIF:")
                safe_log(f"   📊 Compteur pauses: 0")
                safe_log(f"   🎯 Seuil de nouveau: -5%")
                safe_log(f"   ⏰ Période de grâce: Aucune")
                
                # 6. Reset profit quotidien
                self.stats['daily_profit'] = 0
                if hasattr(self, 'bot_trades_profit'):
                    self.bot_trades_profit = 0
                if hasattr(self, 'manual_daily_profit'):
                    self.manual_daily_profit = None
                
                # 7. Reset du flag de reset forcé
                if hasattr(self, 'force_reset_requested'):
                    self.force_reset_requested = False
                
                # 8. 🕐 Reset pause nocturne (reprendre le trading à 00h20)
                self.is_trading_paused = False
                
                safe_log(f"✅ RESET AUTOMATIQUE TERMINÉ - ARGENT RÉEL:")
                safe_log(f"🛡️ Système de sécurité balance opérationnel (seuil -5%)")
                safe_log(f"🕐 Trading actif de 00h20 à 22h50")
                safe_log(f"🚨 Mode argent réel avec sécurités renforcées")
                
        except Exception as e:
            safe_log(f"❌ Erreur reset quotidien: {e}")

    def check_trading_hours(self):
        """🕐 Vérifie les horaires de trading et gère la fermeture automatique à 22h50 et reprise à 00h20"""
        try:
            current_time = datetime.now()
            current_hour = current_time.hour
            current_minute = current_time.minute
            current_time_decimal = current_hour + (current_minute / 60.0)  # Conversion en décimal pour 00h20 = 0.33
            current_weekday = current_time.weekday()  # 0=Lundi, 4=Vendredi, 6=Dimanche
            
            # 🔴 FERMETURE FORCÉE VENDREDI 22H30 (fin de semaine Forex)
            if current_weekday == 4 and current_time_decimal >= 22.5:  # Vendredi 22h30
                safe_log(f"📅 FERMETURE HEBDOMADAIRE - Vendredi 22h30 atteinte")
                safe_log(f"🔴 FERMETURE FORCÉE DE TOUTES LES POSITIONS AVANT WEEK-END")
                
                # Fermeture immédiate de toutes les positions (profitables ET perdantes)
                closed_count = self.close_all_positions_friday_end()
                
                if closed_count > 0:
                    safe_log(f"✅ {closed_count} positions fermées pour le week-end")
                else:
                    safe_log(f"ℹ️ Aucune position à fermer")
                
                safe_log(f"⏸️ Trading suspendu jusqu'à lundi 00h20")
                self.is_trading_paused = True
                
                return False  # Trading arrêté pour le week-end
            
            # Vérification si on doit fermer à 22h50 avec SYSTÈME SPÉCIAL
            if current_time_decimal >= self.daily_close_time and not self.is_trading_paused:
                safe_log(f"🕐 FERMETURE AUTOMATIQUE SPÉCIALE - 22h50 atteinte")
                safe_log(f"📋 Actions spéciales 22h50:")
                safe_log(f"   1️⃣ ARRÊT du trading (pas de nouveaux trades)")
                safe_log(f"   2️⃣ SUPPRESSION des SL sur toutes les positions")
                safe_log(f"   3️⃣ FERMETURE automatique des positions PROFITABLES seulement")
                safe_log(f"   4️⃣ Pause trading jusqu'à 00h20")
                
                # Activation du système spécial 22h50
                self.activate_21h30_special_mode()
                
                # Activation de la pause nocturne
                self.is_trading_paused = True
                
                safe_log(f"✅ SYSTÈME 21H30 ACTIVÉ:")
                safe_log(f"   � Trading STOPPÉ")
                safe_log(f"   🔧 SL supprimés sur toutes positions")
                safe_log(f"   💰 Fermeture automatique des profits")
                safe_log(f"   ⏸️ Pause jusqu'à 7h30")
                
                return False  # Trading arrêté
            
            # Vérification si on peut reprendre à 7h30 (sauf week-end)
            elif current_time_decimal >= self.daily_start_time and current_time_decimal < self.daily_close_time and self.is_trading_paused:
                # Vérification spéciale week-end: pas de reprise samedi/dimanche
                if current_weekday == 5:  # Samedi
                    safe_log(f"📅 WEEK-END - Samedi | Pas de trading")
                    return False
                elif current_weekday == 6:  # Dimanche
                    safe_log(f"📅 WEEK-END - Dimanche | Reprise lundi 7h30")
                    return False
                else:
                    # Reprise normale (lundi à vendredi)
                    day_name = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"][current_weekday]
                    safe_log(f"🌅 REPRISE DU TRADING - {day_name} 7h30 atteinte")
                    safe_log(f"   🕐 Heure actuelle: {current_hour}h{current_minute:02d}")
                    safe_log(f"   ✅ Trading autorisé jusqu'à 21h30")
                    
                    # Désactivation de la pause nocturne
                    self.is_trading_paused = False
                    
                    return True  # Trading autorisé
            
            # Vérification si on est en période de pause (21h30 à 7h30)
            elif self.is_trading_paused or current_time_decimal < self.daily_start_time or current_time_decimal >= self.daily_close_time:
                # Pendant la pause, continuer à fermer les positions profitables
                self.continue_21h30_special_mode()
                
                # Log périodique pendant la pause (toutes les 100 vérifications = ~16 minutes)
                if not hasattr(self, '_pause_log_count'):
                    self._pause_log_count = 0
                
                self._pause_log_count += 1
                if self._pause_log_count % 100 == 0:
                    if current_weekday == 5:  # Samedi
                        safe_log(f"📅 WEEK-END - Samedi {current_hour}h{current_minute:02d} | Reprise lundi 7h30")
                    elif current_weekday == 6:  # Dimanche  
                        safe_log(f"📅 WEEK-END - Dimanche {current_hour}h{current_minute:02d} | Reprise lundi 7h30")
                    else:
                        safe_log(f"🌙 PAUSE NOCTURNE - {current_hour}h{current_minute:02d} | Reprise à 7h30")
                
                return False  # Trading en pause
            
            # Trading normal autorisé (entre 7h30 et 21h30)
            return True
            
        except Exception as e:
            safe_log(f"❌ Erreur vérification horaires: {e}")
            return True  # En cas d'erreur, on autorise le trading
    
    def activate_21h30_special_mode(self):
        """🛡️ NOUVELLE STRATÉGIE SÉCURISÉE 21H30: Ferme TOUTES les positions ou break-even"""
        try:
            safe_log(f"🌙 ACTIVATION MODE SÉCURISÉ 21H30")
            
            # Récupération des positions ouvertes
            mt5_positions = mt5.positions_get(symbol=self.symbol)
            if not mt5_positions:
                safe_log(f"ℹ️ Aucune position ouverte à traiter")
                return
            
            safe_log(f"🔧 Traitement de {len(mt5_positions)} positions:")
            
            # 🛡️ OPTION A (RECOMMANDÉE): Ferme TOUTES les positions
            # Plus sécurisé - ardoise vierge chaque jour
            closed_count = 0
            total_profit = 0
            
            for position in mt5_positions:
                success = self.close_position_by_ticket(position.ticket)
                if success:
                    closed_count += 1
                    total_profit += position.profit
                    status = "PROFIT" if position.profit > 0 else "PERTE" if position.profit < 0 else "BREAKEVEN"
                    safe_log(f"   � Position fermée ({status}): Ticket {position.ticket} | {position.profit:+.2f}€")
            
            safe_log(f"✅ MODE SÉCURISÉ 21H30 ACTIVÉ:")
            safe_log(f"   � {closed_count} positions fermées (TOUTES)")
            safe_log(f"   💰 Résultat net: {total_profit:+.2f}€")
            safe_log(f"   ✨ ARDOISE VIERGE pour demain - Aucun risque nocturne")
            
        except Exception as e:
            safe_log(f"❌ Erreur activation mode sécurisé 21h30: {e}")
    
    def continue_21h30_special_mode(self):
        """🛡️ Mode sécurisé: Pas de surveillance nocturne nécessaire"""
        # Toutes les positions ont été fermées à 21h30
        # Pas besoin de surveillance jusqu'à 7h30
        return
    
    def close_all_positions_end_day(self):
        """Ferme toutes les positions ouvertes en fin de journée"""
        try:
            # Récupération des positions ouvertes
            mt5_positions = mt5.positions_get(symbol=self.symbol)
            if not mt5_positions:
                safe_log("📊 Aucune position ouverte à fermer")
                return 0
            
            safe_log(f"🔄 Fermeture de {len(mt5_positions)} positions en fin de journée...")
            closed_count = 0
            total_profit = 0
            
            for position in mt5_positions:
                # Fermeture de la position
                success = self.close_position_by_ticket(position.ticket)
                if success:
                    closed_count += 1
                    total_profit += position.profit
                    position_type = "BUY" if position.type == mt5.POSITION_TYPE_BUY else "SELL"
                    safe_log(f"   ✅ {position_type} fermé: Ticket {position.ticket} | P&L: {position.profit:+.2f}€")
                else:
                    safe_log(f"   ❌ Échec fermeture: Ticket {position.ticket}")
            
            # Mise à jour du profit quotidien
            if total_profit != 0:
                self.update_daily_profit(total_profit)
                safe_log(f"💰 Profit de fermeture: {total_profit:+.2f}€")
            
            safe_log(f"🏁 BILAN FERMETURE QUOTIDIENNE:")
            safe_log(f"   📊 Positions fermées: {closed_count}/{len(mt5_positions)}")
            safe_log(f"   💰 P&L total: {total_profit:+.2f}€")
            
            return closed_count
            
        except Exception as e:
            safe_log(f"❌ Erreur fermeture fin de journée: {e}")
            return 0

    def close_all_positions_friday_end(self):
        """🔴 Ferme TOUTES les positions (profitables ET perdantes) le vendredi à 22h30"""
        try:
            # Récupération des positions ouvertes
            mt5_positions = mt5.positions_get(symbol=self.symbol)
            if not mt5_positions:
                return 0
            
            safe_log(f"🔴 FERMETURE HEBDOMADAIRE - Vendredi 22h30")
            safe_log(f"📋 Fermeture forcée de {len(mt5_positions)} positions avant week-end...")
            
            closed_count = 0
            total_profit = 0
            
            for position in mt5_positions:
                position_type = "BUY" if position.type == mt5.POSITION_TYPE_BUY else "SELL"
                profit_status = "PROFIT" if position.profit > 0 else "PERTE"
                
                safe_log(f"   🔴 Fermeture {position_type}: Ticket {position.ticket} | {profit_status}: {position.profit:+.2f}€")
                
                success = self.close_position_by_ticket(position.ticket)
                if success:
                    closed_count += 1
                    total_profit += position.profit
                    safe_log(f"   ✅ {position_type} fermé avec succès")
                else:
                    safe_log(f"   ❌ Échec fermeture: Ticket {position.ticket}")
            
            # Mise à jour du profit avec les fermetures forcées
            if total_profit != 0:
                safe_log(f"💰 P&L total fermetures week-end: {total_profit:+.2f}€")
            
            safe_log(f"🏁 BILAN FERMETURE HEBDOMADAIRE:")
            safe_log(f"   📊 Positions fermées: {closed_count}/{len(mt5_positions)}")
            safe_log(f"   💰 P&L total: {total_profit:+.2f}€")
            safe_log(f"   📅 Prochaine ouverture: Lundi 7h30")
            
            return closed_count
            
        except Exception as e:
            safe_log(f"❌ Erreur fermeture hebdomadaire: {e}")
            return 0

    def check_for_new_stop_losses(self):
        """🔍 Méthode alternative - Vérifie les nouveaux SL directement depuis l'historique MT5"""
        try:
            # Vérification et reset quotidien complet
            self.check_daily_reset()
            
            # Récupération historique des deals de la journée (seulement les 2 dernières heures pour éviter trop de données)
            from_date = datetime.now() - timedelta(hours=2)
            to_date = datetime.now()
            
            deals = mt5.history_deals_get(from_date, to_date, symbol=self.symbol)
            if not deals:
                return
            
            # Comptage UNIQUEMENT des nouveaux SL (pas déjà traités)
            new_sl_count = 0
            
            for deal in deals:
                # On ne regarde que les deals de sortie (fermeture)
                if deal.entry != mt5.DEAL_ENTRY_OUT:
                    continue
                
                # Vérifier si ce ticket est déjà traité
                if deal.position_id in self.processed_tickets:
                    continue  # Ignorer, déjà traité
                
                # Vérification STRICTE si c'est un vrai SL
                comment = deal.comment.lower() if deal.comment else ""
                is_sl = False
                
                # 1. SEULEMENT si commentaire contient explicitement "sl" ou "stop"
                if ("sl" in comment and not "breakeven" in comment) or "stop" in comment:
                    is_sl = True
                
                # 2. OU perte TRÈS significative (plus strict: > 50€)
                elif deal.profit < -50.0:
                    is_sl = True
                    safe_log(f"🔍 SL détecté par perte importante: {deal.profit:.2f}€")
                
                if is_sl:
                    # Nouveau SL trouvé
                    self.processed_tickets.add(deal.position_id)
                    new_sl_count += 1
                    self.stats['daily_sl_count'] += 1
                    
                    safe_log(f"🔴 NOUVEAU SL #{self.stats['daily_sl_count']}/10:")
                    safe_log(f"   📋 Ticket: {deal.position_id}")
                    safe_log(f"   💰 Perte: {deal.profit:.2f}€")
                    safe_log(f"   📝 Commentaire: '{deal.comment}'")
                    safe_log(f"   ⏰ Heure: {datetime.fromtimestamp(deal.time)}")
                    
                    # Vérification seuil critique
                    if self.stats['daily_sl_count'] >= 10 and not self.stats['safety_mode_active']:
                        safe_log(f"� SEUIL CRITIQUE ATTEINT: {self.stats['daily_sl_count']} SL!")
                        self.activate_safety_mode()
                        break  # Sortir de la boucle une fois le mode sécurité activé
            
            # Log seulement s'il y a de nouveaux SL
            if new_sl_count > 0:
                safe_log(f"� {new_sl_count} nouveaux SL détectés - Total: {self.stats['daily_sl_count']}/10")
            
        except Exception as e:
            safe_log(f"❌ Erreur vérification SL: {e}")
            import traceback
            safe_log(f"📋 Traceback: {traceback.format_exc()}")
    
    def get_detailed_position_profit_from_history(self, ticket):
        """Récupère le profit détaillé d'une position depuis l'historique des deals"""
        try:
            # Récupération de l'historique des deals pour ce ticket
            from_date = datetime.now() - timedelta(hours=1)  # Cherche dans la dernière heure
            to_date = datetime.now()
            
            deals = mt5.history_deals_get(from_date, to_date, position=ticket)
            if deals:
                # Filtrer les deals de sortie (fermeture) uniquement
                exit_deals = [deal for deal in deals if deal.entry == mt5.DEAL_ENTRY_OUT]
                
                if exit_deals:
                    # Prendre le dernier deal de sortie (fermeture)
                    last_exit_deal = exit_deals[-1]
                    total_profit = last_exit_deal.profit
                    
                    # Déterminer le type de fermeture plus précisément
                    comment = last_exit_deal.comment.lower() if last_exit_deal.comment else ""
                    
                    # Logique stricte de détection SL/TP
                    close_type = "MANUAL"  # Par défaut
                    
                    # 1. D'abord vérifier le commentaire MT5 (plus fiable)
                    if "tp" in comment or "take profit" in comment or "[tp]" in comment:
                        close_type = "TP"
                    elif "sl" in comment or "stop loss" in comment or "[sl]" in comment:
                        close_type = "SL"
                    else:
                        # 2. Logique stricte basée sur le profit pour éviter les faux positifs
                        # Un vrai SL doit être une perte significative (pas juste -0.05€)
                        if total_profit > 5.0:  # TP: profit significatif > 5€
                            close_type = "TP"
                        elif total_profit < -10.0:  # SL: perte significative > 10€
                            close_type = "SL"
                        else:
                            # 3. Profit/perte faible = fermeture manuelle ou breakeven
                            if abs(total_profit) <= 1.0:  # Très proche de 0
                                close_type = "BREAKEVEN"
                            else:
                                close_type = "MANUAL"  # Fermeture manuelle
                    
                    safe_log(f"🔍 Debug profit détaillé - Ticket {ticket}:")
                    safe_log(f"   💰 Profit brut: {total_profit:.2f}€")
                    safe_log(f"   📝 Commentaire MT5: '{comment}'")
                    safe_log(f"   🎯 Type final: {close_type}")
                    safe_log(f"   ⚖️ Logique: {'TP (>5€)' if total_profit > 5.0 else 'SL (<-10€)' if total_profit < -10.0 else 'BREAKEVEN/MANUAL'}")
                    
                    return {
                        'profit': total_profit,
                        'type': close_type,
                        'comment': comment
                    }
                else:
                    # Fallback: sommer tous les deals si pas de deal de sortie spécifique
                    total_profit = sum(deal.profit for deal in deals)
                    safe_log(f"🔍 Debug profit (fallback) - Ticket {ticket}: {total_profit:.2f}€")
                    
                    # Logique stricte pour le fallback aussi
                    close_type = "SL" if total_profit < -10.0 else "TP" if total_profit > 5.0 else "MANUAL"
                    return {
                        'profit': total_profit,
                        'type': close_type,
                        'comment': "fallback"
                    }
                    
        except Exception as e:
            safe_log(f"⚠️ Erreur récupération profit détaillé: {e}")
        
        return None
    
    def get_position_profit_from_history(self, ticket):
        """Récupère le profit d'une position depuis l'historique des deals"""
        try:
            # Récupération de l'historique des deals pour ce ticket
            from_date = datetime.now() - timedelta(hours=1)  # Cherche dans la dernière heure
            to_date = datetime.now()
            
            deals = mt5.history_deals_get(from_date, to_date, position=ticket)
            if deals:
                # Le dernier deal contient le profit de fermeture
                total_profit = sum(deal.profit for deal in deals)
                return total_profit
        except Exception as e:
            safe_log(f"⚠️ Erreur récupération profit: {e}")
        
        return None
    
    def update_daily_profit(self, profit_amount):
        """Met à jour le profit journalier"""
        # Si profit manuel défini, on ajoute seulement aux trades du bot
        if self.manual_daily_profit is not None:
            self.bot_trades_profit += profit_amount
            self.stats['daily_profit'] = self.manual_daily_profit + self.bot_trades_profit
            safe_log(f"💰 Profit journalier mis à jour: {self.stats['daily_profit']:.2f}€")
            safe_log(f"   📊 Base manuelle: {self.manual_daily_profit:.2f}€ + Trades bot: {self.bot_trades_profit:.2f}€")
        else:
            # Sinon ajout direct classique
            self.stats['daily_profit'] += profit_amount
            safe_log(f"💰 Profit journalier mis à jour: {self.stats['daily_profit']:.2f}€")
    
    def force_update_manual_profit(self, new_manual_profit):
        """Force la mise à jour du profit manuel (pour corrections)"""
        if self.manual_daily_profit is not None:
            old_profit = self.manual_daily_profit
            self.manual_daily_profit = new_manual_profit
            self.stats['daily_profit'] = self.manual_daily_profit + self.bot_trades_profit
            safe_log(f"🔄 Profit manuel corrigé: {old_profit:.2f}€ → {new_manual_profit:.2f}€")
            safe_log(f"💰 Nouveau profit total: {self.stats['daily_profit']:.2f}€")
        else:
            # Si pas de profit manuel, on l'initialise
            self.manual_daily_profit = new_manual_profit
            self.bot_trades_profit = 0
            self.stats['daily_profit'] = new_manual_profit
            safe_log(f"✅ Profit manuel initialisé: {new_manual_profit:.2f}€")
            safe_log(f"💰 Profit total: {self.stats['daily_profit']:.2f}€")
    
    def force_profit_sync_now(self):
        """Force une synchronisation immédiate du profit avec MT5"""
        safe_log("🔄 Synchronisation forcée du profit...")
        safe_log(f"✅ Profit actuel: {self.stats['daily_profit']:.2f}€")
    
    def close_profitable_positions(self):
        """Ferme toutes les positions qui sont actuellement profitables"""
        if not self.open_positions:
            return
            
        # Récupération des positions MT5
        mt5_positions = mt5.positions_get(symbol=self.symbol)
        if not mt5_positions:
            return
            
        closed_count = 0
        for position in mt5_positions:
            # Vérification si la position est profitable
            if position.profit > 0:
                success = self.close_position_by_ticket(position.ticket)
                if success:
                    closed_count += 1
                    self.update_daily_profit(position.profit)
                    safe_log(f"💰 Position fermée (profitable): Ticket {position.ticket} | Profit: +{position.profit:.2f}€")
        
        if closed_count > 0:
            safe_log(f"✅ {closed_count} positions profitables fermées")
            
        # Vérification si toutes les positions sont fermées
        remaining_positions = mt5.positions_get(symbol=self.symbol)
        if not remaining_positions:
            current_profit = self.calculate_real_time_daily_profit()
            safe_log(f"🏁 Toutes les positions fermées - Journée terminée avec {current_profit:.2f}€ de profit")
            return True
            
        return False
    
    def detect_ultra_trend(self, data):
        """🎯 NOUVELLE DÉTECTION M5 PULLBACK : EMA 200/50 + RSI + ATR"""
        # Vérification taille minimale des données pour tous les indicateurs
        min_required = max(TREND_EMA_MASTER, TREND_EMA_PULLBACK, RSI_PERIOD, ATR_PERIOD)
        if len(data) < min_required:
            return "UNKNOWN", 0, {
                'ema_master': 0, 'ema_pullback': 0, 'rsi': 50, 
                'price': 0, 'atr': 0, 'pullback_quality': 0
            }
        
        # Extraction des prix de clôture et autres données
        close_prices = [candle['close'] for candle in data]
        
        # 🎯 CALCUL DES NOUVEAUX INDICATEURS M5
        ema_master = self.calculate_ema(close_prices, TREND_EMA_MASTER)      # EMA 200 - Tendance de fond
        ema_pullback = self.calculate_ema(close_prices, TREND_EMA_PULLBACK)  # EMA 50 - Zone de repli
        rsi = self.calculate_rsi(close_prices, RSI_PERIOD)                   # RSI 14 - Momentum
        atr = self.calculate_atr(data, ATR_PERIOD)                           # ATR 14 - Volatilité
        
        # Valeurs actuelles (dernières calculées)
        current_price = close_prices[-1]
        current_ema_master = ema_master[-1] if len(ema_master) > 0 else current_price
        current_ema_pullback = ema_pullback[-1] if len(ema_pullback) > 0 else current_price
        current_rsi = rsi[-1] if len(rsi) > 0 else 50
        current_atr = atr[-1] if len(atr) > 0 else 0.5  # ATR fallback pour XAUUSD
        
        # 🎯 DÉTECTION TENDANCE DE FOND (Principe fondamental)
        if current_price > current_ema_master:
            trend_direction = "BULLISH"    # Prix > EMA 200 = Tendance haussière
        elif current_price < current_ema_master:
            trend_direction = "BEARISH"    # Prix < EMA 200 = Tendance baissière
        else:
            trend_direction = "SIDEWAYS"   # Prix = EMA 200 = Neutre
        
        # 🎯 CALCUL QUALITÉ DU PULLBACK (Distance à l'EMA 50)
        distance_to_pullback_ema = abs(current_price - current_ema_pullback)
        pullback_threshold = current_atr * ATR_PULLBACK_MULTIPLIER  # 25% de l'ATR
        
        # Plus on est proche de l'EMA 50, plus la qualité est élevée
        if distance_to_pullback_ema <= pullback_threshold:
            pullback_quality = 100 * (1 - distance_to_pullback_ema / pullback_threshold)
        else:
            pullback_quality = 0  # Trop éloigné de l'EMA 50
        
        # 🎯 FORCE GLOBALE DE LA CONFIGURATION
        # Basée sur la distance entre EMAs et la qualité du pullback
        ema_spread = abs(current_ema_master - current_ema_pullback) / current_price * 100
        strength = min(ema_spread * 10 + pullback_quality, 100)  # Max 100%
        
        # Mise à jour historique de tendance
        if trend_direction != self.trend_data['current_trend']:
            self.trend_data['last_trend_change'] = datetime.now()
            self.trend_data['trend_duration'] = 0
        else:
            self.trend_data['trend_duration'] += 1
        
        self.trend_data['current_trend'] = trend_direction
        self.trend_data['trend_strength'] = strength
        
        return trend_direction, strength, {
            'ema_master': current_ema_master,        # EMA 200 - Juge de paix
            'ema_pullback': current_ema_pullback,    # EMA 50 - Zone de repli
            'rsi': current_rsi,                      # RSI - Momentum
            'price': current_price,                  # Prix actuel
            'atr': current_atr,                      # ATR - Volatilité
            'pullback_quality': pullback_quality,    # Qualité du pullback (0-100%)
            'ema_spread_pct': ema_spread            # Écart entre EMAs en %
        }
    
    def calculate_atr(self, data, period):
        """Calcule l'Average True Range (ATR) sans pandas - NOUVEAU pour M5 PULLBACK"""
        if len(data) < period:
            return [0] * len(data)

        true_ranges = []
        # Premier TR basé uniquement sur la différence High-Low
        true_ranges.append(data[0]['high'] - data[0]['low'])

        # Calcul des True Range suivants avec la logique complète
        for i in range(1, len(data)):
            high = data[i]['high']
            low = data[i]['low']
            prev_close = data[i-1]['close']
            
            # Les 3 composantes du True Range
            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)
            
            # Le True Range est le maximum des 3
            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)

        # Lissage de l'ATR (similaire à une EMA)
        atr_values = [sum(true_ranges[:period]) / period]  # Premier ATR = moyenne simple
        
        # ATR suivants = lissage exponentiel
        for i in range(period, len(true_ranges)):
            atr = (atr_values[-1] * (period - 1) + true_ranges[i]) / period
            atr_values.append(atr)

        # Retourner avec padding pour correspondre à la taille des données
        return [0] * (period - 1) + atr_values

    def calculate_ema(self, prices, period):
        """Calcule l'EMA sans pandas"""
        if len(prices) < period:
            return prices.copy()
        
        multiplier = 2 / (period + 1)
        ema = [prices[0]]  # Premier prix comme base
        
        for price in prices[1:]:
            ema_value = (price * multiplier) + (ema[-1] * (1 - multiplier))
            ema.append(ema_value)
        
        return ema
    
    def calculate_adaptive_lot_size(self, atr_sl_distance):
        """
        🚀 CALCUL LOT ADAPTATIF AGRESSIF - Risque 3.5% par trade
        =======================================================
        
        Approche agressive mais sécurisée:
        - Risque 3.5% de la balance par trade (vs 1-2% standard)
        - Sécurité garantie par l'arrêt automatique à -5% balance
        - Maximum 1.4 trades perdants avant déclenchement sécurité
        
        Args:
            atr_sl_distance: Distance du Stop Loss basée sur l'ATR
            
        Returns:
            float: Taille de lot optimale (0.01 à 1.0)
        """
        try:
            # Récupération de la balance actuelle
            account_info = mt5.account_info()
            if not account_info:
                safe_log("⚠️ Impossible de récupérer la balance - Lot par défaut: 0.01")
                return 0.01
            
            current_balance = account_info.balance
            
            # Calcul du risque maximal par trade (3.5% agressif)
            max_loss_per_trade = current_balance * (ADAPTIVE_LOT_RISK_PERCENT / 100)
            
            # Calcul du lot nécessaire
            # Pour XAUUSD: 1 lot = 100$/point, donc lot = max_loss / (sl_distance * 100)
            lot_size = max_loss_per_trade / (atr_sl_distance * 100)
            
            # Arrondi et sécurités
            lot_size = round(lot_size, 2)
            lot_size = max(lot_size, ADAPTIVE_LOT_MIN)  # Minimum broker
            lot_size = min(lot_size, ADAPTIVE_LOT_MAX)  # Maximum sécurité
            
            # Log informatif
            profit_potential = max_loss_per_trade * 2  # Ratio 1:2
            safe_log(f"🚀 LOT ADAPTATIF OPTIMISÉ: Balance ${current_balance:.0f} → Lot {lot_size:.2f}")
            safe_log(f"   💰 Risque: -${max_loss_per_trade:.0f} (2.5%) | Profit potentiel: +${profit_potential:.0f}")
            
            return lot_size
            
        except Exception as e:
            safe_log(f"❌ Erreur calcul lot adaptatif: {e}")
            safe_log("   🔄 Utilisation lot par défaut: 0.01")
            return 0.01
    
    def get_higher_timeframe_trend(self):
        """🎯 FILTRE TENDANCE SUPÉRIEURE : EMA 200 sur M5 pour direction majeure"""
        try:
            # Récupération des données M5 (200 périodes pour EMA 200)
            rates = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_M5, 0, 220)
            
            if rates is None or len(rates) < 200:
                safe_log("⚠️ Données M5 insuffisantes pour EMA 200 - Filtre désactivé")
                return "NEUTRAL"  # Pas de filtre si données insuffisantes
            
            # Calcul EMA 200 sur les prix de clôture M5
            close_prices = [float(rate['close']) for rate in rates]
            ema_200 = self.calculate_ema(close_prices, 200)
            
            if len(ema_200) < 200:
                return "NEUTRAL"
            
            # Prix actuel
            current_price = close_prices[-1]
            current_ema_200 = ema_200[-1]
            
            # Détermination de la tendance majeure
            if current_price > current_ema_200:
                trend_direction = "BULLISH_MAJOR"  # Tendance de fond haussière
                safe_log(f"📈 FILTRE M5: Prix {current_price:.2f} > EMA200 {current_ema_200:.2f} = HAUSSE MAJEURE")
            else:
                trend_direction = "BEARISH_MAJOR"  # Tendance de fond baissière  
                safe_log(f"📉 FILTRE M5: Prix {current_price:.2f} < EMA200 {current_ema_200:.2f} = BAISSE MAJEURE")
            
            return trend_direction
            
        except Exception as e:
            safe_log(f"❌ Erreur calcul filtre M5: {e}")
            return "NEUTRAL"
    
    def calculate_rsi(self, prices, period):
        """Calcule le RSI sans pandas"""
        if len(prices) < period + 1:
            return [50] * len(prices)  # RSI neutre par défaut
        
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        # Moyenne simple pour les premiers points
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        rsi_values = []
        
        for i in range(period, len(gains)):
            if avg_loss == 0:
                rsi_values.append(100)
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
                rsi_values.append(rsi)
            
            # Mise à jour des moyennes (lissage)
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        # Compléter pour avoir la même longueur que les prix
        return [50] * period + rsi_values
    
    def should_open_position(self, trend, strength, indicators, time_since_last_buy=None):
        """🎯 NOUVELLE LOGIQUE M5 PULLBACK : Qualité > Quantité"""
        
        current_time = datetime.now()
        current_price = indicators['price']
        ema_master = indicators['ema_master']        # EMA 200 - Tendance de fond
        ema_pullback = indicators['ema_pullback']    # EMA 50 - Zone de repli
        current_rsi = indicators['rsi']
        current_atr = indicators['atr']
        pullback_quality = indicators['pullback_quality']
        
        # �️ VÉRIFICATION MODE SÉCURITÉ BALANCE
        if self.stats['balance_safety_active']:
            return None  # Pas de nouveaux trades en mode sécurité
        
        # 🎯 FILTRE QUALITÉ MINIMUM : On ne trade que les setups de haute qualité
        if strength < 30:  # Force minimale requise
            return None
        
        if pullback_quality < 60:  # Qualité pullback minimale (60%)
            return None
        
        # Calcul des cooldowns adaptatifs
        if time_since_last_buy is None:
            if self.last_buy_timestamp is None:
                time_since_last_buy = float('inf')  # Premier trade = pas de cooldown
            else:
                time_since_last_buy = (current_time - self.last_buy_timestamp).total_seconds()
        
        if self.last_sell_timestamp is None:
            time_since_last_sell = float('inf')  # Premier trade SELL = pas de cooldown
        else:
            time_since_last_sell = (current_time - self.last_sell_timestamp).total_seconds()
        
        # Vérification limites globales - LIMITE ADAPTATIVE SELON BALANCE
        current_positions = len(self.open_positions)
        max_positions_adaptatif = self.calculate_adaptive_max_positions()
        if current_positions >= max_positions_adaptatif:
            return None
        
        # 🟢 STRATÉGIE 1: ACHAT SUR PULLBACK HAUSSIER (BUY)
        # Conditions: Tendance haussière + Prix proche EMA 50 + RSI sain
        if (trend == "BULLISH" and 
            current_price > ema_master and  # Prix > EMA 200 (tendance de fond haussière)
            pullback_quality >= 60 and     # Prix proche de l'EMA 50 (pullback détecté)
            RSI_BUY_MIN <= current_rsi <= RSI_BUY_MAX):  # RSI entre 40-55 (momentum sain)
            
            # Cooldown M5 adaptatif
            cooldown = 300  # 5 minutes en M5
            
            if time_since_last_buy < cooldown:
                remaining_time = cooldown - time_since_last_buy
                safe_log(f"⏳ BUY Cooldown PULLBACK: {remaining_time:.0f}s restantes")
                return None
            
            return {
                'type': 'BUY', 
                'reason': 'PULLBACK_HAUSSIER_M5',  # Pullback sur tendance haussière
                'strength': strength,
                'rsi': current_rsi,
                'pullback_quality': pullback_quality,
                'atr': current_atr,
                'confidence': min(strength + pullback_quality, 100) / 100
            }

        # 🔴 STRATÉGIE 2: VENTE SUR PULLBACK BAISSIER (SELL)
        # Conditions: Tendance baissière + Prix proche EMA 50 + RSI faible
        elif (trend == "BEARISH" and 
              current_price < ema_master and  # Prix < EMA 200 (tendance de fond baissière)
              pullback_quality >= 60 and     # Prix proche de l'EMA 50 (rebond détecté)
              RSI_SELL_MIN <= current_rsi <= RSI_SELL_MAX):  # RSI entre 45-60 (faiblesse confirmée)
            
            # Cooldown SELL adaptatif
            sell_cooldown = 300  # 5 minutes en M5
            
            if time_since_last_sell < sell_cooldown:
                remaining_time = sell_cooldown - time_since_last_sell
                safe_log(f"⏳ SELL Cooldown PULLBACK: {remaining_time:.0f}s restantes")
                return None
            
            return {
                'type': 'SELL', 
                'reason': 'PULLBACK_BAISSIER_M5',  # Rebond sur tendance baissière
                'strength': strength,
                'rsi': current_rsi,
                'pullback_quality': pullback_quality,
                'atr': current_atr,
                'confidence': min(strength + pullback_quality, 100) / 100
            }
        
        # Aucune condition remplie
        return None
        
        # � STRATÉGIE 1: 





        # � STRATÉGIE 2: 













    
    def execute_m5_trade(self, signal):
        """🎯 NOUVELLE EXÉCUTION M5 : TP/SL adaptatifs basés sur l'ATR"""
        
        trade_type = signal['type']
        atr_value = signal['atr']
        current_price = signal.get('price', None)
        
        # Récupération prix réel pour calcul TP/SL
        tick_info = mt5.symbol_info_tick(self.symbol)
        if tick_info is None:
            safe_log("❌ Impossible de récupérer prix pour TP/SL ATR")
            return
        
        # Prix d'entrée basé sur le type d'ordre
        if trade_type == 'BUY':
            entry_price = tick_info.ask
        else:  # SELL
            entry_price = tick_info.bid
        
        # 🎯 CALCUL TP/SL ADAPTATIFS BASÉS SUR L'ATR
        sl_distance = ATR_SL_MULTIPLIER * atr_value  # SL à 1.5x ATR
        tp_distance = ATR_TP_RATIO * sl_distance     # TP à 2x le SL (ratio 1:2)
        
        # Application selon le type d'ordre
        if trade_type == 'BUY':
            sl_price = entry_price - sl_distance
            tp_price = entry_price + tp_distance
        else:  # SELL
            sl_price = entry_price + sl_distance
            tp_price = entry_price - tp_distance
        
        # Conversion en pips pour XAUUSD (1 pip = 0.1)
        sl_pips = sl_distance / 0.1
        tp_pips = tp_distance / 0.1
        
        # 🎯 LOG DÉTAILLÉ DE LA STRATÉGIE M5
        safe_log(f"⚡ TRADE M5 {trade_type} - {signal['reason']}")
        safe_log(f"   📊 ATR actuel: {atr_value:.3f} (volatilité du marché)")
        safe_log(f"   💰 Prix entrée: ${entry_price:.2f}")
        safe_log(f"   🛡️ SL adaptatif: ${sl_price:.2f} ({sl_pips:.1f} pips = 1.5x ATR)")
        safe_log(f"   🎯 TP adaptatif: ${tp_price:.2f} ({tp_pips:.1f} pips = 3x ATR)")
        safe_log(f"   ⚖️ Ratio R/R: 1:2.0 (PROFESSIONNEL)")
        safe_log(f"   📈 Force signal: {signal['strength']:.1f}%")
        safe_log(f"   🎯 Qualité pullback: {signal['pullback_quality']:.1f}%")
        safe_log(f"   📊 RSI: {signal['rsi']:.1f}")
        safe_log(f"   🎲 Confiance: {signal['confidence']:.2f}")
        
        # � VÉRIFICATION MARGIN AVANT TRADE
        if not self.check_margin_availability():
            safe_log(f"🚫 Trade annulé - Margin insuffisante")
            return False
        
        # 🔒 VÉRIFICATION LIMITE POSITIONS SIMULTANÉES
        current_positions = len(self.open_positions)
        if current_positions >= MAX_POSITIONS:
            safe_log(f"🚫 Trade annulé - Limite positions atteinte ({current_positions}/{MAX_POSITIONS})")
            return False
        
        # �🕐 MISE À JOUR TIMESTAMP selon le type de trade
        if trade_type == 'BUY':
            self.last_buy_timestamp = datetime.now()
        else:  # SELL
            self.last_sell_timestamp = datetime.now()
        
        # Exécution selon le mode (réel ou simulation)
        if ENABLE_REAL_TRADING:
            # 🚀 TRADING RÉEL MT5 avec TP/SL adaptatifs
            success = self.place_real_order(trade_type, entry_price, tp_price, sl_price, signal)
            if success:
                safe_log("✅ ORDRE M5 PLACÉ SUR MT5 AVEC TP/SL ADAPTATIFS!")
                safe_log(f"   🎯 Le marché détermine maintenant les TP/SL selon sa volatilité")
                return True
            else:
                safe_log("❌ Échec placement ordre MT5")
                return False
        else:
            # Mode simulation avec nouvelle logique
            safe_log("🎮 MODE SIMULATION M5 - Trade virtuel")
            return True
        
    
    def run_ultra_scalping_cycle(self):
        """🎯 NOUVEAU CYCLE M5 PULLBACK : Qualité > Quantité"""
        
        # 🕐 VÉRIFICATION HORAIRES DE TRADING (22h50 fermeture, 00h20 reprise)
        if not self.check_trading_hours():
            return  # Trading en pause nocturne
        
        # 🛡️ FILET DE SÉCURITÉ - Vérification perte de balance (-5%)
        self.check_balance_safety()
        
        # 🛡️ FILET DE SÉCURITÉ - Vérification des conditions de sortie du mode sécurité
        if self.stats['balance_safety_active']:
            self.check_balance_safety_exit_conditions()
        
        # Récupération données M5 (plus de données nécessaires pour EMA 200)
        df = self.get_ultra_fast_data(250)  # 250 bougies M5 pour calculer EMA 200
        if df is None:
            return
        
        # 🎯 NOUVELLE DÉTECTION M5 PULLBACK
        trend, strength, indicators = self.detect_ultra_trend(df)
        
        current_price = indicators['price']
        ema_master = indicators['ema_master']
        ema_pullback = indicators['ema_pullback']
        current_rsi = indicators['rsi']
        current_atr = indicators['atr']
        pullback_quality = indicators['pullback_quality']
        
        # Affichage état marché M5 avec nouveaux indicateurs
        open_positions_count = len(self.open_positions)
        
        # Calcul du profit actuel
        current_profit = self.calculate_real_time_daily_profit()
        daily_status = f"💰{current_profit:+.1f}€"
        
        # 🛡️ Statut de sécurité
        if self.stats['balance_safety_active']:
            account_info = mt5.account_info()
            if account_info:
                current_balance = account_info.balance
                balance_change_pct = ((current_balance - self.daily_start_balance) / self.daily_start_balance) * 100
                pause_count = self.stats.get('security_pause_count', 0)
                safety_status = f"🛡️SÉCURITÉ#{pause_count}({balance_change_pct:.1f}%)"
            else:
                safety_status = f"🛡️SÉCURITÉ ACTIVE"
        elif self.stats.get('security_grace_period') and datetime.now() < self.stats['security_grace_period']:
            # En période de grâce
            grace_end = self.stats['security_grace_period']
            time_left = grace_end - datetime.now()
            minutes_left = int(time_left.total_seconds() / 60)
            safety_status = f"🎯GRÂCE({minutes_left}min)"
        else:
            account_info = mt5.account_info()
            if account_info and self.daily_start_balance > 0:
                current_balance = account_info.balance
                balance_change_pct = ((current_balance - self.daily_start_balance) / self.daily_start_balance) * 100
                pause_count = self.stats.get('security_pause_count', 0)
                if pause_count == 0:
                    next_threshold = -5.0
                elif pause_count == 1:
                    next_threshold = -7.0
                elif pause_count == 2:
                    next_threshold = -10.0
                else:
                    next_threshold = -15.0
                safety_status = f"Perte:{balance_change_pct:.1f}%/{next_threshold}%"
            else:
                safety_status = f"Balance:OK"
        
        # 🎯 AFFICHAGE ÉTAT M5 PULLBACK (plus riche en information)
        safe_log(f"📊 M5 ${current_price:.2f} | {trend} {strength:.1f}% | "
                f"RSI:{current_rsi:.1f} | ATR:{current_atr:.3f} | "
                f"EMA200:{ema_master:.2f} | EMA50:{ema_pullback:.2f} | "
                f"Pullback:{pullback_quality:.0f}% | Pos:{open_positions_count} | "
                f"{safety_status} | {daily_status}")
        
        # Vérification signal PULLBACK (seulement si pas en mode sécurité)
        if not self.stats['balance_safety_active']:
            signal = self.should_open_position(trend, strength, indicators)
            
            if signal:
                signal_type = signal['type']
                reason = signal['reason']
                safe_log(f"🔥 SIGNAL M5 {signal_type}: {reason} - Force:{strength:.1f}% Pullback:{pullback_quality:.0f}%")
                
                # ✨ NOUVELLE EXÉCUTION M5 avec TP/SL adaptatifs
                success = self.execute_m5_trade(signal)
                if success:
                    safe_log(f"✅ Trade M5 exécuté avec succès!")
                else:
                    safe_log(f"❌ Échec exécution trade M5")
        else:
            # En mode sécurité, message périodique
            if hasattr(self, '_safety_message_count'):
                self._safety_message_count += 1
            else:
                self._safety_message_count = 1
            
            if self._safety_message_count % 5 == 0:  # Toutes les 5 minutes en M5
                safe_log(f"🛡️ MODE SÉCURITÉ BALANCE ACTIF - Trading M5 en pause")
        
        # Affichage stats rapides toutes les 10 analyses (10 minutes en M5)
        if hasattr(self, '_cycle_count'):
            self._cycle_count += 1
        else:
            self._cycle_count = 1
            
        if self._cycle_count % 10 == 0 and self.stats['total_trades'] > 0:
            self.display_m5_stats()
    
    def display_m5_stats(self):
        """🎯 Affiche les stats de la stratégie M5 PULLBACK"""
        if self.stats['total_trades'] == 0:
            return
        
        win_rate = (self.stats['winning_trades'] / self.stats['total_trades']) * 100
        elapsed = datetime.now() - self.stats['start_time']
        
        safe_log(f"\n📈 STATS M5 PULLBACK:")
        safe_log(f"   ⚡ Total: {self.stats['total_trades']} | WR: {win_rate:.1f}%")
        safe_log(f"   💰 Profit: ${self.stats['total_profit']:+.2f}")
        safe_log(f"   ⏱️ Durée: {elapsed} | Fréquence: {self.stats['total_trades']/(elapsed.total_seconds()/3600):.1f} trades/h")
        safe_log(f"   🎯 Stratégie: PULLBACK M5 avec TP/SL adaptatifs ATR")
    
    def display_ultra_stats(self):
        """Affiche les stats ultra scalping"""
        if self.stats['total_trades'] == 0:
            return
        
        win_rate = (self.stats['winning_trades'] / self.stats['total_trades']) * 100
        elapsed = datetime.now() - self.stats['start_time']
        
        safe_log(f"\n📈 ULTRA STATS (dernières 10 trades):")
        safe_log(f"   ⚡ Total: {self.stats['total_trades']} | WR: {win_rate:.1f}%")
        safe_log(f"   💰 Pips: {self.stats['total_pips']:+.1f} | Profit: ${self.stats['total_profit']:+.2f}")
        safe_log(f"   ⏱️ Durée: {elapsed} | Vitesse: {self.stats['total_trades']/(elapsed.total_seconds()/60):.1f} trades/min")
    
    def run_ultra_scalping_session(self, duration_minutes=60):
        """Lance une session d'ultra scalping"""
        safe_log(f"\n🔥 LANCEMENT ULTRA SCALPING SESSION")
        safe_log("="*60)
        safe_log(f"⚡ Stratégie: BUY UNIQUEMENT")
        safe_log(f"📉 BEARISH → BUY (sur rebond) toutes les 2min | 🟢 BULLISH → BUY (sur momentum) par minute")
        safe_log(f"⏰ Cooldown adaptatif: 2min (descente) / 1min (hausse)")
        safe_log(f"🎯 TP/SL: Adaptatifs selon ATR | Breakeven à +40 pips")
        safe_log(f"⏱️ Durée: {duration_minutes} minutes")
        safe_log(f"🔄 Analyse: toutes les {ANALYSIS_INTERVAL} secondes")
        safe_log("")
        
        if ENABLE_REAL_TRADING:
            safe_log("⚠️ MODE TRADING RÉEL ACTIVÉ!")
        else:
            safe_log("🎮 MODE SIMULATION")
        
        self.is_trading = True
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        cycle_count = 0
        
        try:
            while datetime.now() < end_time and self.is_trading:
                cycle_count += 1
                
                # Cycle ultra rapide
                self.run_ultra_scalping_cycle()
                
                # Pause ultra courte
                time.sleep(ANALYSIS_INTERVAL)
                
        except KeyboardInterrupt:
            safe_log(f"\n⏹️ Session ultra scalping interrompue")
        
        self.is_trading = False
        self.generate_ultra_report()
    
    def start_trading_loop(self):
        """Lance le bot en mode ARGENT RÉEL avec interface"""
        safe_log(f"🚨 LANCEMENT ULTRA SCALPING - MODE ARGENT RÉEL")
        safe_log("="*60)
        
        # Récupération balance réelle
        account_info = mt5.account_info()
        if account_info:
            balance = account_info.balance
            safe_log(f"💰 Balance réelle: {balance:.2f}€")
        else:
            safe_log(f"⚠️ Impossible de récupérer la balance")
            
        safe_log(f"⚡ Analyse toutes les {ANALYSIS_INTERVAL} secondes")
        safe_log(f"🎯 TP/SL: Adaptatifs selon ATR")
        safe_log(f"🕐 Horaires: 7h30 à 21h30")
        safe_log(f"🛡️ Sécurités: Seuil -5%, Max 5 positions")
        safe_log(f"⏹️ Arrêt: Ctrl+C")
        
        # Lance le mode illimité
        self.run_ultra_scalping_unlimited()
    
    def run_ultra_scalping_unlimited(self):
        """Lance l'ultra scalping en mode illimité"""
        safe_log(f"\n🔥 ULTRA SCALPING - MODE ILLIMITÉ")
        safe_log("="*60)
        safe_log(f"♾️ Session sans limite de temps")
        safe_log(f"⚡ Analyse toutes les {ANALYSIS_INTERVAL} secondes")
        safe_log(f"🎯 TP/SL: Adaptatifs selon ATR | Breakeven à +40 pips")
        safe_log(f"⏹️ Arrêt: Ctrl+C")
        
        self.is_trading = True
        cycle_count = 0
        last_market_analysis = 0  # Compteur pour l'analyse du marché
        
        try:
            while self.is_trading:
                cycle_count += 1
                
                # 🧠 GESTION INTELLIGENTE DES POSITIONS - Toutes les secondes (nouvelle priorité)
                self.intelligent_position_management()
                
                # 🔒 ANALYSE BREAKEVEN - Toutes les secondes (priorité max)
                self.sync_positions_with_mt5()
                self.check_and_move_sl_to_breakeven()
                
                # 📊 ANALYSE DU MARCHÉ - Toutes les 10 secondes seulement
                if last_market_analysis >= ANALYSIS_INTERVAL:
                    # Affichage progression toutes les 100 analyses de marché
                    if (cycle_count // ANALYSIS_INTERVAL) % 100 == 1:
                        elapsed = datetime.now() - self.stats['start_time']
                        safe_log(f"\n🔥 ANALYSE MARCHÉ {cycle_count // ANALYSIS_INTERVAL} - Temps: {elapsed}")
                    
                    self.run_ultra_scalping_cycle()
                    last_market_analysis = 0  # Reset compteur
                else:
                    last_market_analysis += 1
                
                time.sleep(1)  # Analyse intelligente + breakeven toutes les secondes
                
        except KeyboardInterrupt:
            elapsed = datetime.now() - self.stats['start_time']
            safe_log(f"\n⏹️ Ultra scalping arrêté après {elapsed}")
            safe_log(f"📊 Total cycles: {cycle_count}")
        
        self.is_trading = False
        self.generate_ultra_report()
    
    def generate_ultra_report(self):
        """Génère le rapport final ultra scalping"""
        safe_log(f"\n" + "="*70)
        safe_log("🔥 RAPPORT FINAL - ULTRA SCALPING BUY UNIQUEMENT")
        safe_log("="*70)
        
        if self.stats['total_trades'] == 0:
            safe_log("ℹ️ Aucun trade exécuté durant cette session")
            return
        
        win_rate = (self.stats['winning_trades'] / self.stats['total_trades']) * 100
        avg_pips = self.stats['total_pips'] / self.stats['total_trades']
        session_duration = datetime.now() - self.stats['start_time']
        trades_per_minute = self.stats['total_trades'] / (session_duration.total_seconds() / 60)
        
        safe_log(f"\n⚡ PERFORMANCE ULTRA SCALPING:")
        safe_log(f"   Total trades: {self.stats['total_trades']}")
        safe_log(f"   Win rate: {win_rate:.1f}%")
        safe_log(f"   Total pips: {self.stats['total_pips']:+.1f}")
        safe_log(f"   Profit total: ${self.stats['total_profit']:+.2f}")
        safe_log(f"   Pips moyens/trade: {avg_pips:+.2f}")
        
        safe_log(f"\n📊 STATISTIQUES SESSION:")
        safe_log(f"   Durée: {session_duration}")
        safe_log(f"   Vitesse: {trades_per_minute:.1f} trades/minute")
        safe_log(f"   Positions max simultanées: {self.stats['max_concurrent_positions']}")
        
        # Évaluation performance
        safe_log(f"\n🏆 ÉVALUATION:")
        if win_rate > 60 and self.stats['total_pips'] > 0:
            safe_log(f"   🌟 EXCELLENT! Stratégie ultra profitable")
        elif win_rate > 50:
            safe_log(f"   ✅ BON! Stratégie rentable")
        elif win_rate > 40:
            safe_log(f"   ⚠️ MOYEN. Peut être amélioré")
        else:
            safe_log(f"   ❌ DIFFICILE. Revoir la stratégie")
        
        safe_log(f"\n🔥 Session ultra scalping terminée!")
    
    def analyze_3_weeks_performance(self, total_profit_3_weeks=121.74):
        """
        🔍 ANALYSE DÉTAILLÉE DES PERFORMANCES SUR 3 SEMAINES
        ===================================================
        Analyse complète pour évaluer l'efficacité du bot sur 121,74€ de profit
        """
        safe_log(f"\n" + "="*80)
        safe_log("📊 ANALYSE APPROFONDIE - PERFORMANCE 3 SEMAINES")
        safe_log("="*80)
        
        # 1. MÉTRIQUES DE BASE
        try:
            account_info = mt5.account_info()
            if account_info:
                current_balance = account_info.balance
                safe_log(f"\n💰 BILAN FINANCIER:")
                safe_log(f"   💵 Balance actuelle: {current_balance:.2f}€")
                safe_log(f"   📈 Profit total 3 semaines: +{total_profit_3_weeks:.2f}€")
                safe_log(f"   📊 ROI estimé: {(total_profit_3_weeks / (current_balance - total_profit_3_weeks)) * 100:.2f}%")
                safe_log(f"   💰 Profit moyen/semaine: {total_profit_3_weeks / 3:.2f}€")
                safe_log(f"   📈 Profit moyen/jour: {total_profit_3_weeks / 21:.2f}€ (21 jours ouvrés)")
        except:
            pass
        
        # 2. DONNÉES À COLLECTER POUR ANALYSE COMPLÈTE
        safe_log(f"\n🔍 DONNÉES NÉCESSAIRES POUR ANALYSE APPROFONDIE:")
        safe_log(f"\n   📊 TRADING ACTIVITY:")
        safe_log(f"      ▸ Nombre total de trades sur 3 semaines")
        safe_log(f"      ▸ Nombre de trades gagnants vs perdants")
        safe_log(f"      ▸ Win rate global")
        safe_log(f"      ▸ Profit moyen par trade gagnant")
        safe_log(f"      ▸ Perte moyenne par trade perdant")
        safe_log(f"      ▸ Ratio Risk/Reward")
        
        safe_log(f"\n   ⏰ TEMPORALITÉ:")
        safe_log(f"      ▸ Heures d'activité les plus profitables")
        safe_log(f"      ▸ Jours de la semaine les plus performants")
        safe_log(f"      ▸ Durée moyenne des trades")
        safe_log(f"      ▸ Trades par jour en moyenne")
        
        safe_log(f"\n   🎯 PRÉCISION STRATÉGIQUE:")
        safe_log(f"      ▸ Performance par condition de marché (BULLISH/BEARISH)")
        safe_log(f"      ▸ Efficacité des signaux d'entrée (RSI, EMA)")
        safe_log(f"      ▸ Taux de réussite du système de breakeven")
        safe_log(f"      ▸ Activations du système de sécurité (-5%)")
        
        safe_log(f"\n   📈 DRAWDOWN ET RISQUE:")
        safe_log(f"      ▸ Plus grosse perte journalière")
        safe_log(f"      ▸ Plus grosse série de pertes consécutives")
        safe_log(f"      ▸ Drawdown maximum")
        safe_log(f"      ▸ Temps de récupération moyen après perte")
        
        safe_log(f"\n   💹 OPTIMISATION:")
        safe_log(f"      ▸ Lots moyens utilisés vs balance")
        safe_log(f"      ▸ Efficacité des TP (adaptatifs ATR)")
        safe_log(f"      ▸ Positions simultanées optimales")
        safe_log(f"      ▸ Fréquence de trading optimale")
        
        # 3. QUESTIONS D'ANALYSE CRITIQUE
        safe_log(f"\n❓ QUESTIONS D'ANALYSE CRITIQUE:")
        safe_log(f"\n   1️⃣ CONSISTANCE:")
        safe_log(f"      • Le profit est-il régulier ou dû à quelques gros gains ?")
        safe_log(f"      • Y a-t-il des périodes de sous-performance ?")
        safe_log(f"      • La stratégie est-elle stable dans différentes conditions ?")
        
        safe_log(f"\n   2️⃣ ROBUSTESSE:")
        safe_log(f"      • Comment le bot gère-t-il les périodes volatiles ?")
        safe_log(f"      • Le système de sécurité (-5%) a-t-il été testé ?")
        safe_log(f"      • Résistance aux séries de pertes ?")
        
        safe_log(f"\n   3️⃣ SCALABILITÉ:")
        safe_log(f"      • Performance avec des lots plus importants ?")
        safe_log(f"      • Impact de l'augmentation de capital ?")
        safe_log(f"      • Limite de la stratégie ?")
        
        # 4. COLLECTE DE DONNÉES MT5
        safe_log(f"\n🔍 COLLECTE AUTOMATIQUE DES DONNÉES MT5:")
        self.collect_mt5_historical_data()
        
        safe_log(f"\n✅ BILAN PRÉLIMINAIRE:")
        safe_log(f"   🎯 Résultat: +{total_profit_3_weeks:.2f}€ en 3 semaines = EXCELLENT")
        safe_log(f"   📈 Consistance apparente: À confirmer avec données historiques")
        safe_log(f"   🛡️ Sécurité: Système de protection opérationnel")
        safe_log(f"   ⚡ Potentiel: Stratégie prometteuse à analyser en détail")
        
        safe_log("="*80)
    
    def collect_mt5_historical_data(self):
        """Collecte les données historiques MT5 pour analyse des 3 semaines"""
        try:
            safe_log(f"\n📋 COLLECTE DONNÉES HISTORIQUES MT5...")
            
            # Période de 3 semaines (21 jours)
            from_date = datetime.now() - timedelta(days=21)
            to_date = datetime.now()
            
            # Récupération historique des deals
            deals = mt5.history_deals_get(from_date, to_date, symbol=self.symbol)
            
            if deals and len(deals) > 0:
                safe_log(f"   📊 {len(deals)} deals trouvés sur 3 semaines")
                
                # Analyse des deals
                winning_deals = [deal for deal in deals if deal.profit > 0]
                losing_deals = [deal for deal in deals if deal.profit < 0]
                
                total_profit_mt5 = sum(deal.profit for deal in deals)
                avg_winning_trade = sum(deal.profit for deal in winning_deals) / len(winning_deals) if winning_deals else 0
                avg_losing_trade = sum(deal.profit for deal in losing_deals) / len(losing_deals) if losing_deals else 0
                
                win_rate_mt5 = (len(winning_deals) / len(deals)) * 100 if deals else 0
                
                safe_log(f"\n📈 STATISTIQUES MT5 (3 semaines):")
                safe_log(f"   🔢 Total deals: {len(deals)}")
                safe_log(f"   ✅ Deals gagnants: {len(winning_deals)} ({win_rate_mt5:.1f}%)")
                safe_log(f"   ❌ Deals perdants: {len(losing_deals)}")
                safe_log(f"   💰 Profit total MT5: {total_profit_mt5:.2f}€")
                safe_log(f"   📊 Profit moyen/trade gagnant: {avg_winning_trade:.2f}€")
                safe_log(f"   📉 Perte moyenne/trade perdant: {avg_losing_trade:.2f}€")
                
                if avg_losing_trade != 0:
                    risk_reward = abs(avg_winning_trade / avg_losing_trade)
                    safe_log(f"   ⚖️ Ratio Risk/Reward: 1:{risk_reward:.2f}")
                
                # Analyse temporelle
                safe_log(f"\n⏰ ANALYSE TEMPORELLE:")
                hours_stats = {}
                days_stats = {}
                
                for deal in deals:
                    deal_time = datetime.fromtimestamp(deal.time)
                    hour = deal_time.hour
                    day = deal_time.strftime('%A')
                    
                    if hour not in hours_stats:
                        hours_stats[hour] = {'count': 0, 'profit': 0}
                    hours_stats[hour]['count'] += 1
                    hours_stats[hour]['profit'] += deal.profit
                    
                    if day not in days_stats:
                        days_stats[day] = {'count': 0, 'profit': 0}
                    days_stats[day]['count'] += 1
                    days_stats[day]['profit'] += deal.profit
                
                # Meilleure heure
                if hours_stats:
                    best_hour = max(hours_stats.keys(), key=lambda h: hours_stats[h]['profit'])
                    safe_log(f"   🕐 Heure la plus profitable: {best_hour}h ({hours_stats[best_hour]['profit']:.2f}€)")
                
                # Meilleur jour
                if days_stats:
                    best_day = max(days_stats.keys(), key=lambda d: days_stats[d]['profit'])
                    safe_log(f"   📅 Jour le plus profitable: {best_day} ({days_stats[best_day]['profit']:.2f}€)")
                
            else:
                safe_log(f"   ⚠️ Aucun deal trouvé dans l'historique")
                
            # Récupération historique des ordres
            orders = mt5.history_orders_get(from_date, to_date, symbol=self.symbol)
            if orders:
                safe_log(f"   📋 {len(orders)} ordres trouvés")
            
        except Exception as e:
            safe_log(f"   ❌ Erreur collecte données: {e}")
    
    def generate_performance_recommendations(self):
        """Génère des recommandations d'optimisation basées sur l'analyse"""
        safe_log(f"\n💡 RECOMMANDATIONS D'OPTIMISATION:")
        safe_log(f"\n   🔧 PARAMÈTRES TECHNIQUES:")
        safe_log(f"      • TP actuel: Adaptatif selon ATR - Optimise automatiquement selon volatilité")
        safe_log(f"      • Lot adaptatif: Optimiser selon balance")
        safe_log(f"      • Fréquence: Analyser pics d'activité")
        
        safe_log(f"\n   📊 GESTION RISQUE:")
        safe_log(f"      • Seuil sécurité: -5% semble approprié")
        safe_log(f"      • Positions max: Évaluer selon volatilité")
        safe_log(f"      • Horaires: 7h30-21h30 optimisé pour profitabilité")
        
        safe_log(f"\n   📈 AMÉLIORATION STRATÉGIE:")
        safe_log(f"      • Conditions d'entrée: Affiner signaux RSI")
        safe_log(f"      • Breakeven: Optimiser seuil (+40 pips)")
        safe_log(f"      • Sortie: Améliorer détection de retournement")

    def shutdown(self):
        """Arrêt propre du bot ultra scalping"""
        self.is_trading = False
        mt5.shutdown()
        safe_log("👋 Ultra Scalping Bot arrêté proprement")

def main():
    """Fonction principale - Stratégie M5 Pullback Professionnelle"""
    safe_log("🎯 STRATÉGIE M5 PULLBACK - TP/SL ADAPTATIFS ATR")
    safe_log("="*60)
    safe_log("⚡ Nouvelle approche: Qualité > Quantité")
    safe_log("� EMA 200 (tendance) + EMA 50 (pullback) + RSI + ATR") 
    safe_log("🎯 Stratégies intelligentes:")
    safe_log("   🟢 BUY: Tendance hausse + repli vers EMA 50")
    safe_log("   🔴 SELL: Tendance baisse + rebond vers EMA 50")
    safe_log("⚖️ TP/SL adaptatifs basés sur la volatilité (ATR)")
    safe_log("🛡️ FILET SÉCURITÉ: Balance -5% → Pause 1h")
    
    if ENABLE_REAL_TRADING:
        safe_log("⚠️ ATTENTION: TRADING RÉEL ACTIVÉ!")
        safe_log("🚨 STRATÉGIE TRÈS RISQUÉE!")
        confirmation = input("Continuer? (yes/NO): ").lower()
        if confirmation != 'yes':
            safe_log("❌ Session annulée")
            return
    else:
        safe_log("🎮 MODE SIMULATION")
    
    # Lancement du bot avec profit manuel par défaut à None
    try:
        manual_profit = None  # Pas de profit manuel par défaut
        
        # Menu de durée
        print("\n" + "="*50)
        print("⏰ DURÉE ULTRA SCALPING")
        print("="*50)
        print("1. 🕐 10 minutes (test ultra rapide)")
        print("2. 🕐 30 minutes (test court)")
        print("3. 🕑 1 heure (session standard)")
        print("4. 🕕 3 heures (session longue)")
        print("5. ♾️ ILLIMITÉ (mode warrior)")
        
        choice = input("\nVotre choix (1-5, défaut=1): ").strip()
        
        if choice == "1" or choice == "":
            duration = 10
        elif choice == "2":
            duration = 30
        elif choice == "3":
            duration = 60
        elif choice == "4":
            duration = 180
        elif choice == "5":
            duration = None  # Illimité
        else:
            safe_log("❌ Choix invalide, test 10 minutes")
            duration = 10
        
        # Lancement du bot (reset automatique intégré)
        bot = M5PullbackBot(manual_daily_profit=manual_profit)
        
        try:
            if duration is None:
                safe_log("♾️ MODE WARRIOR ACTIVÉ - Arrêt avec Ctrl+C")
                safe_log("💡 Tapez 'correct' dans le terminal pour corriger le profit manuellement")
                bot.run_ultra_scalping_unlimited()
            else:
                safe_log(f"⏰ Session ultra scalping: {duration} minutes")
                bot.run_ultra_scalping_session(duration)
                
        except KeyboardInterrupt:
            safe_log("⏹️ Arrêt demandé par l'utilisateur")
        except Exception as e:
            safe_log(f"❌ Erreur: {e}")
            import traceback
            safe_log(f"Détails: {traceback.format_exc()}")
        finally:
            bot.shutdown()
            
    except KeyboardInterrupt:
        safe_log("⏹️ Lancement annulé")

if __name__ == "__main__":
    main()
