from fastapi import FastAPI, BackgroundTasks, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict, Any, List, Optional
import os
from pathlib import Path

from .config import settings
from .store_analyzer import StoreAnalyzer
from .pricing_engine import PricingEngine
from .catalog_injector import CatalogInjector
from .order_dispatcher import OrderDispatcher
from .suppliers import get_all_supplier_adapters
from .suppliers.base import SupplierProduct
from .suppliers.supplier_directory import SupplierDirectoryHunter

supplier_directory_hunter = SupplierDirectoryHunter()

app = FastAPI(
    title="Shopify Supplier Scout Agent API",
    description="Autonomous Dropshipping Sourcing & Fulfillment Microservice",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Services
pricing_engine = PricingEngine(
    default_multiplier=settings.default_price_multiplier,
    min_margin_pct=settings.min_profit_margin_pct
)

store_analyzer = StoreAnalyzer(
    store_domain=settings.shopify_store_domain,
    access_token=settings.shopify_access_token,
    api_version=settings.shopify_api_version
)

catalog_injector = CatalogInjector(
    store_domain=settings.shopify_store_domain,
    access_token=settings.shopify_access_token,
    api_version=settings.shopify_api_version
)

order_dispatcher = OrderDispatcher(
    store_domain=settings.shopify_store_domain,
    access_token=settings.shopify_access_token,
    api_version=settings.shopify_api_version
)

# In-memory staged products cache
staged_products_cache: Dict[str, SupplierProduct] = {}

# Locate static UI directory
STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "web" / "public"

@app.get("/")
def get_dashboard():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "service": "Shopify Supplier Scout Agent",
        "status": "online",
        "store": settings.shopify_store_domain,
        "mode": "autonomous_scout"
    }

@app.get("/api/health")
def get_health():
    return {
        "service": "Shopify Supplier Scout Agent",
        "status": "online",
        "store": settings.shopify_store_domain,
        "mode": "autonomous_scout",
        "supported_suppliers": ["CJ Dropshipping", "AliExpress Open", "Printify POD", "Open Supplier Hunter"]
    }

@app.get("/api/store/analyze")
async def analyze_store():
    """Analyzes the merchant store to determine current niche keywords and pricing metrics."""
    result = await store_analyzer.fetch_store_catalog(limit=50)
    return result

@app.get("/api/suppliers/companies")
async def get_supplier_companies(
    niche: Optional[str] = Query(None, description="Analyzed store niche")
):
    """
    Finds verified supplier companies, direct factories, and domestic dropship partners
    specializing in the merchant's analyzed store category.
    """
    search_niche = niche
    if not search_niche:
        analysis = await store_analyzer.fetch_store_catalog(limit=20)
        search_niche = analysis.get("primary_niche", "Gnome & Decor")

    companies = supplier_directory_hunter.hunt_suppliers_for_niche(search_niche)
    return {
        "analyzed_niche": search_niche,
        "total_suppliers_found": len(companies),
        "suppliers": [c.model_dump() for c in companies]
    }
async def scout_suppliers(
    query: Optional[str] = Query(None, description="Custom niche search query"),
    multiplier: Optional[float] = Query(None, description="Price multiplier override"),
    limit_per_supplier: int = Query(3, ge=1, le=10)
):
    """
    Scouts CJ Dropshipping, AliExpress, Printify, and Open Supplier Hunter
    for products matching the store's niche, calculates retail prices and profit margins.
    """
    search_term = query
    if not search_term:
        analysis = await store_analyzer.fetch_store_catalog(limit=20)
        keywords = analysis.get("top_keywords", ["artisan craft"])
        search_term = keywords[0] if keywords else "trending craft"

    adapters = get_all_supplier_adapters()
    discovered: List[Dict[str, Any]] = []

    for adapter in adapters:
        try:
            items = await adapter.search_niche_products(search_term, limit=limit_per_supplier)
            for item in items:
                retail_p, compare_p, margin = pricing_engine.calculate_prices(
                    item.supplier_cost,
                    multiplier=multiplier
                )
                item.retail_price = retail_p
                item.compare_at_price = compare_p
                item.margin_pct = margin
                staged_products_cache[item.id] = item
                discovered.append(item.model_dump())
        except Exception:
            continue

    return {
        "niche_queried": search_term,
        "total_discovered": len(discovered),
        "products": discovered
    }

@app.post("/api/products/import")
async def import_product(payload: Dict[str, Any] = Body(...)):
    """Imports a staged supplier product into the Shopify store."""
    product_id = payload.get("product_id")
    publish_live = payload.get("publish_live", False)

    target_product = staged_products_cache.get(product_id)
    if not target_product:
        # Reconstruct product from payload if not found in memory
        target_product = SupplierProduct(
            id=product_id or "gen_1",
            supplier_name=payload.get("supplier_name", "CJ Dropshipping"),
            title=payload.get("title", "Imported Supplier Item"),
            description=payload.get("description", "High demand dropshipped item"),
            niche_category=payload.get("niche_category", "Merchandise"),
            supplier_cost=float(payload.get("supplier_cost", 10.0)),
            retail_price=float(payload.get("retail_price", 27.99)),
            compare_at_price=float(payload.get("compare_at_price", 39.99)),
            images=payload.get("images", []),
            shipping_days_estimate=payload.get("shipping_days_estimate", "4-7 days")
        )

    result = await catalog_injector.import_product(target_product, publish_live=publish_live)
    return result

@app.post("/api/webhooks/orders-paid")
async def handle_order_paid(
    payload: Dict[str, Any] = Body(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Webhook endpoint for Shopify orders/paid to trigger automated fulfillment dispatch."""
    auto_dispatch = settings.auto_dispatch_orders
    result = await order_dispatcher.process_paid_order(payload, auto_dispatch=auto_dispatch)
    return result

@app.get("/api/settings")
def get_settings():
    return {
        "shopify_store_domain": settings.shopify_store_domain,
        "default_price_multiplier": settings.default_price_multiplier,
        "min_profit_margin_pct": settings.min_profit_margin_pct,
        "auto_publish_threshold_pct": settings.auto_publish_threshold_pct,
        "auto_dispatch_orders": settings.auto_dispatch_orders
    }

@app.post("/api/settings")
def update_settings(payload: Dict[str, Any] = Body(...)):
    if "default_price_multiplier" in payload:
        settings.default_price_multiplier = float(payload["default_price_multiplier"])
    if "min_profit_margin_pct" in payload:
        settings.min_profit_margin_pct = float(payload["min_profit_margin_pct"])
    if "auto_dispatch_orders" in payload:
        settings.auto_dispatch_orders = bool(payload["auto_dispatch_orders"])
    return {"status": "updated", "settings": get_settings()}
