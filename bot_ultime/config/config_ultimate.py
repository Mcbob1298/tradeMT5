# =============================================================================
# CONFIGURATION DU BOT ULTIME - SYSTÈME MULTI-STRATÉGIES
# =============================================================================

# --- CONNEXION MT5 ---
MT5_LOGIN = 5039079528
MT5_PASSWORD = "PuY_M2Ba"
MT5_SERVER = "MetaQuotes-Demo"
SYMBOL = "XAUUSD"
VOLUME = 0.01  # Taille du lot standard
DEVIATION = 20  # Déviation autorisée en points

# --- GESTION GLOBALE DU RISQUE ---
MAX_TOTAL_TRADES = 5  # Nombre maximum de trades ouverts simultanément, toutes stratégies confondues
RISK_PER_TRADE_PERCENT = 1.0  # Risque par trade (utilisé par chaque stratégie)
MAX_DAILY_LOSS = -500  # Arrêt d'urgence si perte quotidienne dépasse ce montant
MAX_DAILY_PROFIT = 1000  # Arrêt des trades si profit quotidien atteint ce montant

# --- PARAMÈTRES GÉNÉRAUX ---
ANALYSIS_INTERVAL = 5  # Intervalle d'analyse en secondes pour le superviseur
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR

# --- STRATÉGIE M15 "LE STRATÈGE" ---
M15_SNIPER_CONFIG = {
    "ENABLED": True,
    "NAME": "Sniper M15",
    "MAGIC_NUMBER": 15001,
    "TIMEFRAME": "M15",
    "ADX_THRESHOLD": 25,
    "MIN_DIVERGENCE_STRENGTH": 6.5,
    "RR_RATIO": 1.8,
    "SCAN_INTERVAL": 900,  # 15 minutes en secondes
    "VOLUME": 0.02,  # Volume spécifique pour M15
    "COLOR": "\033[94m",  # Bleu
    "EMOJI": "🎯"
}

# --- STRATÉGIE M5 "LE COMMANDO" ---
M5_COMMANDO_CONFIG = {
    "ENABLED": True,
    "NAME": "Commando M5", 
    "MAGIC_NUMBER": 5001,
    "TIMEFRAME": "M5",
    "ADX_THRESHOLD": 24,
    "MIN_DIVERGENCE_STRENGTH": 4.5,
    "RR_RATIO": 2.0,
    "SCAN_INTERVAL": 300,  # 5 minutes en secondes
    "VOLUME": 0.015,  # Volume spécifique pour M5
    "COLOR": "\033[92m",  # Vert
    "EMOJI": "⚡"
}

# --- STRATÉGIE M1 "L'HYPER-SCALPER" ---
M1_SCALPER_CONFIG = {
    "ENABLED": True,
    "NAME": "Hyper-Scalper M1",
    "MAGIC_NUMBER": 1001,
    "TIMEFRAME": "M1",
    "ADX_THRESHOLD": 15,
    "MIN_DIVERGENCE_STRENGTH": 2.0,
    "RR_RATIO": 1.2,
    "SCAN_INTERVAL": 60,  # 1 minute en secondes
    "VOLUME": 0.01,  # Volume spécifique pour M1 (plus petit)
    "COLOR": "\033[91m",  # Rouge
    "EMOJI": "🚀"
}

# --- CODES COULEURS POUR L'AFFICHAGE ---
COLORS = {
    "RESET": "\033[0m",
    "BOLD": "\033[1m",
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "BLUE": "\033[94m",
    "PURPLE": "\033[95m",
    "CYAN": "\033[96m",
    "WHITE": "\033[97m"
}

# --- LISTE DES STRATÉGIES ACTIVES ---
ACTIVE_STRATEGIES = []
if M15_SNIPER_CONFIG["ENABLED"]:
    ACTIVE_STRATEGIES.append(("M15", M15_SNIPER_CONFIG))
if M5_COMMANDO_CONFIG["ENABLED"]:
    ACTIVE_STRATEGIES.append(("M5", M5_COMMANDO_CONFIG))
if M1_SCALPER_CONFIG["ENABLED"]:
    ACTIVE_STRATEGIES.append(("M1", M1_SCALPER_CONFIG))

print(f"🎯 Configuration Bot Ultime chargée: {len(ACTIVE_STRATEGIES)} stratégies actives")
