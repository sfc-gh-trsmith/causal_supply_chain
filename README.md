# Causal Chain: Strategy Simulator

Supply chain financial simulator demonstrating causal relationships between operational metrics and financial outcomes. Built for CFO-level strategic planning and what-if analysis.

## Features

- **Strategy Modes**: GROWTH, MARGIN, CASH prioritization with dynamic trade-off visualization
- **Shock Scenarios**: Supply disruption, port strike, and demand surge simulations
- **ROCE Sensitivity Calculator**: Real-time impact modeling for inventory and lead time changes
- **AI-Powered Causal Analysis**: Cortex COMPLETE explains metric relationships
- **Interactive Dashboards**: Trade-off triangle, inventory decomposition, financial bridge

## Quick Start

```bash
# Deploy infrastructure, data, and Streamlit app
./deploy.sh

# Run validation tests
./run.sh test

# Get Streamlit URL
./run.sh streamlit

# Teardown all resources
./clean.sh -y
```

## Architecture

| Component | Resource |
|-----------|----------|
| Database | CAUSAL_CHAIN |
| Warehouse | CAUSAL_CHAIN_WH (X-SMALL, 90-min auto-suspend) |
| Role | CAUSAL_CHAIN_ROLE |
| Streamlit App | STRATEGY_SIMULATOR |
| AI Model | Cortex COMPLETE (mistral-large2) |

## Data Model

```
ANALYTICS.FACT_PERFORMANCE_SNAPSHOT  -- Monthly metrics by strategy mode
ANALYTICS.DIM_INVENTORY_STRUCTURE    -- Inventory type definitions
ANALYTICS.SCENARIO_CONTROL           -- Strategy weights and shock modifiers
CONSUMPTION.PREDICTIVE_BRIDGE        -- ML predictions with confidence intervals
INTELLIGENCE.CAUSAL_TRACE_DEFINITIONS -- Metric relationship weights
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SNOWFLAKE_CONNECTION_NAME | demo | Snowflake CLI connection name |
| ENV_PREFIX | (none) | Optional prefix for multi-tenant deployment |

## Project Structure

```
causal_supply_chain/
├── deploy.sh              # Full deployment script
├── run.sh                 # Validation and utility commands
├── clean.sh               # Teardown script
├── sql/                   # DDL and data loading scripts
│   ├── 01_infrastructure.sql
│   ├── 02_schemas.sql
│   ├── 03_tables.sql
│   ├── 04_data.sql
│   ├── 05_cortex_search.sql
│   └── 06_semantic_model.sql
├── streamlit/             # Streamlit application
│   ├── streamlit_app.py
│   ├── snowflake.yml
│   ├── environment.yml
│   └── utils/
├── data/synthetic/        # Pre-generated demo data (CSV)
└── semantic/              # Cortex Analyst semantic model
```

## Requirements

- Snowflake account with Cortex enabled
- Snowflake CLI (`snow`) installed
- ACCOUNTADMIN role (for initial setup)
