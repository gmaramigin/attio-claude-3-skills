---
name: attio-databar-enrichment
description: >
  Enrich Attio CRM records (companies and people) using Databar's unified enrichment API. Supports
  single-record enrichment, bulk enrichment of Attio lists/filters, waterfall enrichment across 90+
  data providers, and auto-discovery of Attio field mappings. Use this skill whenever the user
  mentions "enrich", "enrichment", "Databar", "fill in missing data", "find emails", "find phone
  numbers", "company data", "firmographic data", or wants to augment their Attio CRM with external
  data. Also trigger when the user asks to "look up company info", "get employee count", "find
  LinkedIn profiles", "enrich my CRM", "enrich contacts", "bulk enrich", or mentions enriching
  records that are missing fields like industry, revenue, description, or social links. Even casual
  requests like "what do we know about this company?" or "can you fill in the blanks on these leads?"
  should trigger this skill.
---

# Attio + Databar Enrichment Skill

You are running an enrichment workflow that pulls data from Databar (an aggregation layer connecting 90+ data providers) and writes it into Attio CRM. This skill handles both company and person enrichment, individually or in bulk.

## Tools Available

This skill uses two sets of MCP tools:

**Databar MCP tools** (for enrichment):
- `mcp__databar__get_user_balance` — check credit balance
- `mcp__databar__search_enrichments` — discover enrichments by keyword
- `mcp__databar__get_enrichment_details` — get params/response fields for an enrichment
- `mcp__databar__run_enrichment` — run a single enrichment
- `mcp__databar__run_bulk_enrichment` — run enrichment on multiple inputs
- `mcp__databar__search_waterfalls` — discover waterfall enrichments
- `mcp__databar__run_waterfall` — run a waterfall (tries multiple providers)
- `mcp__databar__run_bulk_waterfall` — run waterfall on multiple inputs

**Attio MCP tools** (for CRM read/write):
- `mcp__attio-mcp__discover_record_attributes` — discover schema
- `mcp__attio-mcp__search_records` — find records
- `mcp__attio-mcp__get_record_details` — get full record data
- `mcp__attio-mcp__update_record` — write enrichment data back
- `mcp__attio-mcp__create_record` — create new records
- `mcp__attio-mcp__get_record_attribute_options` — get valid select/status values

At the start of every run, verify both Databar and Attio MCP tools are available. If Databar MCP tools are missing, fall back to the Python SDK approach (see `scripts/enrich.py`).

## How Databar Works

Databar is an aggregation layer — one API, 90+ data providers. There are two main ways to enrich:

**Individual enrichments** — Call a specific provider's endpoint by ID. Use `search_enrichments` to find the right one, `get_enrichment_details` to see its params and pricing, then `run_enrichment` to execute.

**Waterfall enrichments** — Try multiple providers in sequence until data is found. This maximizes match rates. Use `search_waterfalls` to discover them, then `run_waterfall` to execute. Available waterfalls:

| Identifier | Name | Input Params | Output |
|---|---|---|---|
| `company_lookup` | Lookup company data | `company_website` | name, description, LinkedIn, employees, industries, revenue, funding |
| `email_getter` | Email by name waterfall | `first_name`, `last_name`, `company` | email |
| `person_getter` | Reverse email lookup | `email` | first_name, last_name, linkedin_url |
| `person_by_link` | Email by link waterfall | `link` (LinkedIn URL) | first_name, last_name, work_email, personal_email |
| `phone_getter` | Phone waterfall | `linkedin` (LinkedIn URL) | phone |
| `job_postings_getter` | Job postings by company | `company_website` | jobs, job_links, descriptions, locations |

**Always prefer waterfalls** over individual enrichments — they try multiple providers automatically and give the best coverage.

## The Enrichment Workflow

### Step 1: Check Balance & Discover Attio Schema

Before enriching anything:

1. Check the Databar credit balance:
```
mcp__databar__get_user_balance()
```

2. Discover what fields exist in the user's Attio workspace:
```
mcp__attio-mcp__discover_record_attributes(resource_type="companies")
mcp__attio-mcp__discover_record_attributes(resource_type="people")
```

This tells you what fields are available to write to. Pay attention to field types (text, number, select, etc.) — you need to match Databar's output to the right format.

### Step 2: Identify Records to Enrich

**Single record:** The user names a specific company or person. Search Attio to find the record:
```
mcp__attio-mcp__search_records(resource_type="companies", query="Stripe")
```
Then fetch its current data with `get_record_details` to see what's already filled in vs. what's missing.

**Bulk enrichment by filter:** The user wants to enrich records matching criteria (e.g., "all companies missing industry"). Use `search_records` with filters:
```
mcp__attio-mcp__search_records(resource_type="companies", filters={
  "filters": [{"attribute": {"slug": "industry"}, "condition": "is_empty", "value": true}]
}, limit=100)
```

**Bulk enrichment by list:** The user references an Attio list. Use `get-list-entries` or `filter-list-entries` to get the records.

For bulk operations, process records one at a time or in small batches. Report progress as you go — "Enriched 5/23 companies so far..."

### Step 3: Call Databar for Enrichment Data

**For companies**, the primary input is the company's domain/website. Extract this from the Attio record (look for `domain`, `website`, or parse it from the company URL). Use the `company_lookup` waterfall:

```
mcp__databar__run_waterfall(
  waterfall_identifier="company_lookup",
  params={"company_website": "stripe.com"}
)
```

The result contains `enrichment_data` keyed by provider name (e.g., Diffbot, Owler). Extract and merge the data — prefer the first provider that returned results (it's the highest priority).

**For people**, choose the right waterfall based on what data you already have:

- Have email → `person_getter` waterfall:
  ```
  mcp__databar__run_waterfall(waterfall_identifier="person_getter", params={"email": "patrick@stripe.com"})
  ```

- Have LinkedIn URL → `person_by_link` waterfall:
  ```
  mcp__databar__run_waterfall(waterfall_identifier="person_by_link", params={"link": "https://linkedin.com/in/patrickcollison"})
  ```

- Have name + company → `email_getter` waterfall:
  ```
  mcp__databar__run_waterfall(waterfall_identifier="email_getter", params={"first_name": "Patrick", "last_name": "Collison", "company": "stripe.com"})
  ```

- Need phone → `phone_getter` waterfall (needs LinkedIn URL):
  ```
  mcp__databar__run_waterfall(waterfall_identifier="phone_getter", params={"linkedin": "https://linkedin.com/in/patrickcollison"})
  ```

**For bulk operations**, use the bulk variants:
```
mcp__databar__run_bulk_waterfall(
  waterfall_identifier="company_lookup",
  params_list=[
    {"company_website": "stripe.com"},
    {"company_website": "notion.so"},
    {"company_website": "figma.com"}
  ]
)
```

### Step 4: Map and Write Back to Attio

Read `references/field-mapping.md` for the detailed mapping between Databar response fields and common Attio attributes. The mapping is a starting point — always check what the user's actual Attio schema looks like via `discover_record_attributes` and adapt accordingly.

Use `update_record` to write enrichment data back:
```
mcp__attio-mcp__update_record(resource_type="companies", record_id="...", record_data={
  "description": "enriched description here",
  "employee_count": 8500,
  ...
})
```

**Important rules for writing back:**
- Never overwrite data that's already present unless the user explicitly asks you to. Only fill in empty/missing fields by default.
- For select/status fields, check valid options first with `get_record_attribute_options` before writing.
- If Databar returns data that doesn't map to any existing Attio field, mention it to the user — they might want to create a custom field for it.
- After writing, confirm what was updated: "Updated Stripe with: description, employee count (8,500), industry (Financial Services), LinkedIn URL."

### Step 5: Report Results

After enrichment completes, provide a clear summary:
- How many records were enriched
- What fields were filled in
- Any records that couldn't be enriched (and why — no domain found, provider returned no data, etc.)
- Databar credits consumed (check balance before and after with `get_user_balance`)
- Any fields returned by Databar that couldn't be mapped to Attio

For bulk enrichment, create a summary table showing each record and what was updated.

## Choosing the Right Enrichment

When the user's request is ambiguous, use this decision tree:

1. **"Enrich this company"** → `company_lookup` waterfall with the company's domain
2. **"Find someone's email"** → `email_getter` waterfall (needs name + company) or `person_by_link` (needs LinkedIn URL)
3. **"Look up this person"** → `person_getter` waterfall if you have email, `person_by_link` if you have LinkedIn
4. **"Get phone numbers"** → `phone_getter` waterfall (needs LinkedIn URL)
5. **"What jobs are open at X?"** → `job_postings_getter` waterfall
6. **"Enrich everything"** → Start with `company_lookup` for all companies, then use results to feed person enrichments

For specialized needs beyond waterfalls (tech stack, competitors, funding details, SEO data), search for specific enrichments:
```
mcp__databar__search_enrichments(query="tech stack", category="company")
# Review results, pick the right one, then:
mcp__databar__run_enrichment(enrichment_id=977, params={"domain": "stripe.com"})
```

## Error Handling

- **Insufficient credits**: Always check `get_user_balance` before bulk operations. Warn the user if balance is low. Each waterfall call costs roughly $3-15 depending on which providers fire.
- **No data found**: Some companies/people simply aren't in any provider's database. Report these clearly — don't treat them as errors.
- **Rate limits**: The Databar MCP handles retries automatically. For very large bulk operations (100+ records), process in batches of 10-20.
- **Auth errors on specific enrichments**: Some enrichments require the user's own API key for the underlying provider (marked as `auth_method: "user"`). Waterfalls generally use Databar's network keys and work out of the box.

## Cost Awareness

Always be transparent about costs. Before running bulk enrichment:
1. Check the user's credit balance with `get_user_balance`
2. Estimate the cost: number of records × approximate cost per waterfall call
3. Tell the user: "This will enrich ~50 companies using the company lookup waterfall. Estimated cost: ~$150-250 in Databar credits. Your current balance is [X]. Want to proceed?"
4. After completion, check balance again and report actual credits consumed
