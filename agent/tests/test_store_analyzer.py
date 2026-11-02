import pytest
from app.store_analyzer import StoreAnalyzer

def test_store_analyzer_fallback():
    analyzer = StoreAnalyzer(store_domain="demo.myshopify.com", access_token="")
    analysis = analyzer._generate_fallback_analysis()
    assert analysis["shop_name"] == "Connected Merchant Store"
    assert "top_keywords" in analysis
    assert len(analysis["recommended_supplier_queries"]) > 0

def test_analyze_data():
    analyzer = StoreAnalyzer(store_domain="test.myshopify.com", access_token="")
    sample_data = {
        "shop": {"name": "Gnome & Dragon Den", "currencyCode": "USD"},
        "products": {
            "edges": [
                {
                    "node": {
                        "id": "1",
                        "title": "Obsidian Protection Pyramid",
                        "productType": "Esoteric Crafts",
                        "tags": ["crystals", "pyramid", "obsidian"],
                        "variants": {"edges": [{"node": {"id": "v1", "price": "45.00"}}]}
                    }
                },
                {
                    "node": {
                        "id": "2",
                        "title": "Clear Quartz Energy Wand",
                        "productType": "Wands",
                        "tags": ["quartz", "crystal", "energy"],
                        "variants": {"edges": [{"node": {"id": "v2", "price": "35.00"}}]}
                    }
                }
            ]
        },
        "collections": {"edges": [{"node": {"id": "c1", "title": "Bestsellers"}}]}
    }
    result = analyzer.analyze_data(sample_data)
    assert result["shop_name"] == "Gnome & Dragon Den"
    assert result["price_metrics"]["average_price"] == 40.0
    assert "crystal" in result["top_keywords"] or "obsidian" in result["top_keywords"]
