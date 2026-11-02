from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SupplierVariant(BaseModel):
    id: str
    title: str
    sku: Optional[str] = None
    supplier_cost: float
    stock: int = 100
    options: Dict[str, str] = Field(default_factory=dict)
    image_url: Optional[str] = None

class SupplierProduct(BaseModel):
    id: str
    supplier_name: str
    title: str
    description: str
    niche_category: str
    supplier_cost: float
    retail_price: Optional[float] = None
    compare_at_price: Optional[float] = None
    margin_pct: Optional[float] = None
    images: List[str] = Field(default_factory=list)
    variants: List[SupplierVariant] = Field(default_factory=list)
    shipping_days_estimate: str = "4-7 business days"
    source_url: Optional[str] = None
    in_stock: bool = True
    tags: List[str] = Field(default_factory=list)

class BaseSupplierAdapter(ABC):
    @property
    @abstractmethod
    def supplier_name(self) -> str:
        pass

    @abstractmethod
    async def search_niche_products(self, query: str, limit: int = 10) -> List[SupplierProduct]:
        """Search products in the supplier catalog for a specific niche query."""
        pass

    @abstractmethod
    async def get_product_details(self, product_id: str) -> Optional[SupplierProduct]:
        """Fetch detailed specs, variant pricing and live stock for an item."""
        pass

    @abstractmethod
    async def dispatch_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit automated order to the supplier fulfillment center."""
        pass
