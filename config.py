# Configuration du Bot de Trading XAUUSD - Version Adaptative
# Modifiez ces paramètres selon vos besoins

# =============================================================================
# PARAMÈTRES DE CONNEXION MT5
# =============================================================================
MT5_LOGIN = 95431708
MT5_PASSWORD = "5uBpUk-p"
MT5_SERVER = "MetaQuotes-Demo"  # Changez selon votre broker

# =============================================================================
# PARAMÈTRES DE TRADING ADAPTATIF
# =============================================================================
SYMBOL = "XAUUSD"

# === GESTION DU RISQUE ADAPTATIVE ===
RISK_REWARD_RATIO = 1.5  # Ratio Risk/Reward (1.5:1 = 1.5$ de gain pour 1$ de risque)
ATR_MULTIPLIER = 1.5     # Multiplicateur ATR pour calcul dynamique SL/TP
MIN_SL_DISTANCE = 0.10   # Distance minimum SL en $ (sécurité)
MAX_SL_DISTANCE = 2.00   # Distance maximum SL en $ (éviter les SL trop larges)

# === SCORE DE CONFIANCE CONFIGURABLE ===
# 1 = Ultra-agressif (1/3 conditions = BEAUCOUP de trades)
# 2 = Équilibré (2/3 conditions = trades fréquents mais filtrés)  [RECOMMANDÉ]
# 3 = Conservateur (3/3 conditions = trades rares mais de haute qualité)
CONFIDENCE_SCORE_REQUIRED = 2

# =============================================================================
# PARAMÈTRES D'ANALYSE TECHNIQUE (LEGACY - GARDÉS POUR COMPATIBILITÉ)
# =============================================================================
MA_PERIOD = 5
TICK_COUNT = 20
VOLATILITY_THRESHOLD = 0.5
LOT_SIZE = 0.01  # ⚠️ Obsolète - Maintenant calculé dynamiquement
TAKE_PROFIT_PIPS = 8  # ⚠️ Obsolète - Maintenant basé sur ATR

# =============================================================================
# PARAMÈTRES OPÉRATIONNELS
# =============================================================================
ANALYSIS_INTERVAL = 1  # Intervalle entre analyses (en secondes)
MAGIC_NUMBER = 123456  # Numéro magique pour identifier les trades du bot

# =============================================================================
# PARAMÈTRES DE LOG
# =============================================================================
LOG_ACTIVE_INTERVAL = 60  # Fréquence du log "bot actif" (en itérations)
LOG_POSITION_INTERVAL = 30  # Fréquence du log "position ouverte" (en itérations)
