import httpx
from typing import Dict, Any, List
from .suppliers import get_all_supplier_adapters
from .pricing_engine import PricingEngine

class OrderDispatcher:
    def __init__(self, store_domain: str, access_token: str, api_version: str = "2026-07"):
        self.store_domain = store_domain
        self.access_token = access_token
        self.api_version = api_version
        self.endpoint = f"https://{store_domain}/admin/api/{api_version}/graphql.json"
        self.pricing_engine = PricingEngine()
        self.suppliers = {adapter.supplier_name: adapter for adapter in get_all_supplier_adapters()}

    async def process_paid_order(self, order_payload: Dict[str, Any], auto_dispatch: bool = True) -> Dict[str, Any]:
        """
        Processes an incoming orders/paid Shopify webhook.
        Evaluates margin safety, routes to the supplier, and sets up tracking.
        """
        order_id = str(order_payload.get("id", "0"))
        order_name = order_payload.get("name", f"#{order_id}")
        total_price = float(order_payload.get("total_price", "0.0"))
        line_items = order_payload.get("line_items", [])
        shipping_address = order_payload.get("shipping_address", {})

        # Calculate estimated total supplier cost
        supplier_routing_results = []
        total_supplier_cost = 0.0

        for item in line_items:
            vendor = item.get("vendor", "CJ Dropshipping")
            qty = int(item.get("quantity", 1))
            # Extract explicit supplier cost if present, else standard 38% ratio
            estimated_unit_cost = float(item.get("supplier_cost", float(item.get("price", "20.0")) * 0.38))
            total_supplier_cost += (estimated_unit_cost * qty)

            matched_adapter = self.suppliers.get(vendor) or list(self.suppliers.values())[0]

            if auto_dispatch:
                # Failsafe margin check: ensure revenue covers supplier costs
                if not self.pricing_engine.is_margin_safe(total_supplier_cost, total_price):
                    return {
                        "status": "held_for_review",
                        "order_id": order_id,
                        "order_name": order_name,
                        "reason": f"Margin Safety Triggered: Total revenue ${total_price:.2f} is under safe margin against supplier cost ${total_supplier_cost:.2f}."
                    }

                dispatch_res = await matched_adapter.dispatch_order({
                    "order_id": order_id,
                    "line_item": item.get("name"),
                    "quantity": qty,
                    "shipping_address": shipping_address
                })
                supplier_routing_results.append({
                    "item": item.get("name"),
                    "supplier": matched_adapter.supplier_name,
                    "supplier_order_id": dispatch_res.get("supplier_order_id"),
                    "carrier": dispatch_res.get("carrier")
                })

        return {
            "status": "dispatched" if auto_dispatch else "ready_for_approval",
            "order_id": order_id,
            "order_name": order_name,
            "total_revenue": total_price,
            "estimated_supplier_cost": round(total_supplier_cost, 2),
            "estimated_net_profit": round(total_price - total_supplier_cost, 2),
            "routings": supplier_routing_results
        }

    async def sync_fulfillment_tracking(self, fulfillment_order_id: str, tracking_number: str, tracking_company: str = "USPS") -> Dict[str, Any]:
        """Pushes carrier tracking numbers to Shopify to notify the customer."""
        mutation = """
        mutation fulfillmentCreateV2($fulfillment: FulfillmentV2Input!) {
          fulfillmentCreateV2(fulfillment: $fulfillment) {
            fulfillment {
              id
              status
              trackingInfo {
                company
                number
                url
              }
            }
            userErrors {
              field
              message
            }
          }
        }
        """
        variables = {
            "fulfillment": {
                "lineItemsByFulfillmentOrder": [
                    {"fulfillmentOrderId": fulfillment_order_id}
                ],
                "trackingInfo": {
                    "company": tracking_company,
                    "number": tracking_number,
                    "url": f"https://tools.usps.com/go/TrackConfirmAction?tLabels={tracking_number}"
                },
                "notifyCustomer": True
            }
        }
        if not self.access_token:
            return {"success": True, "simulated": True, "tracking_number": tracking_number}

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_token
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(self.endpoint, json={"query": mutation, "variables": variables}, headers=headers)
                return {"success": True, "data": res.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
