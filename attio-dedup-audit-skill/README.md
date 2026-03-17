# Attio Dedup Audit

A Claude skill for detecting and resolving duplicate records in [Attio CRM](https://attio.com). Works with People, Companies, Custom Objects, and Lists.

## What it does

This skill walks you through a structured deduplication workflow: detect duplicates, review a report, then merge with your approval. Nothing happens without you saying "go."

It supports two execution modes — **API (MCP)** for programmatic access, or **Browser (Chrome)** for visual confirmation through the Attio UI. Both follow the same detect → report → merge flow.

### Key features

- **Multi-rule matching** — Match on one or more attributes (e.g., email + name for people, domain + company name for companies). You pick the rules.
- **AND / OR logic** — Choose whether ALL rules must match (strict) or ANY rule is enough (broad). You decide each time.
- **Completeness-based winner scoring** — The record with the most filled attributes survives the merge. Ties go to the most recently updated record.
- **Transparent reporting** — Every duplicate cluster shows which rules matched, what data would transfer, and where conflicts exist. OR-logic matches with partial rule hits get flagged for careful review.
- **Fuzzy matching** — Optionally catch near-duplicates like "Jon Smith" vs "John Smith" with similarity-based matching, reported separately at lower confidence.
- **Custom objects and lists** — Not just People and Companies. Deduplicate any object type or list entries using whatever attributes make sense.

### Defaults

| Object type | Default matching attribute |
|---|---|
| People | `email_addresses` |
| Companies | `domains` |
| Custom objects | You choose |

Defaults are suggestions — you can add more rules or replace them entirely.

## Prerequisites

You need at least one of:

- **Attio MCP connection** — for API mode. Requires the Attio MCP server configured with your workspace credentials.
- **Chrome browser tools** — for browser mode. Requires being logged into Attio in Chrome.

### API mode limitations

The Attio API does not have a delete endpoint. In API mode, data is merged into the winner record, but loser records remain as empty shells. You'll need to delete them manually in the Attio UI, or switch to browser mode for that step.

Browser mode handles merge + deletion in one step via Attio's built-in merge feature.

## Install

Download `attio-dedup-audit.skill` and open it in Claude (double-click or drag into the chat).

Or manually copy the `attio-dedup-audit/` folder into your skills directory.

## Usage examples

```
Find duplicate people in my Attio CRM. Match by email and name — both should match.
```

```
Clean up duplicate companies in Attio. Match by domain OR company name.
```

```
Deduplicate entries in my sales pipeline list by company name.
```

```
Check for duplicate contacts. Match by phone number. Use the browser.
```

## License

MIT
