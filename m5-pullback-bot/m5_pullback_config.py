# -*- coding: utf-8 -*-
"""
CONFIGURATION ULTRA SCALPING BOT
================# Configuration YOLO (extrêmement risquée)
YOLO_CONFIG = {
    'TP_PIPS': 1,
    'USE_STOP_LOSS': False,
    'SL_PIPS': 0,
    'MAX_POSITIONS': 999,
    'RSI_OVERBOUGHT': 65,  # ULTRA AGRESSIF : 65 au lieu de 75
    'RSI_OVERSOLD': 35,    # ULTRA AGRESSIF : 35 au lieu de 25
    'MIN_TREND_STRENGTH': 0.08  # Plus strict : 0.08 au lieu de 0.005
}====

Paramètres pour le bot ultra agressif contre-tendance
Modifiez ces valeurs pour ajuster l'agressivité
"""

# =============================================================================
# PARAMÈTRES PRINCIPAUX
# =============================================================================

# Symbole et timeframe
SYMBOL = "XAUUSD"           # Or (très volatil pour scalping)
TIMEFRAME_M1 = True         # True = M1, False = M5
LOT_SIZE = 0.01             # Taille des lots (commencer petit!)

# Take Profit et Stop Loss
TP_PIPS = 2                 # Take Profit en pips (ultra petit!)
USE_STOP_LOSS = False       # True = SL activé, False = YOLO mode
SL_PIPS = 10                # Stop Loss en pips (si activé)

# Gestion des positions
MAX_POSITIONS = 5           # Nombre max de positions simultanées
ANALYSIS_INTERVAL = 10      # Secondes entre chaque analyse

# =============================================================================
# DÉTECTION DE TENDANCE (Ultra Sensible)
# =============================================================================

# EMAs pour détection rapide
TREND_EMA_FAST = 5          # EMA rapide (5 périodes)
TREND_EMA_SLOW = 10         # EMA lente (10 périodes)

# RSI ultra réactif
RSI_PERIOD = 7              # Période RSI (très court)
RSI_OVERBOUGHT = 65         # Seuil overbought (plus bas = plus sensible)
RSI_OVERSOLD = 35           # Seuil oversold (plus haut = plus sensible)

# Force minimum de tendance
MIN_TREND_STRENGTH = 0.015  # 0.015% minimum pour trader

# =============================================================================
# CONFIGURATIONS PRÉDÉFINIES
# =============================================================================

# Configuration CONSERVATIVE (moins risquée)
CONSERVATIVE_CONFIG = {
    'TP_PIPS': 3,
    'USE_STOP_LOSS': True,
    'SL_PIPS': 8,
    'MAX_POSITIONS': 2,
    'RSI_OVERBOUGHT': 70,
    'RSI_OVERSOLD': 30,
    'MIN_TREND_STRENGTH': 0.02
}

# Configuration BALANCED (équilibrée)
BALANCED_CONFIG = {
    'TP_PIPS': 2,
    'USE_STOP_LOSS': False,
    'SL_PIPS': 10,
    'MAX_POSITIONS': 3,
    'RSI_OVERBOUGHT': 65,
    'RSI_OVERSOLD': 35,
    'MIN_TREND_STRENGTH': 0.015
}

# Configuration AGGRESSIVE (très risquée)
AGGRESSIVE_CONFIG = {
    'TP_PIPS': 1,
    'USE_STOP_LOSS': False,
    'SL_PIPS': 15,
    'MAX_POSITIONS': 8,
    'RSI_OVERBOUGHT': 60,
    'RSI_OVERSOLD': 40,
    'MIN_TREND_STRENGTH': 0.01
}

# Configuration YOLO (extrêmement risquée)
YOLO_CONFIG = {
    'TP_PIPS': 1,
    'USE_STOP_LOSS': False,
    'SL_PIPS': 0,
    'MAX_POSITIONS': 10,
    'RSI_OVERBOUGHT': 55,
    'RSI_OVERSOLD': 45,
    'MIN_TREND_STRENGTH': 0.005
}

# =============================================================================
# CONFIGURATION ACTIVE
# =============================================================================

# Choisissez votre configuration ici:
ACTIVE_CONFIG = BALANCED_CONFIG  # Changez ici: CONSERVATIVE, BALANCED, AGGRESSIVE, YOLO

def get_active_config():
    """Retourne la configuration active"""
    return ACTIVE_CONFIG

def apply_config(config_name):
    """Applique une configuration prédéfinie"""
    global ACTIVE_CONFIG
    
    configs = {
        'CONSERVATIVE': CONSERVATIVE_CONFIG,
        'BALANCED': BALANCED_CONFIG, 
        'AGGRESSIVE': AGGRESSIVE_CONFIG,
        'YOLO': YOLO_CONFIG
    }
    
    if config_name in configs:
        ACTIVE_CONFIG = configs[config_name]
        return True
    return False

# =============================================================================
# SESSIONS DE TRADING OPTIMALES
# =============================================================================

# Sessions recommandées pour l'ultra scalping (UTC)
OPTIMAL_SESSIONS = {
    'LONDON_OPEN': (8, 10),      # Ouverture Londres (volatile)
    'NY_OPEN': (13, 15),         # Ouverture New York (très volatile)
    'OVERLAP': (13, 16),         # Overlap Londres/NY (maximal volatilité)
    'ASIAN_CLOSE': (6, 8),       # Fermeture Asie (mouvements)
}

def is_optimal_session():
    """Vérifie si on est dans une session optimale"""
    from datetime import datetime
    current_hour = datetime.utcnow().hour
    
    for session, (start, end) in OPTIMAL_SESSIONS.items():
        if start <= current_hour < end:
            return True, session
    
    return False, None

# =============================================================================
# NOTES D'UTILISATION
# =============================================================================

USAGE_NOTES = """
🔥 ULTRA SCALPING - NOTES D'UTILISATION

⚡ STRATÉGIE:
  - Détecte la tendance principale
  - Trade CONTRE la tendance (fade strategy)
  - TP ultra petit (1-3 pips)
  - SL optionnel (ou mode YOLO)

📈 LOGIQUE:
  - Hausse détectée → SELL (bet sur correction)
  - Baisse détectée → BUY (bet sur rebond)

⚠️ RISQUES:
  - Stratégie très risquée
  - Peut générer beaucoup de pertes sans SL
  - Nécessite surveillance constante
  - Capital à risque uniquement

🎯 OPTIMISATIONS:
  - Trader pendant sessions volatiles
  - Ajuster TP selon la volatilité
  - Limiter le nombre de positions
  - Tester en simulation d'abord

💡 CONSEILS:
  - Commencer avec config CONSERVATIVE
  - Augmenter progressivement l'agressivité
  - Toujours tester en démo d'abord
  - Définir une limite de perte quotidienne
"""

def print_usage_notes():
    """Affiche les notes d'utilisation"""
    print(USAGE_NOTES)

if __name__ == "__main__":
    print("📋 CONFIGURATION ULTRA SCALPING")
    print("="*50)
    print(f"Configuration active: {list(ACTIVE_CONFIG.keys())[0] if ACTIVE_CONFIG else 'Personnalisée'}")
    print("\nParamètres actuels:")
    for key, value in ACTIVE_CONFIG.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*50)
    print_usage_notes()
