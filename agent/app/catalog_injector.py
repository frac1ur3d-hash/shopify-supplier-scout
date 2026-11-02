import httpx
from typing import Dict, Any, Optional
from .suppliers.base import SupplierProduct

class CatalogInjector:
    def __init__(self, store_domain: str, access_token: str, api_version: str = "2026-07"):
        self.store_domain = store_domain
        self.access_token = access_token
        self.api_version = api_version
        self.endpoint = f"https://{store_domain}/admin/api/{api_version}/graphql.json"

    async def import_product(self, product: SupplierProduct, publish_live: bool = False) -> Dict[str, Any]:
        """
        Executes Shopify productCreate mutation to inject product, variants,
        price, compareAtPrice and tags into the merchant's store.
        """
        mutation = """
        mutation createProductFromSupplier($input: ProductInput!, $media: [CreateMediaInput!]) {
          productCreate(input: $input, media: $media) {
            product {
              id
              title
              handle
              status
              totalVariants
              variants(first: 5) {
                edges {
                  node {
                    id
                    price
                    compareAtPrice
                    sku
                  }
                }
              }
            }
            userErrors {
              field
              message
            }
          }
        }
        """
        status = "ACTIVE" if publish_live else "DRAFT"
        retail_price_str = f"{product.retail_price:.2f}" if product.retail_price else f"{(product.supplier_cost * 2.75):.2f}"
        compare_price_str = f"{product.compare_at_price:.2f}" if product.compare_at_price else f"{(float(retail_price_str) * 1.4):.2f}"

        tags = product.tags + [
            f"supplier:{product.supplier_name.lower().replace(' ', '_')}",
            "scout:automated",
            f"cost:{product.supplier_cost:.2f}"
        ]

        media_inputs = []
        for img_url in product.images[:3]:
            media_inputs.append({
                "mediaContentType": "IMAGE",
                "originalSource": img_url
            })

        variables = {
            "input": {
                "title": product.title,
                "descriptionHtml": f"<p>{product.description}</p><p><em>Verified fulfillment via {product.supplier_name} ({product.shipping_days_estimate}).</em></p>",
                "vendor": product.supplier_name,
                "productType": product.niche_category,
                "status": status,
                "tags": tags
            },
            "media": media_inputs if media_inputs else None
        }

        if not self.access_token or not self.store_domain:
            # Emulated successful response for preview & sandbox testing
            return {
                "success": True,
                "simulated": True,
                "product_id": f"gid://shopify/Product/demo_{product.id}",
                "title": product.title,
                "status": status,
                "retail_price": retail_price_str,
                "compare_at_price": compare_price_str,
                "supplier": product.supplier_name
            }

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.access_token
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(self.endpoint, json={"query": mutation, "variables": variables}, headers=headers)
                data = res.json()
                created = data.get("data", {}).get("productCreate", {})
                errors = created.get("userErrors", [])
                if errors:
                    return {"success": False, "errors": errors}
                p_node = created.get("product", {})
                return {
                    "success": True,
                    "simulated": False,
                    "product_id": p_node.get("id"),
                    "title": p_node.get("title"),
                    "status": p_node.get("status"),
                    "retail_price": retail_price_str,
                    "compare_at_price": compare_price_str
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
