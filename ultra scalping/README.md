# 🎯 BOT DE TRADING M5 PULLBACK - STRATÉGIE PROFESSIONNELLE

## 📊 Vue d'ensemble

Ce bot implémente une stratégie de trading professionnelle sur le timeframe M5, basée sur l'identification de pullbacks (replis) dans la tendance principale. 

**Philosophie : Qualité > Quantité**

## ⚡ Stratégie de Trading

### 🎯 Principe de Base
1. **IDENTIFICATION TENDANCE** : Utilise une EMA 200 pour déterminer la direction principale du marché
2. **DÉTECTION PULLBACK** : Attend que le prix revienne vers l'EMA 50 (support/résistance dynamique)
3. **VALIDATION MOMENTUM** : Confirme le signal avec le RSI pour éviter les faux signaux

### 📈 Signaux de Trading
- **🟢 BUY** : Tendance haussière (prix > EMA 200) + pullback vers EMA 50 + RSI entre 40-55
- **🔴 SELL** : Tendance baissière (prix < EMA 200) + rebond vers EMA 50 + RSI entre 45-60

### ⚖️ Gestion du Risque Adaptative
- **TP/SL Adaptatifs** : Calculés en fonction de l'ATR (Average True Range) pour s'adapter à la volatilité
- **Stop Loss** : 1.5× ATR
- **Take Profit** : 3× ATR (ratio Risque/Rendement de 1:2)
- **Breakeven** : Déplacement automatique du SL en profit à 75% du TP

## 🛡️ Sécurités Intégrées

- **Pause Automatique** : Arrêt du trading 1h si perte journalière ≥ 5% de la balance
- **Fermeture Quotidienne** : Fermeture automatique de toutes les positions à 22h50
- **Fermeture Week-end** : Fermeture automatique le vendredi soir
- **Stop Loss Obligatoire** : Toutes les positions ont un SL (jamais supprimé)

## 🚀 Installation et Configuration

### 1. Configuration MT5
Dans `m5_pullback_bot.py`, lignes 62-64 :
```python
MT5_LOGIN = 10007787600       # Votre numéro de compte
MT5_PASSWORD = "VotreMotDePasse"    # Votre mot de passe
MT5_SERVER = "VotreServeur"   # Votre serveur MT5
```

### 2. Lancement
```bash
python start_m5_pullback.py
```

### 3. Paramètres Principaux
- **Symbole** : XAUUSD (Or)
- **Timeframe** : M5 (5 minutes)
- **Lot Size** : Adaptatif selon la balance
- **Heures de Trading** : 00h20 - 22h50

## 📋 Structure des Fichiers

```
m5_pullback_bot.py      # 🤖 Bot principal avec logique de trading
m5_pullback_config.py   # ⚙️ Configuration des paramètres RSI
start_m5_pullback.py    # 🚀 Script de lancement
```

## 📊 Indicateurs Utilisés

- **EMA 200** : Tendance de fond
- **EMA 50** : Zone de pullback/rebond
- **RSI 14** : Momentum et validation
- **ATR 14** : Volatilité pour TP/SL adaptatifs

## ⚠️ Avertissements

🚨 **ATTENTION ARGENT RÉEL** : Ce bot trade avec de l'argent réel
- Utilisez uniquement un capital que vous pouvez vous permettre de perdre
- Testez d'abord en mode démo
- Surveillez les performances régulièrement

## 📈 Optimisations

- **Lot Size Adaptatif** : Augmente avec la balance (1 lot par tranche de 1000€)
- **Positions Limitées** : Maximum calculé selon le risque acceptable (5% de la balance)
- **TP/SL Dynamiques** : S'adaptent automatiquement à la volatilité du marché

---

**Auteur** : Ultra Scalper  
**Version** : M5 Pullback Professional  
**Date** : 03 octobre 2025
