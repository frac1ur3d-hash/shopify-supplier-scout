import httpx
from typing import List, Optional, Dict, Any
from .base import BaseSupplierAdapter, SupplierProduct, SupplierVariant

class PrintifyPODAdapter(BaseSupplierAdapter):
    def __init__(self, api_token: str = ""):
        self.api_token = api_token
        self.base_url = "https://api.printify.com/v1"

    @property
    def supplier_name(self) -> str:
        return "Printify POD"

    async def search_niche_products(self, query: str, limit: int = 10) -> List[SupplierProduct]:
        """
        Supplies Print-on-Demand blank and custom printed merchandise for the niche.
        """
        pod_catalog = [
            {"name": f"Heavyweight Cotton Unisex Tee — {query.title()} Custom Graphic", "cost": 9.25, "days": "3-5 days (US Local Print)"},
            {"name": f"Ceramic Ceramic Coffee Mug (15oz) — {query.title()} Theme", "cost": 5.40, "days": "2-4 days (US Local Print)"},
            {"name": f"Canvas Tote Bag (Eco Friendly) — {query.title()} Signature", "cost": 7.80, "days": "3-5 days (Local Print)"},
            {"name": f"Premium Matte Vertical Poster (18x24) — {query.title()}", "cost": 6.10, "days": "2-4 days (Local Print)"}
        ]

        products: List[SupplierProduct] = []
        for idx, item in enumerate(pod_catalog[:limit]):
            cost = item["cost"]
            products.append(SupplierProduct(
                id=f"pod_{idx+1}",
                supplier_name=self.supplier_name,
                title=item["name"],
                description=f"Premium print-on-demand custom item for {query}. Produced and shipped locally to your customer upon order placement.",
                niche_category=query,
                supplier_cost=cost,
                images=[
                    "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800",
                    "https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=800"
                ],
                variants=[
                    SupplierVariant(id=f"pod_v_{idx}_s", title="Small / Natural", supplier_cost=cost, stock=999),
                    SupplierVariant(id=f"pod_v_{idx}_m", title="Medium / Natural", supplier_cost=cost, stock=999),
                    SupplierVariant(id=f"pod_v_{idx}_l", title="Large / Natural", supplier_cost=cost + 1.00, stock=999)
                ],
                shipping_days_estimate=item["days"],
                source_url="https://printify.com",
                tags=["pod", "print_on_demand", "local_fulfillment", query.lower()]
            ))
        return products

    async def get_product_details(self, product_id: str) -> Optional[SupplierProduct]:
        res = await self.search_niche_products("POD Product", limit=1)
        return res[0] if res else None

    async def dispatch_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "success",
            "supplier_order_id": f"POD-JOB-{order_data.get('order_id', '777')}",
            "carrier": "USPS First Class",
            "estimated_dispatch_hours": 36
        }
