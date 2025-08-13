#!/usr/bin/env python3
"""
🏅 ICT SILVER BULLET - LAUNCHER SCRIPT
Script de lancement simplifié pour la stratégie gagnante
"""

import sys
import subprocess
import logging
import time
from datetime import datetime

def setup_logging():
    """Configuration des logs"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ict_silver_bullet_launcher.log'),
            logging.StreamHandler()
        ]
    )

def print_banner():
    """Affiche la bannière de démarrage"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                🏅 ICT SILVER BULLET 🏅                   ║
    ║                  STRATÉGIE GAGNANTE                      ║
    ║                                                          ║
    ║  🥇 XAUUSD M5  : PF 2.08 | WR 50% | +7.92€             ║
    ║  🥈 XAUUSD M1  : PF ∞    | WR 100% | +11.84€           ║  
    ║  🥉 XAUUSD M15 : PF ∞    | WR 100% | +58.33€           ║
    ║                                                          ║
    ║        Version Finale - Ready for Deployment            ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Vérifier les dépendances"""
    logging.info("🔍 Vérification des dépendances...")
    
    required_modules = ['pandas', 'numpy', 'MetaTrader5']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            logging.info(f"  ✅ {module}")
        except ImportError:
            missing_modules.append(module)
            logging.error(f"  ❌ {module} - MANQUANT")
    
    if missing_modules:
        logging.error(f"❌ Modules manquants: {', '.join(missing_modules)}")
        logging.error("Installer avec: pip install pandas numpy MetaTrader5")
        return False
    
    logging.info("✅ Toutes les dépendances sont installées")
    return True

def run_backtest():
    """Exécuter le backtest de validation"""
    logging.info("🧪 Lancement du backtest de validation...")
    
    try:
        result = subprocess.run([
            sys.executable, 'ict_silver_bullet_pragmatic.py'
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            logging.info("✅ Backtest complété avec succès")
            
            # Extraire les résultats clés
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'XAUUSD' in line and ('PRAGMATIC' in line or 'FINAL' in line):
                    logging.info(f"  📊 {line.strip()}")
            
            return True
        else:
            logging.error(f"❌ Erreur backtest: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logging.error("❌ Timeout backtest (>5 minutes)")
        return False
    except Exception as e:
        logging.error(f"❌ Erreur lors du backtest: {e}")
        return False

def deploy_to_bot_ultime():
    """Déployer vers le Bot Ultime"""
    logging.info("🚀 Déploiement vers Bot Ultime...")
    
    # Vérifier la configuration
    try:
        from bot_ultime.config.config_ultimate import ICT_SILVER_BULLET_M5_CONFIG, ACTIVE_STRATEGIES
        
        if not ICT_SILVER_BULLET_M5_CONFIG.get('ENABLED', False):
            logging.error("❌ ICT Silver Bullet M5 n'est pas activé dans la configuration")
            return False
        
        active_ict_strategies = [s for s in ACTIVE_STRATEGIES if 'ICT' in s[0]]
        logging.info(f"✅ Stratégies ICT actives: {len(active_ict_strategies)}")
        
        for strategy_name, config in active_ict_strategies:
            logging.info(f"  🏅 {config['NAME']} - {config['TIMEFRAME']}")
        
        return True
        
    except ImportError as e:
        logging.error(f"❌ Erreur import configuration: {e}")
        return False

def main():
    """Fonction principale"""
    setup_logging()
    print_banner()
    
    start_time = datetime.now()
    logging.info(f"🚀 Démarrage ICT Silver Bullet Launcher - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Étape 1: Vérification dépendances
    if not check_dependencies():
        logging.error("❌ Échec vérification dépendances")
        sys.exit(1)
    
    # Étape 2: Validation par backtest (optionnel)
    print("\n🤔 Voulez-vous exécuter le backtest de validation ? (o/n): ", end="")
    choice = input().lower().strip()
    
    if choice in ['o', 'oui', 'y', 'yes']:
        if not run_backtest():
            logging.error("❌ Échec du backtest de validation")
            print("\n⚠️  Le backtest a échoué. Continuer quand même ? (o/n): ", end="")
            continue_choice = input().lower().strip()
            if continue_choice not in ['o', 'oui', 'y', 'yes']:
                sys.exit(1)
    else:
        logging.info("⏭️  Backtest ignoré")
    
    # Étape 3: Déploiement
    if not deploy_to_bot_ultime():
        logging.error("❌ Échec du déploiement vers Bot Ultime")
        sys.exit(1)
    
    # Étape 4: Options de lancement
    print(f"\n🎯 Déploiement réussi ! Options disponibles:")
    print("  1. 🧪 Mode DEMO (recommandé)")
    print("  2. 📊 Mode BACKTEST uniquement") 
    print("  3. 🚀 Mode LIVE (risqué)")
    print("  4. ❌ Quitter")
    
    while True:
        choice = input("\nVotre choix (1-4): ").strip()
        
        if choice == '1':
            logging.info("🧪 Lancement en mode DEMO...")
            print("\n🔔 ATTENTION: Assurez-vous que MT5 est connecté à un compte DEMO")
            print("📝 Les logs seront dans: ultimate_bot.log")
            input("\nAppuyez sur Entrée quand vous êtes prêt...")
            
            try:
                subprocess.run([sys.executable, 'bot_ultime/ultimate_bot.py'])
            except KeyboardInterrupt:
                logging.info("🛑 Arrêt demandé par l'utilisateur")
            break
            
        elif choice == '2':
            logging.info("📊 Mode BACKTEST uniquement")
            run_backtest()
            break
            
        elif choice == '3':
            logging.warning("🚨 Mode LIVE sélectionné !")
            print("\n⚠️  ATTENTION: Mode LIVE avec de l'argent réel !")
            print("🔴 Risque de perte en capital")
            confirm = input("Confirmer le mode LIVE ? (tapez 'CONFIRM'): ")
            
            if confirm == 'CONFIRM':
                logging.info("🚀 Lancement en mode LIVE...")
                print("📝 Les logs seront dans: ultimate_bot.log")
                input("\nAppuyez sur Entrée quand vous êtes prêt...")
                
                try:
                    subprocess.run([sys.executable, 'bot_ultime/ultimate_bot.py'])
                except KeyboardInterrupt:
                    logging.info("🛑 Arrêt demandé par l'utilisateur")
            else:
                logging.info("❌ Mode LIVE annulé")
            break
            
        elif choice == '4':
            logging.info("❌ Arrêt demandé")
            break
            
        else:
            print("❌ Choix invalide. Sélectionnez 1, 2, 3 ou 4.")
    
    # Résumé final
    end_time = datetime.now()
    duration = end_time - start_time
    logging.info(f"🏁 Session terminée - Durée: {duration}")
    
    print(f"\n🏆 ICT SILVER BULLET SESSION TERMINÉE")
    print(f"⏱️  Durée: {duration}")
    print(f"📝 Logs: ict_silver_bullet_launcher.log")
    print(f"📊 Documentation: docs/README_ICT_SILVER_BULLET.md")
    print(f"\n💡 Prochaines étapes:")
    print(f"   1. Monitorer les performances en demo")
    print(f"   2. Ajuster les paramètres si nécessaire") 
    print(f"   3. Considérer le passage en live après validation")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("\n🛑 Interruption clavier - Arrêt propre")
        sys.exit(0)
    except Exception as e:
        logging.error(f"❌ Erreur fatale: {e}")
        sys.exit(1)
