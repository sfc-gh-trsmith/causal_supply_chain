import base64
from typing import List, Dict
import pandas as pd

CONSULTING_PALETTE = {
    'bg': '#1a1a2e',
    'card_bg': '#16213e',
    'driver': '#e94560',
    'lever': '#0f4c75',
    'outcome': '#1b9aaa',
    'positive': '#00b894',
    'negative': '#d63031',
    'text': '#f8f9fa',
    'subtext': '#adb5bd',
    'line': '#495057'
}

def create_causal_svg(traces_df: pd.DataFrame, selected_relationship: str = None) -> str:
    if traces_df.empty:
        return _empty_svg()
    
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
    
    width, height = 1000, 600
    row_y = {'drivers': 80, 'levers': 300, 'outcomes': 520}
    node_width = 160
    node_height = 44
    
    def get_x_positions(items: List[str], total_width: int) -> Dict[str, int]:
        if not items:
            return {}
        spacing = min(node_width + 30, (total_width - 100) / max(len(items), 1))
        start_x = (total_width - spacing * (len(items) - 1)) / 2
        return {item: int(start_x + i * spacing) for i, item in enumerate(items)}
    
    driver_x = get_x_positions(drivers, width)
    lever_x = get_x_positions(levers, width)
    outcome_x = get_x_positions(outcomes, width)
    
    def format_label(n: str) -> str:
        acronyms = {'DIOH': 'DIOH', 'MAPE': 'MAPE', 'OEE': 'OEE', 'ROCE': 'ROCE', 
                    'FCF': 'FCF', 'OTIF': 'OTIF', 'COGS': 'COGS', 'SKU': 'SKU', 'NPI': 'NPI'}
        result = n.replace('_', ' ').replace(' PCT', '%').replace(' USD', '$').replace(' VALUE', '').title()
        for acr_upper, acr_display in acronyms.items():
            result = result.replace(acr_upper.title(), acr_display)
        return result
    
    rel_data = []
    for _, row in traces_df.iterrows():
        rel_id = f"{row['SOURCE_METRIC']}__{row['TARGET_METRIC']}"
        rel_data.append({
            'id': rel_id,
            'source': row['SOURCE_METRIC'],
            'target': row['TARGET_METRIC'],
            'weight': abs(row['CAUSAL_WEIGHT']),
            'is_positive': row['RELATIONSHIP_TYPE'] == 'POSITIVE'
        })
    
    svg_parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" style="font-family: 'Inter', 'Helvetica Neue', Arial, sans-serif;">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#0d1b2a"/>
      <stop offset="100%" style="stop-color:#1b263b"/>
    </linearGradient>
    <linearGradient id="driverGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#e94560"/>
      <stop offset="100%" style="stop-color:#ff6b6b"/>
    </linearGradient>
    <linearGradient id="leverGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#0077b6"/>
      <stop offset="100%" style="stop-color:#00b4d8"/>
    </linearGradient>
    <linearGradient id="outcomeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#2a9d8f"/>
      <stop offset="100%" style="stop-color:#40c9a2"/>
    </linearGradient>
    <filter id="cardShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000" flood-opacity="0.3"/>
    </filter>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <filter id="glowStrong">
      <feGaussianBlur stdDeviation="4" result="blur"/>
      <feFlood flood-color="#29b5e8" flood-opacity="0.5" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge><feMergeNode in="glow"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <marker id="arrowPos" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,10 L10,5 z" fill="#00b894" opacity="0.9"/>
    </marker>
    <marker id="arrowNeg" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,10 L10,5 z" fill="#d63031" opacity="0.9"/>
    </marker>
    <marker id="arrowPosSelected" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,12 L12,6 z" fill="#00b894"/>
    </marker>
    <marker id="arrowNegSelected" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,12 L12,6 z" fill="#d63031"/>
    </marker>
  </defs>
  <rect width="{width}" height="{height}" fill="url(#bgGrad)"/>
''']
    
    svg_parts.append(f'''
  <text x="{width // 2}" y="35" text-anchor="middle" fill="#e94560" font-size="12" font-weight="600" letter-spacing="1.5">PROCESS DRIVERS</text>
  <text x="{width // 2}" y="255" text-anchor="middle" fill="#00b4d8" font-size="12" font-weight="600" letter-spacing="1.5">ECONOMIC LEVERS</text>
  <text x="{width // 2}" y="475" text-anchor="middle" fill="#40c9a2" font-size="12" font-weight="600" letter-spacing="1.5">FINANCIAL OUTCOMES</text>
''')
    
    for rel in rel_data:
        src, tgt = rel['source'], rel['target']
        weight = rel['weight']
        is_positive = rel['is_positive']
        rel_id = rel['id']
        
        if src in driver_x:
            x1, y1 = driver_x[src], row_y['drivers'] + node_height // 2 + 10
        elif src in lever_x:
            x1, y1 = lever_x[src], row_y['levers'] + node_height // 2 + 10
        else:
            continue
            
        if tgt in lever_x:
            x2, y2 = lever_x[tgt], row_y['levers'] - node_height // 2 + 10
        elif tgt in outcome_x:
            x2, y2 = outcome_x[tgt], row_y['outcomes'] - node_height // 2 + 10
        else:
            continue
        
        is_selected = selected_relationship == rel_id
        
        color = '#00b894' if is_positive else '#d63031'
        base_opacity = 0.35 + weight * 0.35
        opacity = 1.0 if is_selected else base_opacity
        stroke_width = (1.5 + weight * 2.5) * (2.2 if is_selected else 1.0)
        
        if is_selected:
            marker = 'arrowPosSelected' if is_positive else 'arrowNegSelected'
        else:
            marker = 'arrowPos' if is_positive else 'arrowNeg'
        
        ctrl_y1 = y1 + (y2 - y1) * 0.4
        ctrl_y2 = y1 + (y2 - y1) * 0.6
        
        glow_filter = 'filter="url(#glowStrong)"' if is_selected else ''
        
        hit_area = f'''  <path d="M{x1},{y1} C{x1},{ctrl_y1} {x2},{ctrl_y2} {x2},{y2}" 
        fill="none" stroke="transparent" stroke-width="20" 
        style="cursor:pointer;" data-rel-id="{rel_id}" class="causal-path-hit"/>
'''
        svg_parts.append(hit_area)
        
        svg_parts.append(f'''  <path id="rel_{rel_id}" d="M{x1},{y1} C{x1},{ctrl_y1} {x2},{ctrl_y2} {x2},{y2}" 
        fill="none" stroke="{color}" stroke-width="{stroke_width:.1f}" opacity="{opacity:.2f}" 
        marker-end="url(#{marker})" {glow_filter} style="cursor:pointer; pointer-events:none;" class="causal-path-visual" data-rel-id="{rel_id}"/>
''')
    
    for node, x in driver_x.items():
        y = row_y['drivers']
        label = format_label(node)
        svg_parts.append(_create_node_card(x, y, label, 'driverGrad', '#e94560'))
    
    for node, x in lever_x.items():
        y = row_y['levers']
        label = format_label(node)
        svg_parts.append(_create_node_card(x, y, label, 'leverGrad', '#00b4d8'))
    
    for node, x in outcome_x.items():
        y = row_y['outcomes']
        label = format_label(node)
        svg_parts.append(_create_node_card(x, y, label, 'outcomeGrad', '#40c9a2'))
    
    svg_parts.append(_create_legend(width, height))
    svg_parts.append('</svg>')
    
    return ''.join(svg_parts)


def _create_node_card(x: int, y: int, label: str, gradient: str, accent: str) -> str:
    card_width, card_height = 160, 44
    rx = x - card_width // 2
    ry = y - card_height // 2
    
    lines = _wrap_text(label, 18)
    if len(lines) == 1:
        text_content = f'<text x="{x}" y="{y + 5}" text-anchor="middle" fill="#f8f9fa" font-size="12" font-weight="500">{lines[0]}</text>'
    else:
        text_content = f'''<text x="{x}" y="{y - 4}" text-anchor="middle" fill="#f8f9fa" font-size="11" font-weight="500">{lines[0]}</text>
    <text x="{x}" y="{y + 10}" text-anchor="middle" fill="#f8f9fa" font-size="11" font-weight="500">{lines[1]}</text>'''
    
    return f'''  <g filter="url(#cardShadow)">
    <rect x="{rx}" y="{ry}" width="{card_width}" height="{card_height}" rx="6" fill="#1e3a5f" stroke="{accent}" stroke-width="1.5"/>
    <rect x="{rx}" y="{ry}" width="4" height="{card_height}" rx="2" fill="url(#{gradient})"/>
    {text_content}
  </g>
'''


def _wrap_text(text: str, max_chars: int) -> List[str]:
    if len(text) <= max_chars:
        return [text]
    words = text.split()
    lines = []
    current = []
    for word in words:
        if sum(len(w) for w in current) + len(current) + len(word) <= max_chars:
            current.append(word)
        else:
            if current:
                lines.append(' '.join(current))
            current = [word]
    if current:
        lines.append(' '.join(current))
    return lines[:2]


def _create_legend(width: int, height: int) -> str:
    legend_y = height - 25
    return f'''
  <g transform="translate({width // 2 - 120}, {legend_y})">
    <line x1="0" y1="0" x2="30" y2="0" stroke="#00b894" stroke-width="2.5"/>
    <polygon points="28,-4 36,0 28,4" fill="#00b894"/>
    <text x="42" y="4" fill="#adb5bd" font-size="10">Positive Impact</text>
    <line x1="140" y1="0" x2="170" y2="0" stroke="#d63031" stroke-width="2.5"/>
    <polygon points="168,-4 176,0 168,4" fill="#d63031"/>
    <text x="182" y="4" fill="#adb5bd" font-size="10">Negative Impact</text>
  </g>
'''


def _empty_svg() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 600">
  <rect width="1000" height="600" fill="#0d1b2a"/>
  <text x="500" y="300" text-anchor="middle" fill="#6c757d" font-size="14" font-family="Inter, Arial, sans-serif">No causal relationships to display</text>
</svg>'''


def svg_to_base64(svg_string: str) -> str:
    return base64.b64encode(svg_string.encode('utf-8')).decode('utf-8')
