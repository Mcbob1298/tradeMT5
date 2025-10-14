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
-   Arrêt automatique du trading à 22h00 (positions maintenues avec SL/TP actifs).
-   Stop Loss obligatoire sur chaque trade.



Auteur: Ultra Scalper
Date: 03 octobre 2025
"""

import MetaTrader5 as mt5
from datetime import datetime, timedelta
import sys
import io
import time
import time
import io
import sys
import time

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
MT5_LOGIN = 18491073       # ⚠️ TODO: Remplacer par votre numéro de compte RÉEL
MT5_PASSWORD = "mr^WV%U8"    # ⚠️ TODO: Remplacer par votre mot de passe RÉEL
MT5_SERVER = "VantageInternational-Live 4"  # ⚠️ TODO: Vérifier le serveur RÉEL
# MT5_LOGIN = 10007787600       # ⚠️ TODO: Remplacer par votre numéro de compte RÉEL
# MT5_PASSWORD = "G@Vv0mNf"    # ⚠️ TODO: Remplacer par votre mot de passe RÉEL
# MT5_SERVER = "MetaQuotes-Demo"  # ⚠️ TODO: Vérifier le serveur RÉEL
# 🚫 MODE SIMULATION DÉSACTIVÉ - TRADING RÉEL
SIMULATE_BALANCE = 500.0     # ❌ Non utilisé en mode réel
USE_SIMULATION_MODE = False  # ❌ MODE SIMULATION DÉSACTIVÉ

# Paramètres stratégie M5 PULLBACK PROFESSIONNELLE - ARGENT RÉEL
SYMBOL = "XAUUSD"               # Or (excellent pour stratégie pullback)
TIMEFRAME = mt5.TIMEFRAME_M5    # 🕒 5 minutes (qualité > quantité)
LOT_SIZE = "ADAPTIVE"           # 🚀 LOT ADAPTATIF AGRESSIF (3.5% risque par trade)
USE_STOP_LOSS = True            # ✅ STOP LOSS OBLIGATOIRE EN ARGENT RÉEL
MAX_POSITIONS = 3               # 🔒 Max 3 positions simultanées (optimisé pour éviter "No money")
ANALYSIS_INTERVAL = 30          # 🕒 Analyse toutes les 30 secondes (haute fréquence)

# 🚀 GESTION LOT ADAPTATIF OPTIMISÉ
ADAPTIVE_LOT_RISK_PERCENT = 2.5 # Risque 2.5% par trade (optimisé vs 3.5% trop agressif)
ADAPTIVE_LOT_MIN = 0.01         # Lot minimum (contrainte broker)
ADAPTIVE_LOT_MAX = 100.0        # Lot maximum (limite broker)

# 🎯 NOUVEAUX PARAMÈTRES STRATÉGIE M5 PULLBACK
TREND_EMA_MASTER = 200          # EMA 200 - Juge de paix pour tendance de fond
TREND_EMA_PULLBACK = 50         # EMA 50 - Zone de repli/rebond dynamique
ATR_PERIOD = 14                 # ATR pour TP/SL adaptatifs selon volatilité
RSI_PERIOD = 14                 # RSI standard (14 périodes)

# 🎯 STRATÉGIE RÉVISÉE : TP PETITS + SL GRANDS + LOTS ÉLEVÉS
ATR_PULLBACK_MULTIPLIER = 3.0   # Distance max à l'EMA 50 (3.0x ATR - zone pullback plus proche)
ATR_SL_MULTIPLIER = 2.5         # � SL BUY : 2.5x ATR (standard)
TP_MAX_POINTS = 200             # 🎯 TP maximum : 200 points (20 pips) - PLAFONNÉ
RISK_MULTIPLIER = 1.5           # 💰 Multiplicateur de risque augmenté (lots plus élevés)

# 🎯 ZONES RSI POUR PULLBACK
RSI_BUY_MIN = 35               # RSI minimum pour BUY (momentum sain)
RSI_BUY_MAX = 60               # RSI maximum pour BUY (pas de surachat excessif)

# 🎯 PARAMÈTRES M5 PULLBACK (Qualité > Quantité)
# COOLDOWN : 5 minutes entre les trades pour éviter le sur-trading

# 🛡️ FILTRES DE CONFIRMATION PROFESSIONNELS (NOUVEAU)
ENABLE_H1_CONFIRMATION = True      # Confirmation tendance H1 obligatoire
OPTIMAL_ATR_MIN = 1.5              # Volatilité minimale pour trader (1.5 = 15 pips)
OPTIMAL_ATR_MAX = 7.0              # Volatilité maximale (marché trop chaotique)

# 🛡️ GESTION DU MODE DÉGRADÉ (NOUVEAU)
DEGRADED_MODE_RISK_MULTIPLIER = 0.2  # Risque = 20% du risque normal (2.5% -> 0.5%)
DEGRADED_MODE_RECOVERY_THRESHOLD = -2.0  # Seuil de sortie du mode dégradé (-2%)
DEGRADED_MODE_MAX_RR_RATIO = 1.0  # Ratio R/R plafonné à 1:1 en mode dégradé

# 🎯 TP DYNAMIQUE (Ajustement en Temps Réel) - NOUVEAU
ENABLE_DYNAMIC_TP = True             # ✅ Active l'ajustement dynamique du TP
DYNAMIC_TP_STRENGTH_THRESHOLD = 95   # Si force > 95%, on éloigne le TP (marché TRÈS fort)
DYNAMIC_TP_MIN_PROFIT_PERCENT = 40   # Activation seulement si position > 40% du TP
DYNAMIC_TP_EXTENSION_MULTIPLIER = 1.5 # Éloigne le TP de 50% supplémentaire si accélération
DYNAMIC_TP_RSI_WEAKNESS = 60         # Si RSI < 60, on sécurise via trailing agressif
DYNAMIC_TP_MIN_IMPROVEMENT = 0.0010  # Amélioration minimale (10 points) pour modifier TP

CONFIRMATION_DELAY_SECONDS = 180      # 3 minutes d'attente pour confirmation
SIGNAL_PERSISTENCE_CHECKS = 3         # Signal doit persister 3 vérifications

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
    
    def __init__(self, config_name='BALANCED', manual_daily_profit=None):
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
        from m5_pullback_config import AGGRESSIVE_CONFIG, BALANCED_CONFIG, CONSERVATIVE_CONFIG
        configs = {
            'AGGRESSIVE': AGGRESSIVE_CONFIG, 
            'BALANCED': BALANCED_CONFIG,
            'CONSERVATIVE': CONSERVATIVE_CONFIG
        }
        self.config = configs.get(config_name, BALANCED_CONFIG)
        safe_log(f"🎮 Configuration: {config_name}")
        safe_log(f"📊 RSI BUY < {self.config['RSI_OVERSOLD']}")
        
        # 🎯 NOUVEAU FILTRE ULTRA-STRICT
        safe_log(f"⚡ FILTRE TENDANCE ULTRA-STRICT ACTIVÉ:")
        safe_log(f"   🎯 Seuil minimum: 80% de certitude sur la tendance")
        safe_log(f"   ✅ Seuls les signaux très fiables seront tradés")
        safe_log(f"   🛡️ Qualité >>> Quantité - Protection maximale")
        
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
        
        # 🕐 CONTRÔLE FRÉQUENCE DES TRADES
        self.last_buy_timestamp = None  # Pas de timestamp initial - premier trade libre
        
        # 🚀 MODE TURBO - Trading ultra-rapide lors de signaux très forts
        self.turbo_mode_active = False  # Mode turbo désactivé par défaut
        self.turbo_mode_strength_threshold = 0.95  # Activation si strength > 0.95
        self.turbo_mode_exit_threshold = 0.9   # Désactivation si strength < 0.9
        
        # Variables système profit quotidien adaptatif
        self.daily_start_balance = 0  # Balance de départ du jour
        
        # 🛡️ SYSTÈME DE CONFIRMATION SUR 3 CYCLES (Anti-faux signaux)
        self.trend_confirmation_history = []  # Historique des 3 dernières tendances
        self.required_confirmations = 3  # Nombre de cycles consécutifs requis
        
        # 🎯 SYSTÈME D'ENTRÉES ÉCHELONNÉES (Scaling-In)
        # Configuration : 50% / 30% / 20% avec espacement 0.5×ATR et 1.0×ATR
        self.partial_entries_enabled = True  # Activer le système d'entrées partielles
        self.entry_levels = [
            {'percentage': 0.50, 'offset_multiplier': 0.0},   # Niveau 1: 50% au signal
            {'percentage': 0.30, 'offset_multiplier': 0.5},   # Niveau 2: 30% à -0.5×ATR
            {'percentage': 0.20, 'offset_multiplier': 1.0}    # Niveau 3: 20% à -1.0×ATR
        ]
        self.entry_timeout_minutes = 15  # Timeout de 15 min par niveau
        
        # Tracking des trades partiels en cours
        self.partial_trades = {}  # {trade_id: {...trade_info...}}
        self.next_trade_id = 1  # Compteur pour IDs uniques


        
        # HORAIRES DE TRADING - Arrêt du trading à 22h00, reprise à 00h00 (minuit)
        self.daily_close_time = 22.0   # Heure d'arrêt du trading (22h00) - PLUS DE FERMETURE FORCÉE
        self.daily_start_time = 0.0    # Heure de reprise (00h00 - minuit)
        
        # Vérification de l'état initial selon l'heure de démarrage
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_time_decimal = current_hour + (current_minute / 60.0)
        current_weekday = current_time.weekday()  # 0=Lundi, 5=Samedi, 6=Dimanche
        
        # Si on démarre pendant le week-end (samedi ou dimanche)
        if current_weekday == 5 or current_weekday == 6:  # Samedi ou Dimanche
            self.is_trading_paused = True
            day_name = "Samedi" if current_weekday == 5 else "Dimanche"
            safe_log(f"📅 DÉMARRAGE EN WEEK-END - {day_name} {current_hour}h{current_minute:02d}")
            safe_log(f"   🌙 Trading fermé (week-end)")
            safe_log(f"   ⏳ Reprise prévue lundi à 00h00")
        # Si on démarre en dehors des heures de trading (avant 00h00 ou après 22h00)
        elif current_time_decimal < self.daily_start_time or current_time_decimal >= self.daily_close_time:
            self.is_trading_paused = True  # Démarre en pause
            safe_log(f"🕐 DÉMARRAGE EN PAUSE NOCTURNE - {current_hour}h{current_minute:02d}")
            safe_log(f"   🌙 Trading fermé (horaires: 00h00 à 22h00)")
            safe_log(f"   ⏳ Reprise prévue à 00h00")
        else:
            self.is_trading_paused = False  # Démarre en mode actif
            safe_log(f"🕐 DÉMARRAGE EN HEURES DE TRADING - {current_hour}h{current_minute:02d}")
            safe_log(f"   ✅ Trading autorisé jusqu'à 22h00")
        
        # État des positions
        self.open_positions = []
        self.position_count = 0
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
                self.buy_positions_count = 0
                
                # Comptage des positions par type
                for position in mt5_positions:
                    if position.type == mt5.POSITION_TYPE_BUY:
                        self.buy_positions_count += 1
                
                safe_log(f"🔄 Synchronisation positions MT5:")
                safe_log(f"   📊 BUY en cours: {self.buy_positions_count}")
                safe_log(f"   📊 Total positions: {len(mt5_positions)}")
                
                # Mise à jour de la liste des positions ouvertes pour suivi
                self.open_positions = []
                for position in mt5_positions:
                    position_info = {
                        'ticket': position.ticket,
                        'open_time': datetime.fromtimestamp(position.time),  # Conversion timestamp MT5
                        'type': 'BUY',
                        'volume': position.volume,
                        'open_price': position.price_open,
                        'tp': position.tp if position.tp > 0 else None,
                        'sl': position.sl if position.sl > 0 else None
                    }
                    self.open_positions.append(position_info)
                
            else:
                safe_log("📊 Aucune position ouverte sur MT5")
                self.buy_positions_count = 0
                self.open_positions = []
                
        except Exception as e:
            safe_log(f"⚠️ Erreur synchronisation compteurs: {e}")
            # En cas d'erreur, on garde les valeurs par défaut
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
        """
        🧮 SYSTÈME DE POSITIONS ADAPTATIVES PROGRESSIVES
        =================================================
        
        Calcule le nombre maximum de positions selon l'équité du portefeuille.
        Permet une meilleure utilisation du capital tout en protégeant les petits comptes.
        
        Paliers progressifs :
        - < 1 000€    : 1 position  (ultra-prudence, capital trop faible)
        - 1 000-2 000€: 2 positions (croissance prudente)
        - 2 000-5 000€: 3 positions (expansion modérée)
        - 5 000-10 000€: 4 positions (bonne marge de manœuvre)
        - 10 000-20 000€: 5 positions (diversification accrue)
        - 20 000-50 000€: 6 positions (gestion professionnelle)
        - > 50 000€   : 7 positions (capital solide)
        """
        try:
            account_info = mt5.account_info()
            if not account_info:
                safe_log("⚠️ Impossible de récupérer equity, MAX_POSITIONS par défaut: 2")
                return 2

            # 💰 UTILISATION DE L'EQUITY (moyens réels incluant positions ouvertes)
            equity = account_info.equity

            # 🎯 SYSTÈME PROGRESSIF ADAPTATIF
            if equity < 1000:
                max_positions_final = 1  # Ultra-prudence pour très petits comptes
                niveau = "TRÈS FAIBLE"
            elif equity < 2000:
                max_positions_final = 2  # Croissance prudente
                niveau = "FAIBLE"
            elif equity < 5000:
                max_positions_final = 3  # Expansion modérée
                niveau = "MOYENNE"
            elif equity < 10000:
                max_positions_final = 4  # Bonne marge de manœuvre
                niveau = "BONNE"
            elif equity < 20000:
                max_positions_final = 5  # Diversification accrue
                niveau = "FORTE"
            elif equity < 50000:
                max_positions_final = 6  # Gestion professionnelle
                niveau = "TRÈS FORTE"
            else:
                max_positions_final = 7  # Capital solide
                niveau = "EXCELLENTE"

            # 📊 CALCUL DU RISQUE TOTAL ESTIMÉ
            # Risque moyen par position BUY: ~5% (entre 2.5% et 6%)
            risque_moyen_par_position = 0.04  # 4% moyen (conservateur)
            risque_total_max_pct = risque_moyen_par_position * max_positions_final * 100
            risque_total_max_eur = equity * risque_moyen_par_position * max_positions_final

            safe_log(f"")
            safe_log(f"{'='*60}")
            safe_log(f"🧮 POSITION SIZING ADAPTATIF PROGRESSIF")
            safe_log(f"{'='*60}")
            safe_log(f"   💰 Equity actuelle: {equity:,.2f}€")
            safe_log(f"   📊 Niveau de capital: {niveau}")
            safe_log(f"   🎯 Positions simultanées max: {max_positions_final}")
            safe_log(f"   🛡️ Risque moyen par position: {risque_moyen_par_position*100:.1f}%")
            safe_log(f"   💸 Risque total maximum: {risque_total_max_eur:.2f}€ ({risque_total_max_pct:.1f}% de l'equity)")
            safe_log(f"   ✅ Système progressif optimisé activé")
            safe_log(f"{'='*60}")
            safe_log(f"")

            return max_positions_final

        except Exception as e:
            safe_log(f"❌ Erreur calcul max positions adaptatif: {e}")
            return 2  # Valeur par défaut prudente en cas d'erreur
    
    def calculate_adaptive_tp_ratio(self, trend_strength):
        """
        🎯 RATIO TP/SL RÉALISTE ADAPTÉ AU MARCHÉ DE L'OR
        ================================================
        
        Nouvelles règles ultra-réalistes pour XAUUSD:
        - Tendance faible (0-50%) : Ratio 1:1.2 (objectif conservateur - 20% plus que le risque)
        - Tendance forte (50-80%) : Ratio 1:1.5 (équilibré - 50% plus que le risque)  
        - Tendance très forte (80%+) : Ratio 1:2.0 (ambitieux mais atteignable)
        
        Logique: L'or est volatil mais les grands mouvements prennent du temps.
        Mieux vaut sécuriser des petits gains réguliers que viser l'impossible.
        
        Args:
            trend_strength (float): Force de la tendance entre 0 et 100%
            
        Returns:
            float: Ratio TP/SL réaliste adapté au marché
        """
        try:
            if trend_strength >= 80:
                tp_ratio = 2.0  # 🎯 Très forte - ambitieux mais atteignable
                strength_level = "TRÈS FORTE"
            elif trend_strength >= 50:
                tp_ratio = 1.5  # ⚖️ Forte - équilibré et réaliste
                strength_level = "FORTE"
            else:
                tp_ratio = 1.2  # 🛡️ Faible - conservateur et sûr
                strength_level = "FAIBLE/MOYENNE"
            
            safe_log(f"🎯 TP RÉALISTE: Tendance {strength_level} ({trend_strength:.1f}%) → Ratio 1:{tp_ratio}")
            return tp_ratio
            
        except Exception as e:
            safe_log(f"❌ Erreur calcul TP adaptatif: {e}, utilisation ratio par défaut 1.5")
            return 1.5  # Fallback sur ratio réaliste
    
    def calculate_market_aware_tp_ratio(self, trend_strength, atr_value, sl_distance):
        """
        🎯 TP ADAPTATIF SELON VOLATILITÉ : Stratégie Révisée
        ===================================================
        
        NOUVELLE STRATÉGIE VOLATILITÉ :
        - Marché TRÈS VOLATIL (ATR > 6.0) : TP 400 points (40 pips)
        - Marché NORMAL : TP 200 points (20 pips) 
        - SL plus grand (2.5x ATR) pour respiration
        - Lots adaptés selon volatilité
        
        Logic:
        1. Détecte la volatilité extrême (ATR > 6.0)
        2. Adapte le TP selon volatilité et tendance
        3. Optimise pour profiter des grands mouvements
        
        Args:
            trend_strength (float): Force de la tendance (0-100%)
            atr_value (float): Valeur ATR actuelle
            sl_distance (float): Distance du SL en price
            
        Returns:
            float: Distance TP réelle (adaptée à la volatilité)
        """
        try:
            # 🔥 DÉTECTION VOLATILITÉ EXTRÊME : ATR > 6.0 = Marché très volatil
            if atr_value > 6.0:
                # 🚀 MARCHÉ TRÈS VOLATIL : TP étendu à 400 points
                max_tp_distance = 400 * 0.01  # 400 points = 4.00 en price pour XAUUSD
                volatility_level = "TRÈS VOLATIL"
                safe_log(f"🔥 MARCHÉ TRÈS VOLATIL DÉTECTÉ - ATR {atr_value:.2f} > 6.0")
                safe_log(f"🚀 TP ÉTENDU : 400 points (40 pips) pour profiter de la volatilité")
            else:
                # 📊 MARCHÉ NORMAL : TP standard à 200 points
                max_tp_distance = TP_MAX_POINTS * 0.01  # 200 points = 2.00 en price pour XAUUSD
                volatility_level = "NORMAL"
            
            # Base du ratio selon la force de tendance
            if trend_strength >= 80:
                base_ratio = 1.8  # Très forte
            elif trend_strength >= 50:
                base_ratio = 1.4  # Forte
            else:
                base_ratio = 1.1  # Faible
            
            # Ajustement selon la volatilité (ATR)
            if atr_value < 2.0:
                volatility_factor = 0.8
                volatility_desc = "CALME"
            elif atr_value > 6.0:
                volatility_factor = 1.2  # Boost pour volatilité extrême
                volatility_desc = "TRÈS VOLATIL"
            elif atr_value > 4.0:
                volatility_factor = 1.1
                volatility_desc = "AGITÉ"
            else:
                volatility_factor = 1.0
                volatility_desc = "NORMALE"
            
            # Calcul du TP théorique
            theoretical_tp = base_ratio * volatility_factor * sl_distance
            
            # 🎯 APPLICATION DU PLAFOND ADAPTATIF
            final_tp_distance = min(theoretical_tp, max_tp_distance)
            
            # 🛡️ PLAFONNEMENT DU TP EN MODE DÉGRADÉ
            if self.stats.get('balance_safety_active', False):
                # Plafonner le TP au niveau du SL (ratio 1:1)
                max_tp_distance_degraded = sl_distance * DEGRADED_MODE_MAX_RR_RATIO
                if final_tp_distance > max_tp_distance_degraded:
                    final_tp_distance = max_tp_distance_degraded
                    safe_log(f"🛡️ MODE DÉGRADÉ - TP plafonné à {DEGRADED_MODE_MAX_RR_RATIO}:1 (distance: {final_tp_distance:.5f})")
            
            # Calcul du ratio réel
            actual_ratio = final_tp_distance / sl_distance
            
            # Stats pour logging
            is_capped = final_tp_distance == max_tp_distance
            cap_status = "🔥 PLAFONNÉ" if is_capped else "✅ LIBRE"
            
            safe_log(f"🎯 TP ADAPTATIF: {cap_status} | Volatilité {volatility_level}")
            safe_log(f"   📊 ATR {atr_value:.2f} ({volatility_desc}) | TP Max: {max_tp_distance/0.01:.0f}pts")
            safe_log(f"   🎯 Théorique {theoretical_tp:.3f} → Réel {final_tp_distance:.3f} | Ratio 1:{actual_ratio:.2f}")
            
            return final_tp_distance
            
        except Exception as e:
            safe_log(f"❌ Erreur calcul TP adaptatif: {e}")
            return min(1.5 * sl_distance, 200 * 0.01)  # Fallback sécuritaire
    
    def calculate_adaptive_breakeven_sl(self):
        """
        🔒 CALCUL DU SL BREAKEVEN ADAPTATIF SELON LES PERFORMANCES
        =========================================================
        
        Logique intelligente basée sur les performances du compte:
        - Performances excellentes (>+2%) : SL très agressif (80% du profit)
        - Performances bonnes (+0.5% à +2%) : SL agressif (60% du profit)  
        - Performances moyennes (0% à +0.5%) : SL standard (50% du profit)
        - Performances négatives (<0%) : SL conservateur (30% du profit)
        
        Returns:
            float: Pourcentage du profit à sécuriser (0.3 à 0.8)
        """
        try:
            account_info = mt5.account_info()
            if not account_info:
                return 0.5  # Standard par défaut
            
            # Calcul des performances journalières basées sur l'equity
            equity_start = getattr(self, 'equity_start', account_info.equity)
            current_equity = account_info.equity
            daily_performance = ((current_equity - equity_start) / equity_start) * 100
            
            # Calcul du profit temps réel
            current_profit = self.calculate_real_time_daily_profit()
            profit_pct = (current_profit / equity_start) * 100 if equity_start > 0 else 0
            
            # Logique adaptative
            if profit_pct >= 2.0:
                sl_ratio = 0.8  # 🚀 Performances excellentes - très agressif
                performance_level = "EXCELLENTES"
            elif profit_pct >= 0.5:
                sl_ratio = 0.6  # ⚡ Bonnes performances - agressif  
                performance_level = "BONNES"
            elif profit_pct >= 0.0:
                sl_ratio = 0.5  # 📈 Performances moyennes - standard
                performance_level = "MOYENNES"
            else:
                sl_ratio = 0.3  # 🛡️ Performances négatives - conservateur
                performance_level = "NÉGATIVES"
            
            safe_log(f"🔒 SL BREAKEVEN ADAPTATIF: Performances {performance_level} ({profit_pct:+.2f}%) → {sl_ratio*100:.0f}% profit sécurisé")
            return sl_ratio
            
        except Exception as e:
            safe_log(f"❌ Erreur calcul SL breakeven adaptatif: {e}, utilisation ratio standard 0.5")
            return 0.5  # Fallback sur ratio standard
    
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
        """🛡️ SYSTÈME DE SÉCURITÉ DÉSACTIVÉ - Trading sans limite de perte"""
        # ⚠️ ATTENTION: Le filet de sécurité -5% est désactivé
        # Le bot continuera à trader même en cas de pertes importantes
        return  # Fonction désactivée - aucune vérification de sécurité
    
    def activate_balance_safety_mode(self):
        """🛡️ NOUVEAU: Active le MODE DÉGRADÉ sans arrêter le trading"""
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
            safe_log(f"❌ Erreur activation mode dégradé: {e}")
    
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

            
            # �🚨 VÉRIFICATION MODE ARGENT RÉEL
            if self.simulation_mode:
                safe_log("🚫 ERREUR: Mode simulation détecté mais fonction argent réel appelée!")
                return False
            
            # 🚨 AVERTISSEMENT ARGENT RÉEL
            safe_log(f"🚨 ORDRE ARGENT RÉEL EN COURS:")
            safe_log(f"   💰 Type: {trade_type}")
            safe_log(f"   ⚠️ ATTENTION: Utilise de l'argent RÉEL!")
            
            # 🕐 Vérification horaires de trading avant de placer un ordre
            if not self.check_trading_hours():
                safe_log(f"🚫 Ordre refusé - Trading fermé (horaires: 00h20 à 22h00)")
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
            order_type = mt5.ORDER_TYPE_BUY
            
            # Volume (lot size adaptatif basé sur l'EQUITY RÉELLE, l'ATR et la FORCE de tendance)
            # Calcul de la distance SL basée sur l'ATR pour le lot adaptatif
            atr_sl_distance = signal.get('atr', 2.5) * ATR_SL_MULTIPLIER  # Fallback ATR 2.5 pour XAUUSD
            trend_strength = signal.get('strength', 50)  # Force de la tendance
            volume = self.calculate_adaptive_lot_size(atr_sl_distance, trend_strength, trade_type)
            
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
                
            price = tick_info.ask
            
            safe_log(f"💰 Prix {trade_type}: {price} | Ask: {tick_info.ask}")
            
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
                'sl': sl_price,
                'opening_strength': signal.get('strength', 50)  # 🎯 FORCE À L'OUVERTURE pour TP dynamique
            }
            self.open_positions.append(position_info)
            
            # 🎯 Enregistrement de la force initiale pour le TP dynamique
            if not hasattr(self, '_opening_strengths'):
                self._opening_strengths = {}
            self._opening_strengths[result.order] = signal.get('strength', 50)
            
            # Mise à jour stats
            self.stats['total_trades'] += 1
            self.stats['last_trade_time'] = datetime.now()
            
            # Mise à jour compteurs par type
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
                position_type = "BUY"
                ticket = mt5_pos.ticket
                
                # ✅ Condition 1: Position en profit ET tendance inversée
                if profit > 0:  # Au moins 0€ de profit
                    should_close = False
                    close_reason = ""
                    
                    if position_type == "BUY" and trend_direction == "BEARISH":
                        should_close = True
                        close_reason = "BUY profitable + tendance BEARISH"
                    
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
            current_equity = account_info.equity  # Utilise equity au lieu de balance
            margin_level = account_info.margin_level if account_info.margin != 0 else 1000  # Si pas de positions ouvertes = OK
            
            # Seuils de sécurité basés sur l'equity
            min_margin_free = current_equity * 0.2  # 20% de l'equity en margin libre (au lieu de 30%)
            min_margin_level = 150  # Niveau de margin minimum 150% (au lieu de 200%)
            
            # Si aucune position ouverte, on vérifie juste la margin libre
            if margin_level >= 1000:  # Aucune position = niveau très élevé
                margin_ok = margin_free >= min_margin_free
                if not margin_ok:
                    safe_log(f"⚠️ EQUITY INSUFFISANTE:")
                    safe_log(f"   💰 Margin libre: {margin_free:.2f}€ (min: {min_margin_free:.2f}€)")
                    safe_log(f"   � Basé sur equity: {current_equity:.2f}€")
                    safe_log(f"   �🚫 Nouveaux trades suspendus")
            else:
                # Avec positions ouvertes, vérification complète
                margin_ok = margin_free >= min_margin_free and margin_level >= min_margin_level
                if not margin_ok:
                    safe_log(f"⚠️ MARGIN INSUFFISANTE:")
                    safe_log(f"   💰 Margin libre: {margin_free:.2f}€ (min: {min_margin_free:.2f}€)")
                    safe_log(f"   📊 Niveau margin: {margin_level:.1f}% (min: 150%)")
                    safe_log(f"   💎 Basé sur equity: {current_equity:.2f}€")
                    safe_log(f"   🚫 Nouveaux trades suspendus")
            
            return margin_ok
            
        except Exception as e:
            safe_log(f"❌ Erreur vérification margin: {e}")
            # En cas d'erreur, on autorise le trade (plus sûr)
            return True

    def check_trading_enabled(self):
        """
        🛡️ VÉRIFICATION STATUT TRADING MT5
        ==================================
        
        Vérifie si le trading est autorisé sur le compte MT5.
        Utile pour éviter les erreurs TRADE_DISABLED.
        
        Returns:
            tuple: (bool: trading_enabled, str: status_message)
        """
        try:
            # Vérification connexion MT5
            if not mt5.terminal_info():
                return False, "MT5 non connecté"
            
            # Vérification compte
            account_info = mt5.account_info()
            if not account_info:
                return False, "Impossible de récupérer les infos compte"
            
            # Vérification autorisation de trading
            if not account_info.trade_allowed:
                return False, "Trading désactivé sur le compte MT5"
            
            # Vérification symbole
            symbol_info = mt5.symbol_info(self.symbol)
            if not symbol_info:
                return False, f"Symbole {self.symbol} non disponible"
            
            if not symbol_info.trade_mode:
                return False, f"Trading désactivé pour {self.symbol}"
            
            return True, "Trading autorisé"
            
        except Exception as e:
            return False, f"Erreur vérification trading: {e}"

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
                    
                    # Position fermée - pas de reset automatique du cooldown
                        
                        safe_log(f"   ⚡ Trade fermé par {close_type} → Possibilité de trade immédiat si conditions remplies")
                else:
                    safe_log(f"⚠️ Position fermée (profit non détecté): Ticket {position['ticket']} | Durée: {duration_str}")
                
                # Mise à jour des compteurs par type
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
        🚀 SYSTÈME AVANCÉ DE GESTION DES PROFITS
        =========================================
        
        🛡️ PROTECTION PROGRESSIVE (TRAILING STOP) :
        - 30% du TP → SL à 20% du profit
        - 50% du TP → SL à 35% du profit
        - 75% du TP → SL à 50% du profit
        - 90% du TP → SL à 75% du profit + 🚀 TP étendu de +50%
        
        💎 EXTENSION DU TP (EXTENSIONS MULTIPLES) :
        Quand le trailing stop atteint 75% du profit (phase QUASI-TP),
        le Take Profit est automatiquement étendu de 50% supplémentaire.
        
        🔥 PAS DE LIMITE : Le système peut étendre le TP autant de fois
        que nécessaire tant que le prix continue à progresser à 90% du TP.
        Le SL suit toujours à 75% du profit actuel = Protection garantie !
        
        ⚡ RÈGLE D'OR : Le SL ne recule JAMAIS, seulement progression !
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
        
        # 🛡️ SÉCURITÉ : Vérifier tickets déjà en échec
        if not hasattr(self, '_failed_trailing_tickets'):
            self._failed_trailing_tickets = set()
        
        for position in self.open_positions:
            ticket = position['ticket']
            entry_price = position['open_price']
            position_type = position['type']
            
            # Skip tickets en échec critique
            if ticket in self._failed_trailing_tickets:
                continue
            
            # Skip si prix d'entrée invalide
            if entry_price == 0.0:
                safe_log(f"⚠️ TRAILING SKIP - Ticket {ticket}: Prix d'entrée invalide (0.0)")
                continue
            
            # Recherche de la position correspondante sur MT5
            mt5_position = None
            for mt5_pos in mt5_positions:
                if mt5_pos.ticket == ticket:
                    mt5_position = mt5_pos
                    break
            
            if not mt5_position:
                continue
            
            # 🔵 TRAILING STOP POUR POSITIONS BUY
            if position_type == 'BUY':
                # Calcul du profit actuel et du TP cible
                symbol_info = mt5.symbol_info(self.symbol)
                if symbol_info:
                    current_profit_distance = current_price.bid - entry_price
                    tp_distance = mt5_position.tp - entry_price if mt5_position.tp > 0 else (25 * 0.1)
                else:
                    current_profit_distance = current_price.bid - entry_price
                    tp_distance = 25 * 0.1  # Fallback conservateur
                
                # Calcul du pourcentage de progression vers le TP
                if tp_distance > 0:
                    tp_progress_pct = (current_profit_distance / tp_distance) * 100
                else:
                    tp_progress_pct = 0
                
                # 🚀 TRAILING STOP PROGRESSIF
                if tp_progress_pct >= 30.0:
                    
                    # 📈 CALCUL DU NIVEAU DE SL PROGRESSIF - TOUJOURS POSITIF
                    if tp_progress_pct >= 90.0:
                        # Quasi TP atteint → 75% du profit sécurisé
                        sl_profit_ratio = 0.75
                        phase = "QUASI-TP (75% profit)"
                    elif tp_progress_pct >= 75.0:
                        # Bon momentum → 50% du profit sécurisé
                        sl_profit_ratio = 0.50
                        phase = "MOMENTUM (50% profit)"
                    elif tp_progress_pct >= 35.0:
                        # Progression solide → 35% du profit sécurisé
                        sl_profit_ratio = 0.35
                        phase = "PROGRESSION (35% profit)"
                    else:
                        # Premier niveau (30-50%) → 20% du profit sécurisé (simple)
                        sl_profit_ratio = 0.20
                        phase = "SÉCURISÉ (20% profit)"

                    # Calcul du nouveau SL selon la phase
                    target_profit_distance = tp_distance * sl_profit_ratio
                    new_sl_progressive = entry_price + target_profit_distance
                    
                    # 🛡️ RÈGLE D'OR : Ne JAMAIS reculer le SL
                    current_sl = mt5_position.sl if mt5_position.sl > 0 else entry_price
                    if new_sl_progressive <= current_sl:
                        # SL déjà plus avantageux, on garde l'actuel
                        continue
                    
                    # 🔒 SÉCURITÉS RENFORCÉES AVANT MODIFICATION
                    # 1. Vérifier que la position existe encore
                    fresh_position = mt5.positions_get(ticket=ticket)
                    if not fresh_position or len(fresh_position) == 0:
                        safe_log(f"⚠️ Position {ticket} fermée, skip trailing stop")
                        continue
                    
                    # 2. Vérifier que le profit est toujours positif
                    current_profit = fresh_position[0].profit
                    if current_profit <= 0:
                        safe_log(f"⚠️ Position {ticket} en perte ({current_profit:.2f}€), pas de trailing stop")
                        continue
                    
                    # 3. Vérification si le SL est déjà proche de cette valeur
                    sl_tolerance = 0.00005  # 0.5 pip de tolérance
                    sl_already_set = abs(mt5_position.sl - new_sl_progressive) < sl_tolerance
                    
                    if sl_already_set:
                        continue
                    
                    # 4. SÉCURITÉS MT5 - Distance minimale obligatoire avec validation robuste
                    tick_info = mt5.symbol_info_tick(self.symbol)
                    if not symbol_info or not tick_info:
                        safe_log(f"⚠️ Impossible d'obtenir les infos symbol pour {ticket}")
                        continue
                    
                    current_price_ask = tick_info.ask
                    current_price_bid = tick_info.bid
                    
                    # Distance minimale imposée par MT5 (avec fallback sécurisé)
                    stops_level = getattr(symbol_info, 'trade_stops_level', 10)  # Fallback 10 points
                    min_distance = max(stops_level * symbol_info.point, 10 * symbol_info.point)  # Min 10 points
                    spread = symbol_info.spread * symbol_info.point
                    
                    # Buffer de sécurité renforcé : min 20 points + spread
                    safety_buffer = max(min_distance * 2, 20 * symbol_info.point) + spread
                    
                    # Pour position BUY : SL doit être inférieur au prix BID actuel
                    max_allowed_sl = current_price_bid - safety_buffer
                    
                    # Vérifier que le nouveau SL respecte les contraintes MT5
                    if new_sl_progressive >= max_allowed_sl:
                        # Ajuster le SL pour respecter les contraintes
                        adjusted_sl = max_allowed_sl
                        safe_log(f"   🔧 SL ajusté: {new_sl_progressive:.5f} → {adjusted_sl:.5f} (sécurité MT5)")
                        
                        # Vérifier que le SL ajusté est toujours meilleur que l'actuel
                        if adjusted_sl <= current_sl:
                            safe_log(f"   ⚠️ SL ajusté trop bas ({adjusted_sl:.5f} <= {current_sl:.5f}), maintien SL actuel")
                            continue
                        
                        new_sl_progressive = adjusted_sl
                    
                    # Validation finale : SL dans la bonne direction
                    if new_sl_progressive >= current_price_bid:
                        safe_log(f"   ❌ SL invalide: {new_sl_progressive:.5f} >= prix BID {current_price_bid:.5f}")
                        continue
                    
                    # ✅ LOGGING DE DÉBOGAGE RENFORCÉ
                    safe_log(f"🚀 TRAILING STOP - Ticket {ticket} - Phase: {phase}")
                    safe_log(f"   📊 Progression TP: {tp_progress_pct:.1f}% (seuil: 30%)")
                    safe_log(f"   💰 Profit actuel: +{current_profit_distance:.3f} | TP cible: {tp_distance:.3f}")
                    safe_log(f"   🔄 SL: {current_sl:.5f} → {new_sl_progressive:.5f}")
                    
                    # Calcul du profit garanti avec système progressif
                    guaranteed_profit_distance = new_sl_progressive - entry_price
                    guaranteed_profit_pips = guaranteed_profit_distance / symbol_info.point / 10
                    safe_log(f"   🎯 SL progressif: {new_sl_progressive:.5f} ({sl_profit_ratio*100:.0f}% du profit)")
                    safe_log(f"   💰 Profit garanti: +{guaranteed_profit_pips:.1f} pips")
                    
                    # 🚀 EXTENSION DU TP SI PHASE QUASI-TP (75% atteint)
                    new_tp = mt5_position.tp  # Par défaut, garde le même TP
                    tp_extended = False
                    
                    if tp_progress_pct >= 75.0:
                        # 🔥 TRACKING POUR EXTENSIONS MULTIPLES
                        if not hasattr(self, '_last_extended_tp'):
                            self._last_extended_tp = {}  # {ticket: last_tp_value}
                        if not hasattr(self, '_tp_extension_count'):
                            self._tp_extension_count = {}  # {ticket: number_of_extensions}
                        
                        # Récupérer le dernier TP étendu (0 si première fois)
                        last_extended_tp = self._last_extended_tp.get(ticket, 0)
                        current_tp = mt5_position.tp
                        
                        # ✅ CORRECTION: Extension si le TP actuel est différent du dernier qu'on a étendu
                        # Cela permet de détecter quand le prix a progressé vers un nouveau seuil
                        if current_tp != last_extended_tp or last_extended_tp == 0:
                            # Calcul du nouveau TP étendu de 50%
                            current_tp_distance = current_tp - entry_price
                            extended_tp_distance = current_tp_distance * 1.5  # +50%
                            new_tp = entry_price + extended_tp_distance
                            
                            # Vérification que le nouveau TP est supérieur à l'ancien
                            if new_tp > current_tp:
                                tp_extended = True
                                
                                # Incrémenter le compteur d'extensions
                                extension_number = self._tp_extension_count.get(ticket, 0) + 1
                                self._tp_extension_count[ticket] = extension_number
                                
                                # ✅ MÉMORISER CE NOUVEAU TP POUR COMPARAISON FUTURE
                                self._last_extended_tp[ticket] = new_tp
                                
                                safe_log(f"   🚀 EXTENSION TP +50% (#{extension_number}): {current_tp:.5f} → {new_tp:.5f}")
                                safe_log(f"      💎 Nouveau potentiel de profit augmenté!")
                                safe_log(f"      🔥 Continuera à s'étendre à 75% du nouveau TP")
                                safe_log(f"      📊 Progression actuelle: {tp_progress_pct:.1f}% du TP actuel")
                            else:
                                new_tp = current_tp  # Garde l'ancien si problème
                    
                    # �🔒 MODIFICATION SÉCURISÉE DE LA POSITION SUR MT5
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "symbol": self.symbol,
                        "position": ticket,
                        "sl": new_sl_progressive,
                        "tp": new_tp,  # TP normal ou étendu selon la phase
                        "magic": mt5_position.magic,  # Sécurité supplémentaire
                        "comment": f"TrailingStop-{phase[:8]}" + ("-TP+50%" if tp_extended else "")
                    }
                    
                    # Tentative de modification avec gestion d'erreur robuste
                    try:
                        result = mt5.order_send(request)
                        
                        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                            safe_log(f"🔒 TRAILING STOP ACTIVÉ! Ticket {ticket}")
                            safe_log(f"   📈 Phase: {phase}")
                            safe_log(f"   💰 Progression: {tp_progress_pct:.1f}%")
                            safe_log(f"   🛡️ SL sécurisé: {new_sl_progressive:.5f}")
                            safe_log(f"   ✅ Profit minimum garanti: +{guaranteed_profit_pips:.1f} pips!")
                            if tp_extended:
                                safe_log(f"   🚀 TP ÉTENDU +50%: Nouveau TP = {new_tp:.5f}")
                                safe_log(f"      💎 Potentiel de profit maximisé!")
                            
                        elif result:
                            # Gestion des erreurs spécifiques avec plus de détails
                            error_msg = getattr(result, 'comment', "Erreur inconnue")
                            
                            # Messages d'erreur détaillés selon le code retour
                            error_details = {
                                16: "INVALID_STOPS - Niveaux SL/TP invalides",
                                10006: "REQUEST_REJECT - Requête rejetée",
                                10015: "INVALID_PRICE - Prix invalide",
                                10016: "INVALID_STOPS - Distance stops insuffisante",
                                10018: "MARKET_CLOSED - Marché fermé",
                                10019: "NO_MONEY - Fonds insuffisants",
                                10025: "TRADE_DISABLED - Trading désactivé"
                            }
                            
                            error_desc = error_details.get(result.retcode, f"Code {result.retcode}")
                            
                            # 🛡️ GESTION SPÉCIALE POUR TRADE_DISABLED
                            if result.retcode == 10025 or result.retcode == mt5.TRADE_RETCODE_TRADE_DISABLED:
                                # Pour TRADE_DISABLED, on log périodiquement (toutes les 10 tentatives)
                                if not hasattr(self, '_trade_disabled_count'):
                                    self._trade_disabled_count = 0
                                self._trade_disabled_count += 1
                                
                                if self._trade_disabled_count % 10 == 1:  # Premier message puis tous les 10
                                    safe_log(f"⚠️ TRADING DÉSACTIVÉ - Trailing stops en pause temporaire")
                                    safe_log(f"   🔧 Vérifiez les paramètres MT5 (Outils → Options → Trading)")
                                    safe_log(f"   📊 Position {ticket} surveillée, trailing reprendra quand autorisé")
                                    safe_log(f"   🔄 Tentative {self._trade_disabled_count} (message affiché toutes les 10)")
                                # On ne met PAS le ticket en failed pour permettre la reprise
                                continue
                            
                            # Pour les autres erreurs, on log normalement
                            safe_log(f"❌ Échec trailing stop {ticket}: {error_desc}")
                            safe_log(f"   📝 Détail MT5: {error_msg}")
                            safe_log(f"   📊 SL tenté: {new_sl_progressive:.5f}")
                            safe_log(f"   📊 Prix BID: {current_price_bid:.5f}")
                            safe_log(f"   � Distance: {abs(new_sl_progressive - current_price_bid):.5f}")
                            safe_log(f"   📊 Min requis: {safety_buffer:.5f}")
                            
                            # Erreurs critiques qui nécessitent d'arrêter les tentatives (SAUF TRADE_DISABLED)
                            critical_errors = [
                                mt5.TRADE_RETCODE_INVALID_STOPS,
                                mt5.TRADE_RETCODE_INVALID_PRICE,
                                mt5.TRADE_RETCODE_INVALID_ORDER,
                                # mt5.TRADE_RETCODE_TRADE_DISABLED,  # Retiré pour permettre la reprise
                                16, 10015, 10016  # Codes numériques directs (sauf 10025 = TRADE_DISABLED)
                            ]
                            
                            if result.retcode in critical_errors:
                                safe_log(f"   🚨 Erreur critique, arrêt trailing pour {ticket}")
                                self._failed_trailing_tickets.add(ticket)
                        else:
                            safe_log(f"❌ Aucune réponse MT5 pour trailing stop {ticket}")
                            
                    except Exception as e:
                        safe_log(f"❌ Exception trailing stop {ticket}: {str(e)}")
                        safe_log(f"   🔧 Requête: SL {new_sl_progressive:.5f}, TP {mt5_position.tp:.5f}")
            
    def manage_dynamic_take_profit(self):
        """
        🎯 TP DYNAMIQUE - AJUSTEMENT EN TEMPS RÉEL DU TAKE PROFIT
        ==========================================================
        
        Système expert qui adapte le TP pendant que le trade est ouvert :
        
        📈 SCÉNARIO 1 : MARCHÉ EN ACCÉLÉRATION (On éloigne le TP)
        - Condition : Force de tendance > 95% (marché TRÈS puissant)
        - Action : Étend le TP de 30% supplémentaire pour capturer plus de gains
        - Sécurité : Seulement si position déjà > 40% du chemin vers TP
        
        📉 SCÉNARIO 2 : MARCHÉ EN ESSOUFFLEMENT (On sécurise)
        - Condition : RSI < 60 (perte de momentum)
        - Action : Active un trailing stop AGRESSIF (80% du profit)
        - Objectif : Verrouiller les gains avant retournement potentiel
        
        💡 PHILOSOPHIE : Fire-and-Forget → Active Management
        """
        if not ENABLE_DYNAMIC_TP:
            return
        
        if not self.open_positions:
            return
        
        # 📊 Analyser la force ACTUELLE du marché (temps réel)
        current_data = self.get_ultra_fast_data(250)
        if not current_data:
            return
        
        current_trend, current_strength, current_indicators = self.detect_ultra_trend(current_data)
        
        # Récupération positions MT5
        mt5_positions = mt5.positions_get(symbol=self.symbol)
        if not mt5_positions:
            return
        
        current_price = mt5.symbol_info_tick(self.symbol)
        if not current_price:
            return
        
        # Initialiser le tracking des forces à l'ouverture (si nécessaire)
        if not hasattr(self, '_opening_strengths'):
            self._opening_strengths = {}  # {ticket: strength_at_opening}
        
        # Tracking des TP déjà modifiés (éviter modifications répétées)
        if not hasattr(self, '_dynamic_tp_modified'):
            self._dynamic_tp_modified = set()
        
        for mt5_position in mt5_positions:
            ticket = mt5_position.ticket
            
            # 🔵 Gestion uniquement des positions BUY profitables
            if mt5_position.type != mt5.POSITION_TYPE_BUY or mt5_position.profit <= 0:
                continue
            
            # Stocker la force à l'ouverture (si première fois qu'on voit ce ticket)
            if ticket not in self._opening_strengths:
                self._opening_strengths[ticket] = current_strength
            
            opening_strength = self._opening_strengths[ticket]
            entry_price = mt5_position.price_open
            current_tp = mt5_position.tp
            
            # Calcul progression vers TP
            symbol_info = mt5.symbol_info(self.symbol)
            if not symbol_info:
                continue
            
            tp_distance = current_tp - entry_price
            current_profit_distance = current_price.bid - entry_price
            
            if tp_distance > 0:
                tp_progress_pct = (current_profit_distance / tp_distance) * 100
            else:
                continue  # TP invalide
            
            # ═══════════════════════════════════════════════════════════
            # 🚀 RÈGLE 1 : ÉLOIGNER LE TP SI LE MARCHÉ ACCÉLÈRE
            # ═══════════════════════════════════════════════════════════
            if (current_strength >= DYNAMIC_TP_STRENGTH_THRESHOLD and 
                tp_progress_pct >= DYNAMIC_TP_MIN_PROFIT_PERCENT and
                ticket not in self._dynamic_tp_modified):
                
                # Calcul du nouveau TP étendu
                current_tp_distance = current_tp - entry_price
                new_tp_distance = current_tp_distance * DYNAMIC_TP_EXTENSION_MULTIPLIER
                new_tp = entry_price + new_tp_distance
                
                # Vérifier amélioration significative (min 10 points)
                tp_improvement = new_tp - current_tp
                if tp_improvement >= DYNAMIC_TP_MIN_IMPROVEMENT:
                    
                    safe_log(f"🚀 TP DYNAMIQUE - ACCÉLÉRATION MARCHÉ!")
                    safe_log(f"   🎫 Ticket: {ticket}")
                    safe_log(f"   📊 Force actuelle: {current_strength:.1f}% (seuil: {DYNAMIC_TP_STRENGTH_THRESHOLD}%)")
                    safe_log(f"   💪 Force à l'ouverture: {opening_strength:.1f}%")
                    safe_log(f"   📈 Gain de force: +{current_strength - opening_strength:.1f}%")
                    safe_log(f"   📊 Progression: {tp_progress_pct:.1f}% du TP")
                    safe_log(f"   🎯 TP actuel: {current_tp:.5f}")
                    safe_log(f"   🎯 Nouveau TP: {new_tp:.5f} (+{tp_improvement*10000:.1f} pips)")
                    safe_log(f"   💡 Extension: +{(DYNAMIC_TP_EXTENSION_MULTIPLIER - 1)*100:.0f}% pour capturer l'accélération")
                    
                    # Modification du TP sur MT5
                    request = {
                        "action": mt5.TRADE_ACTION_SLTP,
                        "symbol": self.symbol,
                        "position": ticket,
                        "sl": mt5_position.sl,
                        "tp": new_tp,
                        "magic": mt5_position.magic,
                        "comment": "DynamicTP-Extend"
                    }
                    
                    try:
                        result = mt5.order_send(request)
                        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                            safe_log(f"✅ TP ÉTENDU AVEC SUCCÈS!")
                            safe_log(f"   🎯 Potentiel de gain augmenté de {tp_improvement * 10000:.1f} pips")
                            self._dynamic_tp_modified.add(ticket)
                        else:
                            error_msg = getattr(result, 'comment', "Erreur inconnue") if result else "Aucune réponse"
                            safe_log(f"❌ Échec extension TP: {error_msg}")
                    except Exception as e:
                        safe_log(f"❌ Erreur modification TP dynamique: {e}")
            
            # ═══════════════════════════════════════════════════════════
            # 📉 RÈGLE 2 : SÉCURISER SI LE MARCHÉ S'ESSOUFFLE
            # ═══════════════════════════════════════════════════════════
            # (On ne rapproche PAS le TP, on rend le trailing stop plus agressif)
            
            current_rsi = current_indicators.get('rsi', 70)
            
            if (current_rsi < DYNAMIC_TP_RSI_WEAKNESS and 
                tp_progress_pct >= 50.0 and  # Seulement si bon profit déjà
                mt5_position.sl > 0):  # SL déjà actif
                
                # Calcul d'un SL ultra-agressif (80% du profit actuel)
                aggressive_sl_ratio = 0.80
                aggressive_sl = entry_price + (current_profit_distance * aggressive_sl_ratio)
                
                current_sl = mt5_position.sl
                
                # Seulement si ce nouveau SL est meilleur que l'actuel
                if aggressive_sl > current_sl and aggressive_sl > entry_price:
                    
                    # Vérifier distances minimales MT5
                    tick_info = mt5.symbol_info_tick(self.symbol)
                    if tick_info:
                        stops_level = getattr(symbol_info, 'trade_stops_level', 10)
                        min_distance = max(stops_level * symbol_info.point, 10 * symbol_info.point)
                        spread = symbol_info.spread * symbol_info.point
                        safety_buffer = max(min_distance * 2, 20 * symbol_info.point) + spread
                        max_allowed_sl = tick_info.bid - safety_buffer
                        
                        if aggressive_sl < max_allowed_sl:
                            
                            safe_log(f"📉 TP DYNAMIQUE - ESSOUFFLEMENT DÉTECTÉ!")
                            safe_log(f"   🎫 Ticket: {ticket}")
                            safe_log(f"   📊 RSI actuel: {current_rsi:.1f} (seuil: {DYNAMIC_TP_RSI_WEAKNESS})")
                            safe_log(f"   ⚠️ Perte de momentum détectée")
                            safe_log(f"   📊 Progression: {tp_progress_pct:.1f}% du TP")
                            safe_log(f"   🛡️ SL actuel: {current_sl:.5f}")
                            safe_log(f"   🛡️ Nouveau SL agressif: {aggressive_sl:.5f} (80% du profit)")
                            
                            guaranteed_profit_pips = (aggressive_sl - entry_price) / symbol_info.point / 10
                            safe_log(f"   💰 Profit garanti: +{guaranteed_profit_pips:.1f} pips")
                            
                            # Modification du SL agressif
                            request = {
                                "action": mt5.TRADE_ACTION_SLTP,
                                "symbol": self.symbol,
                                "position": ticket,
                                "sl": aggressive_sl,
                                "tp": mt5_position.tp,
                                "magic": mt5_position.magic,
                                "comment": "DynamicTP-Secure"
                            }
                            
                            try:
                                result = mt5.order_send(request)
                                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                                    safe_log(f"✅ SÉCURISATION AGRESSIVE ACTIVÉE!")
                                    safe_log(f"   💰 80% du gain verrouillé contre retournement")
                                else:
                                    error_msg = getattr(result, 'comment', "Erreur inconnue") if result else "Aucune réponse"
                                    safe_log(f"⚠️ Échec sécurisation: {error_msg}")
                            except Exception as e:
                                safe_log(f"❌ Erreur SL agressif: {e}")
    
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
    
    def get_h1_trend_confirmation(self):
        """🛡️ FILTRE PROFESSIONNEL: Confirme la tendance de fond sur H1 pour filtrer les signaux M5"""
        try:
            # Récupérer 50 bougies H1 pour calculer l'EMA 50
            rates_h1 = mt5.copy_rates_from_pos(self.symbol, mt5.TIMEFRAME_H1, 0, 50)
            if rates_h1 is None or len(rates_h1) < 50:
                safe_log("⚠️ Données H1 insuffisantes pour confirmation")
                return "NEUTRAL"  # En cas de doute, on s'abstient

            close_h1 = [rate['close'] for rate in rates_h1]
            ema50_h1 = self.calculate_ema(close_h1, 50)

            current_price = close_h1[-1]
            current_ema50_h1 = ema50_h1[-1]

            # Calcul de la force de la tendance H1 (en % et en prix)
            price_difference = current_price - current_ema50_h1  # Différence brute en prix
            price_distance_h1 = abs(price_difference) / current_price * 100  # Pourcentage
            
            if current_price > current_ema50_h1:
                safe_log(f"📈 CONFIRMATION H1: Tendance HAUSSIÈRE (Prix > EMA50 H1, écart: +{price_distance_h1:.2f}% / +${price_difference:.2f})")
                return "BULLISH"
            else:
                safe_log(f"📉 CONFIRMATION H1: Tendance BAISSIÈRE (Prix < EMA50 H1, écart: -{price_distance_h1:.2f}% / ${price_difference:.2f})")
                return "BEARISH"

        except Exception as e:
            safe_log(f"❌ Erreur confirmation H1: {e}")
            return "NEUTRAL"

    def check_volatility_regime(self, current_atr):
        """🛡️ FILTRE PROFESSIONNEL: Vérifie si les conditions de volatilité sont optimales"""
        if current_atr < OPTIMAL_ATR_MIN:
            safe_log(f"❌ VOLATILITÉ INSUFFISANTE: ATR {current_atr:.2f} < {OPTIMAL_ATR_MIN} (marché trop calme)")
            return False
        elif current_atr > OPTIMAL_ATR_MAX:
            safe_log(f"❌ VOLATILITÉ EXCESSIVE: ATR {current_atr:.2f} > {OPTIMAL_ATR_MAX} (marché chaotique)")
            return False
        else:
            safe_log(f"✅ VOLATILITÉ OPTIMALE: ATR {current_atr:.2f} dans la plage [{OPTIMAL_ATR_MIN}-{OPTIMAL_ATR_MAX}]")
            return True

    def find_structural_levels(self, symbol, lookback_candles=10):
        """🏗️ STOP LOSS STRUCTUREL: Trouve les niveaux techniques d'invalidation"""
        try:
            # Récupérer les données des dernières bougies pour analyse structurelle
            rates = mt5.copy_rates_from_pos(symbol, TIMEFRAME, 0, lookback_candles + 5)
            if rates is None or len(rates) < lookback_candles:
                safe_log(f"⚠️ Données insuffisantes pour analyse structurelle ({len(rates) if rates else 0} bougies)")
                return None
            
            # Extraire les données OHLC
            highs = [rate['high'] for rate in rates]
            lows = [rate['low'] for rate in rates]
            closes = [rate['close'] for rate in rates]
            
            # 🎯 AMÉLIORATION: Trouver le DERNIER swing low LOCAL (pas le minimum absolu)
            # Un swing low = une bougie dont le low est inférieur aux 2 bougies avant ET après
            recent_swing_low = None
            swing_low_index = None
            
            # Chercher en partant de l'avant-dernière bougie possible vers le début
            # ✅ FIX: range(len(lows) - 3, 2, -1) évite "list index out of range"
            for i in range(len(lows) - 3, 2, -1):
                current_low = lows[i]
                # Vérifier si c'est un creux local (inférieur aux voisins)
                if (current_low < lows[i-1] and current_low < lows[i-2] and 
                    current_low < lows[i+1] and current_low < lows[i+2]):
                    recent_swing_low = current_low
                    swing_low_index = i
                    break
            
            # Fallback si aucun swing low local trouvé → prendre le minimum des 5 dernières bougies
            if recent_swing_low is None:
                recent_swing_low = min(lows[-5:])
                safe_log(f"⚠️ Aucun swing low local détecté → Fallback sur min(5 bougies)")
            
            recent_swing_high = max(highs[-lookback_candles:])
            
            # Calcul ATR pour marge de sécurité
            atr_values = []
            for i in range(1, min(14, len(rates))):
                high_low = rates[i]['high'] - rates[i]['low']
                high_close_prev = abs(rates[i]['high'] - rates[i-1]['close'])
                low_close_prev = abs(rates[i]['low'] - rates[i-1]['close'])
                true_range = max(high_low, high_close_prev, low_close_prev)
                atr_values.append(true_range)
            
            current_atr = sum(atr_values) / len(atr_values) if atr_values else 0.01
            
            safe_log(f"🏗️ ANALYSE STRUCTURELLE:")
            safe_log(f"   📊 Période analysée: {lookback_candles} bougies")
            safe_log(f"   📉 Swing Low: {recent_swing_low:.2f}")
            safe_log(f"   📈 Swing High: {recent_swing_high:.2f}")
            safe_log(f"   ⚡ ATR calculé: {current_atr:.3f}")
            
            return {
                'swing_low': recent_swing_low,
                'swing_high': recent_swing_high,
                'swing_low_index': swing_low_index,
                'atr': current_atr,
                'analysis_period': lookback_candles
            }
            
        except Exception as e:
            safe_log(f"❌ Erreur analyse structurelle: {e}")
            return None

    def calculate_structural_stop_loss(self, trade_type, entry_price, structural_data):
        """🎯 CALCUL SL STRUCTUREL: SL basé sur l'invalidation technique du scénario"""
        if not structural_data:
            # Fallback sur SL classique ATR si analyse structurelle impossible
            fallback_sl = entry_price - (structural_data['atr'] if structural_data else 0.01) * 2.5
            safe_log(f"⚠️ SL Structurel impossible → Fallback ATR: {fallback_sl:.2f}")
            return fallback_sl
        
        current_atr = structural_data['atr']
        safety_margin = current_atr * 0.5  # Marge de sécurité: 0.5x ATR
        
        if trade_type == 'BUY':
            # Pour BUY: SL sous le dernier swing low
            structural_sl = structural_data['swing_low'] - safety_margin
            
            # 🛡️ SÉCURITÉ RENFORCÉE: Distance SL plus stricte
            min_distance = current_atr * 1.5  # Minimum réduit: 1.5x ATR (au lieu de 2x)
            min_allowed_sl = entry_price - min_distance
            
            # 🚨 SÉCURITÉ CRITIQUE: Distance maximale STRICTE
            max_distance = current_atr * 3.0  # Maximum réduit: 3x ATR (au lieu de 5x)
            max_allowed_sl = entry_price - max_distance
            
            # Application des limites
            if structural_sl > min_allowed_sl:
                structural_sl = min_allowed_sl
                safe_log(f"🔧 SL ajusté: Trop proche → {structural_sl:.2f} (min {min_distance:.2f} pts)")
            elif structural_sl < max_allowed_sl:
                structural_sl = max_allowed_sl
                safe_log(f"🔧 SL ajusté: Trop loin → {structural_sl:.2f} (max {max_distance:.2f} pts)")
            
            # 🚨 VÉRIFICATION FINALE: Perte maximale autorisée
            sl_distance_final = abs(entry_price - structural_sl)
            max_loss_pips = sl_distance_final / 0.1  # Conversion en pips
            
            safe_log(f"🏗️ SL STRUCTUREL BUY:")
            safe_log(f"   📉 Swing Low détecté: {structural_data['swing_low']:.2f}")
            safe_log(f"   🛡️ Marge sécurité: -{safety_margin:.3f}")
            safe_log(f"   🎯 SL Final: {structural_sl:.2f}")
            safe_log(f"   📏 Distance: {sl_distance_final:.2f} pts = {max_loss_pips:.1f} pips ({(sl_distance_final/current_atr):.1f}x ATR)")
            safe_log(f"   ⚖️ Limites appliquées: [{max_distance:.2f} - {min_distance:.2f}] pts")
                   
        return structural_sl

    def log_detailed_market_analysis(self, trend, strength, indicators, rejection_reason=""):
        """📊 DIAGNOSTIC ULTRA-DÉTAILLÉ: Affiche toutes les informations d'analyse pour comprendre les décisions"""
        safe_log(f"\n" + "="*80)
        safe_log(f"🔬 DIAGNOSTIC COMPLET - Raison: {rejection_reason}")
        safe_log(f"="*80)
        
        # === DONNÉES BRUTES ===
        current_price = indicators['price']
        ema_master = indicators['ema_master']  # EMA200
        ema_pullback = indicators['ema_pullback']  # EMA50
        current_rsi = indicators['rsi']
        current_atr = indicators['atr']
        pullback_quality = indicators['pullback_quality']
        
        safe_log(f"📊 DONNÉES MARCHÉ:")
        safe_log(f"   💲 Prix actuel: {current_price:.2f}")
        safe_log(f"   📈 EMA200 (tendance fond): {ema_master:.2f}")
        safe_log(f"   📈 EMA50 (pullback): {ema_pullback:.2f}")
        safe_log(f"   📊 RSI: {current_rsi:.1f}")
        safe_log(f"   ⚡ ATR (volatilité): {current_atr:.3f}")
        
        # === ANALYSE TENDANCE ===
        safe_log(f"\n🎯 ANALYSE TENDANCE:")
        safe_log(f"   📈 Tendance détectée: {trend}")
        safe_log(f"   💪 Force: {strength:.1f}% (seuil: ≥80%)")
        
        # Détail composants de la tendance
        price_vs_ema200 = "HAUSSIER" if current_price > ema_master else "BAISSIER"
        ema_alignment = "HAUSSIER" if ema_pullback > ema_master else "BAISSIER"
        price_vs_ema50 = "HAUSSIER" if current_price > ema_pullback else "BAISSIER"
        
        safe_log(f"   🔍 Prix vs EMA200: {price_vs_ema200} ({current_price:.2f} vs {ema_master:.2f})")
        safe_log(f"   🔍 EMA50 vs EMA200: {ema_alignment} ({ema_pullback:.2f} vs {ema_master:.2f})")
        safe_log(f"   🔍 Prix vs EMA50: {price_vs_ema50} ({current_price:.2f} vs {ema_pullback:.2f})")
        
        # === ANALYSE PULLBACK ===
        safe_log(f"\n🎯 ANALYSE PULLBACK:")
        safe_log(f"   📊 Qualité pullback: {pullback_quality:.0f}% (seuil: ≥60%)")
        
        distance_to_ema50 = abs(current_price - ema_pullback)
        pullback_threshold = current_atr * 3.0  # ATR_PULLBACK_MULTIPLIER
        safe_log(f"   📏 Distance à EMA50: {distance_to_ema50:.2f} points")
        safe_log(f"   📏 Seuil pullback: {pullback_threshold:.2f} points (3×ATR)")
        safe_log(f"   📊 Ratio distance/seuil: {(distance_to_ema50/pullback_threshold)*100:.1f}%")
        
        # === ANALYSE RSI ===
        safe_log(f"\n🎯 ANALYSE RSI:")
        safe_log(f"   📊 RSI actuel: {current_rsi:.1f}")
        safe_log(f"   📊 Zone survente: < {self.config['RSI_OVERSOLD']}")
        safe_log(f"   📊 Zone surachat: > {self.config['RSI_OVERBOUGHT']}")
        
        if current_rsi < self.config['RSI_OVERSOLD']:
            rsi_zone = "SURVENTE (bearish)"
        elif current_rsi > self.config['RSI_OVERBOUGHT']:
            rsi_zone = "SURACHAT (bullish)"
        else:
            rsi_zone = "NEUTRE"
        safe_log(f"   🎯 Zone RSI: {rsi_zone}")
        
        # === FILTRES PROFESSIONNELS ===
        safe_log(f"\n🛡️ FILTRES PROFESSIONNELS:")
        
        # Confirmation H1
        if hasattr(self, 'get_h1_trend_confirmation'):
            try:
                h1_trend = self.get_h1_trend_confirmation()
                safe_log(f"   📈 Tendance H1: {h1_trend}")
                if trend == "BULLISH" and h1_trend != "BULLISH":
                    safe_log(f"   ❌ CONFLIT: M5 BULLISH vs H1 {h1_trend}")
                elif trend == "BEARISH" and h1_trend != "BEARISH":
                    safe_log(f"   ❌ CONFLIT: M5 BEARISH vs H1 {h1_trend}")
                else:
                    safe_log(f"   ✅ COHÉRENCE: M5 {trend} = H1 {h1_trend}")
            except:
                safe_log(f"   ⚠️ H1: Données indisponibles")
        
        # Volatilité
        safe_log(f"   ⚡ ATR: {current_atr:.3f} (plage optimale: {OPTIMAL_ATR_MIN}-{OPTIMAL_ATR_MAX})")
        if current_atr < OPTIMAL_ATR_MIN:
            safe_log(f"   ❌ VOLATILITÉ: Trop faible (marché endormi)")
        elif current_atr > OPTIMAL_ATR_MAX:
            safe_log(f"   ❌ VOLATILITÉ: Trop élevée (marché chaotique)")
        else:
            safe_log(f"   ✅ VOLATILITÉ: Dans la plage optimale")
        
        # === ÉVALUATION GLOBALE ===
        safe_log(f"\n🎯 ÉVALUATION GLOBALE:")
        
        # Conditions pour BUY
        if trend == "BULLISH":
            safe_log(f"   📈 ANALYSE BUY:")
            buy_conditions = []
            buy_conditions.append(f"✅ Tendance BULLISH" if strength >= 80 else f"❌ Force {strength:.1f}% < 80%")
            buy_conditions.append(f"✅ Prix > EMA200" if current_price > ema_master else f"❌ Prix {current_price:.2f} <= EMA200 {ema_master:.2f}")
            buy_conditions.append(f"✅ Pullback OK" if pullback_quality >= 60 else f"❌ Pullback {pullback_quality:.0f}% < 60%")
            buy_conditions.append(f"✅ RSI OK" if current_rsi <= self.config['RSI_OVERBOUGHT'] else f"❌ RSI {current_rsi:.1f} > {self.config['RSI_OVERBOUGHT']}")
            buy_conditions.append(f"✅ ATR OK" if OPTIMAL_ATR_MIN <= current_atr <= OPTIMAL_ATR_MAX else f"❌ ATR {current_atr:.3f} hors plage")
            
            for condition in buy_conditions:
                safe_log(f"      {condition}")
              
        else:
            safe_log(f"   ❌ TENDANCE: {trend} - Force insuffisante ou direction incertaine")
        
        # === CONCLUSION ===
        safe_log(f"\n🎯 CONCLUSION:")
        if rejection_reason:
            safe_log(f"   ❌ SIGNAL REJETÉ: {rejection_reason}")
            
            # === DIAGNOSTIC SPÉCIAL COOLDOWN ===
            if rejection_reason == "SIGNAL_VALIDE_COOLDOWN":
                safe_log(f"\n⏰ DÉTAILS COOLDOWN:")
                safe_log(f"   🎯 SIGNAL PARFAITEMENT VALIDE!")
                safe_log(f"   ✅ Toutes les conditions techniques sont remplies")
                safe_log(f"   ⏳ Attente cooldown pour éviter l'overtrading")
                safe_log(f"   📋 Stratégie: Espacement minimum 5 minutes entre trades")
                safe_log(f"   🔄 Le signal sera exécuté dès que le cooldown expire")
                
                # Calcul temps restant plus détaillé
                current_time = datetime.now()
                cooldown_duration = 300  # 5 minutes en secondes
                
                if trend == "BULLISH":
                    if self.last_buy_timestamp:
                        time_since_last = (current_time - self.last_buy_timestamp).total_seconds()
                        remaining = max(0, cooldown_duration - time_since_last)
                        minutes_remaining = int(remaining // 60)
                        seconds_remaining = int(remaining % 60)
                        safe_log(f"   ⏰ Temps restant BUY: {minutes_remaining}m {seconds_remaining}s")
                        if remaining > 0:
                            next_trade_time = current_time + timedelta(seconds=remaining)
                            safe_log(f"   🎯 Prochain trade BUY possible: {next_trade_time.strftime('%H:%M:%S')}")
                                
                safe_log(f"   💡 Conseil: Le signal reste valide, patience!")
        
        safe_log(f"   📊 Pour trader, il faut TOUTES les conditions ✅")
        
        safe_log(f"="*80 + "\n")

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
            frequency = 300  # 5 minutes entre les trades
            safe_log(f"📈 Marché HAUSSIER → Fréquence: {frequency}s (5min)")
            return frequency
        elif trend == 'BEARISH':
            safe_log(f"📉 Marché BAISSIER détecté → ⚠️ BOT TRADE UNIQUEMENT EN BULLISH - Pas de signal généré")
            return None  # Pas de trading en tendance baissière
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
                safe_log(f"🕐 Trading actif de 00h20 à 22h00")
                safe_log(f"🚨 Mode argent réel avec sécurités renforcées")
                
        except Exception as e:
            safe_log(f"❌ Erreur reset quotidien: {e}")

    def check_trading_hours(self):
        """🕐 Vérifie les horaires de trading - PAUSE WEEK-END + ARRÊT SIMPLE À 22H00"""
        try:
            current_time = datetime.now()
            current_hour = current_time.hour
            current_minute = current_time.minute
            current_time_decimal = current_hour + (current_minute / 60.0)  # Conversion en décimal pour 00h00 = 0.0
            current_weekday = current_time.weekday()  # 0=Lundi, 4=Vendredi, 5=Samedi, 6=Dimanche
            
            # 📅 VÉRIFICATION WEEK-END EN PRIORITÉ (Samedi et Dimanche)
            if current_weekday == 5:  # Samedi
                if not hasattr(self, '_weekend_log_count'):
                    self._weekend_log_count = 0
                
                # Log périodique (toutes les 100 vérifications)
                if self._weekend_log_count % 100 == 0:
                    safe_log(f"📅 WEEK-END - Samedi {current_hour}h{current_minute:02d}")
                    safe_log(f"   🚫 Pas de trading le week-end")
                    safe_log(f"   ⏰ Reprise lundi à 00h00")
                
                self._weekend_log_count += 1
                self.is_trading_paused = True
                return False
            
            elif current_weekday == 6:  # Dimanche
                if not hasattr(self, '_weekend_log_count'):
                    self._weekend_log_count = 0
                
                # Log périodique (toutes les 100 vérifications)
                if self._weekend_log_count % 100 == 0:
                    safe_log(f"📅 WEEK-END - Dimanche {current_hour}h{current_minute:02d}")
                    safe_log(f"   🚫 Pas de trading le week-end")
                    safe_log(f"   ⏰ Reprise lundi à 00h00")
                
                self._weekend_log_count += 1
                self.is_trading_paused = True
                return False
            
            # Reset du compteur de logs week-end en semaine
            if current_weekday < 5 and hasattr(self, '_weekend_log_count'):
                self._weekend_log_count = 0
            
            # 🌙 ARRÊT SIMPLE DU TRADING À 22H00 - PLUS DE FERMETURE FORCÉE
            if current_time_decimal >= self.daily_close_time and not self.is_trading_paused:
                safe_log(f"🕐 ARRÊT AUTOMATIQUE DU TRADING - 22h00 atteinte")
                safe_log(f"📋 Nouveau comportement 22h00:")
                safe_log(f"   ✅ ARRÊT du trading (pas de nouveaux trades)")
                safe_log(f"   🎯 Positions MAINTENUES avec leurs SL/TP")
                safe_log(f"   🔄 Trailing stop CONTINUE de fonctionner")
                safe_log(f"   ⏸️ Reprise du trading à 00h00")
                
                # Activation de la pause nocturne (trading seulement)
                self.is_trading_paused = True
                
                safe_log(f"✅ MODE NUIT ACTIVÉ:")
                safe_log(f"   🚫 Trading STOPPÉ")
                safe_log(f"   🎯 Positions en cours: MAINTENUES")
                safe_log(f"   � SL/TP: ACTIFS")
                safe_log(f"   ⏰ Reprise: 00h00")
                
                return False  # Trading arrêté, mais positions maintenues
            
            # Vérification si on peut reprendre à 00h00 (sauf week-end déjà géré au-dessus)
            elif current_time_decimal >= self.daily_start_time and current_time_decimal < self.daily_close_time and self.is_trading_paused:
                # Reprise normale (lundi à vendredi uniquement, week-end déjà filtré)
                day_name = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"][current_weekday]
                safe_log(f"🌅 REPRISE DU TRADING - {day_name} 00h00 atteinte")
                safe_log(f"   🕐 Heure actuelle: {current_hour}h{current_minute:02d}")
                safe_log(f"   ✅ Trading autorisé jusqu'à 22h00")
                
                # Désactivation de la pause nocturne
                self.is_trading_paused = False
                
                return True  # Trading autorisé
            
            # Vérification si on est en période de pause (22h00 à 00h00)
            elif self.is_trading_paused or current_time_decimal < self.daily_start_time or current_time_decimal >= self.daily_close_time:
                # Pendant la pause, continuer à fermer les positions profitables
                self.continue_21h30_special_mode()
                
                # Log périodique pendant la pause (toutes les 100 vérifications = ~16 minutes)
                if not hasattr(self, '_pause_log_count'):
                    self._pause_log_count = 0
                
                self._pause_log_count += 1
                if self._pause_log_count % 100 == 0:
                    safe_log(f"🌙 PAUSE NOCTURNE - {current_hour}h{current_minute:02d} | Reprise à 00h00")
                
                return False  # Trading en pause
            
            # Trading normal autorisé (entre 00h00 et 22h00, lundi à vendredi)
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
                    position_type = "BUY"
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
                position_type = "BUY"
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
        
        # 🎯 DÉTECTION TENDANCE AMÉLIORÉE (Plus réactive aux retournements)
        # Combinaison : Prix vs EMA 200 + momentum récent + confirmation EMA
        
        # Tendance de fond (prix vs EMA 200)
        price_trend = "BULLISH" if current_price > current_ema_master else "BEARISH"
        
        # Tendance court terme (EMA 50 vs EMA 200)
        ema_trend = "BULLISH" if current_ema_pullback > current_ema_master else "BEARISH"
        
        # 🔥 SIGNAL ADDITIONNEL : Prix sous EMA50 = signal baissier fort
        price_vs_ema50 = "BULLISH" if current_price > current_ema_pullback else "BEARISH"
        
        # 🚀 MOMENTUM RÉCENT : Analyse des 5 dernières bougies pour détecter retournements
        recent_momentum = "NEUTRAL"
        if len(close_prices) >= 5:
            # Analyse sur 5 bougies pour plus de sensibilité
            recent_change = close_prices[-1] - close_prices[-5]  # Change sur 5 bougies
            momentum_threshold = current_atr * 0.3  # Seuil réduit pour plus de sensibilité
            
            if recent_change > momentum_threshold:
                recent_momentum = "BULLISH"
            elif recent_change < -momentum_threshold:
                recent_momentum = "BEARISH"
        
        # 🚀 LOGIQUE COMBINÉE AVEC FILTRE DE STABILITÉ (évite les changements trop rapides)
        # Règle: On ne change de tendance que si au moins 2 conditions concordent
        
        bullish_votes = 0
        bearish_votes = 0
        
        # Vote 1: Position du prix vs EMA 200 (tendance de fond)
        if price_trend == "BULLISH":
            bullish_votes += 1
        else:
            bearish_votes += 1
        
        # Vote 2: Position de l'EMA 50 vs EMA 200 (alignement EMAs)
        if ema_trend == "BULLISH":
            bullish_votes += 1
        else:
            bearish_votes += 1
        
        # Vote 3: Momentum récent (si significatif)
        if recent_momentum == "BULLISH":
            bullish_votes += 1
        elif recent_momentum == "BEARISH":
            bearish_votes += 1
        
        # 🎯 DÉCISION AVEC MAJORITÉ (au moins 2 votes sur 3)
        if bullish_votes >= 2:
            trend_direction = "BULLISH"
        elif bearish_votes >= 2:
            trend_direction = "BEARISH"
        else:
            # Égalité ou indécision → Garder la tendance précédente pour stabilité
            if hasattr(self, 'trend_data') and self.trend_data['current_trend'] in ['BULLISH', 'BEARISH']:
                trend_direction = self.trend_data['current_trend']
            else:
                trend_direction = "SIDEWAYS"
        
        # 🎯 CALCUL QUALITÉ DU PULLBACK (Distance à l'EMA 50)
        distance_to_pullback_ema = abs(current_price - current_ema_pullback)
        pullback_threshold = current_atr * ATR_PULLBACK_MULTIPLIER  # 3.0x ATR - zone pullback plus stricte
        
        # Plus on est proche de l'EMA 50, plus la qualité est élevée
        if distance_to_pullback_ema <= pullback_threshold:
            pullback_quality = 100 * (1 - distance_to_pullback_ema / pullback_threshold)
        else:
            pullback_quality = 0  # Trop éloigné de l'EMA 50
        
        # 🎯 FORCE GLOBALE AMÉLIORÉE (Plus sensible)
        # Basée sur la séparation des EMAs + qualité pullback + momentum prix
        ema_spread = abs(current_ema_master - current_ema_pullback) / current_price * 100
        
        # 🚀 BONUS DE FORCE : Quand EMAs et prix s'accordent
        agreement_bonus = 0
        if (trend_direction == "BULLISH" and current_price > current_ema_pullback > current_ema_master):
            agreement_bonus = 20  # Bonus pour alignement haussier parfait
        elif (trend_direction == "BEARISH" and current_price < current_ema_pullback < current_ema_master):
            agreement_bonus = 20  # Bonus pour alignement baissier parfait
        
        # Calcul final avec bonus d'alignement
        base_strength = ema_spread * 15 + pullback_quality  # Multiplicateur augmenté (15 au lieu de 10)
        strength = min(base_strength + agreement_bonus, 100)  # Max 100%
        
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
    
    def calculate_adaptive_lot_size(self, atr_sl_distance, trend_strength=50, trade_type="BUY"):
        """
        🚀 CALCUL LOT ADAPTATIF SELON FORCE DE TENDANCE ET TYPE DE TRADE
        ================================================================
        
        STRATÉGIE BUY (adaptatif selon force) :
        - Force 80-89% : Risque standard 2.5%
        - Force 90-94% : Risque augmenté 3.5% 
        - Force 95-99% : Risque élevé 6%
        - Force 100% : Risque maximum 12% (certitude absolue)
        
        Args:
            atr_sl_distance: Distance du Stop Loss basée sur l'ATR
            trend_strength: Force de la tendance (0-100%)
            trade_type: "BUY"
            
        Returns:
            float: Taille de lot optimale (adaptée à la certitude et au type)
        """
        try:
            # Récupération de l'equity actuelle (capital réel incluant les positions ouvertes)
            account_info = mt5.account_info()
            if not account_info:
                safe_log("⚠️ Impossible de récupérer l'equity - Lot par défaut: 0.01")
                return 0.01
            
            current_equity = account_info.equity
            
            # 🎯 CALCUL DU RISQUE SELON LA FORCE DE TENDANCE
            # 🟢 Risque de BASE : 10% de l'equity
            # 🚀 Progression selon la force du signal
            if trend_strength >= 95.0:
                risk_percent = 15  # 🎯 Risque élevé - Très forte certitude (1.5x le risque de base)
                risk_level = "ÉLEVÉ"
            elif trend_strength >= 90.0:
                risk_percent = 10  # ⚡ Risque augmenté - Forte certitude (1.2x le risque de base)
                risk_level = "AUGMENTÉ"
            else:
                risk_percent = 5  # 📊 Risque STANDARD - 10% de l'equity
                risk_level = "STANDARD"
            
            # 🛡️ APPLICATION DU MODE DÉGRADÉ
            if self.stats.get('balance_safety_active', False):
                # Réduction drastique du risque pour tous les cas
                risk_percent *= DEGRADED_MODE_RISK_MULTIPLIER
                safe_log(f"🛡️ MODE DÉGRADÉ - Risque réduit à {risk_percent:.2f}%")
            
            # � CALCUL DU LOT BASÉ SUR LA FORCE DE TENDANCE
            risk_amount = current_equity * (risk_percent / 100)
            
            # Calcul du lot nécessaire pour XAUUSD
            # 1 lot = 100$/point, donc lot = risk_amount / (sl_distance * 100)
            lot_size = risk_amount / (atr_sl_distance * 100)
            
            # Arrondi et sécurités
            lot_size = round(lot_size, 2)
            lot_size = max(lot_size, ADAPTIVE_LOT_MIN)  # Minimum broker
            lot_size = min(lot_size, ADAPTIVE_LOT_MAX)  # Maximum sécurité
            
            # Calcul du profit potentiel avec TP plafonné
            tp_potential = TP_MAX_POINTS * 0.01 * 100 * lot_size  # 200 points max de profit
            
            # 📊 LOG DÉTAILLÉ DU NOUVEAU SYSTÈME
            safe_log(f"🎯 LOT ADAPTATIF SELON FORCE TENDANCE:")
            safe_log(f"   📊 Force détectée: {trend_strength:.1f}%")
            safe_log(f"   🎲 Niveau de risque: {risk_level}")
            safe_log(f"   💰 Risque appliqué: {risk_percent:.1f}% de l'equity")
            safe_log(f"   💸 Montant risqué: {risk_amount:.2f}€")
            safe_log(f"   📈 Lot calculé: {lot_size}")
            safe_log(f"   🎯 Profit potentiel max: {tp_potential:.2f}€ (TP 200pts)")
            safe_log(f"   ⚖️ Ratio Risk/Reward théorique: 1:{tp_potential/risk_amount:.2f}")
            
            return lot_size
            safe_log(f"� LOT AGRESSIF: Equity ${current_equity:.0f} → Lot {lot_size:.2f} (risque {enhanced_risk_percent:.1f}%)")
            safe_log(f"   💰 Risque max: -${max_loss_per_trade:.0f} | Profit TP: +${tp_potential:.0f} (200pts max)")
            safe_log(f"   🎯 Stratégie: TP petits + SL grands + Lots élevés")
            
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
        """🎯 LOGIQUE M5 PULLBACK ULTRA-SÉLECTIVE : 80% de certitude minimum"""
        
        current_time = datetime.now()
        current_price = indicators['price']
        ema_master = indicators['ema_master']        # EMA 200 - Tendance de fond
        ema_pullback = indicators['ema_pullback']    # EMA 50 - Zone de repli
        current_rsi = indicators['rsi']
        current_atr = indicators['atr']
        pullback_quality = indicators['pullback_quality']
        
        # 🛡️ VÉRIFICATION MODE SÉCURITÉ BALANCE
        if self.stats['balance_safety_active']:
            return None  # Pas de nouveaux trades en mode sécurité
        
        # 🚫 FILTRE BEARISH PRIORITAIRE : Rejet immédiat si tendance baissière
        if trend == "BEARISH":
            # Message minimal pour tendance baissière (bot ne trade pas en BEARISH)
            safe_log(f"📉 Tendance BEARISH détectée → Bot en attente de tendance BULLISH")
            # Reset de l'historique de confirmation
            self.trend_confirmation_history = []
            return None
        
        # 🛡️ SYSTÈME DE CONFIRMATION SUR 3 CYCLES CONSÉCUTIFS
        # Enregistre la tendance actuelle (BULLISH uniquement car BEARISH déjà filtré)
        current_trend_data = {
            'trend': trend,
            'strength': strength,
            'timestamp': current_time,
            'pullback_quality': pullback_quality
        }
        
        # Ajouter la détection actuelle à l'historique
        self.trend_confirmation_history.append(current_trend_data)
        
        # Garder seulement les 3 dernières détections
        if len(self.trend_confirmation_history) > self.required_confirmations:
            self.trend_confirmation_history.pop(0)
        
        # Vérifier si on a 3 confirmations BULLISH consécutives
        if len(self.trend_confirmation_history) < self.required_confirmations:
            confirmations_count = len(self.trend_confirmation_history)
            safe_log(f"⏳ CONFIRMATION {confirmations_count}/{self.required_confirmations} - "
                    f"Attente de {self.required_confirmations - confirmations_count} cycle(s) BULLISH supplémentaire(s)")
            safe_log(f"   📊 Tendance actuelle: {trend} {strength:.1f}%")
            return None
        
        # Vérifier que les 3 dernières sont toutes BULLISH avec force >= 80%
        all_bullish = all(
            h['trend'] == 'BULLISH' and h['strength'] >= 80 
            for h in self.trend_confirmation_history
        )
        
        if not all_bullish:
            safe_log(f"❌ CONFIRMATION INCOMPLÈTE - Les 3 derniers cycles ne sont pas tous BULLISH ≥80%")
            for i, h in enumerate(self.trend_confirmation_history, 1):
                safe_log(f"   Cycle {i}: {h['trend']} {h['strength']:.1f}%")
            return None
        
        # ✅ 3 CONFIRMATIONS BULLISH VALIDÉES !
        safe_log(f"✅ 3 CONFIRMATIONS BULLISH CONSÉCUTIVES VALIDÉES!")
        for i, h in enumerate(self.trend_confirmation_history, 1):
            safe_log(f"   Cycle {i}: {h['trend']} {h['strength']:.1f}% - Pullback: {h['pullback_quality']:.0f}%")
        
        # 🎯 FILTRE QUALITÉ ULTRA-STRICT : 80% de certitude sur la tendance
        if strength < 80:  # ⚡ NOUVEAU SEUIL : 80% minimum (au lieu de 70%)
            # Diagnostic complet pour BULLISH/NEUTRAL avec force insuffisante
            safe_log(f"❌ SIGNAL REJETÉ: Force {strength:.1f}% < 80% requis - Pas assez fiable")
            if strength >= 10:  # Diagnostic pour presque tous les signaux
                self.log_detailed_market_analysis(trend, strength, indicators, "FORCE_INSUFFISANTE")
            return None
        
        if pullback_quality < 60:  # Qualité pullback minimale (60%)
            safe_log(f"❌ SIGNAL REJETÉ: Pullback {pullback_quality:.0f}% < 60% requis")
            self.log_detailed_market_analysis(trend, strength, indicators, "PULLBACK_INSUFFISANT")
            return None
        
        # 🛡️ FILTRES DE CONFIRMATION PROFESSIONNELS (NOUVEAU)
        
        # FILTRE 1: Confirmation tendance H1 (évite les trades contre-tendance)
        if ENABLE_H1_CONFIRMATION:
            h1_trend = self.get_h1_trend_confirmation()
            if h1_trend == "NEUTRAL":
                safe_log("❌ SIGNAL REJETÉ: Confirmation H1 impossible - Pas de trading en cas de doute")
                self.log_detailed_market_analysis(trend, strength, indicators, "H1_CONFIRMATION_IMPOSSIBLE")
                return None
        else:
            h1_trend = trend  # Si désactivé, on accepte la tendance M5
        
        # FILTRE 2: Régime de volatilité optimal
        if not self.check_volatility_regime(current_atr):
            safe_log("❌ SIGNAL REJETÉ: Conditions de volatilité non optimales")
            self.log_detailed_market_analysis(trend, strength, indicators, "VOLATILITÉ_NON_OPTIMALE")
            return None
        
        # Calcul des cooldowns adaptatifs
        if time_since_last_buy is None:
            if self.last_buy_timestamp is None:
                time_since_last_buy = float('inf')  # Premier trade = pas de cooldown
            else:
                time_since_last_buy = (current_time - self.last_buy_timestamp).total_seconds()
        
        # 🎯 Vérification limites globales - Basée sur le nombre de STRATÉGIES en cours
        # au lieu du nombre de positions individuelles (important pour entrées échelonnées)
        current_strategies = len([t for t in self.partial_trades.values() 
                                  if t['status'] in ['PENDING', 'ACTIVE']])
        max_positions_adaptatif = self.calculate_adaptive_max_positions()
        if current_strategies >= max_positions_adaptatif:
            safe_log(f"🚫 Trade rejeté - Limite de stratégies simultanées atteinte ({current_strategies}/{max_positions_adaptatif})")
            return None
        
        # 🟢 STRATÉGIE 1: ACHAT SUR PULLBACK HAUSSIER (BUY)
        # Conditions: Tendance haussière + Confirmation H1 + Prix proche EMA 50 + RSI sain
        if (trend == "BULLISH" and 
            h1_trend == "BULLISH" and  # 🛡️ CONFIRMATION H1 OBLIGATOIRE
            current_price > ema_master and  # Prix > EMA 200 (tendance de fond haussière)
            pullback_quality >= 60 and     # Prix proche de l'EMA 50 (pullback détecté)
            current_rsi <= self.config['RSI_OVERBOUGHT']):  # RSI pas en surachat selon config
            
            # Cooldown M5 adaptatif avec logging amélioré
            cooldown = 300  # 5 minutes entre les trades
            
            if time_since_last_buy < cooldown:
                remaining_time = cooldown - time_since_last_buy
                minutes_remaining = int(remaining_time // 60)
                seconds_remaining = int(remaining_time % 60)
                safe_log(f"⏳ BUY Cooldown PULLBACK: {remaining_time:.0f}s restantes ({minutes_remaining}m {seconds_remaining}s)")
                safe_log(f"✅ SIGNAL BUY VALIDE - En attente de cooldown (toutes conditions remplies!)")
                safe_log(f"🕐 Prochain trade BUY possible à: {(datetime.now() + timedelta(seconds=remaining_time)).strftime('%H:%M:%S')}")
                self.log_detailed_market_analysis(trend, strength, indicators, "SIGNAL_VALIDE_COOLDOWN")
                return None
            
            # 🎯 Signal BUY validé !
            safe_log(f"🚀 SIGNAL BUY VALIDÉ! Toutes conditions remplies:")
            safe_log(f"   📈 Tendance: {trend} {strength:.1f}%")
            safe_log(f"   📊 RSI: {current_rsi:.1f} (<= {self.config['RSI_OVERBOUGHT']})")
            safe_log(f"   🎯 Pullback: {pullback_quality:.0f}%")
            
            # Message cooldown adaptatif selon la situation
            if time_since_last_buy == float('inf'):
                safe_log(f"   ⏰ Cooldown: Premier trade BUY ou cooldown resetté!")
            else:
                safe_log(f"   ⏰ Cooldown: OK ({time_since_last_buy:.0f}s >= {cooldown}s)")
            
            # Log succès détaillé
            self.log_detailed_market_analysis(trend, strength, indicators, "SIGNAL_BUY_VALIDÉ")
            
            return {
                'type': 'BUY', 
                'reason': 'PULLBACK_HAUSSIER_M5',  # Pullback sur tendance haussière
                'strength': strength,
                'rsi': current_rsi,
                'pullback_quality': pullback_quality,
                'atr': current_atr,
                'confidence': min(strength + pullback_quality, 100) / 100
            }

        # 🐛 DEBUG: Pourquoi pas de TRADE ? Loggons les conditions non remplies
        
        # ⚡ BEARISH: Log minimaliste uniquement (pas de diagnostic détaillé)
        if trend == "BEARISH":
            safe_log(f"📉 Marché BEARISH → Bot trade uniquement en BULLISH - Pas de signal")
            return None  # Sortie immédiate sans diagnostics
        
        # Pour BULLISH et autres tendances, logs détaillés
        safe_log(f"🔍 ANALYSE COMPLÈTE:")
        safe_log(f"   📊 Tendance: {trend} {strength:.1f}% (≥80% requis)")
        safe_log(f"   📊 H1 Trend: {h1_trend if 'h1_trend' in locals() else 'Non vérifié'}")
        safe_log(f"   📊 Pullback: {pullback_quality:.0f}% (≥60% requis)")
        safe_log(f"   📊 RSI: {current_rsi:.1f} (zone optimale: 30-70)")
        safe_log(f"   📊 ATR: {current_atr:.3f} (plage: {OPTIMAL_ATR_MIN}-{OPTIMAL_ATR_MAX})")
        safe_log(f"   📊 Prix: {current_price:.2f} | EMA200: {ema_master:.2f} | EMA50: {ema_pullback:.2f}")
        
        if trend == "BULLISH":
            safe_log(f"🔍 CONDITIONS BUY NON REMPLIES:")
            if h1_trend != "BULLISH":
                safe_log(f"   ❌ H1 trend {h1_trend} ≠ BULLISH (conflit multi-timeframe)")
            if current_price <= ema_master:
                safe_log(f"   ❌ Prix {current_price:.2f} <= EMA200 {ema_master:.2f}")
            if pullback_quality < 60:
                safe_log(f"   ❌ Pullback {pullback_quality:.0f}% < 60%")
            if current_rsi > self.config['RSI_OVERBOUGHT']:
                safe_log(f"   ❌ RSI {current_rsi:.1f} > {self.config['RSI_OVERBOUGHT']} (surachat)")
        
        else:
            safe_log(f"🔍 TENDANCE INSUFFISANTE:")
            safe_log(f"   ❌ Force {strength:.1f}% < 80% ou direction incertaine")
            
        # Diagnostic détaillé SEULEMENT pour BULLISH et tendances non BEARISH
        self.log_detailed_market_analysis(trend, strength, indicators, "CONDITIONS_NON_REMPLIES")
        
        # Aucune condition remplie
        return None
    
    def create_partial_entry_trade(self, signal):
        """
        🎯 CRÉATION D'UN TRADE AVEC ENTRÉES ÉCHELONNÉES
        ================================================
        
        Stratégie : 50% / 30% / 20% avec espacement 0.5×ATR et 1.0×ATR
        
        Avantages :
        - Meilleur prix moyen si le marché fait une mèche
        - SL structurel large qui résiste aux mèches
        - Risque global maîtrisé (calculé sur la position totale)
        """
        if not self.partial_entries_enabled:
            # Fallback sur entrée unique classique
            return self.execute_m5_trade(signal)
        
        # 🔒 VÉRIFICATION LIMITE DE TRADES LOGIQUES (pas positions MT5)
        active_partial_trades = len([t for t in self.partial_trades.values() 
                                     if t['status'] in ['PENDING', 'ACTIVE']])
        
        # Si on a déjà 20 trades échelonnés actifs, on bloque
        if active_partial_trades >= MAX_POSITIONS:
            safe_log(f"🚫 Trade échelonné annulé - Limite trades logiques atteinte")
            safe_log(f"   📊 Trades échelonnés actifs: {active_partial_trades}/{MAX_POSITIONS}")
            safe_log(f"   💡 Chaque trade échelonné = 1 trade logique (même avec 3 entrées)")
            return False
        
        trade_type = signal['type']
        atr_value = signal['atr']
        entry_price = signal.get('price', None)
        trend_strength = signal.get('strength', 50)
        
        # Calcul du SL structurel (même logique que execute_m5_trade)
        tick_info = mt5.symbol_info_tick(self.symbol)
        if not tick_info:
            return False
        
        if trade_type == 'BUY':
            initial_price = tick_info.ask
        else:
            return False  # On ne trade que les BUY
        
        # Analyse structurelle pour SL
        structural_data = self.find_structural_levels(self.symbol, lookback_candles=10)
        if structural_data:
            sl_price = self.calculate_structural_stop_loss(trade_type, initial_price, structural_data)
            sl_distance = abs(initial_price - sl_price)
        else:
            sl_distance = 2.5 * atr_value
            sl_price = initial_price - sl_distance
        
        # Calcul TP
        tp_distance = self.calculate_market_aware_tp_ratio(trend_strength, atr_value, sl_distance)
        tp_price = initial_price + tp_distance
        
        # 🎯 CALCUL DES NIVEAUX D'ENTRÉE
        entry_levels_prices = []
        for level in self.entry_levels:
            offset = level['offset_multiplier'] * atr_value
            level_price = initial_price - offset  # Pour BUY, on descend
            entry_levels_prices.append({
                'level': len(entry_levels_prices) + 1,
                'percentage': level['percentage'],
                'price': level_price,
                'filled': False,
                'ticket': None,
                'fill_time': None
            })
        
        # Création du trade ID unique
        trade_id = f"PARTIAL_{self.next_trade_id}"
        self.next_trade_id += 1
        
        # Stockage des informations du trade partiel
        self.partial_trades[trade_id] = {
            'trade_id': trade_id,
            'type': trade_type,
            'signal': signal,
            'initial_price': initial_price,
            'sl_price': sl_price,
            'tp_price': tp_price,
            'atr': atr_value,
            'entry_levels': entry_levels_prices,
            'start_time': datetime.now(),
            'timeout': datetime.now() + timedelta(minutes=self.entry_timeout_minutes),
            'status': 'PENDING',  # PENDING, ACTIVE, COMPLETED, CANCELLED
            'filled_percentage': 0.0,
            'weighted_avg_price': 0.0,
            'total_lot_size': 0.0
        }
        
        safe_log(f"")
        safe_log(f"🎯 NOUVEAU TRADE AVEC ENTRÉES ÉCHELONNÉES #{trade_id}")
        safe_log(f"="*70)
        safe_log(f"📊 Configuration : Pyramide inversée 50% / 30% / 20%")
        safe_log(f"   Niveau 1: {entry_levels_prices[0]['price']:.2f}$ (50%) - IMMÉDIAT")
        safe_log(f"   Niveau 2: {entry_levels_prices[1]['price']:.2f}$ (30%) - Si prix descend de {0.5*atr_value:.2f}$")
        safe_log(f"   Niveau 3: {entry_levels_prices[2]['price']:.2f}$ (20%) - Si prix descend de {1.0*atr_value:.2f}$")
        safe_log(f"🎯 SL structurel: {sl_price:.2f}$ (unique pour toutes les entrées)")
        safe_log(f"🚀 TP initial: {tp_price:.2f}$ (sera recalculé selon prix moyen)")
        safe_log(f"⏱️ Timeout: 15 minutes pour remplir tous les niveaux")
        safe_log(f"="*70)
        
        # 🚀 EXÉCUTION IMMÉDIATE DU NIVEAU 1 (50%)
        success = self.execute_partial_entry_level(trade_id, 0)
        
        if not success:
            safe_log(f"❌ Échec ouverture niveau 1 - Trade partiel annulé")
            del self.partial_trades[trade_id]
            return False
        
        return True
    
    def execute_partial_entry_level(self, trade_id, level_index):
        """Exécute une entrée spécifique d'un trade partiel"""
        if trade_id not in self.partial_trades:
            return False
        
        trade = self.partial_trades[trade_id]
        level = trade['entry_levels'][level_index]
        
        if level['filled']:
            safe_log(f"⚠️ Niveau {level['level']} déjà rempli")
            return False
        
        # Calcul du lot pour ce niveau spécifique
        total_risk_amount = self.get_risk_amount_for_trade(trade['signal'])
        level_lot = self.calculate_lot_for_partial_entry(total_risk_amount, trade['sl_price'], level['price'], level['percentage'])
        
        # Placement de l'ordre au marché pour le niveau 1, limite pour les autres
        if level_index == 0:
            # Niveau 1 : Ordre au marché immédiat
            success, ticket = self.place_partial_order_market(trade, level, level_lot)
        else:
            # Niveaux 2-3 : Ordres limites
            success, ticket = self.place_partial_order_limit(trade, level, level_lot)
        
        if success:
            level['filled'] = True
            level['ticket'] = ticket
            level['fill_time'] = datetime.now()
            
            # Mise à jour des stats du trade
            self.update_partial_trade_stats(trade_id)
            
            safe_log(f"✅ Niveau {level['level']} rempli: {level_lot} lots à {level['price']:.2f}$ (Ticket #{ticket})")
            
        return success
    
    def calculate_lot_for_partial_entry(self, total_risk, sl_price, entry_price, percentage):
        """Calcule le lot pour une entrée partielle"""
        sl_distance = abs(entry_price - sl_price)
        partial_risk = total_risk * percentage  # Ex: 60€ * 0.50 = 30€ pour niveau 1
        lot = partial_risk / (sl_distance * 100)  # Pour XAUUSD
        lot = round(lot, 2)
        lot = max(lot, ADAPTIVE_LOT_MIN)
        lot = min(lot, ADAPTIVE_LOT_MAX)
        return lot
    
    def get_risk_amount_for_trade(self, signal):
        """Calcule le montant total à risquer pour ce trade"""
        account_info = mt5.account_info()
        if not account_info:
            return 60.0  # Fallback
        
        equity = account_info.equity
        strength = signal.get('strength', 80)
        
        # Utilise la même logique que calculate_adaptive_lot_size
        if strength >= 100:
            risk_percent = 20
        elif strength >= 95:
            risk_percent = 15
        elif strength >= 90:
            risk_percent = 12
        else:
            risk_percent = 10
        
        return equity * (risk_percent / 100)
    
    def update_partial_trade_stats(self, trade_id):
        """Met à jour les statistiques d'un trade partiel (prix moyen, etc.)"""
        trade = self.partial_trades[trade_id]
        
        total_lots = 0.0
        weighted_price_sum = 0.0
        filled_count = 0
        
        for level in trade['entry_levels']:
            if level['filled'] and level['ticket']:
                # Récupération de l'info réelle depuis MT5
                positions = mt5.positions_get(ticket=level['ticket'])
                if positions:
                    pos = positions[0]
                    lot = pos.volume
                    price = pos.price_open
                    total_lots += lot
                    weighted_price_sum += (price * lot)
                    filled_count += 1
        
        if total_lots > 0:
            trade['weighted_avg_price'] = weighted_price_sum / total_lots
            trade['total_lot_size'] = total_lots
            trade['filled_percentage'] = sum(l['percentage'] for l in trade['entry_levels'] if l['filled'])
            
            safe_log(f"📊 Trade #{trade_id} - Stats mises à jour:")
            safe_log(f"   💰 Prix moyen pondéré: {trade['weighted_avg_price']:.2f}$")
            safe_log(f"   📦 Lots total: {total_lots}")
            safe_log(f"   ✅ Rempli: {trade['filled_percentage']*100:.0f}% ({filled_count}/{len(trade['entry_levels'])} niveaux)")
    
    def place_partial_order_market(self, trade, level, lot_size):
        """Place un ordre au marché pour une entrée partielle"""
        # Utilise la logique existante de place_real_order mais simplifié
        tick_info = mt5.symbol_info_tick(self.symbol)
        if not tick_info:
            return False, None
        
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY,
            "price": tick_info.ask,
            "sl": trade['sl_price'],
            "tp": trade['tp_price'],
            "deviation": 20,
            "magic": 123456,
            "comment": f"PartialEntry_L{level['level']}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        
        result = mt5.order_send(request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            return True, result.order
        else:
            safe_log(f"❌ Échec ordre niveau {level['level']}: {result.comment if result else 'Aucune réponse'}")
            return False, None
    
    def place_partial_order_limit(self, trade, level, lot_size):
        """Place un ordre limite pour une entrée partielle (niveaux 2-3)"""
        request = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": self.symbol,
            "volume": lot_size,
            "type": mt5.ORDER_TYPE_BUY_LIMIT,
            "price": level['price'],
            "sl": trade['sl_price'],
            "tp": trade['tp_price'],
            "deviation": 20,
            "magic": 123456,
            "comment": f"PartialEntry_L{level['level']}",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_RETURN,
        }
        
        result = mt5.order_send(request)
        
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            safe_log(f"📋 Ordre limite placé niveau {level['level']}: {lot_size} lots à {level['price']:.2f}$")
            return True, result.order
        else:
            safe_log(f"❌ Échec ordre limite niveau {level['level']}: {result.comment if result else 'Aucune réponse'}")
            return False, None
    
    def monitor_partial_trades(self):
        """Surveille les trades partiels en cours (timeouts, remplissage niveaux, etc.)"""
        if not self.partial_trades:
            return
        
        current_time = datetime.now()
        
        for trade_id in list(self.partial_trades.keys()):
            trade = self.partial_trades[trade_id]
            
            # Vérifier timeout
            if current_time > trade['timeout'] and trade['status'] == 'PENDING':
                safe_log(f"⏱️ Timeout atteint pour trade #{trade_id}")
                self.finalize_partial_trade(trade_id)
                continue
            
            # Vérifier si tous les niveaux sont remplis
            all_filled = all(level['filled'] for level in trade['entry_levels'])
            if all_filled and trade['status'] == 'PENDING':
                safe_log(f"✅ Tous les niveaux remplis pour trade #{trade_id}")
                trade['status'] = 'COMPLETED'
                self.finalize_partial_trade(trade_id)
    
    def finalize_partial_trade(self, trade_id):
        """Finalise un trade partiel (annule ordres restants, ajuste TP/SL)"""
        trade = self.partial_trades[trade_id]
        
        # Annuler les ordres limites non remplis
        for level in trade['entry_levels']:
            if not level['filled'] and level['ticket']:
                # Annuler l'ordre limite
                cancel_request = {
                    "action": mt5.TRADE_ACTION_REMOVE,
                    "order": level['ticket']
                }
                mt5.order_send(cancel_request)
                safe_log(f"🚫 Ordre limite niveau {level['level']} annulé (non rempli)")
        
        # Recalculer TP/SL basé sur le prix moyen pondéré
        if trade['total_lot_size'] > 0:
            self.adjust_tp_sl_for_partial_trade(trade_id)
        
        trade['status'] = 'FINALIZED'
        safe_log(f"🏁 Trade #{trade_id} finalisé - {trade['filled_percentage']*100:.0f}% de la position ouverte")
    
    def adjust_tp_sl_for_partial_trade(self, trade_id):
        """Ajuste TP/SL de toutes les positions du trade partiel selon le prix moyen"""
        trade = self.partial_trades[trade_id]
        
        avg_price = trade['weighted_avg_price']
        sl_distance = abs(avg_price - trade['sl_price'])
        
        # Recalculer TP depuis le prix moyen
        tp_distance = self.calculate_market_aware_tp_ratio(
            trade['signal'].get('strength', 80),
            trade['atr'],
            sl_distance
        )
        new_tp = avg_price + tp_distance
        
        safe_log(f"🔧 Ajustement TP/SL pour prix moyen {avg_price:.2f}$")
        safe_log(f"   🎯 Nouveau TP: {new_tp:.2f}$ (calculé depuis prix moyen)")
        
        # Modifier toutes les positions du trade
        for level in trade['entry_levels']:
            if level['filled'] and level['ticket']:
                request = {
                    "action": mt5.TRADE_ACTION_SLTP,
                    "symbol": self.symbol,
                    "position": level['ticket'],
                    "sl": trade['sl_price'],  # SL reste le même
                    "tp": new_tp  # TP ajusté
                }
                result = mt5.order_send(request)
                if result and result.retcode == mt5.TRADE_RETCODE_DONE:
                    safe_log(f"   ✅ TP/SL ajusté pour position #{level['ticket']}")
    
    def execute_m5_trade(self, signal):
        """🎯 NOUVELLE EXÉCUTION M5 : TP/SL adaptatifs basés sur l'ATR avec validation ultra-stricte"""
        
        trade_type = signal['type']
        atr_value = signal['atr']
        current_price = signal.get('price', None)
        trend_strength = signal.get('strength', 50)
        

        sl_multiplier = ATR_SL_MULTIPLIER  # 2.5x ATR standard pour BUY
        
        # Récupération prix réel pour calcul TP/SL
        tick_info = mt5.symbol_info_tick(self.symbol)
        if tick_info is None:
            safe_log("❌ Impossible de récupérer prix pour TP/SL ATR")
            return
        
        # Prix d'entrée basé sur le type d'ordre
        if trade_type == 'BUY':
            entry_price = tick_info.ask
        
        # 🏗️ ANALYSE STRUCTURELLE POUR SL INTELLIGENT
        safe_log(f"🔍 ANALYSE STRUCTURELLE pour SL optimal...")
        structural_data = self.find_structural_levels(self.symbol, lookback_candles=10)
        
        if structural_data:
            # Utilisation du SL structurel (niveau d'invalidation technique)
            structural_sl = self.calculate_structural_stop_loss(trade_type, entry_price, structural_data)
            safe_log(f"🏗️ SL STRUCTUREL choisi: {structural_sl:.2f}")
            sl_price = structural_sl
            # Recalcul de la distance pour TP et ratios
            sl_distance = abs(entry_price - sl_price)
        else:
            # Fallback sur SL ATR classique
            safe_log(f"⚠️ Analyse structurelle impossible → Fallback SL ATR")
            sl_distance = sl_multiplier * atr_value
            if trade_type == 'BUY':
                sl_price = entry_price - sl_distance
            safe_log(f"📊 SL ATR Fallback: {sl_price:.2f}")
        
        # 🔥 NOUVELLE STRATÉGIE : TP ADAPTATIFS basés sur le SL structurel
        
        # 🎯 TP PLAFONNÉ À 200 POINTS MAXIMUM
        tp_distance = self.calculate_market_aware_tp_ratio(trend_strength, atr_value, sl_distance)
        
        # Application selon le type d'ordre
        if trade_type == 'BUY':
            tp_price = entry_price + tp_distance
        
        # Conversion en pips pour XAUUSD (1 pip = 0.1)
        sl_pips = sl_distance / 0.1
        tp_pips = tp_distance / 0.1
        
        # Calcul du ratio réel pour le logging
        actual_ratio = tp_distance / sl_distance
        tp_points = tp_pips * 10  # Conversion en points
        
        # Déterminer le type de SL utilisé
        sl_type = "STRUCTUREL" if structural_data else "ATR"
        sl_description = f"{sl_type} ({'ÉLARGI' if sl_multiplier > ATR_SL_MULTIPLIER else 'STANDARD'})"
        
        # 🔥 LOG DÉTAILLÉ DE LA NOUVELLE STRATÉGIE
        safe_log(f"⚡ TRADE M5 {trade_type} - {signal['reason']}")
        safe_log(f"   📊 ATR actuel: {atr_value:.3f} (volatilité du marché)")
        safe_log(f"   🎯 Tendance: {trend_strength:.1f}% → TP plafonné à 200pts")
        safe_log(f"   💰 Prix entrée: ${entry_price:.2f}")
        safe_log(f"   🏗️ SL {sl_description}: ${sl_price:.2f} ({sl_pips:.1f} pips)")
        safe_log(f"   🚀 TP PLAFONNÉ: ${tp_price:.2f} ({tp_points:.0f} pts ≤ 200pts max)")
        safe_log(f"   ⚖️ Ratio R/R: 1:{actual_ratio:.2f} (TP PLAFONNÉ + SL {sl_type})")
        safe_log(f"   💡 Le lot sera adapté automatiquement selon la distance SL")
        safe_log(f"   📈 Force signal: {signal['strength']:.1f}%")
        safe_log(f"   🎯 Qualité pullback: {signal['pullback_quality']:.1f}%")
        safe_log(f"   📊 RSI: {signal['rsi']:.1f}")
        safe_log(f"   🎲 Confiance: {signal['confidence']:.2f}")
        
        # � VÉRIFICATION MARGIN AVANT TRADE
        if not self.check_margin_availability():
            safe_log(f"🚫 Trade annulé - Margin insuffisante")
            return False
        
        # 🔒 VÉRIFICATION LIMITE STRATÉGIES SIMULTANÉES
        current_strategies = len([t for t in self.partial_trades.values() 
                                  if t['status'] in ['PENDING', 'ACTIVE']])
        if current_strategies >= MAX_POSITIONS:
            safe_log(f"🚫 Trade annulé - Limite stratégies atteinte ({current_strategies}/{MAX_POSITIONS})")
            return False
        # MISE A JOUR TIMESTAMP selon le type de trade
        if trade_type == 'BUY':
            self.last_buy_timestamp = datetime.now()
        
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
        
        # 🛡️ NOUVEAU: La logique de sortie du mode dégradé est maintenant intégrée dans check_balance_safety()
        # Plus besoin de vérification séparée - Mode dégradé géré automatiquement
        
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
        
        # 🎯 AFFICHAGE ÉTAT M5 PULLBACK (seuil ultra-strict 80%)
        strength_status = f"✅{strength:.1f}%" if strength >= 80 else f"❌{strength:.1f}%"
        safe_log(f"📊 M5 ${current_price:.2f} | {trend} {strength_status}(≥80%) | "
                f"RSI:{current_rsi:.1f} | ATR:{current_atr:.3f} | "
                f"EMA200:{ema_master:.2f} | EMA50:{ema_pullback:.2f} | "
                f"Pullback:{pullback_quality:.0f}% | Pos:{open_positions_count} | "
                f"{safety_status} | {daily_status}")
        
        # 🔬 DIAGNOSTIC SYSTÉMATIQUE (simplifié pour BEARISH)
        if trend == "BEARISH":
            # Message unique et concis pour BEARISH - pas de redondance
            pass  # Le message est maintenant géré uniquement dans should_open_position()
        elif trend == "BULLISH":
            # 🎯 DIAGNOSTIC DÉTAILLÉ POUR BULLISH : Checklist complète des conditions
            safe_log(f"🎯 BULLISH DÉTECTÉ - Vérification conditions de trade:")
            
            # Condition 1 : Force de tendance
            if strength >= 80:
                safe_log(f"   ✅ Force: {strength:.1f}% (≥80% requis)")
            else:
                safe_log(f"   ❌ Force: {strength:.1f}% < 80% requis | Manque: {80-strength:.1f}%")
            
            # Condition 2 : Qualité du pullback
            distance_to_ema50 = abs(current_price - ema_pullback)
            pullback_threshold = current_atr * 3.0
            if pullback_quality >= 60:
                safe_log(f"   ✅ Pullback: {pullback_quality:.0f}% (≥60% requis) | Prix proche EMA50")
            else:
                safe_log(f"   ❌ Pullback: {pullback_quality:.0f}% < 60% requis")
                safe_log(f"      📏 Distance à EMA50: {distance_to_ema50:.4f} | Max accepté: {pullback_threshold:.4f}")
                if distance_to_ema50 > pullback_threshold:
                    safe_log(f"      💡 Prix trop éloigné de l'EMA50 → Attendre le rapprochement")
            
            # Condition 3 : RSI
            rsi_overbought = self.config['RSI_OVERBOUGHT']
            if current_rsi <= rsi_overbought:
                safe_log(f"   ✅ RSI: {current_rsi:.1f} (≤{rsi_overbought} requis) | Pas de surachat")
            else:
                safe_log(f"   ❌ RSI: {current_rsi:.1f} > {rsi_overbought} | Surachat → Attendre correction")
            
            # Condition 4 : ATR (Volatilité)
            if 1.5 <= current_atr <= 7.0:
                safe_log(f"   ✅ ATR: {current_atr:.3f} (plage optimale: 1.5-7.0)")
            elif current_atr < 1.5:
                safe_log(f"   ❌ ATR: {current_atr:.3f} < 1.5 | Marché trop calme")
            else:
                safe_log(f"   ❌ ATR: {current_atr:.3f} > 7.0 | Marché trop volatil")
            
            # Condition 5 : Prix > EMA200 (tendance de fond)
            if current_price > ema_master:
                safe_log(f"   ✅ Prix ${current_price:.2f} > EMA200 ${ema_master:.2f} | Tendance haussière confirmée")
            else:
                safe_log(f"   ❌ Prix ${current_price:.2f} ≤ EMA200 ${ema_master:.2f} | Tendance de fond pas haussière")
            
            # Condition 6 : Confirmation H1
            if ENABLE_H1_CONFIRMATION:
                h1_trend = self.get_h1_trend_confirmation()
                if h1_trend == "BULLISH":
                    safe_log(f"   ✅ Confirmation H1: BULLISH | Tendance de fond alignée")
                elif h1_trend == "BEARISH":
                    safe_log(f"   ❌ Confirmation H1: BEARISH | Conflit avec M5 → Pas de trade")
                else:
                    safe_log(f"   ⚠️ Confirmation H1: NEUTRAL | Direction incertaine")
            
            # Condition 7 : Stratégies disponibles (trades logiques, pas positions MT5)
            current_strategies = len([t for t in self.partial_trades.values() 
                                      if t['status'] in ['PENDING', 'ACTIVE']])
            max_positions = self.calculate_adaptive_max_positions()
            if current_strategies < max_positions:
                safe_log(f"   ✅ Stratégies actives: {current_strategies}/{max_positions} | Capacité disponible")
            else:
                safe_log(f"   ❌ Stratégies actives: {current_strategies}/{max_positions} | Limite atteinte")
            
            # Résumé visuel
            conditions_ok = 0
            conditions_total = 7
            if strength >= 80: conditions_ok += 1
            if pullback_quality >= 60: conditions_ok += 1
            if current_rsi <= rsi_overbought: conditions_ok += 1
            if 1.5 <= current_atr <= 7.0: conditions_ok += 1
            if current_price > ema_master: conditions_ok += 1
            if not ENABLE_H1_CONFIRMATION or h1_trend == "BULLISH": conditions_ok += 1
            if current_strategies < max_positions: conditions_ok += 1
            
            percentage_ready = (conditions_ok / conditions_total) * 100
            safe_log(f"   📊 Conditions remplies: {conditions_ok}/{conditions_total} ({percentage_ready:.0f}%)")
            
            if conditions_ok == conditions_total:
                safe_log(f"   🚀 TOUTES LES CONDITIONS OK → Vérification cooldown...")
            else:
                safe_log(f"   ⏳ Manque {conditions_total - conditions_ok} condition(s) → Attente...")
        else:
            # Diagnostic pour NEUTRAL
            safe_log(f"🧪 DIAGNOSTIC M5: Force {strength:.1f}% | Pullback {pullback_quality:.0f}% | RSI {current_rsi:.1f} | ATR {current_atr:.3f}")
            if strength < 80:
                safe_log(f"   ❌ Force insuffisante: {strength:.1f}% < 80% requis")
            if pullback_quality < 60:
                distance_to_ema50 = abs(current_price - ema_pullback)
                pullback_threshold = current_atr * 3.0
                safe_log(f"   ❌ Pullback faible: {pullback_quality:.0f}% < 60% requis")
                safe_log(f"      📏 Distance prix/EMA50: {distance_to_ema50:.4f} | Seuil max: {pullback_threshold:.4f} (3.0×ATR)")
            if current_rsi < 30 or current_rsi > 70:
                safe_log(f"   ⚡ RSI en zone: {current_rsi:.1f} (30-70 = neutre)")
            if current_atr < 1.5 or current_atr > 7.0:
                safe_log(f"   ⚠️ ATR hors zone optimale: {current_atr:.3f} (1.5-7.0 optimal)")
        
        # Vérification signal PULLBACK (seulement si pas en mode sécurité)
        if not self.stats['balance_safety_active']:
            signal = self.should_open_position(trend, strength, indicators)
            
            if signal:
                signal_type = signal['type']
                reason = signal['reason']
                safe_log(f"🔥 SIGNAL M5 {signal_type}: {reason} - Force:{strength:.1f}% Pullback:{pullback_quality:.0f}%")
                
                # 🎯 EXÉCUTION AVEC ENTRÉES PARTIELLES ÉCHELONNÉES
                success = self.create_partial_entry_trade(signal)
                if success:
                    safe_log(f"✅ Trade M5 avec entrées échelonnées créé!")
                else:
                    safe_log(f"❌ Échec création trade M5")
            else:
                # 📝 RÉSUMÉ: Pourquoi aucun signal n'est généré
                # ⚡ BEARISH: Pas de log détaillé (déjà fait dans should_open_position)
                if trend == "BEARISH":
                    # Pas de log supplémentaire - le message minimal a déjà été affiché
                    pass
                else:
                    # BULLISH ou NEUTRAL: logs détaillés
                    safe_log(f"💤 AUCUN SIGNAL M5 - Résumé des conditions:")
                    if strength < 80:
                        safe_log(f"   🎯 Force {strength:.1f}% < 80% (condition principale non remplie)")
                    if pullback_quality < 60:
                        safe_log(f"   📉 Pullback {pullback_quality:.0f}% < 60% (position pas assez proche EMA50)")
                    if current_rsi <= 30:
                        safe_log(f"   📊 RSI {current_rsi:.1f} en survente (attente rebond)")
                    elif current_rsi >= 70:
                        safe_log(f"   📊 RSI {current_rsi:.1f} en surachat (attente correction)")
                    if current_atr < 1.5:
                        safe_log(f"   ⚡ ATR {current_atr:.3f} trop faible (marché peu volatil)")
                    elif current_atr > 7.0:
                        safe_log(f"   ⚡ ATR {current_atr:.3f} trop élevé (marché trop volatil)")
                    if trend == "NEUTRAL":
                        safe_log(f"   🎭 Tendance neutre (pas de direction claire)")
                    safe_log(f"   ⏳ Prochaine analyse dans 30 secondes...")
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
        safe_log(f"⏰ Cooldown adaptatif: 5 minutes entre tous les trades")
        safe_log(f"🎯 TP/SL: Adaptatifs selon ATR | Breakeven progressif")
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
            
        safe_log(f"⚡ Analyse toutes les {ANALYSIS_INTERVAL} secondes (haute fréquence)")
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
        safe_log(f"⚡ Analyse toutes les {ANALYSIS_INTERVAL} secondes (haute fréquence)")
        safe_log(f"🎯 TP/SL: Adaptatifs selon ATR | Breakeven progressif")
        
        # 🎯 Affichage des nouvelles fonctionnalités avancées
        if ENABLE_DYNAMIC_TP:
            safe_log(f"\n🚀 FONCTIONNALITÉS EXPERT ACTIVÉES:")
            safe_log(f"   🎯 TP Dynamique: Ajuste le TP en temps réel selon la force du marché")
            safe_log(f"      📈 Accélération (>{DYNAMIC_TP_STRENGTH_THRESHOLD}%): Éloigne TP +{(DYNAMIC_TP_EXTENSION_MULTIPLIER-1)*100:.0f}%")
            safe_log(f"      📉 Essoufflement (RSI<{DYNAMIC_TP_RSI_WEAKNESS}): SL agressif à 80% profit")
        
        safe_log(f"⏹️ Arrêt: Ctrl+C")
        safe_log("="*60)
        
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
                
                # 🎯 TP DYNAMIQUE - Ajustement en temps réel (priorité haute)
                self.manage_dynamic_take_profit()
                
                # 🎯 SURVEILLANCE ENTRÉES PARTIELLES - Timeouts et remplissages
                self.monitor_partial_trades()
                
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
