---
name: reporting-skill
description: >
  Build interactive dashboards, reports, and data visualizations from Attio CRM data.
  Use this skill whenever the user asks for reports, dashboards, analytics, metrics,
  KPIs, charts, or data visualizations based on their Attio CRM data. Also trigger
  when the user mentions pipeline reports, deal analytics, sales performance,
  activity summaries, contact breakdowns, conversion metrics, or wants to see
  "how things are going" in their CRM. Even casual requests like "show me my
  pipeline" or "how are deals looking" or "give me a sales report" should trigger
  this skill. Covers on-demand reports, scheduled recurring reports, and
  auto-refreshing dashboards.
---

# Attio Dashboard & Reports

You are building dashboards and reports from Attio CRM data. Your job is to pull data using the Attio MCP tools, then produce polished interactive HTML dashboards with charts, KPI cards, and data tables — plus optional export to PDF or XLSX.

## How This Skill Works

The workflow has three phases: **understand**, **pull**, **build**.

1. **Understand** what the user wants — which data, what visualizations, what delivery mode
2. **Pull** the data from Attio using MCP tools
3. **Build** an interactive HTML dashboard and save it for the user

## Step 1: Understand the Request

Before pulling any data, clarify what the user needs. Ask them (using the AskUserQuestion tool) about:

### Delivery Mode
Every time the user requests a report, ask how they want it delivered:

- **On-demand** — Pull fresh data right now, build the dashboard, done
- **Scheduled** — Set up a recurring task (daily, weekly, etc.) that auto-generates the report using the `schedule` skill
- **Auto-refreshing** — Build an HTML dashboard that re-fetches data on a timer (uses JavaScript fetch calls to keep data current)

If the user's intent is clearly on-demand (e.g., "show me my pipeline"), skip the question and just build it.

### Template or Custom
Check if the user wants one of the pre-built templates or a custom report. Read `references/templates.md` for the available templates and what data they need.

If the user asks for something like "pipeline overview" or "sales report", match it to a template and confirm. For anything that doesn't match a template, build custom.

### Data Scope
Understand what Attio objects/lists they want to report on. Common patterns:

- **Pipeline/deals**: Use `list-records-in-list`, `run-basic-report` for aggregations
- **Companies**: Use `list-records` with filters, `run-basic-report` for grouping
- **People/contacts**: Use `list-records`, `search-records` for lookups
- **Lists**: Use `list-lists` to discover, then `list-records-in-list` for entries
- **Custom objects**: Use `list-attribute-definitions` to discover fields first

## Step 2: Pull Data from Attio

Use the Attio MCP tools to pull data. Here's how to approach it:

### Discovering What's Available
If you're not sure what data exists, start with discovery:
- `list-lists` — see all lists/pipelines in the workspace
- `list-attribute-definitions` — see what fields exist on an object
- `list-list-attribute-definitions` — see what fields exist on a list

### Pulling Records
- `list-records` — get records from an object (companies, people, etc.) with filters and sorting
- `list-records-in-list` — get entries from a list/pipeline with filters
- `search-records` — full-text search across records
- `get-records-by-ids` — fetch specific records by ID

### Aggregations and Reports
- `run-basic-report` — the most powerful tool for dashboards. Use it for counts, sums, averages, groupings. It supports:
  - Count of records by group (e.g., deals by stage)
  - Sum/average of numeric fields (e.g., total deal value)
  - Up to two levels of grouping (e.g., deals by stage, then by owner)

### Pagination
Most Attio tools return paginated results (default 10, max 50). For full datasets, loop with `offset` parameter until you have everything. For large datasets, consider whether you actually need all records or if aggregations via `run-basic-report` would be more efficient.

### Data Transformation
After pulling raw data, transform it into a clean structure for the dashboard:
- Extract the values you need from Attio's nested response format
- Normalize dates, currency values, and names
- Group and aggregate as needed
- Store the transformed data as a JSON object that the dashboard HTML will consume

## Step 3: Build the Dashboard

Create a single-file HTML dashboard that includes everything inline (CSS, JavaScript, data). The dashboard should be self-contained so it works when opened directly in a browser.

### Architecture

```html
<!DOCTYPE html>
<html>
<head>
  <title>[Report Title] — Attio Dashboard</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
  <style>/* All styles inline */</style>
</head>
<body>
  <!-- KPI cards at top -->
  <!-- Charts in the middle -->
  <!-- Data tables at bottom -->
  <script>
    const DATA = { /* embedded JSON data from Attio */ };
    // Render charts, populate tables, wire up interactions
  </script>
</body>
</html>
```

### Design Principles

**Layout**: Use a clean, professional layout with a dark header bar, KPI cards in a row at the top, charts in a responsive grid, and data tables below. Think "executive dashboard" — scannable, not cluttered.

**Color Palette**: Use a cohesive color scheme. A good default:
- Primary: `#4F46E5` (indigo)
- Success: `#10B981` (green)
- Warning: `#F59E0B` (amber)
- Danger: `#EF4444` (red)
- Background: `#F9FAFB`
- Card background: `#FFFFFF`
- Text: `#111827`
- Muted text: `#6B7280`

**Typography**: Use system fonts (`-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`). Keep it readable — 14px base, 24-32px for KPI numbers, 16-18px for section headers.

### KPI Cards
Always include a row of KPI summary cards at the top. Each card should have:
- A label (e.g., "Total Pipeline Value")
- A big number (e.g., "$1.2M")
- Optional trend indicator or comparison (e.g., "+12% vs last month")

Format numbers nicely — use `$1.2M` not `$1,234,567`, use `1,234` not `1234`.

### Charts (using Chart.js)
Use Chart.js (loaded from CDN) for all visualizations. Common chart types:

- **Bar chart**: Stage distribution, deal counts by owner, records by category
- **Doughnut/Pie**: Proportional breakdowns (win/loss, by industry)
- **Line chart**: Trends over time (deals created per month, pipeline growth)
- **Horizontal bar**: Ranking/comparison (top companies by deal value)
- **Stacked bar**: Multi-dimensional comparison (deals by stage per month)

Tips for good Chart.js usage:
- Always include `responsive: true` and `maintainAspectRatio: false` in options
- Set explicit height on chart containers (e.g., `height: 300px`)
- Use `plugins.legend.position: 'bottom'` for cleaner layouts
- Format tooltips with currency/percentage symbols where appropriate
- Use `Chart.defaults.font.family` to match the dashboard typography

### Data Tables
Include sortable data tables for detail-level data. Each table should have:
- Column headers with click-to-sort functionality
- Formatted values (dates, currency, status badges)
- Alternating row colors for readability
- A row count indicator

Implement sorting in vanilla JS — no need for external libraries. Status/stage values should render as colored badges.

### Interactivity
Add useful interactive features:
- **Filters**: Dropdown filters for common dimensions (owner, stage, date range)
- **Click-to-sort** on table columns
- **Hover tooltips** on charts (Chart.js handles this)
- **Responsive layout** that works on different screen sizes
- **Print-friendly** styles via `@media print`

### Export Functionality
Include export buttons in the dashboard header:

**Export to PDF**: Add a "Download PDF" button that uses the browser's `window.print()` with print-optimized CSS. Include a `@media print` stylesheet that removes interactive elements, adjusts layout for paper, and ensures charts render properly.

**Export to CSV/XLSX**: Add a "Download Data" button that exports the underlying data as CSV. Use a simple JS function that converts the data array to CSV format and triggers a download via Blob URL. If the user specifically asks for XLSX, use the `xlsx` skill to create a proper Excel file separately.

## Delivery Modes

### On-Demand (default)
Pull data, build the dashboard, save to workspace folder, give the user a link. This is the simplest mode and should be the default unless the user specifies otherwise.

### Scheduled Reports
If the user wants recurring reports, use the `schedule` skill to create a scheduled task. The task prompt should instruct Claude to:
1. Read this skill (reporting-skill)
2. Pull the specified data from Attio
3. Build the dashboard
4. Save it with a timestamped filename

Tell the user you'll be using the schedule skill and help them set the frequency.

### Auto-Refreshing Dashboard
For live dashboards, build the HTML with a JavaScript refresh mechanism:
- Embed the Attio data as the initial state
- Add a "Last updated" timestamp
- Include a "Refresh" button that the user can click to trigger a new data pull
- Note: truly auto-refreshing dashboards that call Attio APIs directly from the browser aren't possible since the MCP tools run server-side. Instead, explain this limitation and suggest the scheduled approach for regular updates, with the refresh button for manual updates.

## File Naming and Output

Save all dashboards to the workspace folder with descriptive names:
- `pipeline-dashboard.html` — for pipeline/deal reports
- `sales-performance-report.html` — for sales reports
- `[custom-name]-report.html` — for custom reports

Always provide the user with a clickable link to the file using the `computer://` protocol.

## Common Patterns and Tips

### Handling Empty Data
If a query returns no results, don't show a blank dashboard. Show a friendly "No data found" message with suggestions (e.g., "Try adjusting the date range or check that records exist in this pipeline").

### Large Datasets
For lists with hundreds of entries, use `run-basic-report` for aggregations instead of pulling every record. Only pull individual records when the user needs a detail table.

### Date Ranges
When the user asks for "this month" or "last quarter", calculate the actual date boundaries. Use today's date from the system context. Format dates consistently as `YYYY-MM-DD` for Attio filters.

### Multiple Data Sources
Some reports combine data from multiple Attio objects (e.g., deals + companies). Pull each data source separately, then join them in your data transformation step before building the dashboard.
