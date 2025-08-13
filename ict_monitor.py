#!/usr/bin/env python3
"""
📊 ICT SILVER BULLET - PERFORMANCE MONITOR
Monitoring en temps réel des performances de la stratégie
"""

import time
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd

class ICTPerformanceMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.trades_log = []
        self.daily_stats = {}
        self.performance_targets = {
            'min_daily_trades': 1,
            'target_win_rate': 50.0,
            'target_profit_factor': 2.0,
            'max_daily_drawdown': -50.0,  # €
            'target_daily_profit': 20.0   # €
        }
        
        # Configuration des logs
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ict_monitor.log'),
                logging.StreamHandler()
            ]
        )
        
        logging.info("📊 ICT Performance Monitor initialisé")
    
    def load_trades_from_log(self, log_file: str = 'ultimate_bot.log') -> List[Dict]:
        """Charger les trades depuis les logs"""
        trades = []
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    # Rechercher les lignes d'entrée ICT
                    if 'ICT SILVER BULLET ENTRY' in line:
                        # Parser les informations de trade
                        try:
                            parts = line.split()
                            timestamp = ' '.join(parts[:2])
                            entry_type = 'SELL' if 'SELL' in line else 'BUY'
                            
                            # Extraire le prix (format variable)
                            price = None
                            for part in parts:
                                if '@' in part:
                                    price_str = part.replace('@', '').replace(',', '')
                                    try:
                                        price = float(price_str)
                                        break
                                    except:
                                        continue
                            
                            if price:
                                trades.append({
                                    'timestamp': timestamp,
                                    'type': entry_type,
                                    'entry_price': price,
                                    'status': 'OPEN'
                                })
                        except Exception as e:
                            logging.warning(f"Erreur parsing ligne trade: {e}")
                    
                    # Rechercher les lignes de sortie
                    elif 'EXIT:' in line and ('TP' in line or 'SL' in line):
                        try:
                            parts = line.split()
                            exit_reason = 'TP' if 'TP' in line else 'SL'
                            
                            # Extraire le profit
                            profit = None
                            for part in parts:
                                if '€' in part:
                                    profit_str = part.replace('€', '').replace('+', '').replace('=', '')
                                    try:
                                        profit = float(profit_str)
                                        break
                                    except:
                                        continue
                            
                            # Mettre à jour le dernier trade ouvert
                            for trade in reversed(trades):
                                if trade.get('status') == 'OPEN':
                                    trade['status'] = 'CLOSED'
                                    trade['exit_reason'] = exit_reason
                                    trade['profit'] = profit
                                    break
                        except Exception as e:
                            logging.warning(f"Erreur parsing ligne exit: {e}")
                            
        except FileNotFoundError:
            logging.warning(f"Fichier de log {log_file} non trouvé")
        except Exception as e:
            logging.error(f"Erreur lecture logs: {e}")
        
        return trades
    
    def calculate_daily_stats(self, trades: List[Dict]) -> Dict:
        """Calculer les statistiques quotidiennes"""
        today = datetime.now().date()
        today_trades = []
        
        for trade in trades:
            try:
                trade_date = datetime.strptime(trade['timestamp'].split()[0], '%Y-%m-%d').date()
                if trade_date == today:
                    today_trades.append(trade)
            except:
                continue
        
        if not today_trades:
            return {
                'date': today.strftime('%Y-%m-%d'),
                'total_trades': 0,
                'open_trades': 0,
                'closed_trades': 0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'net_profit': 0.0,
                'gross_profit': 0.0,
                'gross_loss': 0.0
            }
        
        closed_trades = [t for t in today_trades if t.get('status') == 'CLOSED']
        open_trades = [t for t in today_trades if t.get('status') == 'OPEN']
        
        # Calculs statistiques
        winning_trades = [t for t in closed_trades if t.get('profit', 0) > 0]
        losing_trades = [t for t in closed_trades if t.get('profit', 0) < 0]
        
        win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0.0
        gross_profit = sum(t.get('profit', 0) for t in winning_trades)
        gross_loss = abs(sum(t.get('profit', 0) for t in losing_trades))
        net_profit = gross_profit - gross_loss
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf') if gross_profit > 0 else 0.0
        
        return {
            'date': today.strftime('%Y-%m-%d'),
            'total_trades': len(today_trades),
            'open_trades': len(open_trades),
            'closed_trades': len(closed_trades),
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'net_profit': net_profit,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss
        }
    
    def generate_performance_report(self, stats: Dict) -> str:
        """Générer un rapport de performance"""
        targets = self.performance_targets
        
        # Status indicators
        trades_status = "✅" if stats['total_trades'] >= targets['min_daily_trades'] else "⚠️"
        wr_status = "✅" if stats['win_rate'] >= targets['target_win_rate'] else "❌"
        pf_status = "✅" if stats['profit_factor'] >= targets['target_profit_factor'] else "❌"
        profit_status = "✅" if stats['net_profit'] >= targets['target_daily_profit'] else "⚠️"
        
        if stats['net_profit'] <= targets['max_daily_drawdown']:
            profit_status = "🚨"
        
        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║                🏅 ICT SILVER BULLET - RAPPORT QUOTIDIEN 🏅        ║
╠══════════════════════════════════════════════════════════════════╣
║ Date: {stats['date']}                                         ║
║                                                                  ║
║ 📊 TRADES AUJOURD'HUI:                                          ║
║   Total Trades: {stats['total_trades']:>2} {trades_status}                                  ║
║   Trades Fermés: {stats['closed_trades']:>2}                                   ║
║   Trades Ouverts: {stats['open_trades']:>2}                                  ║
║                                                                  ║
║ 🎯 PERFORMANCE:                                                 ║
║   Win Rate: {stats['win_rate']:>6.1f}% {wr_status}                            ║
║   Profit Factor: {stats['profit_factor']:>6.2f} {pf_status}                          ║
║   Net Profit: {stats['net_profit']:>+8.2f}€ {profit_status}                       ║
║                                                                  ║
║ 💰 DÉTAILS:                                                     ║
║   Profits Bruts: {stats['gross_profit']:>+7.2f}€                          ║
║   Pertes Brutes: {stats['gross_loss']:>+7.2f}€                           ║
║                                                                  ║
║ 🎯 OBJECTIFS QUOTIDIENS:                                       ║
║   Min Trades: {targets['min_daily_trades']} | Win Rate: {targets['target_win_rate']:.0f}% | PF: {targets['target_profit_factor']:.1f} | Profit: {targets['target_daily_profit']:.0f}€ ║
╚══════════════════════════════════════════════════════════════════╝
        """
        
        return report.strip()
    
    def check_alerts(self, stats: Dict) -> List[str]:
        """Vérifier les alertes de performance"""
        alerts = []
        targets = self.performance_targets
        
        if stats['net_profit'] <= targets['max_daily_drawdown']:
            alerts.append(f"🚨 ALERTE DRAWDOWN: {stats['net_profit']:.2f}€ (limite: {targets['max_daily_drawdown']:.0f}€)")
        
        if stats['closed_trades'] >= 3 and stats['win_rate'] < 30:
            alerts.append(f"⚠️ ALERTE WIN RATE FAIBLE: {stats['win_rate']:.1f}% sur {stats['closed_trades']} trades")
        
        if stats['closed_trades'] >= 2 and stats['profit_factor'] < 1.0:
            alerts.append(f"⚠️ ALERTE PROFIT FACTOR: {stats['profit_factor']:.2f} < 1.0")
        
        if stats['total_trades'] == 0 and datetime.now().hour >= 16:
            alerts.append("ℹ️ INFO: Aucun trade aujourd'hui (après 16h)")
        
        return alerts
    
    def save_daily_report(self, stats: Dict, report: str):
        """Sauvegarder le rapport quotidien"""
        try:
            filename = f"reports/daily_report_{stats['date']}.txt"
            
            # Créer le dossier s'il n'existe pas
            import os
            os.makedirs('reports', exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
                f.write(f"\n\n🕐 Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            logging.info(f"📄 Rapport sauvegardé: {filename}")
            
            # Sauvegarder aussi en JSON pour l'historique
            json_filename = f"reports/daily_stats_{stats['date']}.json"
            with open(json_filename, 'w') as f:
                json.dump(stats, f, indent=2)
                
        except Exception as e:
            logging.error(f"❌ Erreur sauvegarde rapport: {e}")
    
    def monitor_loop(self):
        """Boucle de monitoring principal"""
        logging.info("🚀 Démarrage du monitoring ICT Silver Bullet")
        
        last_report_hour = -1
        
        try:
            while True:
                current_hour = datetime.now().hour
                
                # Charger les trades depuis les logs
                trades = self.load_trades_from_log()
                
                # Calculer les stats quotidiennes
                daily_stats = self.calculate_daily_stats(trades)
                
                # Générer le rapport (chaque heure ou à la demande)
                if current_hour != last_report_hour or current_hour in [9, 12, 15, 18, 21]:
                    report = self.generate_performance_report(daily_stats)
                    print(report)
                    
                    # Vérifier les alertes
                    alerts = self.check_alerts(daily_stats)
                    for alert in alerts:
                        logging.warning(alert)
                        print(f"\n{alert}")
                    
                    # Sauvegarder le rapport
                    self.save_daily_report(daily_stats, report)
                    
                    last_report_hour = current_hour
                
                # Monitoring continu léger
                if daily_stats['open_trades'] > 0:
                    logging.info(f"📊 {daily_stats['open_trades']} position(s) ouverte(s)")
                
                # Attendre 5 minutes avant le prochain check
                time.sleep(300)
                
        except KeyboardInterrupt:
            logging.info("🛑 Arrêt du monitoring demandé")
        except Exception as e:
            logging.error(f"❌ Erreur monitoring: {e}")

def main():
    """Fonction principale"""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║            📊 ICT SILVER BULLET PERFORMANCE MONITOR 📊           ║
    ║                                                                  ║
    ║  Monitoring en temps réel des performances de la stratégie       ║
    ║  - Rapport quotidien automatique                                 ║
    ║  - Alertes de performance                                        ║  
    ║  - Sauvegarde historique                                         ║
    ║                                                                  ║
    ║  Ctrl+C pour arrêter                                             ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    monitor = ICTPerformanceMonitor()
    monitor.monitor_loop()

if __name__ == "__main__":
    main()
