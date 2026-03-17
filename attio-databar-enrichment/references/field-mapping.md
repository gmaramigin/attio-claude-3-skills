# Databar → Attio Field Mapping Reference

This document maps Databar enrichment output fields to typical Attio CRM attributes. Since every Attio workspace has a different schema, always run `discover_record_attributes` first and adapt these mappings to what actually exists.

## Company Field Mapping

### From `company_lookup` waterfall

The waterfall tries multiple providers (Diffbot, Owler, ContactOut, Muraena, People Data Labs). Field names vary by provider, so the `enrich.py` script merges results and normalizes keys. Here's how the most common fields map:

| Databar Field | Typical Attio Attribute | Notes |
|---|---|---|
| `name` / `company_name` | `name` | Usually already set in Attio |
| `description` | `description` | Company description/bio |
| `homepage_uri` / `website_url` | `website` or `domain` | Company website |
| `linkedin_uri` / `linkedin_link` | `linkedin` or `linkedin_url` | LinkedIn company page |
| `twitter_uri` / `twitter_url` | `twitter` or `twitter_url` | Twitter/X profile |
| `facebook_handle` / `facebook_url` | `facebook` or `facebook_url` | Facebook page |
| `number_of_employees` / `total_employees` | `employee_count` or `team_size` | Numeric field |
| `revenue_value` / `est_revenue` | `revenue` or `annual_revenue` | May be in different units |
| `industries` / `industry` | `industry` or `sector` | Often a select field — check valid options |
| `address` / `full_address` | `address` or `location` | May be structured (city/state/country) or flat string |
| `city` | `city` | Part of address |
| `country` | `country` | Part of address |
| `founded_year` / `founding_date` | `founded_year` or `founded` | May be timestamp or year |
| `funding` / `fundingevents` | `funding` or `total_funding` | Often JSON; extract total amount |
| `tech_stack` / `technologynames` | `tech_stack` or `technologies` | Often a list/array |
| `competitors` | `competitors` | Usually not a standard Attio field |
| `phone` / `phone_numbers` / `phone_number` | `phone` or `phone_number` | Company main phone |
| `logo` / `company_logo` | Not typically in Attio | Mention to user if they want it |
| `crunchbase_handle` | `crunchbase` or `crunchbase_url` | Crunchbase profile |
| `github_uri` | `github` or `github_url` | GitHub org page |

### From specific enrichments

Some enrichments return additional specialized data:

| Enrichment Type | Key Fields | Typical Attio Mapping |
|---|---|---|
| Tech stack (ID: 977) | technology names, categories | `tech_stack` (custom field) |
| Competitors (ID: 140, 397) | competitor names, domains | `competitors` (custom field) |
| Funding (ID: 679, 913) | rounds, amounts, investors | `funding`, `total_raised` |
| Job postings (waterfall) | titles, locations, descriptions | Usually not stored in Attio |
| Web traffic (ID: 909) | monthly visits, sources | `web_traffic` (custom field) |

## Person Field Mapping

### From `person_getter` waterfall (input: email)

| Databar Field | Typical Attio Attribute | Notes |
|---|---|---|
| `first_name` | `first_name` | Usually already in Attio |
| `last_name` | `last_name` | Usually already in Attio |
| `linkedin_url` / `linkedin` | `linkedin` or `linkedin_url` | LinkedIn profile URL |
| `title` / `job_title` | `job_title` or `title` | Current job title |
| `company` / `company_name` | Linked company record | May need to match/link |

### From `email_getter` waterfall (input: name + company)

| Databar Field | Typical Attio Attribute | Notes |
|---|---|---|
| `email` | `email` or `email_addresses` | Work email |

### From `person_by_link` waterfall (input: LinkedIn URL)

| Databar Field | Typical Attio Attribute | Notes |
|---|---|---|
| `first_name` | `first_name` | |
| `last_name` | `last_name` | |
| `work_email` | `email` or `email_addresses` | Verified work email |
| `personal_email` | `personal_email` | Often not stored in CRM |

### From `phone_getter` waterfall (input: LinkedIn URL)

| Databar Field | Typical Attio Attribute | Notes |
|---|---|---|
| `phone` | `phone` or `phone_numbers` | Direct/mobile phone |

## Mapping Strategy

When writing enrichment data back to Attio:

1. **Discover first**: Run `discover_record_attributes` and match by slug similarity.
2. **Respect types**: If an Attio field is `number`, convert strings to numbers. If it's `select`, use `get_record_attribute_options` to find valid values.
3. **Don't overwrite**: Only fill in fields that are currently empty, unless the user explicitly asks to overwrite.
4. **Normalize URLs**: Strip protocols and trailing slashes for consistency (e.g., `linkedin.com/company/stripe` not `https://www.linkedin.com/company/stripe/`).
5. **Handle arrays**: Some Databar fields return lists. If the Attio field is text, join with commas. If it's a multi-select, map each item.
6. **Log unmapped fields**: If Databar returns useful data that doesn't map to any Attio field, tell the user so they can decide whether to create a custom field.
