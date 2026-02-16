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

FORCE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --force|-y) FORCE=true; shift ;;
        -c) CONNECTION_NAME="$2"; SNOW_CONN="-c $CONNECTION_NAME"; shift 2 ;;
        *) error_exit "Unknown option: $1" ;;
    esac
done

info "Cleaning up Project Causal Chain"
info "This will remove: $DATABASE, $WAREHOUSE, $ROLE"

if [ "$FORCE" != true ]; then
    read -p "Are you sure? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        warn "Cleanup cancelled"
        exit 0
    fi
fi

info "Dropping Cortex Search service..."
snow sql $SNOW_CONN -q "DROP CORTEX SEARCH SERVICE IF EXISTS ${DATABASE}.STRATEGY_SIMULATOR.SUPPLY_CHAIN_CONTEXT_SEARCH;" || warn "Cortex Search service drop skipped"

info "Dropping warehouse..."
snow sql $SNOW_CONN -q "DROP WAREHOUSE IF EXISTS ${WAREHOUSE};" || error_exit "Failed to drop warehouse"

info "Dropping database (cascades all objects)..."
snow sql $SNOW_CONN -q "DROP DATABASE IF EXISTS ${DATABASE};" || error_exit "Failed to drop database"

info "Dropping role..."
snow sql $SNOW_CONN -q "DROP ROLE IF EXISTS ${ROLE};" || error_exit "Failed to drop role"

success "Cleanup complete"
