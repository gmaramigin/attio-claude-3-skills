# Attio + Databar Enrichment Skill

A Claude skill that enriches your Attio CRM records using [Databar](https://databar.ai) — an aggregation layer connecting 90+ data providers through a single API.

## What It Does

This skill connects your Attio CRM to Databar's enrichment network. It can:

- **Enrich companies** — Fill in missing firmographic data (industry, employee count, revenue, description, social links, funding, tech stack) from a company domain
- **Enrich people** — Find emails, phone numbers, LinkedIn profiles, and job titles for contacts in your CRM
- **Bulk enrich** — Process entire Attio lists or filter for records with missing fields and enrich them all at once
- **Waterfall enrichment** — Automatically try multiple data providers in sequence (Diffbot, Owler, People Data Labs, Hunter.io, Leadmagic, etc.) until data is found, maximizing match rates

Just say things like:
- "Enrich Stripe in my Attio"
- "Find the email for John Smith at Acme Corp"
- "Enrich all companies missing their industry field"
- "Look up company info for notion.so"
- "Fill in the blanks on my leads"

## Prerequisites

You need two MCP servers connected to Claude:

### 1. Databar MCP Server

Get your API key from [databar.ai](https://databar.ai) (click your profile → API Key).

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

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

Or clone and build from source: [github.com/databar-ai/databar-mcp-server](https://github.com/databar-ai/databar-mcp-server)

### 2. Attio MCP Server

You need an Attio MCP server connected with read/write access to your workspace. If you don't have one yet, you can use [attio-mcp](https://www.npmjs.com/package/attio-mcp) or any Attio MCP integration available in the Claude connector marketplace.

Your Attio access token needs these permissions:
- **Read**: Records, List entries
- **Write**: Records, List entries, Notes

## Installation

### Option A: Install the .skill file (recommended)

Download the `attio-databar-enrichment.skill` file and double-click it, or drag it into Claude Desktop. The skill installs automatically.

### Option B: Manual installation

Copy the `attio-databar-enrichment/` folder into your Claude skills directory:

- **macOS**: `~/Library/Application Support/Claude/skills/`
- **Windows**: `%APPDATA%\Claude\skills\`

## How It Works

The skill follows a 5-step workflow:

1. **Check balance & discover schema** — Verifies your Databar credit balance and reads your Attio workspace schema to understand what fields exist
2. **Identify records** — Finds the records to enrich (by name, by filter, or by Attio list)
3. **Call Databar** — Runs waterfall enrichments that try multiple providers automatically
4. **Map & write back** — Maps Databar's response fields to your Attio attributes and updates records (only fills in empty fields by default — never overwrites existing data unless you ask)
5. **Report results** — Summarizes what was enriched, what couldn't be found, and how many credits were consumed

## Available Waterfalls

| Waterfall | Use When You Have | Returns |
|---|---|---|
| `company_lookup` | Company domain/website | Name, description, LinkedIn, employees, industries, revenue, funding |
| `email_getter` | Person's name + company | Work email |
| `person_getter` | Person's email | Name, LinkedIn URL |
| `person_by_link` | LinkedIn profile URL | Name, work email, personal email |
| `phone_getter` | LinkedIn profile URL | Phone number |
| `job_postings_getter` | Company domain/website | Open jobs, descriptions, locations |

Beyond waterfalls, you can also search 300+ individual enrichments for specialized data (tech stack, competitors, SEO keywords, funding history, etc.).

## Cost & Credits

Databar uses a credit-based system. Costs vary by provider:

- **Company lookup waterfall**: ~$3-15 per company (depends on which providers fire)
- **Email finder waterfall**: ~$4-6 per person
- **Phone waterfall**: ~$7-35 per person
- **Individual enrichments**: $0.10 - $20+ depending on the provider

The skill always checks your balance before bulk operations and estimates the total cost before proceeding. It will ask for confirmation before running expensive bulk jobs.

You can check your balance anytime by asking: "What's my Databar balance?"

## Important Nuances

### Field Mapping

Every Attio workspace has a different schema. The skill auto-discovers your fields at runtime and maps Databar's output to matching attributes. See `references/field-mapping.md` for the default mapping logic.

If Databar returns useful data that doesn't map to any existing Attio field, the skill will tell you — you can then create a custom field in Attio for it.

### Data Safety

- The skill **never overwrites** existing data by default. It only fills in empty/missing fields.
- For select/status fields, it checks valid options before writing.
- You can explicitly ask it to overwrite if needed: "Re-enrich Stripe and overwrite existing data."

### Auth Methods

Some Databar enrichments require your own API key for the underlying provider (marked as `auth_method: "user"` — e.g., Clearbit, HubSpot lookups). The waterfalls generally use Databar's pooled network keys and work out of the box without additional setup.

### Rate Limits & Errors

- The Databar MCP handles retries automatically
- For bulk operations (100+ records), the skill processes in batches with progress reporting
- If a company/person can't be found in any provider's database, it's reported clearly — not treated as an error

### Fallback Mode

If the Databar MCP server isn't connected, the skill can fall back to using the Databar Python SDK (`pip install databar`). The `scripts/enrich.py` helper handles this case. Set the `DATABAR_API_KEY` environment variable for the fallback to work.

## File Structure

```
attio-databar-enrichment/
├── SKILL.md                          # Main skill instructions
├── README.md                         # This file
├── scripts/
│   └── enrich.py                     # Python SDK fallback script
└── references/
    └── field-mapping.md              # Databar → Attio field mapping guide
```

## Troubleshooting

**"Databar tools not found"** — Make sure the Databar MCP server is configured in your Claude Desktop settings and you've restarted the session after adding it.

**"Insufficient credits"** — Top up your Databar account at [databar.ai](https://databar.ai). The skill checks your balance before operations and will warn you if it's low.

**"Auth required for enrichment"** — Some enrichments need your own API key for the underlying provider. Use waterfalls instead (they use Databar's network keys) or configure the provider key in your Databar account settings.

**"No data found for company X"** — Not all companies are in every provider's database. Try a different enrichment or check that the domain is correct.

**Fields not mapping correctly** — Run `discover_record_attributes` to see your actual Attio schema. The skill adapts to your workspace, but custom field names might not match the default mapping. Tell the skill which field to write to explicitly: "Put the employee count in the 'team_size' field."

## License

MIT
