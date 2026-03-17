---
name: attio-dedup-audit
description: >
  Detect and resolve duplicate records in Attio CRM. Use this skill whenever the user mentions
  Attio duplicates, deduplication, merging Attio records, cleaning CRM data, or finding duplicate
  contacts/companies in Attio. Also trigger when the user asks about combining or consolidating
  records in Attio, even if they don't use the word 'duplicate'. Covers People, Companies, Custom
  Objects, and Lists with exact and fuzzy matching, winner scoring, reports, and merge execution
  via API (MCP) or browser UI.
---

# Attio Dedup Audit

You are helping the user find and merge duplicate records in their Attio CRM. This is a two-phase process: first you detect duplicates and present a report, then — after the user approves — you merge them.

## How it works at a high level

1. **Detect** — Pull records from Attio (via MCP tools or by browsing the Attio UI), group them by a matching key, and identify clusters of duplicates.
2. **Report** — Show the user what you found: which records are duplicates, which one you'd keep as the "winner," and what data would be merged.
3. **Merge** — After the user reviews and approves, combine the data into the winner record and handle the losers.

The user can choose to work via the **API (MCP)** or the **browser (Chrome)**. Ask which they prefer if it's not clear from context. Both modes follow the same detect→report→merge flow, but differ in how they execute.

---

## Step 1: Figure out what to deduplicate

Ask the user which object type they want to clean up and which attributes to match on.

### Matching rules

The user can specify **one or more matching rules** — attributes that identify a record as a duplicate. For example:

- People: match by `email_addresses` + `name` (two rules)
- Companies: match by `domains` + `name` (two rules)
- Custom objects: any combination the user chooses

The defaults (used if the user doesn't specify) are:

| Object type | Default rules |
|---|---|
| People | `email_addresses` |
| Companies | `domains` |
| Custom objects | Ask the user |

But the user can always add more rules or replace the defaults entirely. When presenting the setup, show the defaults and ask: **"These are the default matching rules. Want to add more, or use different ones?"**

### AND vs OR logic

When multiple rules are specified, the user chooses how they combine:

- **AND (strict)**: Records are duplicates only if ALL rules match. Example: same email AND same company name. Fewer false positives, might miss some duplicates.
- **OR (broad)**: Records are duplicates if ANY rule matches. Example: same email OR same company name. Catches more duplicates, but may flag records that aren't truly duplicates.

Ask the user which logic to use each time they set up matching rules. Present it plainly: "Should records match ALL of these rules to count as duplicates, or is matching ANY one of them enough?"

### Lists and custom objects

The user may also want to deduplicate **list entries** (e.g., a sales pipeline where the same company appears twice). For lists, ask which list and which attributes to match on — the same multi-rule system applies.

### Discovering the schema

Before pulling data, use `list-attribute-definitions` (for objects) or `list-list-attribute-definitions` (for lists) to understand what attributes exist, their types, and their API slugs. This is essential for building the matching rules correctly — present the available attributes to the user so they can pick the ones they want.

---

## Step 2: Detect duplicates

### API mode (MCP)

1. Use `list-records` to pull records. Paginate with `offset` — Attio returns max 50 per call. For large datasets, pull all records before grouping.

2. Normalize the matching rule values for each record:
   - **Emails**: lowercase, trim whitespace
   - **Domains**: lowercase, strip `www.` prefix, trim whitespace
   - **Phone numbers**: strip all non-digit characters except leading `+`
   - **Text fields** (names, etc.): lowercase, trim whitespace
   - **Personal names**: normalize to "firstname lastname" lowercase for comparison

3. Compare every pair of records against the matching rules:
   - **AND mode**: a pair is a duplicate only if ALL rules produce a match
   - **OR mode**: a pair is a duplicate if ANY rule produces a match
   - For each rule, two records "match" when they share at least one normalized value for that attribute (important for multi-value fields like emails — if record A has `john@acme.com` and record B has `john@acme.com, j.smith@gmail.com`, they match on email)

4. Cluster matched pairs into groups. If A matches B and B matches C, all three form one cluster (transitive closure).

5. If the user wants **fuzzy matching** (they might say "similar names" or "close matches"), compare text fields using edit distance or substring matching. Flag groups where values are similar but not identical — present these separately as "possible duplicates" with lower confidence. Fuzzy matching is especially useful for name-based rules where slight variations are common ("Jon Smith" vs "John Smith").

### Browser mode (Chrome)

1. Navigate to `https://app.attio.com` and go to the relevant object view (People, Companies, or the custom object).
2. Sort or filter by the matching attribute to visually identify duplicates.
3. Use the page content to extract record data and build duplicate clusters.
4. Browser mode is especially useful when the user wants to visually confirm duplicates or when the Attio MCP connection isn't set up.

---

## Step 3: Score winners

For each duplicate cluster, pick a **winner** — the record that will survive the merge. The default strategy is **most complete**: the record with the most non-empty attribute values wins.

How to score completeness:
- Count the number of attributes that have a non-null, non-empty value
- For multi-value attributes (like email addresses), count as filled if there's at least one value
- Ties go to the most recently updated record (use `updated_at` timestamp if available)

Present the scoring clearly in the report so the user can override if needed.

---

## Step 4: Generate the report

Before doing anything destructive, show the user a clear report. Format it as a markdown table or structured list:

### Report format

For each duplicate cluster:

```
### Cluster #1
Matched on: email_addresses ✓, name ✓  (AND logic — all rules matched)
Records: [count]

| Record | Name | Email | [Other key fields...] | Filled attrs | Winner? |
|--------|------|-------|-----------------------|--------------|---------|
| rec_abc | John Smith | john@acme.com | ... | 12/15 | ✓ Winner |
| rec_def | J. Smith | john@acme.com | ... | 8/15 | Merge into winner |

**Merge plan:**
- Winner keeps all its existing data
- From loser(s), these fields would be added: [list fields that the winner is missing but the loser has]
- These fields conflict (both have values): [list conflicts, note that winner's value will be kept]
```

When using **OR logic**, show which specific rule(s) matched for each pair — this helps the user judge whether it's a real duplicate or a false positive. For example:

```
### Cluster #2
Matched on: domains ✓, name ✗  (OR logic — at least one rule matched)
⚠️  Only 1 of 2 rules matched — review carefully

| Record | Name | Domain | Filled attrs | Winner? |
|--------|------|--------|--------------|---------|
| rec_ghi | Acme Corp | acme.com | 10/12 | ✓ Winner |
| rec_jkl | Acme Inc. | acme.com | 7/12 | Merge into winner |
```

At the end of the report, include a summary:
- Total duplicate clusters found
- Total records that would be merged
- Total records that would remain after dedup

Then ask the user: **"Does this look right? Should I proceed with the merge, or do you want to adjust anything?"**

Do not proceed until the user explicitly approves.

---

## Step 5: Execute the merge

### API mode (MCP)

For each approved cluster:

1. **Update the winner** — Use `update-record` to add any missing attribute values from the loser(s) to the winner. For multi-select attributes, use `patch_multiselect_values: true` to append rather than replace.

2. **Handle conflicts** — When both winner and loser have values for the same single-value attribute, keep the winner's value by default. If the user asked for a different conflict resolution strategy, follow that.

3. **Handle list entries** — If the loser appears in any lists, check if the winner is already in those lists:
   - If the winner is NOT in the list: use `add-record-to-list` to add it, copying over any entry-level attribute values from the loser's entry.
   - If the winner IS already in the list: note this in the summary (data may need manual review).

4. **The loser record** — The Attio MCP does not have a delete endpoint. After merging, tell the user which records are now "empty shells" that should be manually deleted. Provide the record IDs and names so they can find them easily in the Attio UI. If the user prefers, offer to switch to browser mode to delete them.

### Browser mode (Chrome)

For each approved cluster:

1. Navigate to the winner record in Attio.
2. Look for the merge functionality in the Attio UI (usually accessible from the record's menu or via a merge button).
3. Select the loser record(s) to merge into the winner.
4. Confirm the merge in the UI.

Browser mode handles both the data merge and record deletion in one step, which is its main advantage over API mode.

---

## Important notes

**Be conservative.** Deduplication is hard to undo. When in doubt, flag something as a "possible duplicate" rather than a definite one. It's better to miss a duplicate than to incorrectly merge two distinct records.

**Record references matter.** Other records may reference the loser (e.g., a deal linked to a person). In API mode, you can't automatically redirect these references — mention this in the report so the user is aware. In browser mode, Attio's built-in merge typically handles reference redirects.

**Rate limiting.** When working with large datasets via MCP, space out your API calls. Don't fire hundreds of requests in rapid succession. Pull data in batches of 50 and process incrementally.

**Custom objects.** When the user asks to deduplicate a custom object, you'll need to discover its slug first. Use `list-attribute-definitions` with the object slug the user provides to understand its schema, then proceed with the same detect→report→merge flow.

---

## Quick reference: Key MCP tools

| Task | Tool |
|---|---|
| Discover attributes | `list-attribute-definitions` |
| Pull records | `list-records` (with pagination) |
| Search by text | `search-records` |
| Get specific records | `get-records-by-ids` |
| Update winner | `update-record` |
| Add to list | `add-record-to-list` |
| List available lists | `list-lists` |
| List entry attributes | `list-list-attribute-definitions` |
| List entries | `list-records-in-list` |
