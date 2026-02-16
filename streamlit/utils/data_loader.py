from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from typing import Dict, Optional
import streamlit as st

def run_queries_parallel(
    session, 
    queries: Dict[str, str], 
    max_workers: int = 4,
    fail_fast: bool = True
) -> Dict[str, pd.DataFrame]:
    results: Dict[str, pd.DataFrame] = {}
    errors: list = []
    
    def execute_query(name: str, query: str):
        try:
            df = session.sql(query).to_pandas()
            if df is None:
                return name, None, f"Query '{name}' returned None"
            return name, df, None
        except Exception as e:
            return name, None, str(e)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(execute_query, n, q): n for n, q in queries.items()}
        for future in as_completed(futures):
            name, result, error = future.result()
            if error:
                errors.append(f"{name}: {error}")
            else:
                results[name] = result
    
    if errors and fail_fast:
        raise RuntimeError(f"Query failures:\n" + "\n".join(errors))
    
    return results


@st.cache_data(ttl=300)
def load_dashboard_data(_session, strategy_mode: str, shock_event: str) -> Dict[str, pd.DataFrame]:
    shock_filter = "IS NULL" if shock_event == "None" else f"= '{shock_event}'"
    
    queries = {
        'performance': f"""
            SELECT 
                f.PERFORMANCE_MONTH, f.REGION, f.STRATEGY_MODE,
                f.OTIF_PCT, f.FILL_RATE_PCT, f.NET_SALES_GROWTH_PCT,
                f.GROSS_MARGIN_PCT, f.EBITDA_MARGIN_PCT, f.COGS_USD,
                f.ROCE_PCT, f.FREE_CASH_FLOW_USD, f.CASH_CONVERSION_CYCLE_DAYS,
                f.CYCLE_STOCK_VALUE, f.SAFETY_STOCK_VALUE, f.PIPELINE_STOCK_VALUE,
                f.ANTICIPATION_STOCK_VALUE, f.STRATEGIC_STOCK_VALUE, f.TOTAL_INVENTORY_VALUE,
                f.FORECAST_MAPE_PCT, f.LEAD_TIME_DAYS, f.OEE_PCT,
                f.NOPAT_USD, f.CAPITAL_EMPLOYED_USD, f.EVA_USD,
                s.SERVICE_WEIGHT, s.COST_WEIGHT, s.CASH_WEIGHT,
                s.PERMISSIBLE_RED, s.MANDATORY_GREEN, s.ECONOMIC_BET
            FROM STRATEGY_SIMULATOR.FACT_PERFORMANCE_SNAPSHOT f
            JOIN ATOMIC.SCENARIO_CONTROL s 
                ON f.STRATEGY_MODE = s.STRATEGY_MODE 
                AND s.SHOCK_EVENT {shock_filter}
            WHERE f.STRATEGY_MODE = '{strategy_mode}'
            ORDER BY f.PERFORMANCE_MONTH DESC
        """,
        'predictions': f"""
            SELECT 
                p.PERFORMANCE_MONTH, p.REGION,
                p.PREDICTED_FCF_USD, p.PREDICTED_ROCE_PCT,
                p.PREDICTED_SAFETY_STOCK_USD, p.PREDICTED_PIPELINE_STOCK_USD,
                p.LEAD_TIME_IMPACT_FCF, p.FORECAST_ERROR_IMPACT_SAFETY,
                p.FCF_LOWER_BOUND, p.FCF_UPPER_BOUND,
                p.ROCE_LOWER_BOUND, p.ROCE_UPPER_BOUND
            FROM STRATEGY_SIMULATOR.PREDICTIVE_BRIDGE p
            JOIN ATOMIC.SCENARIO_CONTROL s ON p.SCENARIO_ID = s.SCENARIO_ID
            WHERE s.STRATEGY_MODE = '{strategy_mode}'
            AND s.SHOCK_EVENT {shock_filter}
            ORDER BY p.PERFORMANCE_MONTH DESC
        """,
        'causal_traces': """
            SELECT * FROM STRATEGY_SIMULATOR.V_CAUSAL_TRACES 
            ORDER BY CAUSAL_WEIGHT DESC
        """
    }
    
    return run_queries_parallel(_session, queries, max_workers=3, fail_fast=False)


@st.cache_data(ttl=300)
def load_baseline_data(_session, strategy_mode: str) -> pd.DataFrame:
    sql = f"""
        SELECT 
            f.PERFORMANCE_MONTH, f.REGION, f.STRATEGY_MODE,
            f.OTIF_PCT, f.GROSS_MARGIN_PCT, f.ROCE_PCT, f.FREE_CASH_FLOW_USD,
            f.SAFETY_STOCK_VALUE, f.PIPELINE_STOCK_VALUE, f.TOTAL_INVENTORY_VALUE,
            f.CAPITAL_EMPLOYED_USD, f.EVA_USD
        FROM STRATEGY_SIMULATOR.FACT_PERFORMANCE_SNAPSHOT f
        JOIN ATOMIC.SCENARIO_CONTROL s 
            ON f.STRATEGY_MODE = s.STRATEGY_MODE 
            AND s.SHOCK_EVENT IS NULL
        WHERE f.STRATEGY_MODE = '{strategy_mode}'
        ORDER BY f.PERFORMANCE_MONTH DESC
    """
    return _session.sql(sql).to_pandas()
