import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from snowflake.snowpark.context import get_active_session
from utils.data_loader import load_dashboard_data, load_baseline_data as load_baseline_parallel

st.set_page_config(
    page_title="Causal Chain: Strategy Simulator",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DARK_BG = "#000000"
CARD_BG = "#24323D"
BORDER = "#334155"
TEXT = "#FFFFFF"
TEXT_MUTED = "#8A999E"
SNOWFLAKE_BLUE = "#29B5E8"
STAR_BLUE = "#71D3DC"
MID_BLUE = "#11567F"
VALENCIA_ORANGE = "#FF9F36"
PURPLE_MOON = "#7D44CF"
FIRST_LIGHT = "#D45B90"

CATEGORICAL_COLORS = ['#29B5E8', '#FF9F36', '#71D3DC', '#7D44CF', '#D45B90', '#8A999E']
SNOWFLAKE_BLUES = ['#E6F7FC', '#CCF0F9', '#99E1F3', '#66D2ED', '#29B5E8', '#2198C8', '#197BA8', '#11567F', '#003545']
BLUE_ORANGE_DIVERGING = ['#003545', '#11567F', '#29B5E8', '#71D3DC', '#8A999E', '#FFBF6B', '#FF9F36', '#E68A2E', '#CC7A29']

ACRONYM_DEFINITIONS = {
    'ROCE': ('Return on Capital Employed', 'Measures profitability relative to capital invested. ROCE = NOPAT / Capital Employed'),
    'NOPAT': ('Net Operating Profit After Tax', 'Operating profit minus taxes, excluding financing costs. Shows true operational performance'),
    'FCF': ('Free Cash Flow', 'Cash generated after capital expenditures. Available for dividends, debt repayment, or reinvestment'),
    'DIOH': ('Days Inventory On Hand', 'Average number of days inventory is held before sale. Lower = faster turnover'),
    'MAPE': ('Mean Absolute Percentage Error', 'Forecast accuracy metric. Lower values indicate more accurate demand predictions'),
    'OEE': ('Overall Equipment Effectiveness', 'Manufacturing productivity metric combining availability, performance, and quality'),
    'OTIF': ('On Time In Full', 'Delivery performance metric. Percentage of orders delivered complete and on schedule'),
    'COGS': ('Cost of Goods Sold', 'Direct costs of producing goods sold. Includes materials, labor, and manufacturing overhead'),
    'SKU': ('Stock Keeping Unit', 'Unique identifier for each distinct product. SKU breadth = product variety offered'),
    'NPI': ('New Product Introduction', 'Process of bringing new products to market. Impacts SKU breadth and inventory complexity'),
    'CapEx': ('Capital Expenditure', 'Funds used to acquire or upgrade physical assets like equipment or facilities'),
    'WC': ('Working Capital', 'Current assets minus current liabilities. Measures short-term liquidity'),
    'CI': ('Confidence Interval', 'Statistical range likely to contain the true value. Wider CI = more uncertainty'),
    'EVA': ('Economic Value Added', 'Net operating profit minus cost of capital. Positive EVA means value creation above required returns'),
}

def acronym_with_tooltip(acronym, color=None):
    if acronym not in ACRONYM_DEFINITIONS:
        return acronym
    full_name, description = ACRONYM_DEFINITIONS[acronym]
    text_color = color if color else TEXT_MUTED
    return f'''<span style="position: relative; cursor: help; border-bottom: 1px dotted {TEXT_MUTED};" title="{full_name}: {description}">{acronym}<sup style="font-size: 0.5rem; color: {SNOWFLAKE_BLUE}; margin-left: 1px;">ⓘ</sup></span>'''

def text_with_acronym_tooltips(text, color=None):
    result = text
    for acronym in ACRONYM_DEFINITIONS.keys():
        if acronym in result:
            result = result.replace(acronym, acronym_with_tooltip(acronym, color))
    return result

STRATEGY_TARGETS = {
    'GROWTH': {
        'FORECAST_MAPE_PCT': 15.0, 'LEAD_TIME_DAYS': 14.0, 'BATCH_SIZE': 100, 'OEE_PCT': 75.0, 'SKU_BREADTH': 200,
        'SAFETY_STOCK_VALUE': 6_000_000, 'PIPELINE_STOCK_VALUE': 7_000_000, 'CYCLE_STOCK_VALUE': 15_000_000,
        'COGS_USD': 55_000_000, 'DIOH_DAYS': 35,
        'OTIF_PCT': 98.0, 'NET_SALES_GROWTH_PCT': 15.0, 'ROCE_PCT': 12.0, 'FREE_CASH_FLOW_USD': 8_000_000, 'CAPITAL_EMPLOYED_USD': 120_000_000
    },
    'MARGIN': {
        'FORECAST_MAPE_PCT': 18.0, 'LEAD_TIME_DAYS': 10.0, 'BATCH_SIZE': 150, 'OEE_PCT': 80.0, 'SKU_BREADTH': 120,
        'SAFETY_STOCK_VALUE': 3_500_000, 'PIPELINE_STOCK_VALUE': 4_500_000, 'CYCLE_STOCK_VALUE': 10_000_000,
        'COGS_USD': 50_000_000, 'DIOH_DAYS': 22,
        'OTIF_PCT': 94.0, 'NET_SALES_GROWTH_PCT': 8.0, 'ROCE_PCT': 16.0, 'FREE_CASH_FLOW_USD': 12_000_000, 'CAPITAL_EMPLOYED_USD': 85_000_000
    },
    'CASH': {
        'FORECAST_MAPE_PCT': 20.0, 'LEAD_TIME_DAYS': 8.0, 'BATCH_SIZE': 200, 'OEE_PCT': 85.0, 'SKU_BREADTH': 100,
        'SAFETY_STOCK_VALUE': 3_000_000, 'PIPELINE_STOCK_VALUE': 4_000_000, 'CYCLE_STOCK_VALUE': 8_000_000,
        'COGS_USD': 48_000_000, 'DIOH_DAYS': 18,
        'OTIF_PCT': 92.0, 'NET_SALES_GROWTH_PCT': 5.0, 'ROCE_PCT': 18.0, 'FREE_CASH_FLOW_USD': 15_000_000, 'CAPITAL_EMPLOYED_USD': 75_000_000
    }
}

METRIC_DIRECTION = {
    'FORECAST_MAPE_PCT': 'lower', 'LEAD_TIME_DAYS': 'lower', 'BATCH_SIZE': 'context', 'OEE_PCT': 'higher', 'SKU_BREADTH': 'context',
    'SAFETY_STOCK_VALUE': 'context', 'PIPELINE_STOCK_VALUE': 'lower', 'CYCLE_STOCK_VALUE': 'lower',
    'COGS_USD': 'lower', 'DIOH_DAYS': 'lower',
    'OTIF_PCT': 'higher', 'NET_SALES_GROWTH_PCT': 'higher', 'ROCE_PCT': 'higher', 'FREE_CASH_FLOW_USD': 'higher', 'CAPITAL_EMPLOYED_USD': 'context'
}


def apply_dark_theme(fig):
    fig.update_layout(
        paper_bgcolor=DARK_BG,
        plot_bgcolor=CARD_BG,
        font=dict(color=TEXT, family="Inter, sans-serif"),
        title_font=dict(color=SNOWFLAKE_BLUE, size=16),
        hoverlabel=dict(bgcolor=CARD_BG, bordercolor=SNOWFLAKE_BLUE, font_color=TEXT),
        legend=dict(bgcolor='rgba(36, 50, 61, 0.8)', bordercolor=SNOWFLAKE_BLUE, font=dict(color=TEXT)),
        colorway=CATEGORICAL_COLORS,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig.update_xaxes(gridcolor=BORDER, zerolinecolor=BORDER, tickfont=dict(color=TEXT_MUTED))
    fig.update_yaxes(gridcolor=BORDER, zerolinecolor=BORDER, tickfont=dict(color=TEXT_MUTED))
    return fig


def get_variance_color(actual, target, direction='higher'):
    if target == 0:
        return TEXT_MUTED
    variance_pct = ((actual - target) / abs(target)) * 100
    if direction == 'higher':
        if variance_pct >= 5:
            return SNOWFLAKE_BLUE
        elif variance_pct >= -5:
            return TEXT_MUTED
        else:
            return VALENCIA_ORANGE
    elif direction == 'lower':
        if variance_pct <= -5:
            return SNOWFLAKE_BLUE
        elif variance_pct <= 5:
            return TEXT_MUTED
        else:
            return VALENCIA_ORANGE
    else:
        return TEXT_MUTED


def format_variance(actual, target, direction='higher'):
    if target == 0:
        return ""
    variance = actual - target
    variance_pct = (variance / abs(target)) * 100
    color = get_variance_color(actual, target, direction)
    arrow = "▲" if variance > 0 else "▼" if variance < 0 else "–"
    return f'<span style="color: {color}; font-size: 0.65rem;">{arrow} {abs(variance_pct):.0f}% vs target</span>'


@st.cache_resource
def get_session():
    return get_active_session()


@st.cache_data(ttl=300)
def load_all_data(_session, strategy_mode, shock_event, load_baseline=False):
    data = load_dashboard_data(_session, strategy_mode, shock_event)
    df = data.get('performance', pd.DataFrame())
    predictions = data.get('predictions', pd.DataFrame())
    traces = data.get('causal_traces', pd.DataFrame())
    baseline_df = load_baseline_parallel(_session, strategy_mode) if load_baseline else None
    return df, predictions, traces, baseline_df


def render_confidence_metric(label, value, lower, upper, format_str="${:.1f}M", color=SNOWFLAKE_BLUE):
    if value == 0:
        range_pct = 0
    else:
        range_pct = abs((upper - lower) / value * 100) if value != 0 else 0
    
    if range_pct < 10:
        conf_color = SNOWFLAKE_BLUE
        conf_label = "High Confidence"
    elif range_pct < 25:
        conf_color = TEXT_MUTED
        conf_label = "Medium Confidence"
    else:
        conf_color = VALENCIA_ORANGE
        conf_label = "Wide Range"
    
    label_with_tips = label
    for acr in ['FCF', 'ROCE', 'OTIF', 'DIOH', 'MAPE', 'OEE', 'COGS']:
        if acr in label and acr in ACRONYM_DEFINITIONS:
            full_name, desc = ACRONYM_DEFINITIONS[acr]
            tip_html = f'<span style="cursor: help; border-bottom: 1px dotted {TEXT_MUTED};" title="{full_name}: {desc}">{acr}<sup style="font-size: 0.5rem; color: {SNOWFLAKE_BLUE};">ⓘ</sup></span>'
            label_with_tips = label.replace(acr, tip_html)
            break
    
    ci_tip = f'<span style="cursor: help; border-bottom: 1px dotted {TEXT_MUTED};" title="{ACRONYM_DEFINITIONS["CI"][0]}: {ACRONYM_DEFINITIONS["CI"][1]}">CI<sup style="font-size: 0.5rem; color: {SNOWFLAKE_BLUE};">ⓘ</sup></span>'
    
    st.markdown(f'''
    <div class="metric-card">
        <div class="metric-value" style="color: {color};">{format_str.format(value)}</div>
        <div class="metric-label">{label_with_tips}</div>
        <div style="color: {conf_color}; font-size: 0.7rem; margin-top: 0.5rem;">
            90% {ci_tip}: {format_str.format(lower)} - {format_str.format(upper)}
        </div>
        <div style="background: {BORDER}; height: 4px; border-radius: 2px; margin-top: 0.5rem; position: relative;">
            <div style="background: {conf_color}; width: {min(100, max(10, range_pct * 2))}%; height: 100%; border-radius: 2px;"></div>
        </div>
        <div style="color: {BORDER}; font-size: 0.6rem; margin-top: 0.25rem;">{conf_label}</div>
    </div>
    ''', unsafe_allow_html=True)


def render_delta_badge(current, baseline, format_str="{:.1f}%", invert=False):
    delta = current - baseline
    delta_pct = (delta / baseline * 100) if baseline != 0 else 0
    is_positive = delta > 0 if not invert else delta < 0
    color = SNOWFLAKE_BLUE if is_positive else VALENCIA_ORANGE
    arrow = "+" if delta > 0 else ""
    return f'<span style="color: {color}; font-size: 0.75rem; margin-left: 0.5rem;">{arrow}{format_str.format(delta)} ({arrow}{delta_pct:.1f}%)</span>'


def create_causal_tree(traces_df):
    if traces_df.empty:
        return go.Figure()
    
    driver_nodes = ['FORECAST_MAPE_PCT', 'LEAD_TIME_DAYS', 'BATCH_SIZE', 'OEE_PCT', 'SKU_BREADTH']
    lever_nodes = ['SAFETY_STOCK_VALUE', 'PIPELINE_STOCK_VALUE', 'CYCLE_STOCK_VALUE', 'COGS_USD', 'DIOH_DAYS']
    outcome_nodes = ['FREE_CASH_FLOW_USD', 'ROCE_PCT', 'NET_SALES_GROWTH_PCT', 'CAPITAL_EMPLOYED_USD', 'OTIF_PCT']
    
    sources_in_data = set(traces_df['SOURCE_METRIC'].tolist())
    targets_in_data = set(traces_df['TARGET_METRIC'].tolist())
    all_in_data = sources_in_data | targets_in_data
    
    drivers = [n for n in driver_nodes if n in all_in_data]
    levers = [n for n in lever_nodes if n in all_in_data]
    outcomes = [n for n in outcome_nodes if n in all_in_data]
    
    remaining = all_in_data - set(drivers) - set(levers) - set(outcomes)
    for n in remaining:
        if n in sources_in_data and n not in targets_in_data:
            drivers.append(n)
        elif n in targets_in_data and n not in sources_in_data:
            outcomes.append(n)
        else:
            levers.append(n)
    
    def format_label(n):
        return n.replace('_', ' ').replace(' PCT', '%').replace(' USD', '$').replace(' VALUE', '').title()
    
    node_positions = {}
    x_positions = {'drivers': 0, 'levers': 1, 'outcomes': 2}
    
    for i, n in enumerate(drivers):
        node_positions[n] = (x_positions['drivers'], len(drivers) - 1 - i)
    for i, n in enumerate(levers):
        node_positions[n] = (x_positions['levers'], len(levers) - 1 - i)
    for i, n in enumerate(outcomes):
        node_positions[n] = (x_positions['outcomes'], len(outcomes) - 1 - i)
    
    fig = go.Figure()
    
    for _, row in traces_df.iterrows():
        src, tgt = row['SOURCE_METRIC'], row['TARGET_METRIC']
        if src in node_positions and tgt in node_positions:
            x0, y0 = node_positions[src]
            x1, y1 = node_positions[tgt]
            weight = abs(row['CAUSAL_WEIGHT'])
            is_positive = row['RELATIONSHIP_TYPE'] == 'POSITIVE'
            color = f'rgba(41,181,232,{0.3 + weight * 0.5})' if is_positive else f'rgba(255,159,54,{0.3 + weight * 0.5})'
            
            mid_x = (x0 + x1) / 2
            fig.add_trace(go.Scatter(
                x=[x0 + 0.12, mid_x, x1 - 0.12],
                y=[y0, (y0 + y1) / 2, y1],
                mode='lines',
                line=dict(color=color, width=1 + weight * 3, shape='spline'),
                hoverinfo='text',
                hovertext=f"{format_label(src)} → {format_label(tgt)}<br>Weight: {weight:.2f}",
                showlegend=False
            ))
    
    for category, nodes, color, label in [
        ('drivers', drivers, VALENCIA_ORANGE, 'Process Drivers'),
        ('levers', levers, SNOWFLAKE_BLUE, 'Economic Levers'),
        ('outcomes', outcomes, PURPLE_MOON, 'Financial Outcomes')
    ]:
        if not nodes:
            continue
        x_vals = [node_positions[n][0] for n in nodes]
        y_vals = [node_positions[n][1] for n in nodes]
        labels = [format_label(n) for n in nodes]
        
        fig.add_trace(go.Scatter(
            x=x_vals, y=y_vals,
            mode='markers+text',
            marker=dict(size=28, color=color, line=dict(color=BORDER, width=2)),
            text=labels,
            textposition='middle right' if category == 'drivers' else ('middle left' if category == 'outcomes' else 'top center'),
            textfont=dict(size=10, color=TEXT),
            hoverinfo='text',
            hovertext=labels,
            name=label,
            showlegend=True
        ))
    
    max_y = max(len(drivers), len(levers), len(outcomes)) - 1
    fig.update_layout(
        height=450,
        xaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-0.5, 2.5]
        ),
        yaxis=dict(
            showgrid=False, zeroline=False, showticklabels=False,
            range=[-0.8, max_y + 0.8]
        ),
        legend=dict(
            orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5,
            font=dict(size=10)
        ),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    return apply_dark_theme(fig)


def calculate_roce_sensitivity(current_data, safety_reduction_pct, lead_time_delta, batch_delta):
    current_roce = current_data['ROCE_PCT'].mean()
    current_safety = current_data['SAFETY_STOCK_VALUE'].sum()
    current_capital = current_data['CAPITAL_EMPLOYED_USD'].sum()
    current_cycle = current_data['CYCLE_STOCK_VALUE'].sum()
    nopat = current_data['NOPAT_USD'].sum()
    
    capital_freed = current_safety * (safety_reduction_pct / 100)
    pipeline_impact = lead_time_delta * 150000
    cycle_impact = current_cycle * (batch_delta / 100) * 0.5
    
    new_capital = current_capital - capital_freed + pipeline_impact + cycle_impact
    new_roce = (nopat / new_capital) * 100 if new_capital > 0 else 0
    
    return {
        'current_roce': current_roce,
        'new_roce': new_roce,
        'roce_delta': new_roce - current_roce,
        'roce_delta_bps': (new_roce - current_roce) * 100,
        'capital_freed': capital_freed,
        'pipeline_impact': pipeline_impact,
        'cycle_impact': cycle_impact,
        'net_capital_impact': capital_freed - pipeline_impact - cycle_impact
    }


def query_cortex_analyst(session, question):
    prompt = f"""You are a supply chain finance analyst. Answer this question about the causal chain data model concisely.
    
Question: {question}

Data model includes: performance metrics (OTIF, ROCE, FCF, inventory), strategy modes (GROWTH/MARGIN/CASH), shock scenarios, and ML predictions.

Be specific with metrics when relevant. Keep answer under 150 words."""

    try:
        result = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', $${prompt}$$) as RESPONSE
        """).collect()[0]['RESPONSE']
        return {"success": True, "response": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_qbr_docs(session, query):
    try:
        result = session.sql(f"""
            SELECT DOC_NAME, QUARTER, YEAR, CONTENT_TEXT
            FROM RAW.QBR_DOCUMENTS
            WHERE CONTAINS(LOWER(CONTENT_TEXT), LOWER('{query}'))
            LIMIT 3
        """).to_pandas()
        return result.to_dict('records')
    except:
        return []


METRIC_CONTEXT = {
    'FORECAST_MAPE_PCT': ('Mean Absolute Percentage Error', 'demand planning accuracy', 'the variance between forecasted and actual demand'),
    'LEAD_TIME_DAYS': ('Supplier Lead Time', 'procurement cycle duration', 'the elapsed time from order placement to goods receipt'),
    'BATCH_SIZE': ('Production Batch Size', 'manufacturing lot quantities', 'the volume of units produced in a single production run'),
    'OEE_PCT': ('Overall Equipment Effectiveness', 'manufacturing asset utilization', 'the product of availability, performance, and quality rates'),
    'SKU_BREADTH': ('SKU Portfolio Breadth', 'product assortment complexity', 'the total number of distinct stock-keeping units'),
    'SAFETY_STOCK_VALUE': ('Safety Stock Investment', 'demand variability buffer', 'inventory held to protect against forecast error and supply uncertainty'),
    'PIPELINE_STOCK_VALUE': ('Pipeline Stock Investment', 'in-transit inventory', 'goods in movement between supply chain nodes'),
    'CYCLE_STOCK_VALUE': ('Cycle Stock Investment', 'replenishment inventory', 'average inventory held to meet demand between replenishment orders'),
    'COGS_USD': ('Cost of Goods Sold', 'direct production costs', 'the direct costs attributable to goods sold including materials and labor'),
    'DIOH_DAYS': ('Days Inventory On Hand', 'inventory turnover metric', 'the average number of days inventory is held before sale'),
    'FREE_CASH_FLOW_USD': ('Free Cash Flow', 'cash generation capacity', 'operating cash flow minus capital expenditures'),
    'ROCE_PCT': ('Return on Capital Employed', 'capital efficiency metric', 'NOPAT divided by average capital employed'),
    'NET_SALES_GROWTH_PCT': ('Net Sales Growth', 'revenue trajectory', 'year-over-year percentage change in net revenue'),
    'CAPITAL_EMPLOYED_USD': ('Capital Employed', 'total invested capital', 'total assets minus current liabilities'),
    'OTIF_PCT': ('On-Time In-Full', 'delivery performance', 'percentage of orders delivered complete by promised date'),
}


@st.cache_data(ttl=86400, show_spinner=False)
def get_cached_causal_explanation(_session, source_metric, target_metric, relationship_type, weight, strategy_mode):
    source_info = METRIC_CONTEXT.get(source_metric, (source_metric, 'operational metric', 'a key performance indicator'))
    target_info = METRIC_CONTEXT.get(target_metric, (target_metric, 'operational metric', 'a key performance indicator'))
    
    prompt = f"""You are a McKinsey supply chain strategist. Explain this causal link concisely for a CFO.

LINK: {source_info[0]} to {target_info[0]} ({relationship_type}, weight: {weight:.2f})
STRATEGY: {strategy_mode}

Provide 4 brief sections (about 100 words each):

1. MECHANISM: How does {source_info[0]} ({source_info[2]}) mechanically impact {target_info[0]} ({target_info[2]})? One clear cause-effect chain.

2. FINANCIAL IMPACT: If {source_info[0]} improves 10 percent, what is the expected impact on {target_info[0]}? One industry benchmark.

3. STRATEGIC FIT: How does this link align with {strategy_mode} strategy? One key trade-off.

4. ACTION LEVERS: 2-3 specific operational actions to influence {source_info[0]}. Be concrete.

Use markdown headers. Be direct and specific. Max 400 words total. No preamble or follow-up questions."""

    escaped_prompt = prompt.replace("'", "''")
    
    try:
        result = _session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-large2', '{escaped_prompt}') as RESPONSE
        """).collect()[0]['RESPONSE']
        return {"success": True, "response": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_causal_explanation(session, source_metric, target_metric, relationship_type, weight, strategy_mode):
    return get_cached_causal_explanation(session, source_metric, target_metric, relationship_type, weight, strategy_mode)


st.markdown(f"""
<style>
    :root {{
        --sf-midnight: #000000;
        --sf-winter: #24323D;
        --sf-blue: #29B5E8;
        --sf-mid-blue: #11567F;
        --sf-star-blue: #71D3DC;
        --sf-orange: #FF9F36;
        --sf-purple: #7D44CF;
        --sf-rose: #D45B90;
        --sf-neutral: #8A999E;
    }}
    .stApp {{ background-color: var(--sf-midnight); }}
    .kpi-container {{
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
        justify-content: space-between;
    }}
    .kpi-card {{
        flex: 1 1 200px;
        min-width: 180px;
        background: linear-gradient(135deg, var(--sf-winter) 0%, var(--sf-midnight) 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: clamp(0.75rem, 2vw, 1.5rem);
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(41, 181, 232, 0.15);
    }}
    .kpi-value {{
        font-size: clamp(1.5rem, 4vw, 2.5rem);
        font-weight: 700;
        line-height: 1.1;
        white-space: nowrap;
    }}
    .kpi-label {{
        font-size: clamp(0.65rem, 1.5vw, 0.875rem);
        color: var(--sf-neutral);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 0.5rem;
    }}
    .metric-card {{
        background: linear-gradient(135deg, var(--sf-winter) 0%, var(--sf-midnight) 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(41, 181, 232, 0.15);
    }}
    .metric-value {{ font-size: clamp(1.5rem, 3vw, 2.5rem); font-weight: 700; }}
    .metric-label {{ font-size: clamp(0.7rem, 1.2vw, 0.875rem); color: var(--sf-neutral); text-transform: uppercase; }}
    .strategy-badge {{
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.875rem;
    }}
    .growth-badge {{ background: rgba(41, 181, 232, 0.15); color: var(--sf-blue); border: 1px solid var(--sf-blue); }}
    .margin-badge {{ background: rgba(255, 159, 54, 0.15); color: var(--sf-orange); border: 1px solid var(--sf-orange); }}
    .cash-badge {{ background: rgba(125, 68, 207, 0.15); color: var(--sf-purple); border: 1px solid var(--sf-purple); }}
    .control-section {{
        background: var(--sf-winter);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
    }}
    h1, h2, h3 {{ color: var(--sf-blue) !important; }}
    @keyframes pulse-highlight {{
        0% {{ box-shadow: 0 0 0 0 rgba(41, 181, 232, 0.7); }}
        70% {{ box-shadow: 0 0 0 10px rgba(41, 181, 232, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(41, 181, 232, 0); }}
    }}
    .causal-highlight {{ animation: pulse-highlight 1s ease-out; }}
</style>
""", unsafe_allow_html=True)

session = get_session()

if 'compare_baseline' not in st.session_state:
    st.session_state.compare_baseline = False

st.markdown(f"<h1 style='color: {TEXT}; margin-bottom: 0.5rem;'>Causal Chain: Strategy Simulator</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #94a3b8; margin-bottom: 1.5rem;'>Financial flight simulator for supply chain trade-offs</p>", unsafe_allow_html=True)

ctrl_col1, ctrl_col2 = st.columns([1, 1])

with ctrl_col1:
    strategy_mode = st.selectbox(
        "Strategic Priority",
        ["GROWTH", "MARGIN", "CASH"],
        index=0,
        help="Growth: Prioritize service. Margin: Prioritize cost. Cash: Prioritize returns."
    )

with ctrl_col2:
    shock_event = st.selectbox(
        "Shock Scenario",
        ["None", "SUPPLY_DISRUPTION", "PORT_STRIKE", "DEMAND_SURGE"],
        help="Apply a what-if shock scenario"
    )

if shock_event != "None":
    st.checkbox("Compare to Baseline", key="compare_baseline", 
               help="Show side-by-side comparison with baseline scenario")

df, predictions, traces, baseline_df = load_all_data(
    session, strategy_mode, shock_event, st.session_state.compare_baseline
)

if df.empty:
    st.error("No data available for selected filters")
    st.stop()

latest = df.iloc[0] if len(df) > 0 else {}
baseline_latest = baseline_df.iloc[0] if baseline_df is not None and len(baseline_df) > 0 else None

badge_class = f"{strategy_mode.lower()}-badge"

st.subheader("Trade-Off Triangle")

service_weight = float(latest.get('SERVICE_WEIGHT', 0.33))
cost_weight = float(latest.get('COST_WEIGHT', 0.33))
cash_weight = float(latest.get('CASH_WEIGHT', 0.33))

vertices = {'SERVICE': (0.5, 0.9), 'COST': (0.1, 0.1), 'CASH': (0.9, 0.1)}
active_mapping = {'GROWTH': 'SERVICE', 'MARGIN': 'COST', 'CASH': 'CASH'}
active_corner = active_mapping.get(strategy_mode, 'SERVICE')

service_val = float(latest.get('OTIF_PCT', 0))
cost_val = float(latest.get('GROSS_MARGIN_PCT', 0))
cash_val = float(latest.get('ROCE_PCT', 0))

values = {'SERVICE': service_val, 'COST': cost_val, 'CASH': cash_val}
colors_map = {'SERVICE': SNOWFLAKE_BLUE, 'COST': VALENCIA_ORANGE, 'CASH': PURPLE_MOON}
weights = {'SERVICE': service_weight, 'COST': cost_weight, 'CASH': cash_weight}

tri_fig = go.Figure()

tri_fig.add_trace(go.Scatter(
    x=[0.1, 0.5, 0.9, 0.1], y=[0.1, 0.9, 0.1, 0.1],
    mode='lines', line=dict(color=BORDER, width=2),
    fill='toself', fillcolor='rgba(30, 41, 59, 0.5)', hoverinfo='skip'
))

for corner, (x, y) in vertices.items():
    val = values[corner]
    is_active = corner == active_corner
    color = colors_map[corner]
    weight = weights[corner]
    marker_size = 35 + (weight * 30)
    
    if is_active:
        tri_fig.add_trace(go.Scatter(
            x=[x], y=[y], mode='markers',
            marker=dict(size=marker_size + 15, color=color, opacity=0.3, line=dict(width=0)),
            hoverinfo='skip'
        ))
    
    tri_fig.add_trace(go.Scatter(
        x=[x], y=[y], mode='markers+text',
        marker=dict(size=marker_size, color=CARD_BG if not is_active else color,
                    line=dict(color=color, width=3 if is_active else 2), opacity=1 if is_active else 0.7),
        text=[f"<b>{corner}</b><br>{val:.1f}%"],
        textposition='middle center',
        textfont=dict(color='white' if is_active else TEXT, size=11),
        hovertemplate=f'{corner}<br>Value: {val:.1f}%<br>Weight: {weight:.0%}<extra></extra>'
    ))

tri_fig.update_layout(
    showlegend=False, xaxis=dict(visible=False, range=[-0.05, 1.05]),
    yaxis=dict(visible=False, range=[-0.05, 1.1], scaleanchor='x'),
    height=350, margin=dict(l=20, r=20, t=40, b=20),
    title=dict(text=f"Active Mode: {strategy_mode}", font=dict(size=12))
)
tri_fig = apply_dark_theme(tri_fig)

tri_col1, tri_col2 = st.columns([1, 1])
with tri_col1:
    st.plotly_chart(tri_fig, use_container_width=True)

with tri_col2:
    mandatory = latest.get('MANDATORY_GREEN', '')
    permissible = latest.get('PERMISSIBLE_RED', '')
    
    st.markdown(f"""
    **Current Strategy Trade-offs:**
    
    - **Mandatory (Green):** {mandatory} - Must maintain performance
    - **Permissible (Red):** {permissible} - Acceptable to underperform
    
    **Weights:** Service {service_weight:.0%} | Cost {cost_weight:.0%} | Cash {cash_weight:.0%}
    """)
    
    metrics_df = pd.DataFrame({
        'Corner': ['SERVICE', 'COST', 'CASH'],
        'Primary Metric': ['OTIF %', 'Gross Margin %', 'ROCE %'],
        'Value': [service_val, cost_val, cash_val],
        'Weight': [service_weight, cost_weight, cash_weight]
    })
    st.dataframe(metrics_df, hide_index=True, use_container_width=True)

st.markdown("---")

roce_val = float(latest.get('ROCE_PCT', 0))
fcf_val = float(latest.get('FREE_CASH_FLOW_USD', 0)) / 1_000_000
eva_val = float(latest.get('EVA_USD', 0)) / 1_000_000
capital_val = float(latest.get('CAPITAL_EMPLOYED_USD', 0)) / 1_000_000

eva_color = SNOWFLAKE_BLUE if eva_val > 0 else VALENCIA_ORANGE

roce_delta = ""
fcf_delta = ""
eva_delta = ""
if baseline_latest is not None:
    roce_delta = render_delta_badge(roce_val, float(baseline_latest.get('ROCE_PCT', 0)))
    fcf_delta = render_delta_badge(fcf_val, float(baseline_latest.get('FREE_CASH_FLOW_USD', 0)) / 1_000_000, format_str="${:.1f}M")
    eva_delta = render_delta_badge(eva_val, float(baseline_latest.get('EVA_USD', 0)) / 1_000_000, format_str="${:.1f}M")

roce_tip = f'<span style="cursor: help; border-bottom: 1px dotted {TEXT_MUTED};" title="{ACRONYM_DEFINITIONS["ROCE"][0]}: {ACRONYM_DEFINITIONS["ROCE"][1]}">ROCE<sup style="font-size: 0.5em; color: {SNOWFLAKE_BLUE};">ⓘ</sup></span>'
fcf_tip = f'<span style="cursor: help; border-bottom: 1px dotted {TEXT_MUTED};" title="{ACRONYM_DEFINITIONS["FCF"][0]}: {ACRONYM_DEFINITIONS["FCF"][1]}">FCF<sup style="font-size: 0.5em; color: {SNOWFLAKE_BLUE};">ⓘ</sup></span>'
eva_tip = f'<span style="cursor: help; border-bottom: 1px dotted {TEXT_MUTED};" title="{ACRONYM_DEFINITIONS["EVA"][0]}: {ACRONYM_DEFINITIONS["EVA"][1]}">EVA<sup style="font-size: 0.5em; color: {SNOWFLAKE_BLUE};">ⓘ</sup></span>'

st.markdown(f"""
<div class="kpi-container">
    <div class="kpi-card">
        <div class="kpi-value" style="color: {PURPLE_MOON};">{roce_val:.1f}%</div>
        <div class="kpi-label">{roce_tip} {roce_delta}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value" style="color: {SNOWFLAKE_BLUE};">${fcf_val:.1f}M</div>
        <div class="kpi-label">{fcf_tip} {fcf_delta}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value" style="color: {eva_color};">${eva_val:.1f}M</div>
        <div class="kpi-label">{eva_tip} {eva_delta}</div>
    </div>
    <div class="kpi-card">
        <div class="kpi-value" style="color: {TEXT};">${capital_val:.0f}M</div>
        <div class="kpi-label">Capital Employed</div>
    </div>
</div>
""", unsafe_allow_html=True)

if shock_event != "None" and not predictions.empty:
    st.markdown("---")
    st.subheader(f"Scenario Predictions: {shock_event.replace('_', ' ').title()}")
    
    pred_latest = predictions.iloc[0]
    
    has_bounds = 'FCF_LOWER_BOUND' in predictions.columns and pd.notna(pred_latest.get('FCF_LOWER_BOUND'))
    
    pcol1, pcol2, pcol3 = st.columns(3)
    
    with pcol1:
        pred_fcf = float(pred_latest.get('PREDICTED_FCF_USD', 0)) / 1_000_000
        if has_bounds:
            fcf_lower = float(pred_latest.get('FCF_LOWER_BOUND', pred_fcf * 0.85)) / 1_000_000
            fcf_upper = float(pred_latest.get('FCF_UPPER_BOUND', pred_fcf * 1.15)) / 1_000_000
            render_confidence_metric("Predicted FCF", pred_fcf, fcf_lower, fcf_upper, "${:.1f}M", SNOWFLAKE_BLUE)
        else:
            st.metric("Predicted FCF", f"${pred_fcf:.1f}M")
    
    with pcol2:
        pred_roce = float(pred_latest.get('PREDICTED_ROCE_PCT', 0))
        if has_bounds:
            roce_lower = float(pred_latest.get('ROCE_LOWER_BOUND', pred_roce * 0.9))
            roce_upper = float(pred_latest.get('ROCE_UPPER_BOUND', pred_roce * 1.1))
            render_confidence_metric("Predicted ROCE", pred_roce, roce_lower, roce_upper, "{:.1f}%", PURPLE_MOON)
        else:
            st.metric("Predicted ROCE", f"{pred_roce:.1f}%")
    
    with pcol3:
        pred_safety = float(pred_latest.get('PREDICTED_SAFETY_STOCK_USD', 0)) / 1_000_000
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: {VALENCIA_ORANGE};">${pred_safety:.1f}M</div>
            <div class="metric-label">Predicted Safety Stock</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

roce_sens_tip = f'<span style="cursor: help; border-bottom: 1px dotted {TEXT_MUTED};" title="{ACRONYM_DEFINITIONS["ROCE"][0]}: {ACRONYM_DEFINITIONS["ROCE"][1]}">ROCE<sup style="font-size: 0.6rem; color: {SNOWFLAKE_BLUE};">ⓘ</sup></span>'
st.markdown(f"### {roce_sens_tip} Sensitivity Calculator", unsafe_allow_html=True)

sens_col1, sens_col2 = st.columns([1, 2], gap="medium")

with sens_col1:
    st.markdown("**Adjust Parameters:**")
    safety_reduction = st.slider("Safety Stock Reduction %", 0, 30, 10, key="safety_slider")
    lead_time_change = st.slider("Lead Time Change (days)", -5, 10, 0, key="lead_slider")
    batch_change = st.slider("Batch Size Change %", -20, 50, 0, key="batch_slider")

with sens_col2:
    sensitivity = calculate_roce_sensitivity(df, safety_reduction, lead_time_change, batch_change)
    
    gauge_fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=sensitivity['new_roce'],
        delta={'reference': sensitivity['current_roce'], 'relative': False, 'valueformat': '.2f',
               'increasing': {'color': SNOWFLAKE_BLUE}, 'decreasing': {'color': VALENCIA_ORANGE},
               'font': {'color': TEXT}},
        number={'suffix': '%', 'valueformat': '.1f', 'font': {'color': TEXT}},
        title={'text': "Projected ROCE", 'font': {'color': TEXT, 'size': 16}},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, 25], 'tickwidth': 1, 'tickcolor': BORDER},
            'bar': {'color': SNOWFLAKE_BLUE},
            'bgcolor': CARD_BG,
            'borderwidth': 2,
            'bordercolor': BORDER,
            'steps': [
                {'range': [0, 10], 'color': 'rgba(255, 159, 54, 0.2)'},
                {'range': [10, 15], 'color': 'rgba(138, 153, 158, 0.2)'},
                {'range': [15, 25], 'color': 'rgba(41, 181, 232, 0.2)'}
            ],
            'threshold': {'line': {'color': TEXT, 'width': 3}, 'thickness': 0.8, 'value': sensitivity['current_roce']}
        }
    ))
    gauge_fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20))
    gauge_fig = apply_dark_theme(gauge_fig)
    st.plotly_chart(gauge_fig, use_container_width=True, theme=None, key="roce_gauge")
    
    capital_freed_m = sensitivity['capital_freed'] / 1_000_000
    st.markdown(f"""
    **Impact Summary:** A {safety_reduction}% safety stock reduction would improve ROCE by 
    **{sensitivity['roce_delta_bps']:.0f} basis points**, freeing **${capital_freed_m:.1f}M** in capital.
    """)

st.subheader("Interactive Causal Trace")

def render_metrics_tree_dashboard(data_df, traces_df, strategy_mode):
    latest = data_df.iloc[0] if not data_df.empty else {}
    targets = STRATEGY_TARGETS.get(strategy_mode, STRATEGY_TARGETS['GROWTH'])
    
    metric_values = {
        'FORECAST_MAPE_PCT': latest.get('FORECAST_MAPE_PCT', 0),
        'LEAD_TIME_DAYS': latest.get('LEAD_TIME_DAYS', 0),
        'BATCH_SIZE': latest.get('BATCH_SIZE', latest.get('CYCLE_STOCK_VALUE', 0) / 100000) if 'BATCH_SIZE' not in latest else latest.get('BATCH_SIZE', 0),
        'OEE_PCT': latest.get('OEE_PCT', 0),
        'SKU_BREADTH': latest.get('SKU_BREADTH', 150),
        'SAFETY_STOCK_VALUE': latest.get('SAFETY_STOCK_VALUE', 0),
        'PIPELINE_STOCK_VALUE': latest.get('PIPELINE_STOCK_VALUE', 0),
        'CYCLE_STOCK_VALUE': latest.get('CYCLE_STOCK_VALUE', 0),
        'COGS_USD': latest.get('COGS_USD', 0),
        'DIOH_DAYS': latest.get('CASH_CONVERSION_CYCLE_DAYS', 0) * 0.4,
        'FREE_CASH_FLOW_USD': latest.get('FREE_CASH_FLOW_USD', 0),
        'ROCE_PCT': latest.get('ROCE_PCT', 0),
        'NET_SALES_GROWTH_PCT': latest.get('NET_SALES_GROWTH_PCT', 0),
        'CAPITAL_EMPLOYED_USD': latest.get('CAPITAL_EMPLOYED_USD', 0),
        'OTIF_PCT': latest.get('OTIF_PCT', 0)
    }
    
    def format_value(metric, value):
        if 'PCT' in metric:
            return f"{value:.1f}%"
        elif 'USD' in metric or 'VALUE' in metric:
            if abs(value) >= 1_000_000:
                return f"${value/1_000_000:.1f}M"
            elif abs(value) >= 1_000:
                return f"${value/1_000:.0f}K"
            else:
                return f"${value:.0f}"
        elif 'DAYS' in metric:
            return f"{value:.1f}d"
        else:
            return f"{value:.1f}"
    
    def format_label(metric):
        acronym_map = {
            'FORECAST_MAPE_PCT': 'Forecast MAPE',
            'LEAD_TIME_DAYS': 'Lead Time',
            'BATCH_SIZE': 'Batch Size',
            'OEE_PCT': 'OEE',
            'SKU_BREADTH': 'SKU Breadth',
            'SAFETY_STOCK_VALUE': 'Safety Stock',
            'PIPELINE_STOCK_VALUE': 'Pipeline Stock',
            'CYCLE_STOCK_VALUE': 'Cycle Stock',
            'COGS_USD': 'COGS',
            'DIOH_DAYS': 'DIOH',
            'FREE_CASH_FLOW_USD': 'FCF',
            'ROCE_PCT': 'ROCE',
            'NET_SALES_GROWTH_PCT': 'Sales Growth',
            'CAPITAL_EMPLOYED_USD': 'Capital Employed',
            'OTIF_PCT': 'OTIF'
        }
        return acronym_map.get(metric, metric.replace('_', ' ').title())
    
    def format_label_with_tooltip(metric):
        label = format_label(metric)
        acronyms_in_label = ['MAPE', 'OEE', 'SKU', 'COGS', 'DIOH', 'FCF', 'ROCE', 'OTIF']
        for acr in acronyms_in_label:
            if acr in label and acr in ACRONYM_DEFINITIONS:
                full_name, desc = ACRONYM_DEFINITIONS[acr]
                tooltip_html = f'<span style="cursor: help; border-bottom: 1px dotted {TEXT_MUTED};" title="{full_name}: {desc}">{acr}<sup style="font-size: 0.45rem; color: {SNOWFLAKE_BLUE};">ⓘ</sup></span>'
                label = label.replace(acr, tooltip_html)
                break
        return label
    
    drivers = ['FORECAST_MAPE_PCT', 'LEAD_TIME_DAYS', 'BATCH_SIZE', 'OEE_PCT', 'SKU_BREADTH']
    levers = ['SAFETY_STOCK_VALUE', 'PIPELINE_STOCK_VALUE', 'CYCLE_STOCK_VALUE', 'COGS_USD', 'DIOH_DAYS']
    outcomes = ['OTIF_PCT', 'NET_SALES_GROWTH_PCT', 'ROCE_PCT', 'FREE_CASH_FLOW_USD', 'CAPITAL_EMPLOYED_USD']
    
    driver_colors = {'FORECAST_MAPE_PCT': VALENCIA_ORANGE, 'LEAD_TIME_DAYS': '#FFBF6B', 'BATCH_SIZE': '#E68A2E', 'OEE_PCT': '#FF9F36', 'SKU_BREADTH': '#CC7A29'}
    lever_colors = {'SAFETY_STOCK_VALUE': SNOWFLAKE_BLUE, 'PIPELINE_STOCK_VALUE': STAR_BLUE, 'CYCLE_STOCK_VALUE': '#66D2ED', 'COGS_USD': '#99E1F3', 'DIOH_DAYS': MID_BLUE}
    outcome_colors = {'OTIF_PCT': PURPLE_MOON, 'NET_SALES_GROWTH_PCT': '#9B7ED8', 'ROCE_PCT': FIRST_LIGHT, 'FREE_CASH_FLOW_USD': '#E07BA8', 'CAPITAL_EMPLOYED_USD': '#B366C2'}
    
    def metric_card(metric, color):
        value = metric_values.get(metric, 0)
        target = targets.get(metric, 0)
        direction = METRIC_DIRECTION.get(metric, 'higher')
        label = format_label_with_tooltip(metric)
        formatted_val = format_value(metric, value)
        formatted_target = format_value(metric, target)
        variance_html = format_variance(value, target, direction)
        variance_color = get_variance_color(value, target, direction)
        
        return f'''
        <div style="background: linear-gradient(135deg, {CARD_BG} 0%, {DARK_BG} 100%); border: 2px solid {color}; border-radius: 10px; padding: 0.6rem 0.8rem; text-align: center; min-width: 110px;">
            <div style="color: {color}; font-size: 1.4rem; font-weight: 700;">{formatted_val}</div>
            <div style="color: {TEXT_MUTED}; font-size: 0.6rem; text-transform: uppercase; letter-spacing: 0.5px; margin: 0.2rem 0;">{label}</div>
            <div style="color: {TEXT_MUTED}; font-size: 0.55rem; border-top: 1px solid {BORDER}; padding-top: 0.3rem; margin-top: 0.3rem;">
                Target: {formatted_target}
            </div>
            <div>{variance_html}</div>
        </div>
        '''
    
    st.markdown(f"""
    <div style="background: linear-gradient(180deg, {DARK_BG} 0%, {CARD_BG} 100%); border: 1px solid {BORDER}; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;">
        <h4 style="color: {VALENCIA_ORANGE}; text-align: center; margin: 0 0 1rem 0; font-size: 0.85rem; letter-spacing: 1.5px;">PROCESS DRIVERS</h4>
    """, unsafe_allow_html=True)
    
    driver_cols = st.columns(5)
    for i, metric in enumerate(drivers):
        with driver_cols[i]:
            st.markdown(metric_card(metric, driver_colors[metric]), unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="display: flex; justify-content: center; margin: 1rem 0;">
            <svg width="100" height="40" viewBox="0 0 100 40">
                <defs>
                    <marker id="arrow-down" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
                        <path d="M0,0 L10,5 L0,10 Z" fill="{SNOWFLAKE_BLUE}"/>
                    </marker>
                </defs>
                <line x1="50" y1="0" x2="50" y2="30" stroke="{SNOWFLAKE_BLUE}" stroke-width="2" marker-end="url(#arrow-down)"/>
            </svg>
        </div>
        <h4 style="color: {SNOWFLAKE_BLUE}; text-align: center; margin: 0 0 1rem 0; font-size: 0.85rem; letter-spacing: 1.5px;">ECONOMIC LEVERS</h4>
    """, unsafe_allow_html=True)
    
    lever_cols = st.columns(5)
    for i, metric in enumerate(levers):
        with lever_cols[i]:
            st.markdown(metric_card(metric, lever_colors[metric]), unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="display: flex; justify-content: center; margin: 1rem 0;">
            <svg width="100" height="40" viewBox="0 0 100 40">
                <defs>
                    <marker id="arrow-down2" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
                        <path d="M0,0 L10,5 L0,10 Z" fill="{PURPLE_MOON}"/>
                    </marker>
                </defs>
                <line x1="50" y1="0" x2="50" y2="30" stroke="{PURPLE_MOON}" stroke-width="2" marker-end="url(#arrow-down2)"/>
            </svg>
        </div>
        <h4 style="color: {PURPLE_MOON}; text-align: center; margin: 0 0 1rem 0; font-size: 0.85rem; letter-spacing: 1.5px;">FINANCIAL OUTCOMES</h4>
    """, unsafe_allow_html=True)
    
    outcome_cols = st.columns(5)
    for i, metric in enumerate(outcomes):
        with outcome_cols[i]:
            st.markdown(metric_card(metric, outcome_colors[metric]), unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

if not traces.empty:
    render_metrics_tree_dashboard(df, traces, strategy_mode)
    if 'causal_explanations' not in st.session_state:
        st.session_state.causal_explanations = {}
    if 'selected_causal_rel' not in st.session_state:
        st.session_state.selected_causal_rel = None
    
    def format_rel_label(metric):
        acronyms = {'DIOH': 'DIOH', 'MAPE': 'MAPE', 'OEE': 'OEE', 'ROCE': 'ROCE', 
                    'FCF': 'FCF', 'OTIF': 'OTIF', 'COGS': 'COGS', 'SKU': 'SKU', 'NPI': 'NPI'}
        result = metric.replace('_', ' ').replace(' PCT', '%').replace(' USD', '$').replace(' VALUE', '').title()
        for acr_upper, acr_display in acronyms.items():
            result = result.replace(acr_upper.title(), acr_display)
        return result
    
    rel_options = []
    for _, row in traces.iterrows():
        rel_id = f"{row['SOURCE_METRIC']}__{row['TARGET_METRIC']}"
        src_label = format_rel_label(row['SOURCE_METRIC'])
        tgt_label = format_rel_label(row['TARGET_METRIC'])
        rel_type_icon = "+" if row['RELATIONSHIP_TYPE'] == 'POSITIVE' else "-"
        rel_options.append({
            'id': rel_id,
            'label': f"{src_label} → {tgt_label} ({rel_type_icon}{row['CAUSAL_WEIGHT']:.2f})",
            'source': row['SOURCE_METRIC'],
            'target': row['TARGET_METRIC'],
            'type': row['RELATIONSHIP_TYPE'],
            'weight': row['CAUSAL_WEIGHT']
        })
    
    cache_key_prefix = f"precomputed_{strategy_mode}"
    if cache_key_prefix not in st.session_state:
        st.session_state[cache_key_prefix] = False
    
    if not st.session_state[cache_key_prefix]:
        with st.spinner(f"Pre-computing AI analysis for {len(rel_options)} relationships..."):
            progress_bar = st.progress(0)
            for i, rel in enumerate(rel_options):
                cache_key = f"{rel['id']}_{strategy_mode}"
                if cache_key not in st.session_state.causal_explanations:
                    explanation = get_causal_explanation(
                        session, rel['source'], rel['target'], rel['type'], rel['weight'], strategy_mode
                    )
                    if explanation["success"]:
                        st.session_state.causal_explanations[cache_key] = explanation["response"]
                progress_bar.progress((i + 1) / len(rel_options))
            progress_bar.empty()
            st.session_state[cache_key_prefix] = True
    
    st.markdown(f"<p style='text-align:center;color:{TEXT_MUTED};font-size:0.85rem;margin:1rem 0;'>Select a relationship below to view AI-powered causal analysis</p>", unsafe_allow_html=True)
    
    rel_labels = [r['label'] for r in rel_options]
    rel_ids = [r['id'] for r in rel_options]
    
    button_cols = st.columns(min(len(rel_options), 4))
    for i, rel in enumerate(rel_options):
        col_idx = i % 4
        is_selected = rel['id'] == st.session_state.selected_causal_rel
        with button_cols[col_idx]:
            rel_color = SNOWFLAKE_BLUE if rel['type'] == 'POSITIVE' else VALENCIA_ORANGE
            btn_style = f"border: 2px solid {rel_color}; border-radius: 8px;" if is_selected else ""
            if st.button(
                rel['label'], 
                key=f"btn_{rel['id']}", 
                use_container_width=True,
                type="primary" if is_selected else "secondary"
            ):
                st.session_state.selected_causal_rel = rel['id']
                st.rerun()
    
    if st.session_state.selected_causal_rel:
        selected_data = next((r for r in rel_options if r['id'] == st.session_state.selected_causal_rel), None)
        
        if selected_data:
            src_label = format_rel_label(selected_data['source'])
            tgt_label = format_rel_label(selected_data['target'])
            rel_color = SNOWFLAKE_BLUE if selected_data['type'] == 'POSITIVE' else VALENCIA_ORANGE
            rel_symbol = "+" if selected_data['type'] == 'POSITIVE' else "-"
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {CARD_BG} 0%, {DARK_BG} 100%); border: 1px solid {BORDER}; border-radius: 12px; padding: 1.5rem; margin-top: 1rem;">
                <div style="text-align: center; padding: 0.75rem; margin-bottom: 1rem; background: {DARK_BG}; border-radius: 8px; border: 2px solid {rel_color};">
                    <span style="color: {TEXT}; font-size: 1.25rem; font-weight: 600;">{src_label}</span>
                    <span style="color: {rel_color}; font-size: 1.5rem; margin: 0 0.75rem;">→</span>
                    <span style="color: {TEXT}; font-size: 1.25rem; font-weight: 600;">{tgt_label}</span>
                    <br/>
                    <span style="color: {rel_color}; font-weight: 700; font-size: 1.1rem;">{selected_data['type'].title()} ({rel_symbol}{selected_data['weight']:.2f})</span>
                </div>
            """, unsafe_allow_html=True)
            
            cache_key = f"{selected_data['id']}_{strategy_mode}"
            
            if cache_key in st.session_state.causal_explanations:
                st.markdown(st.session_state.causal_explanations[cache_key])
            else:
                with st.spinner("Generating AI analysis..."):
                    explanation = get_causal_explanation(
                        session, selected_data['source'], selected_data['target'], 
                        selected_data['type'], selected_data['weight'], strategy_mode
                    )
                    if explanation["success"]:
                        st.session_state.causal_explanations[cache_key] = explanation["response"]
                        st.markdown(explanation["response"])
                    else:
                        st.error(f"Analysis failed: {explanation.get('error', 'Unknown error')}")
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #334155; border-radius: 12px; padding: 1.5rem; margin-top: 1rem; text-align: center;">
            <h4 style="color: #29b5e8; margin-top: 0;">AI-Powered Analysis</h4>
            <p style="color: #94a3b8; font-size: 1rem;">Click a relationship button above to view pre-computed analysis.</p>
            <p style="color: #64748b; font-size: 0.9rem; margin-top: 0.5rem;">Analysis covers: Mechanism, Financial Impact, Strategic Fit, and Action Levers</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.subheader("Inventory Decomposition")

inv_data = df.groupby('PERFORMANCE_MONTH').agg({
    'CYCLE_STOCK_VALUE': 'sum', 'SAFETY_STOCK_VALUE': 'sum',
    'PIPELINE_STOCK_VALUE': 'sum', 'ANTICIPATION_STOCK_VALUE': 'sum',
    'STRATEGIC_STOCK_VALUE': 'sum'
}).reset_index().sort_values('PERFORMANCE_MONTH')

inv_data_melted = pd.melt(
    inv_data, id_vars=['PERFORMANCE_MONTH'],
    value_vars=['CYCLE_STOCK_VALUE', 'SAFETY_STOCK_VALUE', 'PIPELINE_STOCK_VALUE', 
                'ANTICIPATION_STOCK_VALUE', 'STRATEGIC_STOCK_VALUE'],
    var_name='Type', value_name='Value'
)
inv_data_melted['Type'] = inv_data_melted['Type'].str.replace('_STOCK_VALUE', '').str.replace('_', ' ').str.title()
inv_data_melted['Value'] = inv_data_melted['Value'] / 1_000_000

fig_inv = px.area(
    inv_data_melted, x='PERFORMANCE_MONTH', y='Value', color='Type',
    title='Inventory Structure Over Time ($M)',
    color_discrete_map={'Cycle': SNOWFLAKE_BLUE, 'Safety': VALENCIA_ORANGE, 'Pipeline': STAR_BLUE,
                        'Anticipation': PURPLE_MOON, 'Strategic': FIRST_LIGHT}
)
fig_inv = apply_dark_theme(fig_inv)
fig_inv.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

if st.session_state.compare_baseline and baseline_df is not None:
    baseline_inv = baseline_df.groupby('PERFORMANCE_MONTH')['TOTAL_INVENTORY_VALUE'].sum().reset_index()
    baseline_inv['Value'] = baseline_inv['TOTAL_INVENTORY_VALUE'] / 1_000_000
    fig_inv.add_trace(go.Scatter(
        x=baseline_inv['PERFORMANCE_MONTH'], y=baseline_inv['Value'],
        mode='lines', name='Baseline Total', line=dict(color=BORDER, width=2, dash='dash')
    ))

st.plotly_chart(fig_inv, use_container_width=True)

st.markdown("---")
st.subheader("Financial Bridge")

bridge_data = df.head(12).sort_values('PERFORMANCE_MONTH')

nopat_avg = float(bridge_data['NOPAT_USD'].mean()) / 1_000_000
fcf_avg = float(bridge_data['FREE_CASH_FLOW_USD'].mean()) / 1_000_000

current_inv = float(latest.get('TOTAL_INVENTORY_VALUE', 0)) / 1_000_000
current_safety = float(latest.get('SAFETY_STOCK_VALUE', 0)) / 1_000_000
current_pipeline = float(latest.get('PIPELINE_STOCK_VALUE', 0)) / 1_000_000

inv_change = (float(bridge_data['TOTAL_INVENTORY_VALUE'].iloc[-1]) - float(bridge_data['TOTAL_INVENTORY_VALUE'].iloc[0])) / 1_000_000 if len(bridge_data) > 1 else 0
capital_change = (float(bridge_data['CAPITAL_EMPLOYED_USD'].iloc[-1]) - float(bridge_data['CAPITAL_EMPLOYED_USD'].iloc[0])) / 1_000_000 if len(bridge_data) > 1 else 0

wc_delta = inv_change * 0.8
fa_delta = capital_change - inv_change if capital_change > inv_change else capital_change * 0.2

implied_fcf = nopat_avg - wc_delta - fa_delta

fig_bridge = go.Figure(go.Waterfall(
    name="Financial Bridge", orientation="v",
    measure=["absolute", "relative", "relative", "total"],
    x=["NOPAT", "Working Capital", "Fixed Assets", "Free Cash Flow"],
    y=[nopat_avg, -wc_delta, -fa_delta, 0],
    text=[f"${nopat_avg:.1f}M", f"${-wc_delta:+.1f}M", f"${-fa_delta:+.1f}M", f"${implied_fcf:.1f}M"],
    textposition="outside",
    connector={"line": {"color": BORDER, "width": 2}},
    increasing={"marker": {"color": SNOWFLAKE_BLUE}},
    decreasing={"marker": {"color": VALENCIA_ORANGE}},
    totals={"marker": {"color": PURPLE_MOON}}
))
fig_bridge.update_layout(
    title="Cash Flow Bridge: NOPAT to Free Cash Flow ($M)",
    showlegend=False,
    height=400
)
fig_bridge = apply_dark_theme(fig_bridge)
st.plotly_chart(fig_bridge, use_container_width=True)

bridge_explain_col1, bridge_explain_col2 = st.columns(2)
with bridge_explain_col1:
    nopat_tip = f'<span style="cursor: help; border-bottom: 1px dotted {TEXT_MUTED};" title="{ACRONYM_DEFINITIONS["NOPAT"][0]}: {ACRONYM_DEFINITIONS["NOPAT"][1]}">NOPAT<sup style="font-size: 0.6rem; color: {SNOWFLAKE_BLUE};">ⓘ</sup></span>'
    capex_tip = f'<span style="cursor: help; border-bottom: 1px dotted {TEXT_MUTED};" title="{ACRONYM_DEFINITIONS["CapEx"][0]}: {ACRONYM_DEFINITIONS["CapEx"][1]}">CapEx<sup style="font-size: 0.6rem; color: {SNOWFLAKE_BLUE};">ⓘ</sup></span>'
    st.markdown(f"""
    <div style="color: {TEXT};">
    <strong>Bridge Components:</strong><br/>
    • <strong>{nopat_tip}:</strong> Net Operating Profit After Tax = ${nopat_avg:.1f}M<br/>
    • <strong>Working Capital Delta:</strong> Change in inventory & receivables = ${wc_delta:.1f}M<br/>
    • <strong>Fixed Asset Delta:</strong> {capex_tip} less depreciation = ${fa_delta:.1f}M
    </div>
    """, unsafe_allow_html=True)
with bridge_explain_col2:
    fcf_tip = f'<span style="cursor: help; border-bottom: 1px dotted {TEXT_MUTED};" title="{ACRONYM_DEFINITIONS["FCF"][0]}: {ACRONYM_DEFINITIONS["FCF"][1]}">FCF<sup style="font-size: 0.6rem; color: {SNOWFLAKE_BLUE};">ⓘ</sup></span>'
    st.markdown(f"""
    <div style="color: {TEXT};">
    <strong>Result:</strong><br/>
    • <strong>Free Cash Flow:</strong> ${implied_fcf:.1f}M<br/>
    • <strong>Actual {fcf_tip} (reported):</strong> ${fcf_avg:.1f}M<br/>
    • <strong>Variance:</strong> ${(implied_fcf - fcf_avg):.1f}M (timing adjustments)
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.subheader("Document Search")

doc_col1, doc_col2 = st.columns([3, 1])
with doc_col1:
    doc_query = st.text_input("Search QBR documents", placeholder="Red Sea disruption impact", label_visibility="collapsed")
with doc_col2:
    search_docs = st.button("Search", use_container_width=True)

if search_docs and doc_query:
    with st.spinner("Searching..."):
        docs = search_qbr_docs(session, doc_query)
        if docs:
            for doc in docs:
                with st.expander(f"{doc['DOC_NAME']} ({doc['QUARTER']} {doc['YEAR']})"):
                    st.markdown(str(doc['CONTENT_TEXT'])[:500] + "...")
        else:
            st.info("No matching documents found")

st.markdown("---")
st.subheader("Ask Cortex")

ask_col1, ask_col2 = st.columns([5, 1])
with ask_col1:
    user_question = st.text_input(
        "Ask Cortex",
        placeholder="Why did ROCE drop despite OEE improvement?",
        label_visibility="collapsed"
    )
with ask_col2:
    ask_clicked = st.button("Ask", type="primary", use_container_width=True)

if ask_clicked and user_question:
    with st.spinner("Analyzing..."):
        result = query_cortex_analyst(session, user_question)
        if result["success"]:
            st.info(result["response"])
        else:
            st.error(f"Error: {result.get('error', 'Unknown error')}")
