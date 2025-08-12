# Configuration du Bot de Scalping XAUUSD
# Modifiez ces paramètres selon vos besoins

# =============================================================================
# PARAMÈTRES DE CONNEXION MT5
# =============================================================================
MT5_LOGIN = 95431708
MT5_PASSWORD = "5uBpUk-p"
MT5_SERVER = "MetaQuotes-Demo"  # Changez selon votre broker

# =============================================================================
# PARAMÈTRES DE TRADING
# =============================================================================
SYMBOL = "XAUUSD"
LOT_SIZE = 0.01  # ⚠️ Commencez petit ! Augmentez progressivement si profitable
TAKE_PROFIT_PIPS = 8  # Take Profit en pips (1 pip = 0.1 point sur XAUUSD)

# =============================================================================
# PARAMÈTRES D'ANALYSE TECHNIQUE
# =============================================================================
# Analyse de la moyenne mobile
MA_PERIOD = 5  # Période pour la moyenne mobile rapide

# Analyse de volatilité
TICK_COUNT = 20  # Nombre de ticks à analyser pour la volatilité
VOLATILITY_THRESHOLD = 0.5  # Seuil minimum de volatilité pour agir

# Gestion du risque dynamique (ATR)
RISK_REWARD_RATIO = 1.5  # Ratio Risque/Récompense cible (1.5:1)
ATR_MULTIPLIER = 1.5     # Multiple de l'ATR pour le Stop Loss
MIN_SL_DISTANCE = 0.10   # Distance minimum du SL (10 pips)
MAX_SL_DISTANCE = 2.00   # Distance maximum du SL (200 pips)

# =============================================================================
# PARAMÈTRES OPÉRATIONNELS
# =============================================================================
ANALYSIS_INTERVAL = 1  # Intervalle entre analyses (en secondes)
MAGIC_NUMBER = 123456  # Numéro magique pour identifier les trades du bot

# Limites de positions (SCALPING SAIN : Qualité > Quantité)
MAX_POSITIONS_TOTAL = 2   # Maximum 2 positions simultanées au total
MAX_BUY_POSITIONS = 1     # Maximum 1 position BUY à la fois  
MAX_SELL_POSITIONS = 1    # Maximum 1 position SELL à la fois

# =============================================================================
# SEUILS DE DÉCISION
# =============================================================================
MIN_SIGNALS_REQUIRED = 2  # Nombre minimum de signaux concordants
DECISION_THRESHOLD = 0.3  # Seuil du score pour prendre une décision
MARKET_DEPTH_THRESHOLD = 0.1  # Seuil minimum de pression dans le carnet d'ordres

# =============================================================================
# PARAMÈTRES DE LOG
# =============================================================================
LOG_ACTIVE_INTERVAL = 60  # Fréquence du log "bot actif" (en itérations)
LOG_POSITION_INTERVAL = 30  # Fréquence du log "position ouverte" (en itérations)
