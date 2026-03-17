# Attio Dashboard & Reports Skill

A Claude skill for building interactive dashboards, reports, and data visualizations from your [Attio CRM](https://attio.com) data — on demand, on a schedule, or as auto-refreshing HTML dashboards.

## What It Does

This skill pulls live data from Attio via MCP and produces polished, single-file HTML dashboards with KPI cards, Chart.js visualizations, and sortable data tables. No external BI tools needed — everything opens directly in your browser.

Just say things like:
- "Show me my pipeline"
- "Give me a sales performance report for this month"
- "Build a dashboard for company activity this week"
- "Schedule a weekly pipeline report every Monday"

## Pre-built Templates

| Template | Trigger Phrases | What You Get |
|---|---|---|
| **Pipeline Overview** | "show me my pipeline", "pipeline report" | Deal count/value by stage, by owner, full deals table |
| **Sales Performance** | "sales report", "how are sales" | Won/lost deals, revenue by owner, monthly trend |
| **Activity Summary** | "activity summary", "what's been happening" | New records, updated deals, recent activity log |
| **Company Overview** | "company report", "show me companies" | Companies by industry, location, directory table |

Anything that doesn't match a template gets built as a custom dashboard — just describe what you want.

## Prerequisites

You need an **Attio MCP server** connected to Claude with read access to your workspace. Any Attio MCP integration works — the skill uses these tools:

- `list-lists` / `list-records-in-list` — for pipeline and list data
- `list-records` — for companies and people
- `run-basic-report` — for aggregations and groupings
- `list-attribute-definitions` — for schema discovery

## Installation

### Option A: Install the skill file

Download `reporting-skill.skill` and double-click it, or drag it into Claude Desktop.

### Option B: Manual installation

Copy the `reporting-skill/` folder into your Claude skills directory:

- **macOS**: `~/Library/Application Support/Claude/skills/`
- **Windows**: `%APPDATA%\Claude\skills\`

## Delivery Modes

**On-demand** — Pull fresh data right now and generate the dashboard immediately. The default.

**Scheduled** — Set up a recurring report (daily, weekly, etc.) that auto-generates on a timer and saves with a timestamped filename.

**Manual refresh** — The dashboard includes a "Refresh" button you can click to trigger a new data pull at any time.

## Dashboard Features

Every dashboard includes:
- **KPI summary cards** at the top with formatted numbers
- **Interactive charts** (bar, line, doughnut, horizontal bar) via Chart.js
- **Sortable data tables** with status badges and formatted values
- **Filter dropdowns** for common dimensions (stage, owner, date range)
- **Export to PDF** via browser print
- **Export to CSV** for the underlying data

## File Structure

```
reporting-skill/
├── SKILL.md              # Main skill instructions for Claude
├── README.md             # This file
└── references/
    └── templates.md      # Pre-built dashboard templates
```

## License

MIT
