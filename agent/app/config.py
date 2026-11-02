import os
import json
from pathlib import Path
from pydantic import BaseModel

# Resilient .env loader
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

def get_dynamic_shopify_token() -> str:
    """Retrieves active or renewed Shopify access token automatically from env or cache."""
    # Check if shopify_auth has a valid cached token
    auth_cache = Path(r"C:\Users\N0N3Follows\.gemini\antigravity\scratch\shopify_auth\.token_cache.json")
    if auth_cache.exists():
        try:
            with open(auth_cache, "r", encoding="utf-8") as f:
                data = json.load(f)
                tok = data.get("access_token")
                if tok:
                    return tok
        except Exception:
            pass
    return os.getenv("SHOPIFY_ACCESS_TOKEN", "")

class AppSettings(BaseModel):
    shopify_store_domain: str = os.getenv("SHOPIFY_STORE_DOMAIN", "pjy6kz-0i.myshopify.com")
    shopify_access_token: str = get_dynamic_shopify_token()
    shopify_api_version: str = os.getenv("SHOPIFY_API_VERSION", "2024-10")
    
    # Supplier API Credentials (Free accounts / optional)
    cj_api_key: str = os.getenv("CJ_API_KEY", "")
    printify_api_token: str = os.getenv("PRINTIFY_API_TOKEN", "")
    
    # Autonomy & Pricing Defaults
    default_price_multiplier: float = float(os.getenv("DEFAULT_PRICE_MULTIPLIER", "2.75"))
    min_profit_margin_pct: float = float(os.getenv("MIN_PROFIT_MARGIN_PCT", "35.0"))
    auto_publish_threshold_pct: float = float(os.getenv("AUTO_PUBLISH_THRESHOLD_PCT", "50.0"))
    auto_dispatch_orders: bool = os.getenv("AUTO_DISPATCH_ORDERS", "false").lower() in ("true", "1")

settings = AppSettings()
