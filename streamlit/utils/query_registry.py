from typing import Dict, List, Tuple
from snowflake.snowpark import Session

_QUERY_REGISTRY: Dict[str, Tuple[str, str]] = {}

def register_query(name: str, sql: str, description: str = "") -> str:
    _QUERY_REGISTRY[name] = (sql, description)
    return sql

def get_all_queries() -> Dict[str, Tuple[str, str]]:
    return _QUERY_REGISTRY.copy()

PERFORMANCE_SNAPSHOT_SQL = register_query(
    "performance_snapshot",
    """
    SELECT * FROM ANALYTICS.FACT_PERFORMANCE_SNAPSHOT
    ORDER BY PERFORMANCE_MONTH DESC
    """,
    "Full performance snapshot data"
)

LATEST_METRICS_SQL = register_query(
    "latest_metrics",
    """
    SELECT 
        REGION,
        STRATEGY_MODE,
        ROUND(AVG(OTIF_PCT), 1) as OTIF,
        ROUND(AVG(GROSS_MARGIN_PCT), 1) as MARGIN,
        ROUND(AVG(ROCE_PCT), 1) as ROCE,
        ROUND(SUM(FREE_CASH_FLOW_USD) / 1000000, 2) as FCF_M
    FROM ANALYTICS.FACT_PERFORMANCE_SNAPSHOT
    WHERE PERFORMANCE_MONTH >= DATEADD(MONTH, -3, CURRENT_DATE())
    GROUP BY REGION, STRATEGY_MODE
    ORDER BY REGION, STRATEGY_MODE
    """,
    "Latest 3-month performance metrics"
)

INVENTORY_BREAKDOWN_SQL = register_query(
    "inventory_breakdown",
    """
    SELECT 
        PERFORMANCE_MONTH,
        ROUND(SUM(CYCLE_STOCK_VALUE) / 1000000, 2) as CYCLE_M,
        ROUND(SUM(SAFETY_STOCK_VALUE) / 1000000, 2) as SAFETY_M,
        ROUND(SUM(PIPELINE_STOCK_VALUE) / 1000000, 2) as PIPELINE_M,
        ROUND(SUM(ANTICIPATION_STOCK_VALUE) / 1000000, 2) as ANTICIPATION_M,
        ROUND(SUM(STRATEGIC_STOCK_VALUE) / 1000000, 2) as STRATEGIC_M
    FROM ANALYTICS.FACT_PERFORMANCE_SNAPSHOT
    GROUP BY PERFORMANCE_MONTH
    ORDER BY PERFORMANCE_MONTH
    """,
    "Monthly inventory decomposition"
)

TRIANGLE_METRICS_SQL = register_query(
    "triangle_metrics",
    """
    SELECT 
        STRATEGY_MODE,
        ROUND(AVG(OTIF_PCT), 2) as SERVICE,
        ROUND(AVG(GROSS_MARGIN_PCT), 2) as COST,
        ROUND(AVG(ROCE_PCT), 2) as CASH
    FROM ANALYTICS.FACT_PERFORMANCE_SNAPSHOT
    WHERE PERFORMANCE_MONTH >= DATEADD(MONTH, -1, CURRENT_DATE())
    GROUP BY STRATEGY_MODE
    """,
    "Triangle trade-off metrics by strategy"
)

SCENARIO_CONTROL_SQL = register_query(
    "scenario_control",
    """
    SELECT * FROM ANALYTICS.SCENARIO_CONTROL
    ORDER BY STRATEGY_MODE, SHOCK_EVENT NULLS FIRST
    """,
    "Scenario control parameters"
)

FINANCIAL_BRIDGE_SQL = register_query(
    "financial_bridge",
    """
    SELECT 
        PERFORMANCE_MONTH,
        ROUND(SUM(NOPAT_USD) / 1000000, 2) as NOPAT_M,
        ROUND(SUM(WORKING_CAPITAL_DELTA_USD) / 1000000, 2) as WC_DELTA_M,
        ROUND(SUM(FIXED_ASSET_DELTA_USD) / 1000000, 2) as FA_DELTA_M,
        ROUND(SUM(FREE_CASH_FLOW_USD) / 1000000, 2) as FCF_M,
        ROUND(AVG(ROCE_PCT), 2) as ROCE_PCT
    FROM ANALYTICS.FACT_PERFORMANCE_SNAPSHOT
    GROUP BY PERFORMANCE_MONTH
    ORDER BY PERFORMANCE_MONTH DESC
    LIMIT 12
    """,
    "Financial bridge waterfall data"
)

CAUSAL_TRACES_SQL = register_query(
    "causal_traces",
    """
    SELECT * FROM INTELLIGENCE.CAUSAL_TRACE_DEFINITIONS
    ORDER BY CAUSAL_WEIGHT DESC
    """,
    "Causal trace relationship definitions"
)

PREDICTIONS_SQL = register_query(
    "predictions",
    """
    SELECT 
        p.PERFORMANCE_MONTH,
        p.REGION,
        s.STRATEGY_MODE,
        s.SHOCK_EVENT,
        ROUND(p.PREDICTED_FCF_USD / 1000000, 2) as PRED_FCF_M,
        ROUND(p.PREDICTED_ROCE_PCT, 2) as PRED_ROCE,
        ROUND(p.PREDICTED_SAFETY_STOCK_USD / 1000000, 2) as PRED_SAFETY_M
    FROM CONSUMPTION.PREDICTIVE_BRIDGE p
    JOIN ANALYTICS.SCENARIO_CONTROL s ON p.SCENARIO_ID = s.SCENARIO_ID
    WHERE p.PERFORMANCE_MONTH >= DATEADD(MONTH, -6, CURRENT_DATE())
    ORDER BY p.PERFORMANCE_MONTH DESC
    """,
    "ML predictions with scenario context"
)

PIPELINE_VS_ROCE_SQL = register_query(
    "pipeline_vs_roce",
    """
    SELECT 
        PERFORMANCE_MONTH,
        ROUND(SUM(PIPELINE_STOCK_VALUE) / 1000000, 2) as PIPELINE_M,
        ROUND(AVG(ROCE_PCT), 2) as ROCE
    FROM ANALYTICS.FACT_PERFORMANCE_SNAPSHOT
    WHERE PERFORMANCE_MONTH >= DATEADD(YEAR, -1, CURRENT_DATE())
    GROUP BY PERFORMANCE_MONTH
    ORDER BY PERFORMANCE_MONTH
    """,
    "Pipeline stock vs ROCE trend (Golden Query)"
)
