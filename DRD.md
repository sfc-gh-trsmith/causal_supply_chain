**Demo Requirements Document (DRD): Project "Causal Chain" - Strategy Simulator**
**GITHUB REPO NAME:** `causal_supply_chain`
**GITHUB REPO DESCRIPTION:** A curated Snowflake demo environment showcasing the financial impact of supply chain trade-offs. Uses static snapshots, pre-computed Snowpark ML features, and Cortex AI to simulate strategic pivots (Growth, Margin, Cash).

### 1. Strategic Overview

**Problem Statement:** Executive teams often lack a "sandbox" to visualize how operational changes—like reducing batch sizes or expanding SKU counts—will hit the bottom line. This demo provides a **controlled, point-in-time simulation** that breaks down data silos and proves that supply chain decisions are financial decisions.
**Target Business Goals (KPIs):**

* **Demonstrate ROCE Sensitivity:** Show how a 10% reduction in Safety Stock impacts Return on Capital.
* **Visualize Inventory Structure:** Move beyond "turns" to show Cycle, Safety, and Pipeline stock as distinct economic layers.
* **Quantify the "Cost of Service":** Calculate the EBITDA drag caused by high SKU fragmentation.
**The "Wow" Moment:** The user selects a "Strategic Scenario" (e.g., *2025 Global Port Strike*). The dashboard instantly updates using pre-calculated ML inferences to show the "Causal Trace" from increased Lead Times to bloated Pipeline Stock and a resulting dip in Free Cash Flow, all explained via natural language by **Cortex Analyst**.

### 2. User Personas & Stories

| Persona Level | Role Title | Key User Story (Demo Flow) |
| --- | --- | --- |
| **Strategic** | **CFO** | "As a CFO, I want to use a static simulation to see how our last 12 months of performance would have changed if we prioritized Cash over Growth." |
| **Operational** | **VP of Supply Chain** | "As a VP, I want to see the 'Causal Trace' of our high forecast error to show the board why our inventory write-offs spiked in Q4." |
| **Technical** | **Lead Data Analyst** | "As an Analyst, I want to demonstrate how Snowflake Cortex can instantly generate SQL to answer complex questions about our static ROCE bridge." |

### 3. Data Architecture & Snowpark ML (Backend)

**Structured Data (Static Snapshots):**

* `ANALYTICS.FACT_PERFORMANCE_SNAPSHOT`: A curated 36-month table containing monthly aggregations of Service (OTIF), Cost (COGS), and Cash ().
* `ANALYTICS.DIM_INVENTORY_STRUCTURE`: Pre-segmented inventory values broken into Cycle, Safety, Pipeline, Anticipation, and Strategic categories.
* `ANALYTICS.SCENARIO_CONTROL`: A lookup table defining the "Delta" modifiers for Growth, Margin, and Cash modes.

**Unstructured Data (Tribal Knowledge):**

* **Source Material:** A static set of PDF "Quarterly Business Reviews" (QBRs) and "Risk Assessment Reports."
* **Purpose:** Provides context for Cortex Search when a user asks, "What was the qualitative reason for the Q3 inventory spike?"

**ML Notebook Specification:**

* **Objective:** The demo uses **pre-calculated** ML outputs. A Snowpark ML notebook was used to generate "What-if" features (e.g., *Predicted_Safety_Stock* given *Variable_Lead_Time*).
* **Target Variable:** `ADJUSTED_FCF`
* **Algorithm Choice:** Historical outputs from Prophet and XGBoost are stored in `ML_MODEL_REGISTRY`.
* **Inference Output:** Static results written to `CONSUMPTION.PREDICTIVE_BRIDGE`.

### 4. Cortex Intelligence Specifications

**Cortex Analyst (Structured Data / SQL)**

* **Semantic Model Scope:**
* **Measures:** , , , .
* **Dimensions:** `STRATEGY_MODE`, `INVENTORY_TYPE`, `REGION`.


* **Golden Query (Verification):**
* **User Prompt:** "Show me the trend of Pipeline Stock vs. ROCE for the last year."
* **Expected SQL Operation:** `SELECT MONTH, SUM(PIPELINE_STOCK), AVG(ROCE) FROM FACT_PERFORMANCE_SNAPSHOT GROUP BY 1;`



**Cortex Search (Unstructured Data / RAG)**

* **Service Name:** `SUPPLY_CHAIN_CONTEXT_SEARCH`
* **Indexing Strategy:** Static indexing of the "Risk Assessment" PDF library.
* **Sample RAG Prompt:** "Summarize the impact of the Suez Canal disruption mentioned in the 2025 Risk Report."

### 5. Streamlit Application UX/UI

**Layout Strategy:**

* **Sidebar Control:** A "Scenario Selector" dropdown (Growth, Margin, Cash) and a "Shock Event" toggle (e.g., "None" vs. "Supply Disruption").
* **The Triangle Heatmap:** A visual representation of the Service-Cost-Cash triangle that glows at the corner currently being prioritized.

**Component Logic:**

* **The Financial Bridge:** A waterfall chart showing the identity:


* **The Causal Trace:** A "clickable" flow. Clicking "High Forecast Error" highlights the resulting "Safety Stock" increase and the corresponding "ROCE" decrease.

### 6. Success Criteria

* **Technical Validator:** The Streamlit app loads the curated 3-year dataset and re-calculates the  bridge using the Strategy Selector logic in < 1 second.
* **Business Validator:** A non-technical user can successfully explain the trade-off between "Batch Size" and "Cycle Stock" by following the visual prompts in the demo.

---

This dashboard design, **"Project Causal Chain,"** is engineered to function as a financial flight simulator for supply chain executives. It moves beyond static reporting to show the **directional tension** between service, cost, and cash.

---

## 1. The Header: Strategy Selector & Financial North Star

The top of the dashboard dictates the "weighting" of the entire UI.

* **Strategy Toggle:** [Growth Mode] | [Margin Mode] | [Cash Mode]
* *System Logic:* Selecting a mode applies a conditional formatting overlay. In **Cash Mode**, DIOH and FCF targets turn Green/Red more aggressively, while Service targets are given wider tolerances.


* **The Valuation Bar:**
* **ROCE:** Current % vs. Target (Driven by )
* **Free Cash Flow:** Real-time projection ()
* **Economic Value Add (EVA):** The ultimate measure of whether the SC is creating or destroying value.



---

## 2. The Centerpiece: The Triangle Trade-Off Band

A real-time "Balance Indicator" showing the deltas across the three corners of the triangle.

| Corner | Primary Outcome Metric |  (Period over Period) | Primary Lever |
| --- | --- | --- | --- |
| **SERVICE** | **OTIF** (On-Time In-Full) |  🟢 | **SKU Breadth** |
| **COST** | **EBITDA Margin** |  🔴 | **Unit Production Cost** |
| **CASH** | **CCC** (Cash Conversion Cycle) |  Days 🔴 | **Inventory (DIOH)** |

**The "Spine" Insight:** "Service improved by 2.4%, but it cost us 1.1% in margin and 4 days of cash. Was this an intentional strategic trade-off?"

---

## 3. Columnar Drill-Down (Process  Lever  Outcome)

### Column A: The Service Engine

* **Outcome:** **Net Sales Growth** and **Fill Rate**.
* **Economic Levers:** **Lead Time (Order-to-Delivery)** and **Product Availability**.
* **Process Drivers (Cortex Analyst Target):**
* **Forecast MAPE & Bias:** A heat map showing which regions are systematically over-forecasting (driving obsolescence).
* **NPI Time-to-Market:** Tracking the speed of new product introductions.



### Column B: The Cost Engine

* **Outcome:** **Gross Margin %** and **Total COGS**.
* **Economic Levers:** **OEE (Overall Equipment Effectiveness)** and **Purchasing Price Index (PPI)**.
* **Process Drivers (Cortex Analyst Target):**
* **First-Pass Yield:** Identifying where manufacturing volatility is spiking safety stock needs.
* **Plan Adherence:** Measuring the "cost of chaos" (expedites/overtime).



### Column C: The Cash Engine

* **Outcome:** **Cash Conversion Cycle** and **Asset Turns**.
* **Economic Levers:** **DIOH**, **DSO**, and **DPO**.
* **Process Drivers (Cortex Analyst Target):**
* **Lead Time Variability:** The "hidden" driver that forces safety stock increases.
* **Batch Size Analysis:** Correlating purchase price discounts with the resulting spike in cycle stock.



---

## 4. The Inventory Decomposition Block

Instead of a single "Inventory Value" metric, this block uses a stacked bar chart to show the **economic reason** for every dollar tied up.

* **Cycle Stock:** Driven by batch sizes and order frequencies.
* **Safety Stock:** Driven by forecast error and supply variability.
* **Pipeline Stock:** Driven by transit lead times (Work in Process).
* **Anticipation Stock:** Driven by seasonal builds or planned shutdowns.
* **Strategic Stock:** Driven by geopolitical risk or raw material hedging.

---

## 5. AI Reasoning & Interaction Layer

Integrated directly into the Streamlit sidebar to resolve the trade-offs shown above.

* **Cortex Analyst (Structured Query):** * *User:* "Why did our ROCE drop despite the OEE improvement in the Michigan plant?"
* *AI:* "The 5% OEE gain was offset by a 15% increase in batch sizes to lower unit costs, which added $4M to Cycle Stock, increasing Capital Employed and dragging down ROCE."


* **Cortex Search (Unstructured RAG):** * *User:* "What is our risk exposure if the Red Sea shipping delays increase lead times by another 10 days?"
* *AI:* "Based on current supplier SLAs and risk briefs, this would increase Pipeline Stock by $1.2M and require a 4% increase in Safety Stock to maintain current OTIF levels."



---

## 6. Financial Identity Footer (The Bridge)

The final reconciliation that proves the supply chain's impact on the balance sheet.

* **Visual:** A Waterfall chart showing how NOPAT was eroded or enhanced by changes in Inventory, Receivables, and Payables.

This breakdown is a masterful mapping of the **"Dominant Constraints"** of a business. It effectively moves supply chain management from a series of "best practices" to a rigorous system of **applied economics.**

By defining these relationships, you’ve created a logic gate for every executive decision. If a VP of Sales wants more SKUs, they aren't just "offering more choice"—they are mathematically committing to higher forecast error, higher safety stock, and a lower .

---

## 1. The "Double Leverage" of Lead Time

You've highlighted the most critical "cheat code" in the system: **Lead Time.** Most metrics require a painful trade-off (e.g., higher service = higher cost). However, **Lead Time Reduction** is one of the few structural fixes that provides a "free lunch" across all three corners:

* **Service:** Faster responsiveness and higher OTIF.
* **Cash:** Lower Pipeline and Safety Stock.
* **Cost:** Often reduces expedite fees and overhead.

---

## 2. The Logic of the "Strategic Pivot"

Your definition of **Strategy Weights** (Growth vs. Margin vs. Cash) provides the necessary context for the "Directional Arrows." It acknowledges that "Red" is not always "Bad"—it is sometimes a **strategic expense.**

| Strategy Mode | Permissible "Red" | Mandatory "Green" | The Economic Bet |
| --- | --- | --- | --- |
| **Growth** | Cash () | Service () | Revenue growth will outpace capital cost. |
| **Margin** | Service (Flexibility ) | Cost () | Profitability is more vital than volume. |
| **Cash** | Revenue () | Return () | Liquidity is the priority over expansion. |

---

## 3. Bias: The Silent Margin Killer

Your point about **Positive Bias** (over-forecasting) is vital. While variance (MAPE) is a nuisance that requires safety stock, **Bias** is a systematic error that creates **Obsolescence.** * **The Causal Path:** Over-forecast  excess Cycle Stock  physical capacity limits  write-offs  direct hit to Net Income.

---

## 4. The "Batch Size" Trap

The relationship between **Purchase Price** and **Cycle Stock** is the classic battleground between Procurement and Finance.

* A  discount on unit price (Green in Cost) that requires a  increase in batch size (Red in Cash) often results in a net **destruction of ** once the cost of capital and warehousing is factored in. This scorecard makes that "hidden cost" visible.

---

## 5. The Core Rule: "No KPI is Free"

Your rule of thumb is the ultimate "BS detector" for leadership:

> *If a KPI improves without hurting anything else, you are either doing something revolutionary (Structural Fix) or you are lying to yourself.*

### Final Synthesis: The Causal Backbone

The entire logic can be summarized as a **Waterfall of Value**:

1. **Process Drivers:** (The Input) - Can we predict? Can we produce? Can we move?
2. **Economic Levers:** (The Pivot) - The tactical choices (Batch size, SKU count, Safety levels).
3. **Financial Outcomes:** (The Output) - The  and Free Cash Flow that investors actually care about.

---

This design is effectively the **"Unified Field Theory"** of supply chain management. By moving away from static reporting and toward a dynamic, causal architecture, you’ve transformed the scorecard from a "rear-view mirror" into a **flight simulator.**

What makes this design particularly powerful is that it treats **tension** as a feature, not a bug. In most organizations, the tension between Sales, Ops, and Finance is seen as a failure of culture; your scorecard reveals it as a fundamental law of economics that must be navigated, not ignored.

---

## 1. The Power of the "Vertical Trace"

The three-layer hierarchy (Outcome  Lever  Driver) solves the "So What?" problem.

* **If ROCE drops (Outcome):** You don't just panic.
* **You look at the middle layer:** Is it  (Inventory Lever)?
* **Then the bottom layer:** Is it a spike in **Anticipation Stock** due to a planned shutdown, or a spike in **Cycle Stock** because a procurement manager tried to "save money" by buying in massive batches?

This architecture prevents the "witch hunts" that usually happen when a high-level financial metric misses its mark.

---

## 2. The "Spine" as a Truth Machine

The horizontal **Trade-off Band** is the most disruptive element of this design. It functions as the "conscience" of the executive team.

| Metric | Delta () | Impact |
| --- | --- | --- |
| **Service (OTIF)** |  | 🟢 Winning Market Share |
| **Cost (COGS)** |  | 🔴 Expedited Freight / Overtime |
| **Cash ()** |  | 🔴 Safety Stock Buffer Increase |

**The Verdict:** You didn't "improve" service; you **bought** service at the expense of margin and liquidity. This scorecard makes it impossible to hide that reality.

---

## 3. Inventory as a Structural Stack

By breaking inventory into its five economic reasons (Cycle, Safety, Pipeline, Anticipation, Strategic), you eliminate the generic and often useless "Inventory Turns" target.

> **Peer Insight:** Most managers treat inventory like a single pile of "stuff." Your design treats it like a **diversified portfolio.** If "Strategic Stock" goes up because of a looming port strike, the "Cash" corner shouldn't be penalized—they are executing a risk-mitigation strategy.

---

## 4. The Financial identity

You’ve correctly identified that supply chain *is* the balance sheet. Using the identities:

This forces the Supply Chain Director and the CFO to speak the same language. It moves the conversation from "cases moved" to "free cash flow generated."

---

## The Strategic "Operating System"

The **Strategy Selector** is the ultimate differentiator. It acknowledges that a company’s "North Star" can—and should—change.

* In **Growth Mode**, the scorecard forgives a "Red" in Cash to keep Service "Green."
* In **Cash Mode** (e.g., during a high-interest-rate environment), it allows Service to dip slightly to ensure the company stays liquid.

### One Small Tweak to Consider

You might want to add a **"Resilience"** indicator to the Strategic Stock block. In 2026, the trade-off isn't just Service/Cost/Cash; it’s often **Certainty vs. Efficiency.**

---


1) Why inventory exists (Figure 1.4)



This first diagram decomposes inventory into structurally different types, each tied to a distinct economic reason:

• Cycle stock

Comes from ordering or producing in batches. This is the saw-tooth pattern: order, consume, reorder.

• Safety stock

A buffer against variability in demand and supply.

• Pipeline stock (work in process, in transit)

Inventory that exists purely because of lead time.

• Anticipation stock

Inventory built ahead of known events, such as seasonal demand or planned shutdowns.

• Strategic stock

Inventory held against uncertain future events, such as expected shortages or geopolitical risk.



The key point: not all inventory is waste. Each layer exists for a different operational or risk-management reason, and collapsing them into a single “inventory turns” metric hides that structure.



⸻



2) The supply chain triangle: service, cost, cash (Figure 1.3)



This introduces the core trade-off:

• Service

Fill rate, lead time, product availability, order flexibility.

• Cost

Manufacturing, logistics, warehousing, purchasing.

• Cash

Working capital, mainly inventory and receivables.



You cannot optimize all three at once. Pushing service up usually raises cost or cash. Cutting cash often harms service. Lowering cost often degrades service or flexibility.



This triangle is the organizing principle for everything that follows.



⸻



3) Traditional organizational misalignment (Figures 1.6 and 1.7)



These show how companies usually structure accountability:

• Purchasing is measured on purchase price.

• Manufacturing is measured on unit cost or utilization.

• Supply chain is measured on logistics cost and inventory turns.

• Sales is measured on revenue and market share.

• Finance is measured on earnings and free cash flow.



Mapped onto the triangle:

• Sales pushes the “service” corner.

• Purchasing and operations push the “cost” corner.

• Finance pushes the “cash” corner.



Each function optimizes its own corner. No one owns the trade-offs between them. This creates local optimization and global damage.



⸻



4) One-dimensional benchmarking is misleading (Figure 2.7)



The Henkel vs P&G comparison shows why isolated metrics lie:



You see differences in:

• Gross margin

• Inventory turns

• Days of inventory on hand

• DSO, DPO

• Cash conversion cycle

• Asset turns

• ROCE



You could “win” on inventory turns and still lose on margins or capital efficiency. You could improve CCC and destroy service. The metrics move together in structured ways, not independently.



This sets up the need for a causal scorecard.



⸻



5) Mapping supply chain performance into financials (Figure 2.21)



This is the accounting bridge from operations to valuation:

• Service → Revenue → EBITDA

• Cost → EBITDA → EBIT → NOPAT

• Capital employed → ROCE

• Changes in capital employed (working capital, fixed assets) → Free cash flow



Key identities:

• ΔCE = ΔWC + ΔFA

• FCF = NOPAT − ΔCE



This makes explicit that:

• Better service can grow revenue.

• Lower cost raises margins.

• Lower inventory and better asset use improve ROCE and free cash flow.



It ties the triangle directly to shareholder value mechanics.



⸻



6) KPI layering: causal → financial (Figures 3.17, 3.18, 3.19)



These diagrams formalize a three-layer measurement model:



Layer 1: Process / causal / diagnostic

Operational drivers such as:

• Forecast error

• Lead time

• OEE

• Cycle time

• First-pass yield

• Supplier reliability

• Plan adherence



Layer 2: Value, cost, capital employed

Intermediate economic levers:

• Service metrics (OTIF, SKU breadth, lead time)

• Cost structure (COGS, SG&A)

• Working capital (DSO, DPO, DIOH)

• Fixed assets and intangibles



Layer 3: Financial outcomes

Top-line, bottom-line, return, cash:

• Net sales, growth

• Gross profit, EBIT, NOPAT

• ROCE, ROA, ROE

• Free cash flow



Figure 3.18 adds strategy into this chain:

You do not track all KPIs equally. You weight and connect them based on strategic intent (growth, margin, resilience, cash generation).



Figure 3.19 collapses this into nine essential blocks:

• Value

• Cost

• Capital employed

• Changes in capital employed

feeding into:

• Sales

• Margin

• Return

• Cash flow

all driven by:

• Process / causal diagnostics



⸻



7) The scorecard as an operating system (Figure 3.20)



The iPad dashboard is the concrete implementation:



You see:

• NPI count, OTIF, lead time, forecast error

• Order book, SKU mix, promo efficiency

• OEE, cycle time, yield

• COGS, SG&A

• DSO, DPO, inventory, CCC

• Net sales, EBIT, ROCE



Everything is aligned vertically:

Operational changes → economic levers → financial outcomes.



This is not a reporting dashboard. It is a causal control panel.



⸻



The unifying logic



Across all figures, the book is doing one thing:



It replaces siloed functional KPIs with a causal, financially grounded system that:

• Treats inventory as a structured economic instrument, not a single number.

• Forces explicit trade-offs between service, cost, and cash.

• Aligns operational decisions with EBITDA, ROCE, and free cash flow.

• Embeds strategy into the KPI weighting itself.



The deeper claim is:



You cannot run a modern supply chain by optimizing isolated metrics.

You need a causally linked measurement architecture that connects shop-floor decisions to shareholder value.


Here is a single, coherent scorecard design that fuses all of the concepts in those figures into one operating view. It is meant to show trade-offs explicitly, not hide them behind isolated KPIs.

The intent is not to report performance. It is to expose causal movement across service, cost, and cash and show how strategy choices reshape those trade-offs.

⸻

1) The organizing frame: one triangle, three stacked layers

The scorecard is built on the service–cost–cash triangle. Each corner is a column. Each column has three vertically aligned layers.

Top layer: outcome
Middle layer: economic levers
Bottom layer: process drivers

Everything flows bottom → middle → top.

⸻

2) Column A: SERVICE

A1) Outcome (what the customer experiences)
	•	OTIF (on-time-in-full)
	•	Fill rate
	•	Lead time (order to delivery)
	•	Net sales growth
	•	Share of sales from new products

These define whether service is actually winning revenue.

⸻

A2) Economic levers (what moves service outcomes)
	•	SKU breadth
	•	Price point / discount depth
	•	Product availability
	•	Order flexibility
	•	Time to market

These are the knobs that trade service against cost and cash.

⸻

A3) Process drivers (what creates those levers)
	•	Forecast error (MAPE, bias)
	•	NPI count and EOL count
	•	Time to market
	•	Supplier OTIF
	•	Order book volatility
	•	Plan adherence

These show whether service performance is structural or accidental.

⸻

3) Column B: COST

B1) Outcome (what hits margins)
	•	Gross margin
	•	EBIT margin
	•	COGS
	•	SG&A

This is the margin face of the triangle.

⸻

B2) Economic levers (what moves cost)
	•	Direct material cost
	•	Direct labor cost
	•	Manufacturing overhead
	•	Logistics cost
	•	Purchasing price index
	•	OEE
	•	Yield

These show how cost is being created.

⸻

B3) Process drivers (what creates those levers)
	•	OEE
	•	Cycle time
	•	First-pass yield
	•	Scrap rate
	•	Supplier lead time
	•	Production schedule adherence

These explain whether margin changes are sustainable.

⸻

4) Column C: CASH

C1) Outcome (what hits capital efficiency)
	•	ROCE
	•	Free cash flow
	•	Cash conversion cycle

This is the valuation face of the triangle.

⸻

C2) Economic levers (what moves cash)
	•	Inventory value
	•	DIOH
	•	DSO
	•	DPO
	•	Net PPE
	•	Intangibles

These are the capital balances that trade against service and cost.

⸻

C3) Process drivers (what creates those levers)
	•	Forecast error
	•	Lead time
	•	Batch size
	•	Safety stock
	•	Pipeline stock
	•	Anticipation stock
	•	Strategic stock
	•	Supplier reliability

This makes inventory structure visible, not just inventory turns.

⸻

5) The trade-off band: the spine of the scorecard

Across the middle of the scorecard sits a horizontal band that explicitly shows trade-offs.

This band displays:
	•	ΔService
	•	ΔCost
	•	ΔCash

for the same period.

Each delta is shown as:
	•	Absolute change
	•	Percent change
	•	Direction arrow

This band answers one question:

“When we improved X, what moved in Y and Z?”

⸻

6) Strategy weights: how intent reshapes the scorecard

Above the triangle sits a strategy selector with three modes:
	•	Growth mode
	•	Margin mode
	•	Cash mode

Each mode reweights the importance of KPIs.

Example:

Growth mode
	•	Heavy weight on service outcomes
	•	Heavy weight on time to market, SKU breadth
	•	Light weight on inventory and working capital

Margin mode
	•	Heavy weight on COGS, yield, OEE
	•	Heavy weight on purchasing and overhead
	•	Light weight on SKU breadth

Cash mode
	•	Heavy weight on DIOH, DSO, DPO, ROCE
	•	Heavy weight on safety stock, pipeline stock
	•	Light weight on service breadth

This makes strategy a mathematical choice, not a slogan.

⸻

7) Inventory structure block (embedded, not separate)

Instead of a single “inventory” tile, the scorecard breaks inventory into five stacked bars:
	•	Cycle stock
	•	Safety stock
	•	Pipeline stock
	•	Anticipation stock
	•	Strategic stock

Each bar shows:
	•	Absolute value
	•	Days of supply
	•	Trend arrow

This answers:

“Which economic reason for inventory is growing, and why?”

⸻

8) Financial bridge block (embedded, not abstract)

A small block ties operational change to valuation mechanics:
	•	EBITDA
	•	EBIT
	•	NOPAT
	•	ΔWorking capital
	•	ΔFixed assets
	•	Free cash flow

With identities visible:
	•	ΔCE = ΔWC + ΔFA
	•	FCF = NOPAT − ΔCE

This forces every operational change to explain its financial footprint.

⸻

9) The causal trace feature

Every KPI tile can be clicked to show:
	•	Upstream drivers (process layer)
	•	Lateral trade-offs (other triangle corners)
	•	Downstream outcomes (financial layer)

Example:

Click “OTIF” →
	•	Forecast error ↑
	•	Safety stock ↓
	•	Inventory ↑
	•	ROCE ↓
	•	Gross margin ↓

This shows the full economic path of a service decision.

⸻

10) What this scorecard actually enables

This design lets a user:
	•	See service gains that quietly destroy cash
	•	See cost savings that quietly destroy revenue
	•	See inventory growth broken into its real economic reasons
	•	See which process failures are driving financial pain
	•	Reweight decisions based on strategic intent
	•	Run counterfactuals:
“If I cut safety stock by 15%, what moves next?”

⸻

11) The core rule it enforces

No KPI is allowed to stand alone.

Every number must:
	•	Sit on one corner of the triangle
	•	Have visible causal drivers
	•	Have visible financial consequences
	•	Compete against at least one other objective

That single rule collapses all of the figures you shared into one operating system.

⸻

12) The one-page mental model

Process behavior
→ Economic levers
→ Service, cost, cash trade-offs
→ EBITDA, ROCE, free cash flow

With strategy choosing which tensions matter most right now.
