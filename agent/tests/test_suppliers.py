import asyncio
import pytest
from app.suppliers import get_all_supplier_adapters
from app.suppliers.cj_dropshipping import CJDropshippingAdapter
from app.suppliers.aliexpress import AliExpressAdapter
from app.suppliers.printify_pod import PrintifyPODAdapter
from app.suppliers.open_hunter import OpenSupplierHunter

def test_all_adapters_return_products():
    async def _run():
        adapters = get_all_supplier_adapters()
        assert len(adapters) == 4

        for adapter in adapters:
            items = await adapter.search_niche_products("crystals", limit=2)
            assert len(items) > 0
            p = items[0]
            assert p.supplier_cost > 0.0
            assert p.title != ""
            assert len(p.images) > 0
            assert p.shipping_days_estimate != ""
    asyncio.run(_run())

def test_dispatch_order():
    async def _run():
        cj = CJDropshippingAdapter()
        res = await cj.dispatch_order({"order_id": "1001", "line_item": "Crystal Pendant"})
        assert res["status"] == "success"
        assert "CJ-ORD-1001" in res["supplier_order_id"]
    asyncio.run(_run())
