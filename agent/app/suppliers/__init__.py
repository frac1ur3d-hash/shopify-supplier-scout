from typing import List, Dict
from .base import BaseSupplierAdapter, SupplierProduct, SupplierVariant
from .cj_dropshipping import CJDropshippingAdapter
from .aliexpress import AliExpressAdapter
from .printify_pod import PrintifyPODAdapter
from .open_hunter import OpenSupplierHunter

def get_all_supplier_adapters() -> List[BaseSupplierAdapter]:
    return [
        CJDropshippingAdapter(),
        AliExpressAdapter(),
        PrintifyPODAdapter(),
        OpenSupplierHunter()
    ]
