import pytest
from app.pricing_engine import PricingEngine

def test_round_psychological_99():
    engine = PricingEngine()
    assert engine.round_psychological_99(24.12) == 24.99
    assert engine.round_psychological_99(19.99) == 19.99
    assert engine.round_psychological_99(10.00) == 10.99

def test_calculate_prices():
    engine = PricingEngine(default_multiplier=2.75)
    retail_p, compare_p, margin = engine.calculate_prices(10.00)
    
    # 10.00 * 2.75 = 27.50 -> rounded to 27.99
    assert retail_p == 27.99
    # Compare at price is higher
    assert compare_p > retail_p
    # Margin should be (27.99 - 10) / 27.99 ≈ 64.3%
    assert margin > 60.0

def test_is_margin_safe():
    engine = PricingEngine(min_margin_pct=35.0)
    # 10 cost on 20 price is 50% margin -> safe
    assert engine.is_margin_safe(10.00, 20.00) is True
    # 10 cost on 12 price is 16.7% margin -> below 35% -> unsafe
    assert engine.is_margin_safe(10.00, 12.00) is False
    # Negative margin
    assert engine.is_margin_safe(10.00, 8.00) is False
