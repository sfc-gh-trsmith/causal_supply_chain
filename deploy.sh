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
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

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

ONLY_COMPONENT=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --only-sql) ONLY_COMPONENT="sql"; shift ;;
        --only-streamlit) ONLY_COMPONENT="streamlit"; shift ;;
        --only-data) ONLY_COMPONENT="data"; shift ;;
        *) error_exit "Unknown option: $1" ;;
    esac
done

should_run_step() {
    local step_name="$1"
    [ -z "$ONLY_COMPONENT" ] && return 0
    case "$ONLY_COMPONENT" in
        sql) [[ "$step_name" =~ sql ]] ;;
        streamlit) [[ "$step_name" == "streamlit" ]] ;;
        data) [[ "$step_name" == "data" ]] ;;
        *) return 1 ;;
    esac
}

info "Deploying Project Causal Chain"
info "Database: $DATABASE | Role: $ROLE | Warehouse: $WAREHOUSE"

if should_run_step "sql"; then
    info "Creating infrastructure..."
    {
        echo "SET FULL_PREFIX = '${FULL_PREFIX}';"
        echo "SET PROJECT_ROLE = '${ROLE}';"
        echo "SET PROJECT_WH = '${WAREHOUSE}';"
        echo "SET PROJECT_DB = '${DATABASE}';"
        cat sql/01_infrastructure.sql
    } | snow sql $SNOW_CONN -i || error_exit "Infrastructure setup failed"
    success "Infrastructure created"

    info "Creating schemas and tables..."
    {
        echo "USE ROLE ${ROLE};"
        echo "USE DATABASE ${DATABASE};"
        echo "USE WAREHOUSE ${WAREHOUSE};"
        cat sql/02_schemas.sql
        cat sql/03_tables.sql
    } | snow sql $SNOW_CONN -i || error_exit "Schema/table creation failed"
    success "Schemas and tables created"
fi

if should_run_step "data"; then
    info "Loading synthetic data..."
    {
        echo "USE ROLE ${ROLE};"
        echo "USE DATABASE ${DATABASE};"
        echo "USE WAREHOUSE ${WAREHOUSE};"
        cat sql/04_data.sql
    } | snow sql $SNOW_CONN -i || error_exit "Data loading failed"
    success "Synthetic data loaded"
    
    info "Creating Cortex Search service..."
    {
        echo "USE ROLE ${ROLE};"
        echo "USE DATABASE ${DATABASE};"
        echo "USE WAREHOUSE ${WAREHOUSE};"
        cat sql/05_cortex_search.sql
    } | snow sql $SNOW_CONN -i || warn "Cortex Search creation skipped (may require elevated permissions)"
    
    info "Deploying semantic model..."
    {
        echo "USE ROLE ${ROLE};"
        echo "USE DATABASE ${DATABASE};"
        echo "USE WAREHOUSE ${WAREHOUSE};"
        cat sql/06_semantic_model.sql
    } | snow sql $SNOW_CONN -i || error_exit "Semantic model deployment failed"
    
    snow stage copy semantic/causal_chain_model.yaml @${DATABASE}.STAGES.SEMANTIC_MODELS $SNOW_CONN --overwrite || error_exit "Semantic model upload failed"
    success "Cortex services configured"
fi

if should_run_step "streamlit"; then
    info "Deploying Streamlit application..."
    cd streamlit
    snow streamlit deploy $SNOW_CONN \
        --database $DATABASE \
        --schema APPS \
        --role $ROLE \
        --replace || error_exit "Streamlit deployment failed"
    cd ..
    success "Streamlit deployed"
fi

success "Deployment complete!"
