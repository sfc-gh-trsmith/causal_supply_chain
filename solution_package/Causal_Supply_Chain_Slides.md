# Project Causal Chain: Presentation Slides
## Executive Meeting Deck (8-10 slides)

---

## Slide Structure Overview

| Slide | Phase | Title (Insight Statement) |
|-------|-------|--------------------------|
| 1 | Title | Causal Chain: From Supply Chain Metrics to Financial Outcomes |
| 2 | Situation | Manufacturing loses $163B annually to invisible supply chain trade-offs |
| 3 | Complication | Your functional teams optimize in silos, creating hidden costs |
| 4 | Resolution - Vision | A unified view connects every operational lever to ROCE |
| 5 | Resolution - Solution | The Strategy Simulator makes trade-offs visible in real-time |
| 6 | Resolution - Architecture | Snowflake unifies data, AI, and insights in one platform |
| 7 | Resolution - Demo | Interactive scenario simulation with AI-powered explanations |
| 8 | Proof | Companies achieve 150-300 bps ROCE improvement |
| 9 | Action | Next conversation: Pilot with your data |

---

## Slide 1: Title Slide

### Causal Chain
**From Supply Chain Metrics to Financial Outcomes**

*A Snowflake-powered Strategy Simulator*

[Customer Name] | [Date]

**Presenter:** [Name, Title]

---

## Slide 2: Situation

### Manufacturing loses $163B annually to invisible supply chain trade-offs

**Visual:** Use `assets/problem_impact.svg`

![Problem Impact](assets/problem_impact.svg)

**Speaker Notes:**
- This isn't about one disruption—it's systemic
- The cost compounds because decisions cascade in ways organizations can't see
- [Customer Name] likely has similar hidden costs in their supply chain

---

## Slide 3: Complication

### Your functional teams optimize in silos, creating hidden costs

**Visual:** Three disconnected circles with conflicting arrows

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│     SALES              OPERATIONS           FINANCE         │
│   "Service ↑"          "Cost ↓"            "Cash ↓"         │
│                                                             │
│   ┌───────┐           ┌───────┐           ┌───────┐        │
│   │ More  │           │ Bigger│           │ Less  │        │
│   │ SKUs  │           │ Batch │           │Invent.│        │
│   └───┬───┘           └───┬───┘           └───┬───┘        │
│       │                   │                   │             │
│       └───────────────────┼───────────────────┘             │
│                           │                                 │
│                           ▼                                 │
│              [ WHO OWNS THE TRADE-OFFS? ]                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**The Problem at [Customer Name]:**
- Sales pushes for more SKUs → Higher forecast error → More safety stock
- Operations wants larger batches → Lower unit cost → More cycle stock
- Finance cuts inventory → Service levels drop → Lost revenue

**Speaker Notes:**
- Ask: "How long does it take to answer 'Why did ROCE drop last quarter?'"
- Typical answer: 2 weeks, 5 people, 3 spreadsheets
- This delay means decisions are made without visibility

---

## Slide 4: Vision

### A unified view connects every operational lever to ROCE

**Visual:** Use `assets/before_after.svg`

![Before After Transformation](assets/before_after.svg)

**What Changes:**
- Every metric shows its impact on the other two corners
- Inventory is decomposed by economic reason (Cycle, Safety, Pipeline)
- Executives can simulate scenarios before committing capital

**Speaker Notes:**
- This is not a dashboard—it's a decision support system
- The triangle forces explicit trade-off conversations
- Strategic mode (Growth/Margin/Cash) aligns the entire organization

---

## Slide 5: Solution

### The Strategy Simulator makes trade-offs visible in real-time

**Visual:** Use `assets/dashboard_preview.svg`

![Dashboard Preview](assets/dashboard_preview.svg)

**Speaker Notes:**
- Demo flow: Select "Port Strike" → See instant impact on FCF and ROCE
- Highlight the confidence intervals (statistical rigor)
- Show the Cortex AI response to a natural language question

---

## Slide 6: Architecture

### Snowflake unifies data, AI, and insights in one platform

**Visual:** Use `assets/architecture.svg`

![Architecture](assets/architecture.svg)

**Why Snowflake:**
- **Unified Data:** No pipelines between supply chain and finance systems
- **Native AI:** Cortex services—no external ML infrastructure
- **Governed:** Single source of truth with role-based access

**Speaker Notes:**
- Emphasize: All data stays in Snowflake—no copies, no ETL
- Semantic model = one definition of "ROCE" across the org
- Streamlit runs inside Snowflake—security and performance built-in

---

## Slide 7: Demo

### Interactive scenario simulation with AI-powered explanations

**Visual:** Live demo or video walkthrough

**Demo Script (2-3 minutes):**

1. **Strategy Mode Selection**
   - Start in "GROWTH" mode
   - Show how weights adjust (Service high, Cash tolerant)

2. **Shock Scenario**
   - Select "PORT_STRIKE"
   - Watch metrics update instantly
   - Highlight: Pipeline Stock +$1.2M, ROCE -45 bps

3. **ROCE Sensitivity Calculator**
   - Adjust Safety Stock slider (-15%)
   - Show projected ROCE improvement (+120 bps)
   - "This frees $2.1M in capital"

4. **Causal Trace**
   - Click "Forecast Error" in the Sankey
   - Follow the path: Forecast Error → Safety Stock → Capital Employed → ROCE

5. **AI Assistant**
   - Ask: "Why did ROCE drop despite OEE improvement?"
   - Show Cortex Complete response with financial context

**Speaker Notes:**
- Keep demo under 3 minutes
- End with: "This took 10 seconds. Previously, it took 2 weeks."

---

## Slide 8: Proof

### Companies achieve 150-300 bps ROCE improvement

**Visual:** Use `assets/roi_value.svg`

![ROI Value](assets/roi_value.svg)

**Key Outcomes:**
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ DECISION CYCLE           │  -70% (weeks to days)   │   │
│  │ Scenario simulation replaces spreadsheet analysis   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Sources: Deloitte Working Capital Study (2024),            │
│           Bain Supply Chain Excellence Survey (2024)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**For [Customer Name]:**
- Based on [$X]M in current inventory, a 15% safety stock reduction could free **$[Y]M**
- At your current ROCE of [Z]%, this could add **[N] basis points**

**Speaker Notes:**
- Customize with customer-specific estimates if data available
- Emphasize: These are conservative, externally validated benchmarks
- Offer to build customer-specific ROI model

---

## Slide 9: Action

### Next conversation: Pilot with your data

**Visual:** Clear next steps with timeline

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  PROPOSED PILOT                                             │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ SCOPE                                               │   │
│  │ - One business unit or product line                 │   │
│  │ - 12-24 months of historical performance data       │   │
│  │ - 2-3 key scenarios (disruption, demand shift)      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ TIMELINE                                            │   │
│  │ Week 1-2: Data integration + semantic model         │   │
│  │ Week 3-4: Dashboard customization + ML training     │   │
│  │ Week 5-6: User acceptance + refinement              │   │
│  │ Week 7+: Production deployment                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ INVESTMENT                                          │   │
│  │ - Snowflake consumption: ~$X/month (XS warehouse)   │   │
│  │ - Services: [To be scoped based on data complexity] │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  NEXT STEP: Schedule data assessment call                   │
│  [Contact Name] | [Email] | [Phone]                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Speaker Notes:**
- Be specific about next action: "Can we schedule a 30-minute data assessment call?"
- Offer to provide a sample ROI model with their numbers
- Leave behind: One-pager with solution overview + contact info

---

## Appendix Slides (As Needed)

### A1: Detailed Data Model

| Table | Purpose | Key Fields |
|-------|---------|------------|
| FACT_PERFORMANCE_SNAPSHOT | Monthly KPIs | OTIF, Margin, ROCE, FCF |
| DIM_INVENTORY_STRUCTURE | Inventory types | Cycle, Safety, Pipeline |
| SCENARIO_CONTROL | Strategy parameters | Weights, permissible red |
| PREDICTIVE_BRIDGE | ML predictions | Predicted FCF, confidence |

### A2: Semantic Model Excerpt

```yaml
tables:
  - name: performance
    dimensions:
      - name: region
      - name: strategy_mode
    facts:
      - name: otif_pct
      - name: roce_pct
      - name: free_cash_flow_usd
```

### A3: Security Model

- Role-based access control
- All data stays in Snowflake
- Audit trail for all queries

---

## Quality Checkpoint

- [x] 9 core slides (fits 25-minute delivery)
- [x] Each slide has full-sentence insight title
- [x] Architecture diagram legible in conference room
- [x] Proof slide includes externally validated outcomes
- [x] CTA is specific and actionable (data assessment call)
- [x] Customer-specific placeholders identified ([Customer Name], etc.)

---

*Document Version: 1.0 | Created: 2026-01-25 | Project Causal Chain*
