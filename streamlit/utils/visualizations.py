import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List, Optional, Tuple

DARK_BG = "#0f172a"
CARD_BG = "#1e293b"
BORDER = "#334155"
TEXT = "#e2e8f0"
SNOWFLAKE_BLUE = "#29B5E8"
SERVICE_COLOR = "#22c55e"
COST_COLOR = "#f59e0b"
CASH_COLOR = "#3b82f6"
NEGATIVE_COLOR = "#ef4444"


def apply_dark_theme(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        paper_bgcolor=DARK_BG,
        plot_bgcolor=DARK_BG,
        font=dict(color=TEXT, family="Inter, sans-serif"),
        hoverlabel=dict(bgcolor=CARD_BG, bordercolor=BORDER, font_color=TEXT),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    fig.update_xaxes(gridcolor=BORDER, zerolinecolor=BORDER)
    fig.update_yaxes(gridcolor=BORDER, zerolinecolor=BORDER)
    return fig


def create_causal_sankey(traces_df: pd.DataFrame) -> go.Figure:
    if traces_df.empty:
        return go.Figure()
    
    all_nodes = list(set(traces_df['SOURCE_METRIC'].tolist() + 
                        traces_df['TARGET_METRIC'].tolist()))
    node_indices = {node: i for i, node in enumerate(all_nodes)}
    
    driver_nodes = ['FORECAST_MAPE_PCT', 'LEAD_TIME_DAYS', 'BATCH_SIZE', 'OEE_PCT']
    lever_nodes = ['SAFETY_STOCK_VALUE', 'PIPELINE_STOCK_VALUE', 'CYCLE_STOCK_VALUE', 'COGS_USD']
    outcome_nodes = ['ROCE_PCT', 'FREE_CASH_FLOW_USD', 'GROSS_MARGIN_PCT']
    
    node_colors = []
    for node in all_nodes:
        if node in driver_nodes:
            node_colors.append(COST_COLOR)
        elif node in lever_nodes:
            node_colors.append(SNOWFLAKE_BLUE)
        elif node in outcome_nodes:
            node_colors.append(SERVICE_COLOR)
        else:
            node_colors.append(BORDER)
    
    sources = [node_indices.get(s, 0) for s in traces_df['SOURCE_METRIC']]
    targets = [node_indices.get(t, 0) for t in traces_df['TARGET_METRIC']]
    values = [abs(w) * 10 for w in traces_df['CAUSAL_WEIGHT'].tolist()]
    colors = ['rgba(34,197,94,0.6)' if r == 'POSITIVE' else 'rgba(239,68,68,0.6)' 
              for r in traces_df['RELATIONSHIP_TYPE']]
    
    node_labels = [n.replace('_', ' ').replace(' PCT', '%').replace(' USD', ' $').title() 
                   for n in all_nodes]
    
    fig = go.Figure(go.Sankey(
        arrangement='snap',
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color=BORDER, width=1),
            label=node_labels,
            color=node_colors,
            hovertemplate='%{label}<extra></extra>'
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors,
            hovertemplate='%{source.label} → %{target.label}<br>Weight: %{value:.1f}<extra></extra>'
        )
    ))
    
    fig.update_layout(
        title=dict(text="Causal Relationships: Process Drivers → Economic Levers → Financial Outcomes", 
                   font=dict(size=14)),
        height=400
    )
    
    return apply_dark_theme(fig)


def create_triangle_heatmap(service_val: float, cost_val: float, cash_val: float, 
                            mode: str, weights: Dict[str, float]) -> go.Figure:
    vertices = {
        'SERVICE': (0.5, 0.9),
        'COST': (0.1, 0.1),
        'CASH': (0.9, 0.1)
    }
    
    active_mapping = {
        'GROWTH': 'SERVICE',
        'MARGIN': 'COST', 
        'CASH': 'CASH'
    }
    active_corner = active_mapping.get(mode, 'SERVICE')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[0.1, 0.5, 0.9, 0.1],
        y=[0.1, 0.9, 0.1, 0.1],
        mode='lines',
        line=dict(color=BORDER, width=2),
        fill='toself',
        fillcolor='rgba(30, 41, 59, 0.5)',
        hoverinfo='skip'
    ))
    
    values = {'SERVICE': service_val, 'COST': cost_val, 'CASH': cash_val}
    colors_map = {'SERVICE': SERVICE_COLOR, 'COST': COST_COLOR, 'CASH': CASH_COLOR}
    weight_map = {'SERVICE': weights.get('service', 0.33), 
                  'COST': weights.get('cost', 0.33), 
                  'CASH': weights.get('cash', 0.33)}
    
    for corner, (x, y) in vertices.items():
        val = values[corner]
        is_active = corner == active_corner
        color = colors_map[corner]
        weight = weight_map[corner]
        
        marker_size = 35 + (weight * 30)
        
        if is_active:
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode='markers',
                marker=dict(
                    size=marker_size + 15,
                    color=color,
                    opacity=0.3,
                    line=dict(width=0)
                ),
                hoverinfo='skip'
            ))
        
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(
                size=marker_size,
                color=CARD_BG if not is_active else color,
                line=dict(color=color, width=3 if is_active else 2),
                opacity=1 if is_active else 0.7
            ),
            text=[f"<b>{corner}</b><br>{val:.1f}%"],
            textposition='middle center',
            textfont=dict(color='white' if is_active else TEXT, size=11),
            hovertemplate=f'{corner}<br>Value: {val:.1f}%<br>Weight: {weight:.0%}<extra></extra>'
        ))
    
    fig.update_layout(
        showlegend=False,
        xaxis=dict(visible=False, range=[0, 1]),
        yaxis=dict(visible=False, range=[0, 1], scaleanchor='x'),
        height=300,
        margin=dict(l=10, r=10, t=30, b=10),
        title=dict(text=f"Active Mode: {mode}", font=dict(size=12))
    )
    
    return apply_dark_theme(fig)


def create_comparison_chart(baseline_df: pd.DataFrame, scenario_df: pd.DataFrame,
                           metric: str, title: str) -> go.Figure:
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=baseline_df['PERFORMANCE_MONTH'],
        y=baseline_df[metric],
        mode='lines',
        name='Baseline',
        line=dict(color=BORDER, width=2, dash='dash'),
        hovertemplate='Baseline: %{y:.2f}<extra></extra>'
    ))
    
    fig.add_trace(go.Scatter(
        x=scenario_df['PERFORMANCE_MONTH'],
        y=scenario_df[metric],
        mode='lines+markers',
        name='Scenario',
        line=dict(color=SNOWFLAKE_BLUE, width=2),
        marker=dict(size=6),
        hovertemplate='Scenario: %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=title,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=250
    )
    
    return apply_dark_theme(fig)


def create_roce_gauge(current: float, projected: float, target: float = 15.0) -> go.Figure:
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=projected,
        delta={'reference': current, 'relative': False, 'valueformat': '.2f',
               'increasing': {'color': SERVICE_COLOR}, 'decreasing': {'color': NEGATIVE_COLOR}},
        number={'suffix': '%', 'valueformat': '.1f'},
        title={'text': "Projected ROCE"},
        gauge={
            'axis': {'range': [0, 25], 'tickwidth': 1, 'tickcolor': BORDER},
            'bar': {'color': SNOWFLAKE_BLUE},
            'bgcolor': CARD_BG,
            'borderwidth': 2,
            'bordercolor': BORDER,
            'steps': [
                {'range': [0, 10], 'color': 'rgba(239,68,68,0.3)'},
                {'range': [10, 15], 'color': 'rgba(245,158,11,0.3)'},
                {'range': [15, 25], 'color': 'rgba(34,197,94,0.3)'}
            ],
            'threshold': {
                'line': {'color': TEXT, 'width': 3},
                'thickness': 0.8,
                'value': current
            }
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    
    return apply_dark_theme(fig)


def create_waterfall_impact(impacts: Dict[str, float], title: str) -> go.Figure:
    labels = list(impacts.keys())
    values = list(impacts.values())
    
    measures = ['relative'] * (len(labels) - 1) + ['total']
    
    colors = [SERVICE_COLOR if v > 0 else NEGATIVE_COLOR for v in values[:-1]] + [SNOWFLAKE_BLUE]
    
    fig = go.Figure(go.Waterfall(
        name="Impact",
        orientation="v",
        measure=measures,
        x=labels,
        y=values,
        connector={"line": {"color": BORDER}},
        decreasing={"marker": {"color": NEGATIVE_COLOR}},
        increasing={"marker": {"color": SERVICE_COLOR}},
        totals={"marker": {"color": SNOWFLAKE_BLUE}}
    ))
    
    fig.update_layout(
        title=title,
        height=250,
        showlegend=False
    )
    
    return apply_dark_theme(fig)
