# -*- coding: utf-8 -*-
"""
ULTRA SCALPING BOT - STRATÉGIE BUY UNIQUEMENT
====================================================

🔥 BOT ULTRA AGRESSIF - SCALPING BUY UNIQUEMENT
⚡ Logique: Detecte les baisses et achète sur rebonds
📉 Baisse détectée → BUY (bet sur rebond)
🚫 Plus de SELL - Seulement des achats

⚠️ ATTENTION: Stratégie très risquée!
- TP minimal (quelques pips)
- Stop Loss BUY: 1170 points
- Trading haute fréquence
- Capital à risque uniquement!

Auteur: Ultra Scalper
Date: 14 août 2025
"""

import MetaTrader5 as mt5
import numpy as np
from datetime import datetime, timedelta
import sys
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
# CONFIGURATION ULTRA SCALPING
# =============================================================================
ENABLE_REAL_TRADING = True   # ✅ TRADING RÉEL ACTIVÉ sur compte démo
MT5_LOGIN = 95548488       # Votre compte démo
MT5_PASSWORD = "-uCiJm3j"    
MT5_SERVER = "MetaQuotes-Demo"

# Paramètres ultra agressifs
SYMBOL = "XAUUSD"           # Or (très volatil = parfait pour scalping)
TIMEFRAME = mt5.TIMEFRAME_M1  # 1 minute (ultra rapide)
LOT_SIZE = 0.01             # Lot minimal pour commencer
TP_PIPS = 23                 # Take Profit: 23 pips seulement!
USE_STOP_LOSS = True        # Stop Loss activé pour les SELL
MAX_POSITIONS = 99999999999           # Maximum 5 positions simultanées
ANALYSIS_INTERVAL = 10      # Analyse toutes les 10 secondes
DAILY_PROFIT_LIMIT = 400    # Limite de profit par jour en EUR/USD

# Configuration profit journalier - Balance de référence
INITIAL_BALANCE_TODAY = 3000.00  # Balance de référence (début de journée 15/08/2025)

# Seuils de détection de tendance (ultra sensibles)
TREND_EMA_FAST = 5          # EMA rapide (5 périodes)
TREND_EMA_SLOW = 10         # EMA lente (10 périodes)
RSI_PERIOD = 7              # RSI ultra court
# RSI_OVERBOUGHT et RSI_OVERSOLD sont maintenant définis dans la config
# =============================================================================

def safe_log(message):
    """Log avec timestamp pour ultra scalping"""
    try:
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Millisecondes
        print(f"[{timestamp}] {message}", flush=True)
        sys.stdout.flush()
    except Exception as e:
        print(f"[LOG ERROR] {e}", flush=True)

class UltraScalpingBot:
    """
    Bot de scalping ultra agressif - BUY uniquement
    Stratégie: Achète sur les baisses, bet sur les rebonds
    """
    
    def __init__(self, config_name='YOLO', manual_daily_profit=None):
        self.symbol = SYMBOL
        self.timeframe = TIMEFRAME
        self.is_trading = False
        self.manual_daily_profit = manual_daily_profit  # Profit manuel si fourni
        self.bot_trades_profit = 0  # Profit des trades exécutés par ce bot
        
        # Chargement de la configuration
        from ultra_scalping_config import YOLO_CONFIG, AGGRESSIVE_CONFIG, BALANCED_CONFIG, CONSERVATIVE_CONFIG
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
            'daily_limit_reached': False  # Flag pour limite journalière atteinte
        }
        
        # Variables système profit quotidien adaptatif
        self.daily_start_balance = 0  # Balance de départ du jour
        self.daily_profit_target = 0  # Objectif de profit quotidien calculé automatiquement
        
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
        """Initialise MT5 pour ultra scalping"""
        if not mt5.initialize():
            safe_log("❌ Échec initialisation MT5")
            return False
        
        # Connexion compte
        if not mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
            safe_log(f"❌ Échec connexion compte {MT5_LOGIN}")
            safe_log(f"Erreur: {mt5.last_error()}")
            mt5.shutdown()
            return False
        
        safe_log("✅ MT5 initialisé pour ULTRA SCALPING")
        
        # Infos compte
        account_info = mt5.account_info()
        if account_info:
            safe_log(f"💰 Balance: ${account_info.balance:.2f}")
            safe_log(f"📊 Équité: ${account_info.equity:.2f}")
        
        # Activation symbole
        if mt5.symbol_select(self.symbol, True):
            safe_log(f"⚡ {self.symbol} activé pour ultra scalping")
            
            symbol_info = mt5.symbol_info(self.symbol)
            if symbol_info:
                safe_log(f"📊 Spread: {symbol_info.spread} points")
                safe_log(f"� Ask: {symbol_info.ask}")
                safe_log(f"📉 Bid: {symbol_info.bid}")
                
            return True
        else:
            safe_log(f"❌ Impossible d'activer {self.symbol}")
            return False
    
    def initialize_mt5(self):
        """Initialise MT5 pour ultra scalping"""
        if not mt5.initialize():
            safe_log("❌ Échec initialisation MT5")
            return False
        
        # Connexion compte
        if not mt5.login(MT5_LOGIN, password=MT5_PASSWORD, server=MT5_SERVER):
            safe_log(f"❌ Échec connexion compte {MT5_LOGIN}")
            safe_log(f"Erreur: {mt5.last_error()}")
            mt5.shutdown()
            return False
        
        safe_log("✅ MT5 initialisé pour ULTRA SCALPING")
        
        # Infos compte
        account_info = mt5.account_info()
        if account_info:
            safe_log(f"💰 Balance: ${account_info.balance:.2f}")
            safe_log(f"📊 Équité: ${account_info.equity:.2f}")
        
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
    
    def calculate_adaptive_lot_size(self):
        """Calcule la taille du lot adaptée à la balance du compte"""
        try:
            account_info = mt5.account_info()
            if not account_info:
                safe_log("⚠️ Impossible de récupérer les infos compte, lot par défaut: 0.01")
                return 0.01
            
            balance = account_info.balance
            
            # Logique adaptative basée sur la balance
            if balance < 2000:
                lot_size = 0.01
            elif balance < 3000:
                lot_size = 0.02
            elif balance < 4000:
                lot_size = 0.03
            elif balance < 5000:
                lot_size = 0.04
            elif balance < 6000:
                lot_size = 0.05
            elif balance < 7000:
                lot_size = 0.06
            elif balance < 8000:
                lot_size = 0.07
            elif balance < 9000:
                lot_size = 0.08
            elif balance < 10000:
                lot_size = 0.09
            else:
                # Pour les balances > 10000, on continue la progression par tranches de 1000
                tranche = int(balance / 1000)
                lot_size = min(tranche * 0.01, 500)  # Maximum 500 lots pour la sécurité

            safe_log(f"💰 Balance: ${balance:.2f} → Lot adaptatif: {lot_size}")
            return lot_size
            
        except Exception as e:
            safe_log(f"❌ Erreur calcul lot adaptatif: {e}")
            return 0.01  # Valeur par défaut en cas d'erreur
    
    def calculate_daily_profit_target(self, balance):
        """Calcule l'objectif de profit quotidien basé sur la balance (10% par tranche de 1000€)"""
        try:
            # Calcul par tranches de 1000€ avec objectif de 10% (100€ par tranche de 1000€)
            tranche = int(balance / 1000)  # Tranche de 1000€
            
            if tranche == 0:  # 0-999€
                target = 100
            else:  # 1000€+, 100€ par tranche de 1000€
                target = tranche * 100
            
            safe_log(f"🎯 Balance: ${balance:.2f} → Objectif quotidien: {target}€ (tranche {tranche})")
            return target
            
        except Exception as e:
            safe_log(f"❌ Erreur calcul objectif quotidien: {e}")
            return 100  # Objectif par défaut
    
    def initialize_daily_profit_system(self):
        """Initialise le système de profit quotidien au démarrage ou nouveau jour"""
        try:
            account_info = mt5.account_info()
            if not account_info:
                safe_log("⚠️ Impossible d'initialiser le système de profit quotidien")
                return
            
            current_balance = account_info.balance
            today = datetime.now().date()
            
            # Sauvegarde de la balance de départ du jour
            self.daily_start_balance = current_balance
            self.daily_profit_target = self.calculate_daily_profit_target(current_balance)
            
            # Reset des stats quotidiennes
            self.stats['daily_start'] = today
            self.stats['daily_profit'] = 0
            self.stats['daily_limit_reached'] = False
            
            safe_log(f"🌅 SYSTÈME PROFIT QUOTIDIEN INITIALISÉ:")
            safe_log(f"   📅 Date: {today.strftime('%d/%m/%Y')}")
            safe_log(f"   💰 Balance de départ: {self.daily_start_balance:.2f}€")
            safe_log(f"   🎯 Objectif quotidien: {self.daily_profit_target}€")
            safe_log(f"   📊 Balance cible: {self.daily_start_balance + self.daily_profit_target:.2f}€")
            
        except Exception as e:
            safe_log(f"❌ Erreur initialisation système profit quotidien: {e}")
    
    def display_profit_status(self):
        """Affiche le statut détaillé du profit toutes les 10 secondes"""
        try:
            # Calcul du profit en temps réel
            current_profit = self.calculate_real_time_daily_profit()
            
            # Récupération de la balance actuelle
            account_info = mt5.account_info()
            if not account_info:
                return
            
            current_balance = account_info.balance
            target_balance = self.daily_start_balance + self.daily_profit_target
            remaining_profit = self.daily_profit_target - current_profit
            progress_pct = (current_profit / self.daily_profit_target * 100) if self.daily_profit_target > 0 else 0
            
            # Statut emoji basé sur le progrès
            if progress_pct >= 100:
                status_emoji = "🎯✅"  # Objectif atteint
            elif progress_pct >= 75:
                status_emoji = "🔥"    # Très proche
            elif progress_pct >= 50:
                status_emoji = "📈"    # Bon progrès
            elif progress_pct >= 25:
                status_emoji = "⚡"    # En cours
            else:
                status_emoji = "🌱"    # Démarrage
            
            safe_log(f"")
            safe_log(f"{status_emoji} ═══ STATUT PROFIT QUOTIDIEN ═══")
            safe_log(f"💰 Balance actuelle: {current_balance:.2f}€")
            safe_log(f"🏁 Balance de départ: {self.daily_start_balance:.2f}€")
            safe_log(f"🎯 Objectif du jour: {self.daily_profit_target}€")
            safe_log(f"📊 Profit actuel: {current_profit:+.2f}€")
            safe_log(f"📈 Progrès: {progress_pct:.1f}% ({current_profit:.0f}€/{self.daily_profit_target}€)")
            safe_log(f"⏳ Restant à faire: {remaining_profit:+.2f}€")
            safe_log(f"🎪 Balance cible: {target_balance:.2f}€")
            safe_log(f"════════════════════════════════")
            safe_log(f"")
            
        except Exception as e:
            safe_log(f"⚠️ Erreur affichage statut profit: {e}")
    
    def calculate_real_time_daily_profit(self):
        """Calcule le profit quotidien en temps réel basé sur la balance actuelle"""
        try:
            account_info = mt5.account_info()
            if not account_info:
                return 0
            
            current_balance = account_info.balance
            
            # Formule: (Balance de départ + Objectif) - Balance actuelle = Reste à gagner
            # Donc: Objectif - Reste à gagner = Profit actuel
            balance_target = self.daily_start_balance + self.daily_profit_target
            remaining_to_earn = balance_target - current_balance
            current_profit = self.daily_profit_target - remaining_to_earn
            
            # Debug pour comprendre le calcul
            safe_log(f"🔍 Calcul profit temps réel:")
            safe_log(f"   💰 Balance départ: {self.daily_start_balance:.2f}€")
            safe_log(f"   🎯 Objectif: {self.daily_profit_target}€")
            safe_log(f"   📊 Balance cible: {balance_target:.2f}€")
            safe_log(f"   💳 Balance actuelle: {current_balance:.2f}€")
            safe_log(f"   📈 Reste à gagner: {remaining_to_earn:.2f}€")
            safe_log(f"   ✅ PROFIT ACTUEL: {current_profit:.2f}€/{self.daily_profit_target}€")
            
            return current_profit
            
        except Exception as e:
            safe_log(f"❌ Erreur calcul profit temps réel: {e}")
            return 0
    
    def place_real_order(self, trade_type, entry_price, tp_price, sl_price, signal):
        """Place un ordre réel sur MT5"""
        try:
            # Vérification connexion MT5
            if not mt5.terminal_info():
                safe_log("❌ MT5 non connecté")
                return False
            
            # Type d'ordre
            order_type = mt5.ORDER_TYPE_SELL if trade_type == "SELL" else mt5.ORDER_TYPE_BUY
            
            # Volume (lot size adaptatif basé sur la balance)
            volume = self.calculate_adaptive_lot_size()
            
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
            
            # Calcul TP en points
            point = symbol_info.point
            digits = symbol_info.digits
            
            if trade_type == "SELL":
                tp_points = int((price - tp_price) / point)
            else:
                tp_points = int((tp_price - price) / point)
            
            safe_log(f"🎯 TP Points: {tp_points} | Point size: {point}")
            
            # Request de trading
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": volume,
                "type": order_type,
                "price": price,
                "tp": tp_price,
                "deviation": 20,  # Déviation de prix plus large
                "magic": 123456,  # Magic number
                "comment": f"UltraScalp_{signal['reason'][:20]}",  # Limité à 20 chars
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
                'open_price': result.price,
                'tp': tp_price,
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
    
    def check_and_move_sl_to_breakeven(self):
        """
        🔒 VERROUILLAGE DES GAINS - Stop Loss à Breakeven
        ================================================
        
        Le Principe : Un trade gagnant ne doit jamais se transformer en trade perdant.
        Une fois qu'un certain niveau de profit est atteint, on sécurise la position 
        pour qu'au pire, elle se termine à zéro.
        
        Comment ça marche :
        - Dès que le trade atteint +15 pips (analyse TOUTES LES SECONDES)
        - On déplace automatiquement le SL initial vers le prix d'entrée
        - Scénario 1 (Idéal): Prix continue → TP à 23 pips
        - Scénario 2 (Reversal): Prix se retourne → SL à 0€ au lieu de -30€
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
        
        for position in self.open_positions:
            ticket = position['ticket']
            entry_price = position['open_price']
            position_type = position['type']
            
            # Recherche de la position correspondante sur MT5
            mt5_position = None
            for mt5_pos in mt5_positions:
                if mt5_pos.ticket == ticket:
                    mt5_position = mt5_pos
                    break
            
            if not mt5_position:
                continue
            
            # Vérification si c'est un trade BUY
            if position_type == 'BUY':
                current_profit_pips = (current_price.bid - entry_price) / 0.01  # Profit en pips
                
                # Seuil de verrouillage : +15 pips (breakeven plus agressif)
                if current_profit_pips >= 15.0:
                    
                    # Vérification si le SL n'est pas déjà au breakeven
                    if mt5_position.sl < entry_price - 0.1:  # SL encore loin du prix d'entrée
                        
                        # Déplacement du SL au prix d'entrée (breakeven)
                        new_sl = entry_price
                        
                        # Modification de la position sur MT5
                        request = {
                            "action": mt5.TRADE_ACTION_SLTP,
                            "symbol": self.symbol,
                            "position": ticket,
                            "sl": new_sl,
                            "tp": mt5_position.tp,  # Garde le même TP
                        }
                        
                        result = mt5.order_send(request)
                        
                        if result.retcode == mt5.TRADE_RETCODE_DONE:
                            safe_log(f"🔒 GAINS VERROUILLÉS! Ticket {ticket}")
                            safe_log(f"   💰 Profit actuel: +{current_profit_pips:.1f} pips")
                            safe_log(f"   🛡️ SL déplacé au breakeven: ${new_sl:.2f}")
                            safe_log(f"   ✅ Trade sécurisé: Perte max = 0€")
                        else:
                            safe_log(f"❌ Échec déplacement SL pour {ticket}: {result.comment}")
    
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
                "comment": "Fermeture_timeout_30min",
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
    
    def check_daily_profit_limit(self):
        """Vérifie si la limite journalière de profit est atteinte"""
        today = datetime.now().date()
        
        # Reset si nouveau jour
        if self.stats['daily_start'] != today:
            safe_log(f"🌅 Nouveau jour détecté - Reinitialisation du système")
            self.initialize_daily_profit_system()
        
        # Calcul du profit en temps réel
        current_daily_profit = self.calculate_real_time_daily_profit()
        self.stats['daily_profit'] = current_daily_profit
        
        # Vérification de la limite (objectif atteint)
        if current_daily_profit >= self.daily_profit_target and not self.stats['daily_limit_reached']:
            self.stats['daily_limit_reached'] = True
            safe_log(f"🎯 OBJECTIF QUOTIDIEN ATTEINT ! {current_daily_profit:.2f}€/{self.daily_profit_target}€")
            safe_log(f"⏸️ Arrêt des nouveaux trades - En attente que les positions ouvertes deviennent positives")
            return True
            
        return self.stats['daily_limit_reached']
    
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
                    
                    # Logique améliorée de détection SL/TP
                    close_type = "MANUAL"  # Par défaut
                    
                    # 1. D'abord vérifier le commentaire
                    if "tp" in comment or "take profit" in comment:
                        close_type = "TP"
                    elif "sl" in comment or "stop loss" in comment:
                        close_type = "SL"
                    else:
                        # 2. Si commentaire peu fiable, analyser le profit ET la raison
                        # Pour les SELL: TP = profit positif, SL = profit négatif
                        # Pour les BUY: TP = profit positif, SL = profit négatif
                        if total_profit > 0.05:  # Seuil minimum pour TP
                            close_type = "TP"
                        elif total_profit < -0.05:  # Seuil minimum pour SL
                            close_type = "SL"
                        else:
                            # 3. Profit très faible, analyser plus finement
                            close_type = "BREAKEVEN"
                    
                    safe_log(f"🔍 Debug profit détaillé - Ticket {ticket}:")
                    safe_log(f"   💰 Profit brut: {total_profit:.2f}€")
                    safe_log(f"   📝 Commentaire MT5: '{comment}'")
                    safe_log(f"   🎯 Type final: {close_type}")
                    safe_log(f"   ⚖️ Logique: {'Profit > 0.05' if total_profit > 0.05 else 'Perte < -0.05' if total_profit < -0.05 else 'Neutre'}")
                    
                    return {
                        'profit': total_profit,
                        'type': close_type,
                        'comment': comment
                    }
                else:
                    # Fallback: sommer tous les deals si pas de deal de sortie spécifique
                    total_profit = sum(deal.profit for deal in deals)
                    safe_log(f"🔍 Debug profit (fallback) - Ticket {ticket}: {total_profit:.2f}€")
                    
                    close_type = "SL" if total_profit < -0.05 else "TP" if total_profit > 0.05 else "BREAKEVEN"
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
            safe_log(f"💰 Profit journalier mis à jour: {self.stats['daily_profit']:.2f}€/{DAILY_PROFIT_LIMIT}€")
            safe_log(f"   📊 Base manuelle: {self.manual_daily_profit:.2f}€ + Trades bot: {self.bot_trades_profit:.2f}€")
        else:
            # Sinon ajout direct classique
            self.stats['daily_profit'] += profit_amount
            safe_log(f"💰 Profit journalier mis à jour: {self.stats['daily_profit']:.2f}€/{DAILY_PROFIT_LIMIT}€")
    
    def force_update_manual_profit(self, new_manual_profit):
        """Force la mise à jour du profit manuel (pour corrections)"""
        if self.manual_daily_profit is not None:
            old_profit = self.manual_daily_profit
            self.manual_daily_profit = new_manual_profit
            self.stats['daily_profit'] = self.manual_daily_profit + self.bot_trades_profit
            safe_log(f"🔄 Profit manuel corrigé: {old_profit:.2f}€ → {new_manual_profit:.2f}€")
            safe_log(f"💰 Nouveau profit total: {self.stats['daily_profit']:.2f}€/{DAILY_PROFIT_LIMIT}€")
        else:
            # Si pas de profit manuel, on l'initialise
            self.manual_daily_profit = new_manual_profit
            self.bot_trades_profit = 0
            self.stats['daily_profit'] = new_manual_profit
            safe_log(f"✅ Profit manuel initialisé: {new_manual_profit:.2f}€")
            safe_log(f"💰 Profit total: {self.stats['daily_profit']:.2f}€/{DAILY_PROFIT_LIMIT}€")
    
    def force_profit_sync_now(self):
        """Force une synchronisation immédiate du profit avec MT5"""
        safe_log("🔄 Synchronisation forcée du profit...")
        safe_log(f"✅ Profit actuel: {self.stats['daily_profit']:.2f}€/{DAILY_PROFIT_LIMIT}€")
    
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
            safe_log(f"🏁 Toutes les positions fermées - Journée terminée avec {self.stats['daily_profit']:.2f}€ de profit")
            return True
            
        return False
    
    def detect_ultra_trend(self, data):
        """Détection ultra rapide de tendance pour scalping (sans pandas)"""
        if len(data) < max(TREND_EMA_SLOW, RSI_PERIOD):
            return "UNKNOWN", 0, {'ema_fast': 0, 'ema_slow': 0, 'rsi': 50, 'price': 0, 'ema_diff_pct': 0}
        
        # Extraction des prix de clôture
        close_prices = [candle['close'] for candle in data]
        
        # Calcul EMA rapide (méthode simple)
        ema_fast = self.calculate_ema(close_prices, TREND_EMA_FAST)
        ema_slow = self.calculate_ema(close_prices, TREND_EMA_SLOW)
        
        # Calcul RSI simple
        rsi = self.calculate_rsi(close_prices, RSI_PERIOD)
        
        # Valeurs actuelles
        current_ema_fast = ema_fast[-1]
        current_ema_slow = ema_slow[-1]
        current_rsi = rsi[-1] if rsi else 50
        current_price = close_prices[-1]
        
        # Détection ultra sensible
        ema_diff = current_ema_fast - current_ema_slow
        ema_diff_pct = (ema_diff / current_price) * 100 if current_price != 0 else 0
        
        # Force de tendance (plus élevé = plus fort)
        strength = abs(ema_diff_pct) * 100
        
        # Logique de détection
        if current_ema_fast > current_ema_slow and current_rsi > 50:
            trend = "BULLISH"  # Hausse détectée
        elif current_ema_fast < current_ema_slow and current_rsi < 50:
            trend = "BEARISH"  # Baisse détectée
        else:
            trend = "SIDEWAYS"  # Pas de tendance claire
        
        # Mise à jour historique
        if trend != self.trend_data['current_trend']:
            self.trend_data['last_trend_change'] = datetime.now()
            self.trend_data['trend_duration'] = 0
        else:
            self.trend_data['trend_duration'] += 1
        
        self.trend_data['current_trend'] = trend
        self.trend_data['trend_strength'] = strength
        
        return trend, strength, {
            'ema_fast': current_ema_fast,
            'ema_slow': current_ema_slow,
            'rsi': current_rsi,
            'price': current_price,
            'ema_diff_pct': ema_diff_pct
        }
    
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
    
    def should_open_position(self, trend, strength, indicators):
        """Décide si on doit ouvrir une position BUY"""
        
        # Vérification limite journalière de profit
        if self.stats['daily_limit_reached']:
            return None  # Pas de nouveaux trades si limite atteinte
        
        # Vérification limites globales
        if self.position_count >= MAX_POSITIONS:
            return None
        
        # On ne trade que si la tendance est claire et forte
        if trend == "SIDEWAYS" or strength < 0.01:  # Force minimum 0.01%
            return None
        
        current_rsi = indicators['rsi']
        
        # LOGIQUE BUY UNIQUEMENT:
        # Si marché BEARISH (baisse) → BUY (bet sur rebond)
        # Plus de SELL - Seulement des achats
        
        if trend == "BEARISH" and strength > 0.015:  # Baisse forte
            # Conditions pour ACHETER (contre la baisse)
            if current_rsi < self.config['RSI_OVERSOLD']:  # RSI selon config
                return {
                    'type': 'BUY', 
                    'reason': 'FADE_BEARISH_TREND',
                    'strength': strength,
                    'rsi': current_rsi,
                    'confidence': min(strength * 50, 0.9)
                }
        
        return None
    
    def execute_ultra_scalp_trade(self, signal, current_price):
        """Exécute un trade de scalping ultra rapide"""
        
        trade_type = signal['type']
        
        # Récupération prix réel pour calcul TP
        tick_info = mt5.symbol_info_tick(self.symbol)
        if tick_info is None:
            safe_log("❌ Impossible de récupérer prix pour TP")
            return
        
        # Calcul des niveaux avec prix réel
        if trade_type == 'BUY':
            entry_price = tick_info.ask  # Prix d'achat réel
            tp_price = entry_price + (TP_PIPS * 0.01)  # TP à +TP_PIPS pips
            sl_price = entry_price - (1170 * 0.01)  # SL à -1170 points pour les BUY
        else:  # SELL
            entry_price = tick_info.bid  # Prix de vente réel
            tp_price = entry_price - (TP_PIPS * 0.01)  # TP à -TP_PIPS pips 
            sl_price = entry_price + (TP_PIPS * 2 * 0.01) if USE_STOP_LOSS else None  # SL à 2x TP pour SELL seulement
        
        # Log du signal
        safe_log(f"⚡ ULTRA SCALP {trade_type} - {signal['reason']}")
        safe_log(f"   💰 Prix: ${entry_price:.2f}")
        safe_log(f"   🎯 TP: ${tp_price:.2f} ({TP_PIPS} pips)")
        safe_log(f"   🛡️ SL: {'AUCUN' if sl_price is None else f'${sl_price:.2f}'}")
        safe_log(f"   📊 Force: {signal['strength']:.3f}% | RSI: {signal['rsi']:.1f}")
        safe_log(f"   🎲 Confiance: {signal['confidence']:.2f}")
        
        if ENABLE_REAL_TRADING:
            # 🚀 TRADING RÉEL MT5
            success = self.place_real_order(trade_type, entry_price, tp_price, sl_price, signal)
            if success:
                safe_log("✅ ORDRE PLACÉ SUR MT5!")
                return
            else:
                safe_log("❌ Échec placement ordre MT5")
                return
        
        # Simulation résultat (pour test)
        # Dans le vrai bot, on surveillerait les positions réelles
        # Simulation ultra rapide du résultat
        
        # Calcul du lot adaptatif pour la simulation
        adaptive_lot = self.calculate_adaptive_lot_size()
        
        trade_success = random.random() < 0.85  # 85% de réussite en simulation
        profit_pips = 0
        loss_pips = 0  
        profit_usd = 0
        loss_usd = 0
        
        if trade_success:
            profit_pips = TP_PIPS
            profit_usd = profit_pips * adaptive_lot * 1  # Approximation avec lot adaptatif
            safe_log(f"✅ SCALP GAGNANT: +{profit_pips} pips = +${profit_usd:.2f}")
            self.stats['winning_trades'] += 1
        else:
            # Si pas de SL, on simule une petite perte (marché contre nous)
            if USE_STOP_LOSS:
                loss_pips = -10
                loss_usd = loss_pips * adaptive_lot * 1
                safe_log(f"❌ Scalp perdant: {loss_pips} pips = ${loss_usd:.2f}")
            else:
                # Sans SL, on simule que ça revient en notre faveur rapidement
                if random.random() < 0.8:  # 80% de chance de récupération rapide
                    profit_pips = 1  # Petit profit à terme
                    profit_usd = profit_pips * adaptive_lot * 1
                    safe_log(f"🔄 Récupération: +{profit_pips} pip = +${profit_usd:.2f}")
                    self.stats['winning_trades'] += 1
                else:
                    loss_pips = -5  # Perte modérée sans SL
                    loss_usd = loss_pips * adaptive_lot * 1
                    safe_log(f"⚠️ Position défavorable: {loss_pips} pips = ${loss_usd:.2f}")
        
        # Mise à jour statistiques
        self.stats['total_trades'] += 1
        self.stats['total_pips'] += profit_pips if trade_success else loss_pips
        self.stats['total_profit'] += profit_usd if trade_success else loss_usd
        self.stats['last_trade_time'] = datetime.now()
        
        # Simulation position ouverte/fermée rapidement
        self.position_count += 1
        # Dans un vrai scalping, la position serait fermée en quelques secondes/minutes
        # Ici on simule une fermeture immédiate
        time.sleep(1)  # 1 seconde pour simuler la durée du trade
        self.position_count = max(0, self.position_count - 1)
        
        return True
    
    def run_ultra_scalping_cycle(self):
        """Exécute un cycle d'analyse du marché (toutes les 10 secondes)"""
        
        # Vérification de la limite journalière de profit
        daily_limit_reached = self.check_daily_profit_limit()
        
        # Si limite atteinte, fermer les positions profitables et attendre
        if daily_limit_reached:
            all_closed = self.close_profitable_positions()
            if all_closed:
                safe_log("🏁 Journée terminée - Arrêt du bot")
                self.is_trading = False
                return
            # Continue le cycle pour surveiller les positions restantes
        
        # Récupération données ultra rapides
        df = self.get_ultra_fast_data()
        if df is None:
            return
        
        # Détection tendance ultra rapide
        trend, strength, indicators = self.detect_ultra_trend(df)
        
        current_price = indicators['price']  # Utilise le prix depuis les indicateurs
        
        # Affichage détaillé du statut profit toutes les 10 secondes
        self.display_profit_status()
        
        # Affichage état marché (compact pour scalping)
        open_positions_count = len(self.open_positions)
        daily_status = f"💰{self.stats['daily_profit']:.1f}€/{self.daily_profit_target}€"
        if self.stats['daily_limit_reached']:
            daily_status += " ⏸️"
        safe_log(f"📊 ${current_price:.2f} | {trend} {strength:.3f}% | RSI:{indicators['rsi']:.1f} | BUY:{self.buy_positions_count} | {daily_status}")
        
        # Vérification signal BUY
        signal = self.should_open_position(trend, strength, indicators)
        
        if signal:
            safe_log(f"🔥 SIGNAL BUY: {signal['type']} vs {trend}")
            self.execute_ultra_scalp_trade(signal, current_price)
        
        # Affichage stats rapides toutes les 10 trades
        if self.stats['total_trades'] > 0 and self.stats['total_trades'] % 10 == 0:
            self.display_ultra_stats()
    
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
        safe_log(f"� Baisse → BUY (bet sur rebond)")
        safe_log(f"🚫 Plus de SELL - Seulement des achats")
        safe_log(f"🎯 TP: {TP_PIPS} pips | SL: AUCUN")
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
    
    def run_ultra_scalping_unlimited(self):
        """Lance l'ultra scalping en mode illimité"""
        safe_log(f"\n🔥 ULTRA SCALPING - MODE ILLIMITÉ")
        safe_log("="*60)
        safe_log(f"♾️ Session sans limite de temps")
        safe_log(f"⚡ Analyse toutes les {ANALYSIS_INTERVAL} secondes")
        safe_log(f"🎯 TP: {TP_PIPS} pips | SL: AUCUN")
        safe_log(f"⏹️ Arrêt: Ctrl+C")
        
        self.is_trading = True
        cycle_count = 0
        last_market_analysis = 0  # Compteur pour l'analyse du marché
        
        try:
            while self.is_trading:
                cycle_count += 1
                
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
                
                time.sleep(1)  # Analyse breakeven toutes les secondes
                
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
    """Fonction principale Ultra Scalping"""
    safe_log("🔥 ULTRA SCALPING BOT - BUY UNIQUEMENT")
    safe_log("="*60)
    safe_log("⚡ Stratégie: Achats sur rebonds uniquement")
    safe_log("� Baisse détectée → BUY (bet sur rebond)") 
    safe_log("� Plus de SELL - Seulement des achats")
    safe_log(f"🎯 TP: {TP_PIPS} pips | SL: AUCUN (BUY seulement)")
    
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
        
        # Lancement du bot
        bot = UltraScalpingBot(manual_daily_profit=manual_profit)
        
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
