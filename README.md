# Shopify Supplier Scout 🚀

> **Autonomous Shopify Supplier Sourcing, AI Niche Scout & Auto-Fulfillment Agent**  
> *100% Free & Open Source — Zero Recurring Fees or Software Subscriptions*

[![Test Suite](https://github.com/frac1ur3d-hash/shopify-supplier-scout/actions/workflows/test.yml/badge.svg)](https://github.com/frac1ur3d-hash/shopify-supplier-scout/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Shopify API: 2026-07](https://img.shields.io/badge/Shopify%20API-2026--07-indigo.svg)](https://shopify.dev)

---

## ⚡ Overview

**Shopify Supplier Scout** is an autonomous agent and embedded Shopify app that removes the human bottlenecks from running a high-margin dropshipping store:

1. **Store Catalog Intelligence**: Automatically scans your existing products, tags, collections, and price distributions to identify your store's exact niche and compute optimal retail price bands.
2. **Multi-Provider Supplier Sourcing**: Connects across 4 free channels with **zero monthly subscription fees**:
   - 📦 **CJ Dropshipping API** (US, EU & Asia domestic warehouses, 3–7 day shipping)
   - 🌐 **AliExpress Open** (Massive catalog, verified review ratings)
   - 🎨 **Printify POD API** (Custom print-on-demand merchandise)
   - 🔍 **Open Supplier Hunter** (Direct-from-factory directories with zero middlemen)
3. **Smart Pricing & Discount Generation**:
   - Auto-applies 2.5×–3× markup with psychological `.99` endings (e.g. $10 cost → $27.99 retail).
   - Generates high perceived-value `compareAtPrice` strike-through discounts.
4. **Autonomous Order Routing & Failsafe Dispatch**:
   - Intercepts `orders/paid` webhooks.
   - Evaluates margin protection: automatically dispatches orders to suppliers while halting orders that drop below your profit margin safety threshold.
   - Pushes tracking numbers to Shopify (`fulfillmentCreateV2`) to notify buyers.
5. **Sleek, Zero-Lag Embedded UI**:
   - Glassmorphic Obsidian interface with 60fps micro-interactions.
   - **Orbital Thinking Indicators**: Circular rotating arrows that orbit around whichever module is currently computing or scouting suppliers.

---

## 📁 Repository Structure

```
shopify-supplier-scout/
├── .github/workflows/       # CI test suite & Hugging Face Space auto-deploy
├── agent/                   # Autonomous Python FastAPI Backend
│   ├── app/
│   │   ├── main.py          # API routes & static UI mount
│   │   ├── store_analyzer.py # GraphQL store & niche scanner
│   │   ├── pricing_engine.py # Psychological .99 pricing & margin safety
│   │   ├── catalog_injector.py # GraphQL productCreate mutation
│   │   ├── order_dispatcher.py # orders/paid webhook & fulfillment tracking
│   │   └── suppliers/       # CJ, AliExpress, Printify, Open Hunter adapters
│   ├── tests/               # Pytest suite
│   ├── requirements.txt
│   └── Dockerfile           # Free 24/7 container deployment
├── web/
│   └── public/
│       └── index.html       # Sleek Glassmorphism UI with Orbital Thinking Arrows
└── shopify.app.toml         # Shopify App CLI manifest & scopes
```

---

## 🚀 Quick Start (Local Development)

### 1. Clone & Set Up Python Environment
```bash
git clone https://github.com/frac1ur3d-hash/shopify-supplier-scout.git
cd shopify-supplier-scout/agent
pip install -r requirements.txt
```

### 2. Configure Environment (`agent/.env`)
```env
SHOPIFY_STORE_DOMAIN=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_your_token_here
DEFAULT_PRICE_MULTIPLIER=2.75
MIN_PROFIT_MARGIN_PCT=35.0
AUTO_DISPATCH_ORDERS=true
```

### 3. Run the Agent & Embedded Dashboard
```bash
uvicorn app.main:app --reload --port 7860
```
Open **`http://localhost:7860`** in your browser to view the interactive dashboard with live supplier scouting and orbital thinking arrows.

### 4. Run the Tests
```bash
pytest
```

---

## 🛡️ License

MIT License. Free to use, adapt, and scale.
