PLAYBOOK_SYSTEM = """You are an expert IT Integration Director for M&A (Day-1 to Day-100).
Produce crisp, actionable plans with risks, owners, dependencies, and milestones.
Return Markdown only with clear headings and tables where useful."""

PLAYBOOK_USER = """Create an IT Integration Playbook for:

- Company name: {company_name}
- Company size: {company_size}
- Key systems: {key_systems}
- Day 1 priorities: {day1_priority}
- Integration approach: {integration_approach}
- Timeline: {timeline}

Deliverables:
1) Executive summary (bullets)
2) Workstreams & scope
3) Day-1 controls checklist
4) Integration waves with milestones (table)
5) Risks & mitigations (table)
6) Dependency map (apps/interfaces; bullets)
7) KPI dashboard (bullets)
8) 30/60/90 plan (table)
"""

INVOICE_JSON_INSTRUCTIONS = """Extract structured invoice fields as JSON:
{{
  "invoice_number": "...",
  "invoice_date": "...",
  "supplier_name": "...",
  "supplier_tax_id": null,
  "currency": "...",
  "subtotal": null,
  "tax": null,
  "total": null,
  "line_items": [
    {{"description":"...","quantity":null,"unit_price":null,"amount":null,"gl_hint":null}}
  ],
  "payment_terms": null,
  "po_number": null
}}
Only return valid JSON, no commentary.
"""

READINESS_SCORE_INSTRUCTIONS = """Score migration readiness 0-100 based on: data quality, completeness,
PII/Regulatory risk, interface complexity, downtime tolerance, and team readiness.
Return a short Markdown report with a table per source system and a final risk heat.
"""

PLAYBOOK_DETAILED_USER = """
You are an M&A IT Integration Director.
Create a detailed Integration Playbook for EACH application listed below.

For every application, produce:

### {app_name}
1. **Application Overview**
   - Business owner / module
   - Current landscape and purpose
   - Upstream / downstream dependencies

2. **Integration Strategy**
   - Approach (retain / migrate / retire / interface)
   - Key integration tasks (ordered)
   - Tools or middleware involved

3. **Data Migration / Cutover Plan**
   - Data to be migrated (entities/volumes)
   - Validation & reconciliation steps
   - Cutover window, rollback plan

4. **Risk & Mitigation**
   - Top 3 risks
   - Mitigation actions

5. **Wave & Timeline**
   - Suggested wave (Day-1, Day-30, Day-60, etc.)
   - Resource estimate (FTE weeks)

6. **Gantt Chart**
   - Produce a detailed Gantt chart for integration timelines for a 100 day period with all the key phases on the chart

At the end, produce a **Summary Table** with columns:
Application | Strategy | Wave | Owner | Risk Level.

### 🛠️ Recommendations
Provide actionable suggestions for each application in a bulleted format that contains:
- Which applications to consolidate or prioritize for retirement
- Any short-term vs long-term integration considerations
- Other insights based on the overall portfolio
- Which apps should be retained and migrated?
- Which areas need further investigation before Day 1?
- Mention any compliance, cost-efficiency, or user-experience considerations.

Context:
- Company: {company_name} ({company_size})
- Integration approach: {integration_approach}
- Overall timeline: {timeline}

Applications to cover (one section per app, keep sections concise but specific):
{applications}
"""
