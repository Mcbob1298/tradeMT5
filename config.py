# Configuration du Bot de Scalping XAUUSD
# Modifiez ces paramètres selon vos besoins

# =============================================================================
# PARAMÈTRES DE CONNEXION MT5
# =============================================================================
MT5_LOGIN = 95421851
MT5_PASSWORD = "Rx*xYpA4"
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

# =============================================================================
# PARAMÈTRES OPÉRATIONNELS
# =============================================================================
ANALYSIS_INTERVAL = 1  # Intervalle entre analyses (en secondes)
MAGIC_NUMBER = 123456  # Numéro magique pour identifier les trades du bot

# Limites de positions
MAX_POSITIONS_TOTAL = 40  # Maximum de positions simultanées au total
MAX_BUY_POSITIONS = 20     # Maximum de positions BUY simultanées
MAX_SELL_POSITIONS = 20    # Maximum de positions SELL simultanées

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
