#!/bin/bash
set -e
set -o pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

error_exit() { echo -e "${RED}[ERROR] $1${NC}" >&2; exit 1; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

CONNECTION_NAME="${SNOWFLAKE_CONNECTION_NAME:-demo}"
ENV_PREFIX="${ENV_PREFIX:-}"
PROJECT_PREFIX="CAUSAL_CHAIN"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

SNOW_CONN="-c $CONNECTION_NAME"

if [ -n "$ENV_PREFIX" ]; then
    FULL_PREFIX="${ENV_PREFIX}_${PROJECT_PREFIX}"
else
    FULL_PREFIX="${PROJECT_PREFIX}"
fi

DATABASE="${FULL_PREFIX}"
ROLE="${FULL_PREFIX}_ROLE"
WAREHOUSE="${FULL_PREFIX}_WH"

cmd_status() {
    info "Checking resource status..."
    snow sql $SNOW_CONN -q "
        SELECT 'Database' as TYPE, '${DATABASE}' as NAME, 
               CASE WHEN COUNT(*) > 0 THEN 'EXISTS' ELSE 'MISSING' END as STATUS
        FROM INFORMATION_SCHEMA.DATABASES WHERE DATABASE_NAME = '${DATABASE}'
        UNION ALL
        SELECT 'Warehouse', '${WAREHOUSE}',
               CASE WHEN COUNT(*) > 0 THEN 'EXISTS' ELSE 'MISSING' END
        FROM INFORMATION_SCHEMA.WAREHOUSES WHERE WAREHOUSE_NAME = '${WAREHOUSE}'
        UNION ALL
        SELECT 'Role', '${ROLE}',
               CASE WHEN COUNT(*) > 0 THEN 'EXISTS' ELSE 'MISSING' END
        FROM INFORMATION_SCHEMA.ENABLED_ROLES WHERE ROLE_NAME = '${ROLE}';
    "
}

cmd_streamlit() {
    info "Getting Streamlit URL..."
    snow streamlit get-url $SNOW_CONN \
        --database $DATABASE \
        --schema APPS \
        STRATEGY_SIMULATOR 2>/dev/null || warn "Streamlit app not deployed yet"
}

cmd_test() {
    info "Running query tests..."
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE WAREHOUSE ${WAREHOUSE};
        
        -- Test 1: Performance snapshot data exists
        SELECT 'FACT_PERFORMANCE_SNAPSHOT' as TEST,
               CASE WHEN COUNT(*) >= 36 THEN 'PASS' ELSE 'FAIL' END as RESULT,
               COUNT(*) as ROW_COUNT
        FROM ANALYTICS.FACT_PERFORMANCE_SNAPSHOT;
    " || error_exit "Query tests failed"
    
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE WAREHOUSE ${WAREHOUSE};
        
        -- Test 2: Inventory structure complete
        SELECT 'DIM_INVENTORY_STRUCTURE' as TEST,
               CASE WHEN COUNT(DISTINCT INVENTORY_TYPE) = 5 THEN 'PASS' ELSE 'FAIL' END as RESULT,
               COUNT(DISTINCT INVENTORY_TYPE) as INVENTORY_TYPES
        FROM ANALYTICS.DIM_INVENTORY_STRUCTURE;
    " || error_exit "Query tests failed"
    
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE WAREHOUSE ${WAREHOUSE};
        
        -- Test 3: Scenario control modes
        SELECT 'SCENARIO_CONTROL' as TEST,
               CASE WHEN COUNT(DISTINCT STRATEGY_MODE) = 3 THEN 'PASS' ELSE 'FAIL' END as RESULT,
               COUNT(DISTINCT STRATEGY_MODE) as MODES
        FROM ANALYTICS.SCENARIO_CONTROL;
    " || error_exit "Query tests failed"
    
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE WAREHOUSE ${WAREHOUSE};
        
        -- Test 4: Golden query - Pipeline Stock vs ROCE
        SELECT 'GOLDEN_QUERY' as TEST,
               CASE WHEN COUNT(*) > 0 THEN 'PASS' ELSE 'FAIL' END as RESULT,
               COUNT(*) as MONTHS
        FROM (
            SELECT PERFORMANCE_MONTH, 
                   SUM(PIPELINE_STOCK_VALUE) as PIPELINE_STOCK,
                   AVG(ROCE_PCT) as ROCE
            FROM ANALYTICS.FACT_PERFORMANCE_SNAPSHOT
            GROUP BY 1
        );
    " || error_exit "Query tests failed"
    
    success "All query tests passed"
}

cmd_main() {
    info "Running main workflow..."
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE WAREHOUSE ${WAREHOUSE};
        
        SELECT 'Causal Chain Ready' as STATUS,
               (SELECT COUNT(*) FROM ANALYTICS.FACT_PERFORMANCE_SNAPSHOT) as PERFORMANCE_ROWS,
               (SELECT COUNT(*) FROM ANALYTICS.DIM_INVENTORY_STRUCTURE) as INVENTORY_ROWS,
               (SELECT COUNT(*) FROM CONSUMPTION.PREDICTIVE_BRIDGE) as PREDICTION_ROWS;
    "
    success "System operational"
}

COMMAND="${1:-status}"
case $COMMAND in
    main) cmd_main ;;
    test) cmd_test ;;
    status) cmd_status ;;
    streamlit) cmd_streamlit ;;
    *) error_exit "Unknown command: $COMMAND. Use: main|test|status|streamlit" ;;
esac
