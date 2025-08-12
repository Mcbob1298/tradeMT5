# Bot de Scalping Ultra-Agressif XAUUSD

⚠️ **ATTENTION - STRATÉGIE À TRÈS HAUT RISQUE** ⚠️

Ce bot implémente une stratégie de scalping ultra-agressif sur l'or (XAUUSD) **SANS STOP LOSS**. Les pertes peuvent être illimitées et le compte peut être liquidé rapidement.

## 🚨 Avertissements Critiques

- **AUCUN STOP LOSS** : Ce bot ne place jamais de Stop Loss
- **PERTES ILLIMITÉES POSSIBLES** : En cas de mouvement défavorable
- **LIQUIDATION RAPIDE DU COMPTE** : Risque très élevé
- **TESTEZ UNIQUEMENT SUR COMPTE DEMO** au début
- **Vous êtes seul responsable** des conséquences financières

## 📋 Prérequis

1. **MetaTrader 5** installé et configuré
2. **Python 3.7+** avec les packages :
   - MetaTrader5
   - pandas
   - numpy
3. **Compte de trading** avec accès API
4. **Connexion stable** et faible latence

## 🚀 Installation

1. Clonez ou téléchargez les fichiers dans un dossier
2. Installez les dépendances Python :
   ```bash
   pip install MetaTrader5 pandas numpy
   ```
3. Configurez vos paramètres dans `config.py`

## ⚙️ Configuration

### Fichier `config.py`

Modifiez les paramètres selon vos besoins :

```python
# Connexion MT5
MT5_LOGIN = 5039037137
MT5_PASSWORD = "-2YnWgJj"
MT5_SERVER = "MetaQuotes-Demo"

# Trading
LOT_SIZE = 0.01  # Commencez très petit !
TAKE_PROFIT_PIPS = 8  # Take Profit en pips
```

### Paramètres Critiques

- **LOT_SIZE** : Commencez avec 0.01 lot maximum
- **TAKE_PROFIT_PIPS** : Gains visés par trade (en pips)
- **ANALYSIS_INTERVAL** : Fréquence d'analyse (secondes)

## 🔧 Utilisation

### 1. Test de Connexion (OBLIGATOIRE)

Avant d'utiliser le bot, testez votre configuration :

```bash
python test_connection.py
```

Ce script vérifie :
- ✅ Connexion à MT5
- ✅ Accès au symbole XAUUSD
- ✅ Données de marché disponibles
- ✅ Permissions de trading

### 2. Lancement du Bot

Une fois les tests réussis :

```bash
python scalping_bot_xauusd.py
```

### 3. Arrêt du Bot

Pour arrêter le bot proprement : `Ctrl + C`

## 📊 Stratégie d'Analyse

Le bot utilise une analyse multi-facteurs :

### 1. Market Depth (Carnet d'ordres)
- Analyse la pression acheteuse vs vendeuse
- Poids : 30% dans la décision

### 2. Volatilité des Ticks
- Détecte l'accélération des prix
- Poids : 40% dans la décision

### 3. Moyenne Mobile Rapide
- MA sur 5 périodes (M1)
- Poids : 30% dans la décision

### Conditions de Trade

Un trade n'est ouvert que si :
- ✅ Au moins 2 signaux sont concordants
- ✅ Score composite > seuil de décision
- ✅ Aucune position déjà ouverte

## 🎯 Gestion des Trades

### Entrée
- **Type** : Ordre au marché (instantané)
- **Volume** : Lot fixe (configurable)
- **Take Profit** : TOUJOURS présent
- **Stop Loss** : JAMAIS (volontairement omis)

### Sortie
- **Uniquement par Take Profit** : Le bot ne gère pas les trades après ouverture
- **Fermeture automatique** : Déléguée au serveur MT5

## 📁 Structure des Fichiers

```
tradeMT5/
├── scalping_bot_xauusd.py    # Bot principal
├── config.py                 # Configuration
├── test_connection.py        # Test de connexion
└── README.md                 # Ce fichier
```

## 🔍 Logs et Monitoring

Le bot affiche en temps réel :
- 🤖 État de fonctionnement
- 🔍 Signaux détectés
- 📊 Positions ouvertes
- ✅ Trades exécutés
- ❌ Erreurs rencontrées

## ⚠️ Gestion des Risques

### Mesures de Sécurité Recommandées

1. **COMPTE DEMO UNIQUEMENT** au début
2. **Capital limite** : Argent que vous pouvez perdre entièrement
3. **Surveillance constante** : Ne laissez jamais le bot sans surveillance
4. **Arrêt d'urgence** : Préparez un plan de fermeture manuelle
5. **Taille de lot minimale** : Commencez très petit

### Conditions de Marché Défavorables

Le bot peut être inefficace ou dangereux lors :
- 📰 **Annonces économiques importantes**
- 🌍 **Événements géopolitiques majeurs**
- 💥 **Volatilité extrême du marché**
- 🕐 **Heures de fermeture des marchés**
- 📡 **Problèmes de connexion/latence**

## 🛠️ Dépannage

### Problèmes Courants

1. **Erreur de connexion MT5**
   - Vérifiez que MT5 est ouvert
   - Contrôlez les identifiants dans `config.py`
   - Testez avec `test_connection.py`

2. **Symbole XAUUSD non trouvé**
   - Activez XAUUSD dans MT5
   - Vérifiez auprès de votre broker

3. **Ordres refusés**
   - Vérifiez les permissions de trading
   - Contrôlez la taille de lot minimum
   - Vérifiez la marge disponible

## 📞 Support

En cas de problème technique :
1. Consultez les logs d'erreur
2. Vérifiez votre configuration
3. Testez avec `test_connection.py`
4. Contactez votre broker si nécessaire

---

## ⚖️ Disclaimer Legal

**L'utilisateur assume l'entière responsabilité** de l'utilisation de ce bot. Aucune garantie de performance n'est fournie. Le trading automatisé peut entraîner des pertes importantes et rapides.

**Utilisez à vos propres risques.**