# Project Causal Chain: About Section
## Dual-Audience Application Guide

---

## Overview

This About section is designed for the **Streamlit application** and serves two distinct audiences through a tabbed interface. It explains what the Strategy Simulator does, why it matters, and how to use it.

---

## Tab 1: Executive View

### What Is the Strategy Simulator?

**A financial flight simulator for supply chain decisions.**

The Strategy Simulator transforms how your organization makes operational choices by showing—in real-time—how every lever pulls on your financial outcomes.

### The Core Problem It Solves

Most companies manage supply chain through isolated metrics:
- **Sales** optimizes service (OTIF, fill rate)
- **Operations** optimizes cost (COGS, OEE)
- **Finance** optimizes cash (inventory turns, ROCE)

No one owns the **trade-offs** between them.

When service improves by 2%, what did it cost in margin? When inventory drops, did service suffer? These questions take weeks to answer—if they get answered at all.

**The Strategy Simulator answers them instantly.**

### What You Can Do

| Capability | Business Value |
|------------|----------------|
| **Select a Strategy Mode** | Align the entire dashboard to Growth, Margin, or Cash priorities |
| **Run Shock Scenarios** | See how port strikes or demand surges impact your financials *before* they happen |
| **Trace Causality** | Click any metric to see its upstream drivers and downstream consequences |
| **Simulate ROCE Changes** | Adjust safety stock, lead times, and batch sizes to see projected returns |
| **Ask Questions in Plain English** | Use the AI assistant to query your data without writing SQL |

### The Strategic Framework

```
            ┌─────────────┐
            │   SERVICE   │
            │   (OTIF)    │
            └──────┬──────┘
                   │
        ┌──────────┼──────────┐
        │                     │
        ▼                     ▼
┌───────────────┐     ┌───────────────┐
│     COST      │◄───►│     CASH      │
│   (Margin)    │     │    (ROCE)     │
└───────────────┘     └───────────────┘
```

**You cannot optimize all three corners simultaneously.** The simulator shows you *which* trade-offs you're making and *whether* they align with your strategic intent.

### How to Read the Dashboard

1. **Valuation Bar (Top):** Your financial north star—ROCE, FCF, EVA, Capital Employed
2. **Trade-Off Triangle (Center):** The active corner glows; weights show priority
3. **Causal Trace (Middle):** Interactive flow showing how metrics connect
4. **Inventory Decomposition (Bottom):** Why each dollar of inventory exists
5. **Financial Bridge (Footer):** NOPAT - Working Capital Changes = FCF

### Quick Start for Executives

1. **Select your role** (CFO, VP Supply Chain, Data Analyst)
2. **Choose a Strategy Mode** (Growth, Margin, Cash)
3. **Apply a Shock Event** to see scenario impacts
4. **Use the ROCE Sensitivity Calculator** to test specific changes
5. **Ask the AI Assistant** any question about your data

---

## Tab 2: Technical View

### Architecture Overview

The Strategy Simulator is built entirely on **Snowflake**, leveraging native AI/ML capabilities for real-time insights.

```
┌─────────────────────────────────────────────────────────────────┐
│                     SNOWFLAKE PLATFORM                          │
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │  ANALYTICS  │───►│ CONSUMPTION │───►│   CORTEX    │         │
│  │   LAYER     │    │    LAYER    │    │     AI      │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│        │                   │                  │                 │
│        └───────────────────┴──────────────────┘                 │
│                            │                                    │
│                            ▼                                    │
│                   ┌─────────────────┐                           │
│                   │   STREAMLIT     │                           │
│                   │   IN SNOWFLAKE  │                           │
│                   └─────────────────┘                           │
└─────────────────────────────────────────────────────────────────┘
```

### Data Model

| Table | Schema | Purpose | Row Count |
|-------|--------|---------|-----------|
| FACT_PERFORMANCE_SNAPSHOT | ANALYTICS | Monthly KPIs across Service/Cost/Cash | 432 |
| DIM_INVENTORY_STRUCTURE | ANALYTICS | Inventory type definitions | 5 |
| SCENARIO_CONTROL | ANALYTICS | Strategy modes + shock events | 12 |
| PREDICTIVE_BRIDGE | CONSUMPTION | Pre-computed ML predictions | 1,728 |
| CAUSAL_TRACE_DEFINITIONS | INTELLIGENCE | Metric relationships | 10 |
| QBR_DOCUMENTS | INTELLIGENCE | Document content for RAG | 3 |

### Key Metrics Tracked

**Service Corner:**
- `OTIF_PCT` - On-Time In-Full delivery percentage
- `FILL_RATE_PCT` - Order fill rate
- `NET_SALES_GROWTH_PCT` - YoY revenue growth
- `LEAD_TIME_DAYS` - Order-to-delivery time

**Cost Corner:**
- `GROSS_MARGIN_PCT` - Gross margin percentage
- `EBITDA_MARGIN_PCT` - Operating margin
- `COGS_USD` - Cost of goods sold
- `OEE_PCT` - Overall Equipment Effectiveness

**Cash Corner:**
- `ROCE_PCT` - Return on Capital Employed
- `FREE_CASH_FLOW_USD` - Free cash flow
- `CASH_CONVERSION_CYCLE_DAYS` - CCC
- `DIOH_DAYS` - Days Inventory On Hand

### Inventory Decomposition

The simulator breaks inventory into five economic categories:

| Type | Driver | Reduction Strategy |
|------|--------|-------------------|
| **Cycle** | Batch sizes, order frequency | Reduce EOQ, increase frequency |
| **Safety** | Forecast error, supply variability | Improve MAPE, reduce lead time variance |
| **Pipeline** | Transit lead times | Nearshore, reduce handling |
| **Anticipation** | Seasonal builds, shutdowns | Level production, flexible capacity |
| **Strategic** | Geopolitical risk, hedging | Diversify suppliers, dual-source |

### ML Predictions

Predictions are **pre-computed** using Snowpark ML and stored in `PREDICTIVE_BRIDGE`:

- **Algorithm:** Prophet (time series) + XGBoost (regression)
- **Target Variables:** FCF, ROCE, Safety Stock
- **Confidence Intervals:** 90% CI stored as `FCF_LOWER_BOUND`, `FCF_UPPER_BOUND`
- **Scenario Coverage:** All strategy modes × all shock events

### Cortex AI Integration

| Service | Model | Use Case |
|---------|-------|----------|
| **Cortex Analyst** | Semantic Model | Text-to-SQL for ad-hoc queries |
| **Cortex Search** | Embedding + Vector | RAG over QBR documents |
| **Cortex Complete** | mistral-large2 | Natural language explanations |

**Semantic Model:** `causal_chain_model.yaml`
- 4 tables, 25+ dimensions/metrics
- 6 verified queries for golden path testing

### Visualization Components

| Component | Library | Purpose |
|-----------|---------|---------|
| Trade-Off Triangle | Plotly Scatter | Strategy mode visualization |
| Causal Sankey | Plotly Sankey | Metric flow diagram |
| ROCE Gauge | Plotly Indicator | Sensitivity calculator output |
| Inventory Stack | Plotly Area | Inventory decomposition over time |
| Financial Waterfall | Plotly Waterfall | FCF bridge |

### Performance Optimizations

1. **Query Registry:** Pre-defined SQL stored in `query_registry.py` for sub-second load
2. **Caching:** `@st.cache_data(ttl=300)` on all data fetches
3. **Pre-aggregation:** 36-month data pre-aggregated to monthly level
4. **Batch Predictions:** ML inference done offline, not at runtime

### Session State

| Key | Purpose |
|-----|---------|
| `persona` | Selected role (CFO, VP Supply Chain, Data Analyst) |
| `compare_baseline` | Toggle for baseline vs scenario comparison |

### API Patterns

**Cortex Complete Query:**
```python
session.sql(f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', $${prompt}$$)
""").collect()
```

**Document Search:**
```python
session.sql(f"""
    SELECT * FROM INTELLIGENCE.QBR_DOCUMENTS
    WHERE CONTAINS(LOWER(CONTENT_TEXT), LOWER('{query}'))
""").to_pandas()
```

### Deployment

```bash
# Deploy via Snowflake CLI
snow streamlit deploy \
    --database CAUSAL_CHAIN \
    --schema APPS \
    --warehouse CAUSAL_CHAIN_WH
```

**Files:**
- `streamlit_app.py` - Main application
- `snowflake.yml` - Deployment configuration
- `environment.yml` - Python dependencies

### Error Handling

- All Cortex calls wrapped in try/except with user-friendly messages
- Data loading includes empty dataframe checks
- Confidence intervals gracefully degrade if bounds not present

---

## Integration Guide

### Adding to Streamlit App

```python
import streamlit as st

with st.sidebar:
    with st.expander("About This App"):
        tab1, tab2 = st.tabs(["Executive", "Technical"])
        with tab1:
            st.markdown(EXECUTIVE_CONTENT)
        with tab2:
            st.markdown(TECHNICAL_CONTENT)
```

### Suggested Placement

- **Sidebar:** Collapsible "About" expander (recommended)
- **Footer:** Link to documentation page
- **Help Modal:** Question mark icon in header

---

*Document Version: 1.0 | Created: 2026-01-25 | Project Causal Chain*
