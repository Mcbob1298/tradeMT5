# =============================================================================
# PARAMÈTRES DE CONNEXION MT5
# =============================================================================
MT5_LOGIN = 5039077525
MT5_PASSWORD = "!oNvKqS4"
MT5_SERVER = "MetaQuotes-Demo"  # Changez selon votre broker

# =============================================================================
# STRATÉGIE "HYPER-SCALPING" (GAINS RAPIDES DE QUELQUES CENTIMES)
# =============================================================================
SYMBOL = "XAUUSD"

# === GESTION DU TRADE ===
# Take Profit en points de prix (ex: 0.30 = 0.30 de différence dans le prix XAUUSD). 
# ⚠️ C'est le paramètre le plus important pour cette stratégie !
# 5.0 points de prix = distance bien supérieure au minimum de 0.2 points requis par MT5
FIXED_TP_DOLLARS = 0.25

# Ratio du Stop Loss par rapport au Take Profit.
# 10.0 signifie que le SL sera 10 fois plus grand que le TP (50.0 points de prix pour 5.0 points de gain).
SL_MULTIPLIER = 10.0

# Taille du lot FIXE. Le calcul adaptatif est trop risqué pour cette stratégie.
# ⚠️ COMMENCEZ TRÈS PETIT (0.01) !
FIXED_LOT_SIZE = 0.01

# === NIVEAU D'AGRESSIVITÉ ===
# 1 = Ultra-agressif (fréquence maximale). RECOMMANDÉ pour cette stratégie.
# 2 = Équilibré
# 3 = Conservateur
CONFIDENCE_SCORE_REQUIRED = 3

# =============================================================================
# PARAMÈTRES OPÉRATIONNELS
# =============================================================================
ANALYSIS_INTERVAL = 1  # 1 seconde
MAGIC_NUMBER = 123456

# =============================================================================
# PARAMÈTRES DE LOG
# =============================================================================
LOG_ACTIVE_INTERVAL = 60
LOG_POSITION_INTERVAL = 30

# =============================================================================
# ANCIENS PARAMÈTRES (GARDÉS POUR COMPATIBILITÉ)
# =============================================================================
# Ces paramètres ne sont plus utilisés dans la stratégie Hyper-Scalping
# mais gardés pour éviter les erreurs d'importation
RISK_REWARD_RATIO = 1.5  # Obsolète - remplacé par SL_MULTIPLIER
RISK_PER_TRADE_PERCENT = 1.0  # Obsolète - remplacé par FIXED_LOT_SIZE
MAX_TRADES_PER_MINUTE = 999  # Limite désactivée pour Hyper-Scalping extrême
ATR_MULTIPLIER = 1.5     # Obsolète
MIN_SL_DISTANCE = 0.10   # Obsolète
MAX_SL_DISTANCE = 2.00   # Obsolète
MA_PERIOD = 100
TICK_COUNT = 20
VOLATILITY_THRESHOLD = 0.5
LOT_SIZE = 0.01  # Obsolète
TAKE_PROFIT_PIPS = 8  # Obsolète
