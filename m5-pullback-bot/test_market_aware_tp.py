#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test du nouveau système TP Market-Aware (Tendance + Volatilité)
"""

def test_market_aware_tp():
    """Test du système TP qui combine tendance et volatilité"""
    
    print("🎯 TEST DU SYSTÈME TP MARKET-AWARE")
    print("=" * 70)
    print("Combine force de tendance + volatilité ATR pour des TP ultra-réalistes")
    print()
    
    # Scénarios de test
    test_scenarios = [
        # Marché calme (ATR < 2.0)
        {"atr": 1.5, "trend": 45, "desc": "Marché CALME - Tendance FAIBLE", "expected_factor": 0.8},
        {"atr": 1.8, "trend": 75, "desc": "Marché CALME - Tendance FORTE", "expected_factor": 0.8},
        {"atr": 1.9, "trend": 85, "desc": "Marché CALME - Tendance TRÈS FORTE", "expected_factor": 0.8},
        
        # Marché normal (2.0 <= ATR <= 4.0)
        {"atr": 2.5, "trend": 45, "desc": "Marché NORMAL - Tendance FAIBLE", "expected_factor": 1.0},
        {"atr": 3.0, "trend": 75, "desc": "Marché NORMAL - Tendance FORTE", "expected_factor": 1.0},
        {"atr": 3.5, "trend": 85, "desc": "Marché NORMAL - Tendance TRÈS FORTE", "expected_factor": 1.0},
        
        # Marché agité (ATR > 4.0)
        {"atr": 4.5, "trend": 45, "desc": "Marché AGITÉ - Tendance FAIBLE", "expected_factor": 1.1},
        {"atr": 5.0, "trend": 75, "desc": "Marché AGITÉ - Tendance FORTE", "expected_factor": 1.1},
        {"atr": 6.0, "trend": 85, "desc": "Marché AGITÉ - Tendance TRÈS FORTE", "expected_factor": 1.1},
    ]
    
    def calculate_market_aware_tp_ratio(trend_strength, atr_value):
        """Simulation de la fonction du bot"""
        # Base du ratio selon la force de tendance
        if trend_strength >= 80:
            base_ratio = 2.0  # Très forte
        elif trend_strength >= 50:
            base_ratio = 1.5  # Forte
        else:
            base_ratio = 1.2  # Faible
        
        # Ajustement selon la volatilité (ATR)
        if atr_value < 2.0:
            volatility_factor = 0.8
            volatility_desc = "CALME"
        elif atr_value > 4.0:
            volatility_factor = 1.1
            volatility_desc = "AGITÉ"
        else:
            volatility_factor = 1.0
            volatility_desc = "NORMALE"
        
        # Calcul final avec plafond de sécurité
        final_ratio = base_ratio * volatility_factor
        final_ratio = min(final_ratio, 2.2)  # Plafond absolu
        
        return final_ratio, volatility_desc
    
    print(f"{'Scénario':<40} {'ATR':<6} {'Trend':<6} {'Base':<6} {'Factor':<8} {'Final':<8} {'Status'}")
    print("-" * 80)
    
    for scenario in test_scenarios:
        atr = scenario["atr"]
        trend = scenario["trend"]
        desc = scenario["desc"]
        
        final_ratio, volatility_desc = calculate_market_aware_tp_ratio(trend, atr)
        
        # Calcul des bases pour comparaison
        if trend >= 80:
            base_ratio = 2.0
        elif trend >= 50:
            base_ratio = 1.5
        else:
            base_ratio = 1.2
            
        factor = final_ratio / base_ratio
        
        print(f"{desc:<40} {atr:<6.1f} {trend:<6.0f} {base_ratio:<6.1f} {factor:<8.2f} {final_ratio:<8.2f} {volatility_desc}")
    
    print("-" * 80)
    print("\n📊 ANALYSE DES RÉSULTATS:")
    print("   🔹 MARCHÉ CALME (ATR < 2.0) : TP réduits de 20% (facteur 0.8)")
    print("   🔹 MARCHÉ NORMAL (2.0-4.0) : TP standards (facteur 1.0)")  
    print("   🔹 MARCHÉ AGITÉ (ATR > 4.0) : TP augmentés de 10% (facteur 1.1)")
    print()
    print("🎯 AVANTAGES DU SYSTÈME MARKET-AWARE:")
    print("   ✅ Adapte automatiquement aux conditions de marché")
    print("   ✅ Plus conservateur quand le marché est calme")
    print("   ✅ Plus ambitieux quand la volatilité le permet")
    print("   ✅ Plafond de sécurité à 2.2 pour rester réaliste")
    print("   ✅ Combine intelligence de tendance + réalisme de marché")

if __name__ == "__main__":
    test_market_aware_tp()
