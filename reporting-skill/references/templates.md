# Dashboard Templates

Pre-built report templates that users can request by name. Each template defines what data to pull from Attio and how to visualize it.

## Pipeline Overview

**Trigger phrases**: "pipeline overview", "pipeline report", "show me my pipeline", "deal pipeline", "how's the pipeline"

**Data to pull**:
- All entries from the primary deals/pipeline list (`list-records-in-list`)
- Aggregate deal count and value by stage (`run-basic-report` with group_by stage)
- Aggregate deal count by owner (`run-basic-report` with group_by owner)

**Visualizations**:
- KPI cards: Total deals, Total pipeline value, Average deal size, Win rate
- Funnel or horizontal bar chart: Deals by stage
- Doughnut chart: Pipeline value by stage
- Bar chart: Deals by owner
- Data table: All deals with name, company, stage, value, owner, created date

---

## Sales Performance

**Trigger phrases**: "sales performance", "sales report", "how are sales", "revenue report", "sales dashboard"

**Data to pull**:
- Deals won in current period (`list-records-in-list` filtered by stage = Won/Closed Won)
- Deals lost in current period
- Deal value aggregations by owner (`run-basic-report`)
- Deal count by month/week for trend (`run-basic-report` with time grouping)

**Visualizations**:
- KPI cards: Total won value, Deals won, Deals lost, Win rate, Average deal cycle
- Bar chart: Won revenue by owner
- Line chart: Deals won over time (monthly trend)
- Pie chart: Win/Loss/Open ratio
- Data table: Recent closed deals with outcome, value, owner, duration

---

## Activity Summary

**Trigger phrases**: "activity summary", "activity report", "what's been happening", "team activity", "CRM activity"

**Data to pull**:
- Recently created records (companies, people) via timeframe filtering
- Recently updated deals/pipeline entries
- Record counts by object type (`run-basic-report` with count)

**Visualizations**:
- KPI cards: New companies this week, New contacts this week, Deals updated, Active pipeline value
- Bar chart: New records by day/week
- Data table: Recent activity log (newest first)

---

## Company Overview

**Trigger phrases**: "company report", "company breakdown", "company analytics", "show me companies"

**Data to pull**:
- All companies or filtered subset (`list-records`)
- Company counts by industry/category (`run-basic-report` with group_by)
- Company counts by location if available

**Visualizations**:
- KPI cards: Total companies, New this month, By top industry
- Bar chart: Companies by industry/category
- Map or bar chart: Companies by location (if data available)
- Data table: Company directory with name, domain, industry, employee count

---

## Custom Report

If the user's request doesn't match any template, build a custom dashboard. Follow this process:

1. Ask what Attio objects/lists they want to report on
2. Discover available attributes with `list-attribute-definitions`
3. Ask which metrics and groupings matter
4. Pull the data
5. Build visualizations that best fit the data shape:
   - Categorical data → bar chart or pie chart
   - Time series → line chart
   - Rankings → horizontal bar chart
   - Proportions → doughnut chart
   - Detail data → sortable table
