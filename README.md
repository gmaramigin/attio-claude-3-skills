# Attio Claude Skills

A collection of Claude skills for automating and enhancing your [Attio CRM](https://attio.com) workflows — from cleaning duplicate records, to enriching company data, to building instant sales dashboards.

Each skill is a self-contained folder you can install into Claude Desktop (or Cowork) and invoke with plain English.

---

## Skills in This Repo

### 🔍 [attio-dedup-audit-skill](./attio-dedup-audit-skill)

**Detect and resolve duplicate records in Attio CRM.**

Finds duplicate People, Companies, custom objects, and list entries using configurable matching rules (AND/OR logic, fuzzy matching). Shows you a full report of what it found and what it plans to merge — then waits for your approval before touching anything.

Works in **API mode** (via Attio MCP) or **browser mode** (via Chrome, for full merge + delete in one step).

**Say things like:**
> "Find duplicate people in my Attio CRM, match by email and name."
> "Clean up duplicate companies, match by domain OR company name."
> "Deduplicate entries in my sales pipeline list."

→ [Full docs](./attio-dedup-audit-skill/README.md)

---

### 📊 [reporting-skill](./reporting-skill)

**Build interactive dashboards and reports from Attio data.**

Pulls live data from your Attio workspace and produces self-contained HTML dashboards with KPI cards, Chart.js charts, and sortable tables. Includes pre-built templates for pipeline overviews, sales performance, activity summaries, and company breakdowns. Supports on-demand generation, scheduled recurring reports, and manual refresh.

**Say things like:**
> "Show me my pipeline."
> "Give me a sales performance report for this month."
> "Schedule a weekly pipeline report every Monday morning."

→ [Full docs](./reporting-skill/README.md)

---

### 🔗 [attio-databar-enrichment](./attio-databar-enrichment)

**Enrich Attio CRM records using Databar's network of 90+ data providers.**

Fills in missing firmographic and contact data — industry, employee count, revenue, LinkedIn profiles, work emails, phone numbers — by running waterfall enrichments across providers like Diffbot, People Data Labs, Hunter.io, and more. Works on single records or entire Attio lists. Never overwrites data that's already there.

**Say things like:**
> "Enrich Stripe in my Attio."
> "Find emails for everyone in my leads list."
> "Enrich all companies missing their industry field."

→ [Full docs](./attio-databar-enrichment/README.md)

---

## Prerequisites

All three skills require an **Attio MCP server** connected to Claude. Any Attio MCP integration works — just make sure your access token has read/write permissions on Records, List entries, and Notes.

The **Databar enrichment skill** additionally requires a [Databar](https://databar.ai) account and their MCP server:

```json
{
  "mcpServers": {
    "databar": {
      "command": "npx",
      "args": ["-y", "databar-mcp-server"],
      "env": {
        "DATABAR_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

---

## Installation

### Option A: Skill files (recommended)

Download the `.skill` file for each skill and double-click it (or drag it into Claude Desktop). It installs automatically.

### Option B: Manual

Copy the skill folder into your Claude skills directory:

- **macOS**: `~/Library/Application Support/Claude/skills/`
- **Windows**: `%APPDATA%\Claude\skills\`

---

## License

MIT — use freely, fork freely, build on top freely.
