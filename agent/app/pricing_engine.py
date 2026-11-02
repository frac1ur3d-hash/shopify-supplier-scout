import math
from typing import Tuple

class PricingEngine:
    def __init__(self, default_multiplier: float = 2.75, min_margin_pct: float = 35.0):
        self.default_multiplier = default_multiplier
        self.min_margin_pct = min_margin_pct

    def round_psychological_99(self, raw_price: float) -> float:
        """Rounds price to end in .99 (e.g. 24.12 -> 24.99, 24.00 -> 24.99)."""
        if raw_price <= 0.99:
            return 0.99
        whole = math.floor(raw_price)
        cents = raw_price - whole
        if cents > 0.49:
            return float(whole + 0.99)
        else:
            # If below .49, keep at .49 or round to .99 depending on value
            return float(whole + 0.99)

    def calculate_prices(self, supplier_cost: float, multiplier: float = None) -> Tuple[float, float, float]:
        """
        Calculates (retail_price, compare_at_price, margin_pct).
        - retail_price: The actual selling price ending in .99
        - compare_at_price: Strikethrough anchor price (~1.4x of retail price)
        - margin_pct: Profit margin percentage
        """
        mult = multiplier if multiplier is not None else self.default_multiplier
        base_retail = supplier_cost * mult
        retail_price = round(self.round_psychological_99(base_retail), 2)
        
        # Strikethrough price for perceived value discount (e.g., ~1.35x to 1.45x)
        compare_at = round(self.round_psychological_99(retail_price * 1.40), 2)
        
        profit = retail_price - supplier_cost
        margin_pct = round((profit / retail_price) * 100.0, 1) if retail_price > 0 else 0.0
        
        return retail_price, compare_at, margin_pct

    def is_margin_safe(self, supplier_cost: float, retail_price: float) -> bool:
        """Guardrail check: returns True if margin satisfies minimum safety threshold."""
        if retail_price <= supplier_cost:
            return False
        profit = retail_price - supplier_cost
        margin = (profit / retail_price) * 100.0
        return margin >= self.min_margin_pct
