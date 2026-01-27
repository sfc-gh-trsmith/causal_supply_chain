import random
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

RANDOM_SEED = 42
OUTPUT_DIR = "data/synthetic"

REGIONS = ['NORTH_AMERICA', 'EUROPE', 'ASIA_PACIFIC', 'LATAM']
STRATEGY_MODES = ['GROWTH', 'MARGIN', 'CASH']
INVENTORY_TYPES = ['CYCLE', 'SAFETY', 'PIPELINE', 'ANTICIPATION', 'STRATEGIC']
SHOCK_EVENTS = [None, 'SUPPLY_DISRUPTION', 'PORT_STRIKE', 'DEMAND_SURGE', 'COMMODITY_SPIKE']

def generate_performance_snapshot(months=36):
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    
    end_date = datetime(2025, 12, 1)
    start_date = end_date - relativedelta(months=months-1)
    
    dates = [start_date + relativedelta(months=i) for i in range(months)]
    
    rows = []
    snapshot_id = 1
    
    for date in dates:
        for region in REGIONS:
            for mode in STRATEGY_MODES:
                base_otif = np.random.normal(92, 3)
                base_margin = np.random.normal(35, 5)
                base_roce = np.random.normal(15, 3)
                
                if mode == 'GROWTH':
                    otif_adj = 3
                    margin_adj = -2
                    roce_adj = -1
                elif mode == 'MARGIN':
                    otif_adj = -2
                    margin_adj = 4
                    roce_adj = 1
                else:
                    otif_adj = -1
                    margin_adj = -1
                    roce_adj = 3
                
                seasonal = np.sin(2 * np.pi * date.month / 12) * 2
                trend = (date.month + (date.year - 2023) * 12) * 0.05
                
                cycle_stock = np.random.uniform(5, 15) * 1_000_000
                safety_stock = np.random.uniform(3, 10) * 1_000_000
                pipeline_stock = np.random.uniform(2, 8) * 1_000_000
                anticipation_stock = np.random.uniform(0.5, 3) * 1_000_000 * (1 + seasonal * 0.3)
                strategic_stock = np.random.uniform(1, 5) * 1_000_000
                total_inventory = cycle_stock + safety_stock + pipeline_stock + anticipation_stock + strategic_stock
                
                cogs = np.random.uniform(50, 80) * 1_000_000
                sga = np.random.uniform(10, 20) * 1_000_000
                nopat = np.random.uniform(5, 15) * 1_000_000
                capital_employed = np.random.uniform(80, 120) * 1_000_000
                wc_delta = np.random.uniform(-2, 2) * 1_000_000
                fa_delta = np.random.uniform(-1, 1) * 1_000_000
                fcf = nopat - wc_delta - fa_delta
                eva = nopat - (capital_employed * 0.10)
                
                row = {
                    'SNAPSHOT_ID': snapshot_id,
                    'PERFORMANCE_MONTH': date.strftime('%Y-%m-%d'),
                    'REGION': region,
                    'STRATEGY_MODE': mode,
                    'OTIF_PCT': round(min(99, max(80, base_otif + otif_adj + seasonal)), 2),
                    'FILL_RATE_PCT': round(min(99, max(85, base_otif + otif_adj - 2 + np.random.normal(0, 1))), 2),
                    'NET_SALES_GROWTH_PCT': round(np.random.normal(5, 3) + trend + (2 if mode == 'GROWTH' else 0), 2),
                    'LEAD_TIME_DAYS': round(max(3, np.random.normal(12, 3) + (-2 if mode == 'GROWTH' else 1)), 1),
                    'ORDER_FLEXIBILITY_SCORE': round(np.random.uniform(70, 95), 1),
                    'FORECAST_MAPE_PCT': round(max(5, np.random.normal(18, 5)), 1),
                    'FORECAST_BIAS_PCT': round(np.random.normal(2, 3), 1),
                    'NPI_COUNT': int(max(0, np.random.poisson(3) + (2 if mode == 'GROWTH' else 0))),
                    'GROSS_MARGIN_PCT': round(min(50, max(20, base_margin + margin_adj + seasonal)), 2),
                    'EBITDA_MARGIN_PCT': round(min(25, max(5, base_margin * 0.5 + margin_adj * 0.5)), 2),
                    'COGS_USD': round(cogs, 2),
                    'SGA_USD': round(sga, 2),
                    'OEE_PCT': round(min(95, max(60, np.random.normal(78, 8))), 1),
                    'FIRST_PASS_YIELD_PCT': round(min(99, max(85, np.random.normal(94, 3))), 1),
                    'PURCHASING_PRICE_INDEX': round(np.random.normal(100, 5) + trend * 0.5, 2),
                    'ROCE_PCT': round(min(25, max(5, base_roce + roce_adj + trend * 0.2)), 2),
                    'FREE_CASH_FLOW_USD': round(fcf, 2),
                    'CASH_CONVERSION_CYCLE_DAYS': round(max(20, np.random.normal(45, 10) + (-5 if mode == 'CASH' else 3)), 1),
                    'DIOH_DAYS': round(max(20, np.random.normal(55, 12)), 1),
                    'DSO_DAYS': round(max(25, np.random.normal(40, 8)), 1),
                    'DPO_DAYS': round(max(30, np.random.normal(50, 10)), 1),
                    'ASSET_TURNS': round(np.random.uniform(1.5, 3.5), 2),
                    'CYCLE_STOCK_VALUE': round(cycle_stock, 2),
                    'SAFETY_STOCK_VALUE': round(safety_stock, 2),
                    'PIPELINE_STOCK_VALUE': round(pipeline_stock, 2),
                    'ANTICIPATION_STOCK_VALUE': round(anticipation_stock, 2),
                    'STRATEGIC_STOCK_VALUE': round(strategic_stock, 2),
                    'TOTAL_INVENTORY_VALUE': round(total_inventory, 2),
                    'NOPAT_USD': round(nopat, 2),
                    'WORKING_CAPITAL_DELTA_USD': round(wc_delta, 2),
                    'FIXED_ASSET_DELTA_USD': round(fa_delta, 2),
                    'CAPITAL_EMPLOYED_USD': round(capital_employed, 2),
                    'EVA_USD': round(eva, 2)
                }
                rows.append(row)
                snapshot_id += 1
    
    return pd.DataFrame(rows)

def generate_inventory_structure():
    data = [
        {
            'INVENTORY_ID': 1,
            'INVENTORY_TYPE': 'CYCLE',
            'DESCRIPTION': 'Stock created by ordering or producing in batches. The saw-tooth pattern of order, consume, reorder.',
            'ECONOMIC_DRIVER': 'Batch sizes and order frequencies',
            'TYPICAL_RANGE_PCT_LOW': 25,
            'TYPICAL_RANGE_PCT_HIGH': 40,
            'REDUCTION_STRATEGY': 'Reduce batch sizes, increase order frequency, implement Kanban systems'
        },
        {
            'INVENTORY_ID': 2,
            'INVENTORY_TYPE': 'SAFETY',
            'DESCRIPTION': 'Buffer against variability in demand and supply. Insurance against uncertainty.',
            'ECONOMIC_DRIVER': 'Forecast error and supply variability',
            'TYPICAL_RANGE_PCT_LOW': 15,
            'TYPICAL_RANGE_PCT_HIGH': 30,
            'REDUCTION_STRATEGY': 'Improve forecast accuracy, reduce supplier lead time variability, implement demand sensing'
        },
        {
            'INVENTORY_ID': 3,
            'INVENTORY_TYPE': 'PIPELINE',
            'DESCRIPTION': 'Work in process and in-transit inventory. Exists purely because of lead time.',
            'ECONOMIC_DRIVER': 'Transit lead times and manufacturing cycle times',
            'TYPICAL_RANGE_PCT_LOW': 10,
            'TYPICAL_RANGE_PCT_HIGH': 25,
            'REDUCTION_STRATEGY': 'Reduce lead times, nearshore manufacturing, optimize logistics routes'
        },
        {
            'INVENTORY_ID': 4,
            'INVENTORY_TYPE': 'ANTICIPATION',
            'DESCRIPTION': 'Inventory built ahead of known events such as seasonal demand or planned shutdowns.',
            'ECONOMIC_DRIVER': 'Seasonal patterns and planned capacity constraints',
            'TYPICAL_RANGE_PCT_LOW': 5,
            'TYPICAL_RANGE_PCT_HIGH': 15,
            'REDUCTION_STRATEGY': 'Level production scheduling, flexible capacity, postponement strategies'
        },
        {
            'INVENTORY_ID': 5,
            'INVENTORY_TYPE': 'STRATEGIC',
            'DESCRIPTION': 'Inventory held against uncertain future events such as expected shortages or geopolitical risk.',
            'ECONOMIC_DRIVER': 'Geopolitical risk and commodity hedging decisions',
            'TYPICAL_RANGE_PCT_LOW': 5,
            'TYPICAL_RANGE_PCT_HIGH': 20,
            'REDUCTION_STRATEGY': 'Diversify supplier base, qualify alternate materials, implement risk monitoring'
        }
    ]
    return pd.DataFrame(data)

def generate_scenario_control():
    scenarios = []
    scenario_id = 1
    
    base_scenarios = [
        {
            'STRATEGY_MODE': 'GROWTH',
            'SHOCK_EVENT': None,
            'SERVICE_WEIGHT': 1.5,
            'COST_WEIGHT': 0.8,
            'CASH_WEIGHT': 0.7,
            'OTIF_DELTA_PCT': 3,
            'LEAD_TIME_DELTA_DAYS': -2,
            'SAFETY_STOCK_DELTA_PCT': 10,
            'PIPELINE_STOCK_DELTA_PCT': 5,
            'ROCE_DELTA_PCT': -2,
            'FCF_DELTA_PCT': -5,
            'PERMISSIBLE_RED': 'CASH',
            'MANDATORY_GREEN': 'SERVICE',
            'ECONOMIC_BET': 'Revenue growth will outpace capital cost'
        },
        {
            'STRATEGY_MODE': 'MARGIN',
            'SHOCK_EVENT': None,
            'SERVICE_WEIGHT': 0.8,
            'COST_WEIGHT': 1.5,
            'CASH_WEIGHT': 1.0,
            'OTIF_DELTA_PCT': -2,
            'LEAD_TIME_DELTA_DAYS': 3,
            'SAFETY_STOCK_DELTA_PCT': -5,
            'PIPELINE_STOCK_DELTA_PCT': 0,
            'ROCE_DELTA_PCT': 2,
            'FCF_DELTA_PCT': 3,
            'PERMISSIBLE_RED': 'SERVICE',
            'MANDATORY_GREEN': 'COST',
            'ECONOMIC_BET': 'Profitability is more vital than volume'
        },
        {
            'STRATEGY_MODE': 'CASH',
            'SHOCK_EVENT': None,
            'SERVICE_WEIGHT': 0.7,
            'COST_WEIGHT': 0.9,
            'CASH_WEIGHT': 1.6,
            'OTIF_DELTA_PCT': -1,
            'LEAD_TIME_DELTA_DAYS': 2,
            'SAFETY_STOCK_DELTA_PCT': -15,
            'PIPELINE_STOCK_DELTA_PCT': -10,
            'ROCE_DELTA_PCT': 5,
            'FCF_DELTA_PCT': 10,
            'PERMISSIBLE_RED': 'SERVICE',
            'MANDATORY_GREEN': 'ROCE',
            'ECONOMIC_BET': 'Liquidity is the priority over expansion'
        }
    ]
    
    for base in base_scenarios:
        base['SCENARIO_ID'] = scenario_id
        scenarios.append(base.copy())
        scenario_id += 1
        
        for shock in ['SUPPLY_DISRUPTION', 'PORT_STRIKE', 'DEMAND_SURGE']:
            shocked = base.copy()
            shocked['SCENARIO_ID'] = scenario_id
            shocked['SHOCK_EVENT'] = shock
            
            if shock == 'SUPPLY_DISRUPTION':
                shocked['LEAD_TIME_DELTA_DAYS'] += 5
                shocked['SAFETY_STOCK_DELTA_PCT'] += 20
                shocked['PIPELINE_STOCK_DELTA_PCT'] += 15
                shocked['OTIF_DELTA_PCT'] -= 5
                shocked['FCF_DELTA_PCT'] -= 8
            elif shock == 'PORT_STRIKE':
                shocked['LEAD_TIME_DELTA_DAYS'] += 10
                shocked['PIPELINE_STOCK_DELTA_PCT'] += 30
                shocked['FCF_DELTA_PCT'] -= 12
                shocked['ROCE_DELTA_PCT'] -= 3
            elif shock == 'DEMAND_SURGE':
                shocked['OTIF_DELTA_PCT'] -= 8
                shocked['SAFETY_STOCK_DELTA_PCT'] += 25
                shocked['FCF_DELTA_PCT'] -= 6
            
            scenarios.append(shocked)
            scenario_id += 1
    
    return pd.DataFrame(scenarios)

def generate_predictive_bridge(perf_df, scenario_df):
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    
    rows = []
    bridge_id = 1
    
    months = perf_df['PERFORMANCE_MONTH'].unique()
    regions = perf_df['REGION'].unique()
    
    for month in months:
        for region in regions:
            for _, scenario in scenario_df.iterrows():
                base_perf = perf_df[
                    (perf_df['PERFORMANCE_MONTH'] == month) & 
                    (perf_df['REGION'] == region) &
                    (perf_df['STRATEGY_MODE'] == scenario['STRATEGY_MODE'])
                ]
                
                if len(base_perf) == 0:
                    continue
                    
                base = base_perf.iloc[0]
                
                base_fcf = base['FREE_CASH_FLOW_USD']
                base_roce = base['ROCE_PCT']
                base_safety = base['SAFETY_STOCK_VALUE']
                base_pipeline = base['PIPELINE_STOCK_VALUE']
                
                pred_fcf = base_fcf * (1 + scenario['FCF_DELTA_PCT'] / 100)
                pred_roce = base_roce + scenario['ROCE_DELTA_PCT']
                pred_safety = base_safety * (1 + scenario['SAFETY_STOCK_DELTA_PCT'] / 100)
                pred_pipeline = base_pipeline * (1 + scenario['PIPELINE_STOCK_DELTA_PCT'] / 100)
                
                noise = np.random.normal(0, 0.02)
                
                row = {
                    'BRIDGE_ID': bridge_id,
                    'PERFORMANCE_MONTH': month,
                    'REGION': region,
                    'SCENARIO_ID': scenario['SCENARIO_ID'],
                    'PREDICTED_FCF_USD': round(pred_fcf * (1 + noise), 2),
                    'PREDICTED_ROCE_PCT': round(pred_roce * (1 + noise * 0.5), 2),
                    'PREDICTED_SAFETY_STOCK_USD': round(pred_safety * (1 + noise), 2),
                    'PREDICTED_PIPELINE_STOCK_USD': round(pred_pipeline * (1 + noise), 2),
                    'LEAD_TIME_IMPACT_FCF': round(-scenario['LEAD_TIME_DELTA_DAYS'] * 50000, 2),
                    'FORECAST_ERROR_IMPACT_SAFETY': round(base['FORECAST_MAPE_PCT'] * 20000, 2),
                    'BATCH_SIZE_IMPACT_CYCLE': round(base['CYCLE_STOCK_VALUE'] * 0.1 * np.random.uniform(0.8, 1.2), 2),
                    'FCF_LOWER_BOUND': round(pred_fcf * 0.85, 2),
                    'FCF_UPPER_BOUND': round(pred_fcf * 1.15, 2),
                    'ROCE_LOWER_BOUND': round(pred_roce * 0.9, 2),
                    'ROCE_UPPER_BOUND': round(pred_roce * 1.1, 2),
                    'MODEL_SOURCE': 'XGBOOST' if np.random.random() > 0.3 else 'PROPHET'
                }
                rows.append(row)
                bridge_id += 1
    
    return pd.DataFrame(rows)

def generate_ml_registry():
    data = [
        {
            'PREDICTION_ID': 1,
            'MODEL_NAME': 'PROPHET',
            'MODEL_VERSION': '1.0.0',
            'TARGET_VARIABLE': 'FREE_CASH_FLOW_USD',
            'FEATURE_SET': '["PERFORMANCE_MONTH", "REGION", "STRATEGY_MODE", "SEASONAL_COMPONENT"]',
            'TRAINING_DATE': '2025-01-15',
            'VALIDATION_METRICS': '{"MAPE": 8.2, "RMSE": 450000, "R2": 0.87}',
            'IS_ACTIVE': True
        },
        {
            'PREDICTION_ID': 2,
            'MODEL_NAME': 'XGBOOST',
            'MODEL_VERSION': '2.1.0',
            'TARGET_VARIABLE': 'ADJUSTED_FCF',
            'FEATURE_SET': '["LEAD_TIME_DAYS", "SAFETY_STOCK_VALUE", "FORECAST_MAPE_PCT", "OEE_PCT", "BATCH_SIZE"]',
            'TRAINING_DATE': '2025-02-01',
            'VALIDATION_METRICS': '{"MAPE": 6.5, "RMSE": 380000, "R2": 0.91}',
            'IS_ACTIVE': True
        },
        {
            'PREDICTION_ID': 3,
            'MODEL_NAME': 'XGBOOST',
            'MODEL_VERSION': '2.0.0',
            'TARGET_VARIABLE': 'PREDICTED_SAFETY_STOCK',
            'FEATURE_SET': '["FORECAST_MAPE_PCT", "LEAD_TIME_VARIABILITY", "SERVICE_LEVEL_TARGET"]',
            'TRAINING_DATE': '2025-01-20',
            'VALIDATION_METRICS': '{"MAPE": 5.1, "RMSE": 120000, "R2": 0.93}',
            'IS_ACTIVE': True
        }
    ]
    return pd.DataFrame(data)

def generate_causal_traces():
    traces = [
        {'SOURCE_METRIC': 'FORECAST_MAPE_PCT', 'TARGET_METRIC': 'SAFETY_STOCK_VALUE', 'RELATIONSHIP_TYPE': 'POSITIVE', 'CAUSAL_WEIGHT': 0.85, 
         'DESCRIPTION': 'Higher forecast error requires larger safety stock buffers to maintain service levels',
         'EXAMPLE_SCENARIO': 'A 5% increase in MAPE typically drives a 12-15% increase in safety stock'},
        {'SOURCE_METRIC': 'SAFETY_STOCK_VALUE', 'TARGET_METRIC': 'DIOH_DAYS', 'RELATIONSHIP_TYPE': 'POSITIVE', 'CAUSAL_WEIGHT': 0.72,
         'DESCRIPTION': 'Safety stock directly increases days of inventory on hand',
         'EXAMPLE_SCENARIO': '$1M in safety stock adds approximately 2-3 days to DIOH'},
        {'SOURCE_METRIC': 'DIOH_DAYS', 'TARGET_METRIC': 'ROCE_PCT', 'RELATIONSHIP_TYPE': 'NEGATIVE', 'CAUSAL_WEIGHT': 0.68,
         'DESCRIPTION': 'Higher inventory days increase capital employed, reducing return on capital',
         'EXAMPLE_SCENARIO': 'Each 5-day increase in DIOH reduces ROCE by approximately 0.3-0.5%'},
        {'SOURCE_METRIC': 'LEAD_TIME_DAYS', 'TARGET_METRIC': 'PIPELINE_STOCK_VALUE', 'RELATIONSHIP_TYPE': 'POSITIVE', 'CAUSAL_WEIGHT': 0.92,
         'DESCRIPTION': 'Longer lead times directly increase in-transit and work-in-process inventory',
         'EXAMPLE_SCENARIO': 'A 10-day lead time increase adds $1.5-2M to pipeline stock'},
        {'SOURCE_METRIC': 'PIPELINE_STOCK_VALUE', 'TARGET_METRIC': 'FREE_CASH_FLOW_USD', 'RELATIONSHIP_TYPE': 'NEGATIVE', 'CAUSAL_WEIGHT': 0.78,
         'DESCRIPTION': 'Pipeline stock ties up working capital, reducing free cash flow',
         'EXAMPLE_SCENARIO': '$1M pipeline stock increase reduces FCF by approximately $950K'},
        {'SOURCE_METRIC': 'OEE_PCT', 'TARGET_METRIC': 'COGS_USD', 'RELATIONSHIP_TYPE': 'NEGATIVE', 'CAUSAL_WEIGHT': 0.65,
         'DESCRIPTION': 'Higher overall equipment effectiveness reduces cost per unit',
         'EXAMPLE_SCENARIO': 'A 5% OEE improvement reduces COGS by approximately 2-3%'},
        {'SOURCE_METRIC': 'BATCH_SIZE', 'TARGET_METRIC': 'CYCLE_STOCK_VALUE', 'RELATIONSHIP_TYPE': 'POSITIVE', 'CAUSAL_WEIGHT': 0.88,
         'DESCRIPTION': 'Larger batch sizes increase average cycle stock inventory',
         'EXAMPLE_SCENARIO': 'Doubling batch size increases cycle stock by approximately 50%'},
        {'SOURCE_METRIC': 'CYCLE_STOCK_VALUE', 'TARGET_METRIC': 'CAPITAL_EMPLOYED_USD', 'RELATIONSHIP_TYPE': 'POSITIVE', 'CAUSAL_WEIGHT': 0.75,
         'DESCRIPTION': 'Cycle stock is a direct component of working capital',
         'EXAMPLE_SCENARIO': 'Cycle stock flows 1:1 into capital employed'},
        {'SOURCE_METRIC': 'OTIF_PCT', 'TARGET_METRIC': 'NET_SALES_GROWTH_PCT', 'RELATIONSHIP_TYPE': 'POSITIVE', 'CAUSAL_WEIGHT': 0.55,
         'DESCRIPTION': 'Better service levels drive customer retention and sales growth',
         'EXAMPLE_SCENARIO': 'Each 1% OTIF improvement correlates with 0.3-0.5% revenue retention'},
        {'SOURCE_METRIC': 'SKU_BREADTH', 'TARGET_METRIC': 'FORECAST_MAPE_PCT', 'RELATIONSHIP_TYPE': 'POSITIVE', 'CAUSAL_WEIGHT': 0.62,
         'DESCRIPTION': 'More SKUs increase demand variability and reduce forecast accuracy',
         'EXAMPLE_SCENARIO': '10% SKU proliferation typically increases MAPE by 2-4%'}
    ]
    
    for i, trace in enumerate(traces):
        trace['TRACE_ID'] = i + 1
    
    return pd.DataFrame(traces)

def generate_qbr_documents():
    docs = [
        {
            'DOC_ID': 1,
            'DOC_NAME': 'Q1 2025 Business Review',
            'DOC_TYPE': 'QBR',
            'QUARTER': 'Q1',
            'YEAR': 2025,
            'CONTENT_TEXT': '''Q1 2025 Quarterly Business Review Summary
            
Service Performance: OTIF improved to 94.2% driven by safety stock investments in high-velocity SKUs. 
Lead time reduced by 2 days through carrier optimization program.

Cost Analysis: Gross margin pressure from commodity inflation (PPI +3.2%). 
OEE gains of 4% offset by higher energy costs. First-pass yield stable at 94%.

Cash Position: Working capital increased $4.2M due to strategic stock build for Q2 promotional season.
ROCE declined 0.8% as capital employed grew faster than NOPAT.

Key Risks: Supply chain disruption risk elevated due to Red Sea shipping concerns.
Recommend 15% safety stock increase for EMEA-sourced materials.'''
        },
        {
            'DOC_ID': 2,
            'DOC_NAME': 'Q2 2025 Risk Assessment',
            'DOC_TYPE': 'RISK_ASSESSMENT',
            'QUARTER': 'Q2',
            'YEAR': 2025,
            'CONTENT_TEXT': '''Q2 2025 Supply Chain Risk Assessment

CRITICAL RISK: Port congestion at West Coast facilities creating 7-10 day delays.
Impact: Pipeline stock increased $2.1M. Service risk for 23% of SKU portfolio.

ELEVATED RISK: Single-source supplier dependency for electronic components.
Impact: 18% of BOM at risk. Qualification of alternate supplier in progress.

MODERATE RISK: Forecast bias trending positive (+4.2%) indicating systematic over-forecasting.
Impact: Obsolescence risk increasing. Q4 write-off exposure estimated at $800K.

MITIGATED: Red Sea disruption impact contained through strategic stock positioning.
Container routing shifted to Suez alternatives. Cost impact: $1.2M freight premium.

Recommendations:
1. Accelerate nearshoring initiative for critical components
2. Implement demand sensing to reduce forecast bias
3. Review safety stock parameters for long lead time items'''
        },
        {
            'DOC_ID': 3,
            'DOC_NAME': 'Q3 2025 Business Review',
            'DOC_TYPE': 'QBR',
            'QUARTER': 'Q3',
            'YEAR': 2025,
            'CONTENT_TEXT': '''Q3 2025 Quarterly Business Review Summary

Service Performance: Fill rate declined to 91.3% due to unexpected demand surge in APAC region.
NPI launches exceeded plan with 8 new products successfully introduced.

Cost Analysis: COGS reduction program delivered $3.4M savings through batch size optimization.
Warning: Cycle stock increased 12% as consequence of larger batch procurement.

Cash Position: Cash conversion cycle improved 4 days through DPO extension negotiations.
Free cash flow strong at $8.2M despite inventory build for Q4 peak season.

Causal Analysis: Q3 inventory spike root cause identified as:
- 40% from anticipation stock build (planned)
- 35% from safety stock increase (forecast error response)  
- 25% from cycle stock growth (batch size decision)

Strategic Pivot: Board approved shift to Cash Mode for Q4 given interest rate environment.
Target: 10% working capital reduction while maintaining 92% service floor.'''
        }
    ]
    return pd.DataFrame(docs)

def main():
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)
    
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print("Generating performance snapshot (36 months x 4 regions x 3 modes)...")
    perf_df = generate_performance_snapshot(36)
    perf_df.to_csv(output_path / "fact_performance_snapshot.csv", index=False)
    print(f"  Generated {len(perf_df)} rows")
    
    print("Generating inventory structure definitions...")
    inv_df = generate_inventory_structure()
    inv_df.to_csv(output_path / "dim_inventory_structure.csv", index=False)
    print(f"  Generated {len(inv_df)} rows")
    
    print("Generating scenario control parameters...")
    scenario_df = generate_scenario_control()
    scenario_df.to_csv(output_path / "scenario_control.csv", index=False)
    print(f"  Generated {len(scenario_df)} rows")
    
    print("Generating predictive bridge (ML pre-computed)...")
    bridge_df = generate_predictive_bridge(perf_df, scenario_df)
    bridge_df.to_csv(output_path / "predictive_bridge.csv", index=False)
    print(f"  Generated {len(bridge_df)} rows")
    
    print("Generating ML prediction registry...")
    ml_df = generate_ml_registry()
    ml_df.to_csv(output_path / "ml_prediction_registry.csv", index=False)
    print(f"  Generated {len(ml_df)} rows")
    
    print("Generating causal trace definitions...")
    trace_df = generate_causal_traces()
    trace_df.to_csv(output_path / "causal_trace_definitions.csv", index=False)
    print(f"  Generated {len(trace_df)} rows")
    
    print("Generating QBR documents...")
    qbr_df = generate_qbr_documents()
    qbr_df.to_csv(output_path / "qbr_documents.csv", index=False)
    print(f"  Generated {len(qbr_df)} rows")
    
    print(f"\nAll data generated to {output_path}/")
    print("Run 'git add data/synthetic/' to track generated files")

if __name__ == "__main__":
    main()
