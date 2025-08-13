# 🎯 TradeMT5 - Système de Trading Automatisé Professionnel

## 📁 Structure du Projet

```
tradeMT5/
├── bot_ultime/              # 🚀 Bot de trading principal
│   ├── __init__.py
│   ├── ultimate_bot.py      # Orchestrateur principal avec multi-threading
│   ├── strategies/          # 📊 Stratégies de trading
│   │   ├── __init__.py
│   │   ├── strategy_m15.py  # Stratégie M15 (ADX: 25, RSI: 50/30)
│   │   ├── strategy_m5.py   # Stratégie M5 (ADX: 24, RSI: 45/35) 
│   │   └── strategy_m1.py   # Hyper-Scalper M1 (ADX: 15, RSI: 65/40)
│   ├── config/              # ⚙️ Configuration
│   │   ├── __init__.py
│   │   └── config_ultimate.py
│   └── core/                # 🔒 Modules centraux
│       ├── __init__.py
│       └── risk_manager.py  # Gestionnaire de risques global
├── calibreurs/              # 🎛️ Outils de calibration
│   ├── sniper_auto_calibrator.py    # Calibreur M15
│   ├── sniper_auto_calibrator_M5.py # Calibreur M5
│   └── hyper_scalper_M1.py          # Calibreur M1
├── data/                    # 📈 Données de marché
│   ├── XAUUSD_M1.csv
│   ├── XAUUSD_M5.csv
│   └── XAUUSD_M15.csv
├── tests/                   # 🧪 Tests
│   └── test_ultimate_bot.py
├── docs/                    # 📚 Documentation
│   └── README_BOT_ULTIME.md
└── legacy/                  # 📦 Anciens fichiers
    ├── config.py
    └── README.md
```

## 🚀 Démarrage Rapide

### Lancement du Bot Ultime (Multi-Stratégies)
```bash
cd bot_ultime
python ultimate_bot.py
```

### Calibration des Stratégies
```bash
# Calibration M15
python calibreurs/sniper_auto_calibrator.py

# Calibration M5  
python calibreurs/sniper_auto_calibrator_M5.py

# Calibration M1
python calibreurs/hyper_scalper_M1.py
```

## 🎯 Performance des Stratégies

| Timeframe | Profit Total | ADX Optimal | RSI Optimal |
|-----------|-------------|-------------|-------------|
| **M15**   | 18,423$     | 25          | 50/30       |
| **M5**    | 15,287$     | 24          | 45/35       |
| **M1**    | 12,995$     | 15          | 65/40       |

## ⚡ Fonctionnalités

- ✅ **Multi-Threading**: Exécution simultanée des 3 stratégies
- ✅ **Gestion des Risques**: Limite quotidienne, stop d'urgence  
- ✅ **Filtre ADX**: Détection des tendances fortes
- ✅ **Divergences RSI**: Signaux de retournement
- ✅ **Interface en Temps Réel**: Monitoring complet
- ✅ **Architecture Professionnelle**: Code modulaire et maintenable

## 🔧 Configuration

La configuration se trouve dans `bot_ultime/config/config_ultimate.py`:
- Paramètres MT5 (compte, serveur)
- Limites de risque (3000$ max par jour)
- Paramètres optimisés pour chaque timeframe

## 📊 Monitoring

Le bot affiche en temps réel:
- Status de chaque stratégie
- P&L total et par stratégie  
- Nombre de positions ouvertes
- Alertes de sécurité

## 🔒 Sécurité

- **Risk Manager Global**: Contrôle centralisé des risques
- **Threading Safety**: Verrous pour éviter les conflits
- **Limits Strictes**: Arrêt automatique en cas de perte excessive
- **Validation**: Tous les ordres sont validés avant exécution

---
*Système développé avec MetaTrader 5 API et optimisé sur données historiques XAUUSD*
