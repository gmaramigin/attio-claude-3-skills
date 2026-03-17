#!/usr/bin/env python3
"""
Databar enrichment helper for the Attio-Databar skill.

Usage:
    python enrich.py company --domain stripe.com
    python enrich.py person --email patrick@stripe.com
    python enrich.py person --linkedin "https://linkedin.com/in/patrickcollison"
    python enrich.py person --name "Patrick Collison" --company stripe.com
    python enrich.py company --domain stripe.com --enrichment-id 977  # specific enrichment
    python enrich.py discover --query "tech stack"
    python enrich.py balance

Environment:
    DATABAR_API_KEY  — required, your Databar API key

Output:
    JSON to stdout. Errors go to stderr.
"""

import argparse
import json
import sys
import os

def get_client():
    """Create and return a DatabarClient instance."""
    try:
        from databar import DatabarClient
    except ImportError:
        print("Error: databar package not installed. Run: pip install databar httpx[socks] --break-system-packages", file=sys.stderr)
        sys.exit(1)

    api_key = os.environ.get("DATABAR_API_KEY")
    if not api_key:
        print("Error: DATABAR_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    return DatabarClient(api_key=api_key)


def enrich_company(args):
    """Enrich a company using waterfall or specific enrichment."""
    client = get_client()

    if args.enrichment_id:
        # Use a specific enrichment provider
        enrichment = client.get_enrichment(args.enrichment_id)
        params = {}
        # Map common param names
        for p in enrichment.params:
            if p.name in ("domain", "company_website", "link", "url", "website"):
                params[p.name] = args.domain
            elif p.name == "name" and args.name:
                params[p.name] = args.name

        if not params:
            params = {"domain": args.domain}

        print(f"Running enrichment '{enrichment.name}' (ID: {args.enrichment_id})...", file=sys.stderr)
        result = client.run_enrichment_sync(args.enrichment_id, params)
    else:
        # Use company_lookup waterfall (default)
        print(f"Running company_lookup waterfall for '{args.domain}'...", file=sys.stderr)
        result = client.run_waterfall_sync("company_lookup", {"company_website": args.domain})

    # Flatten waterfall results — extract the best data from the first provider that returned
    output = flatten_waterfall_result(result, "company")
    output["_raw"] = result  # Keep raw for debugging

    json.dump(output, sys.stdout, indent=2, default=str)
    print(file=sys.stderr)
    print(f"Done. Credits remaining: {client.get_user().balance}", file=sys.stderr)


def enrich_person(args):
    """Enrich a person using the appropriate waterfall."""
    client = get_client()

    if args.enrichment_id:
        enrichment = client.get_enrichment(args.enrichment_id)
        params = {}
        for p in enrichment.params:
            if p.name == "email" and args.email:
                params["email"] = args.email
            elif p.name == "link" and args.linkedin:
                params["link"] = args.linkedin
            elif p.name == "linkedin" and args.linkedin:
                params["linkedin"] = args.linkedin
            elif p.name == "first_name" and args.name:
                parts = args.name.split(None, 1)
                params["first_name"] = parts[0]
            elif p.name == "last_name" and args.name:
                parts = args.name.split(None, 1)
                params["last_name"] = parts[1] if len(parts) > 1 else ""
            elif p.name in ("company", "domain") and args.company:
                params[p.name] = args.company

        print(f"Running enrichment '{enrichment.name}' (ID: {args.enrichment_id})...", file=sys.stderr)
        result = client.run_enrichment_sync(args.enrichment_id, params)
    elif args.email:
        print(f"Running person_getter waterfall for '{args.email}'...", file=sys.stderr)
        result = client.run_waterfall_sync("person_getter", {"email": args.email})
    elif args.linkedin:
        print(f"Running person_by_link waterfall for '{args.linkedin}'...", file=sys.stderr)
        result = client.run_waterfall_sync("person_by_link", {"link": args.linkedin})
    elif args.name and args.company:
        parts = args.name.split(None, 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""
        print(f"Running email_getter waterfall for '{args.name}' at '{args.company}'...", file=sys.stderr)
        result = client.run_waterfall_sync("email_getter", {
            "first_name": first_name,
            "last_name": last_name,
            "company": args.company,
        })
    else:
        print("Error: provide --email, --linkedin, or --name + --company", file=sys.stderr)
        sys.exit(1)

    output = flatten_waterfall_result(result, "person")
    output["_raw"] = result

    json.dump(output, sys.stdout, indent=2, default=str)
    print(file=sys.stderr)
    print(f"Done. Credits remaining: {client.get_user().balance}", file=sys.stderr)


def discover(args):
    """Discover available enrichments by search query."""
    client = get_client()
    enrichments = client.list_enrichments(q=args.query)

    results = []
    for e in enrichments[:30]:
        results.append({
            "id": e.id,
            "name": e.name,
            "description": e.description,
            "data_source": e.data_source,
            "price": e.price,
            "auth_method": e.auth_method,
        })

    json.dump(results, sys.stdout, indent=2)
    print(f"\nFound {len(enrichments)} enrichments (showing top {len(results)})", file=sys.stderr)


def show_balance(args):
    """Show current credit balance."""
    client = get_client()
    user = client.get_user()
    json.dump({
        "email": user.email,
        "balance": user.balance,
        "plan": user.plan,
    }, sys.stdout, indent=2)


def show_waterfalls(args):
    """List all available waterfalls."""
    client = get_client()
    waterfalls = client.list_waterfalls()

    results = []
    for w in waterfalls:
        results.append({
            "identifier": w.identifier,
            "name": w.name,
            "description": w.description,
            "input_params": [{"name": p.name, "type": p.type, "required": p.required} for p in w.input_params],
            "output_fields": [{"name": f.name, "label": f.label} for f in w.output_fields],
            "providers": [{"id": e.id, "name": e.name, "price": e.price} for e in w.available_enrichments],
        })

    json.dump(results, sys.stdout, indent=2)


def flatten_waterfall_result(result, record_type="company"):
    """
    Extract the best enrichment data from a waterfall result.

    Waterfall results come as a list of dicts, each with an 'enrichment_data' key
    containing provider-specific data. We merge them, preferring earlier (higher-priority)
    providers for conflicting fields.
    """
    if not result:
        return {"_status": "no_data", "_message": "No providers returned data"}

    if isinstance(result, dict):
        # Single enrichment result (not waterfall)
        return {"_status": "ok", **result}

    if not isinstance(result, list):
        return {"_status": "ok", "_data": result}

    merged = {}
    providers_used = []

    for entry in result:
        if not isinstance(entry, dict):
            continue

        enrichment_data = entry.get("enrichment_data", {})
        if not enrichment_data:
            continue

        for provider_name, provider_data in enrichment_data.items():
            if not provider_data:
                continue
            providers_used.append(provider_name)

            if isinstance(provider_data, dict):
                for key, value in provider_data.items():
                    # Only set if not already present (prefer earlier/higher-priority providers)
                    if key not in merged and value is not None and value != "" and value != []:
                        merged[key] = value

    if not merged:
        return {"_status": "no_data", "_message": "Providers returned empty results", "_providers_tried": providers_used}

    merged["_status"] = "ok"
    merged["_providers_used"] = providers_used
    return merged


def main():
    parser = argparse.ArgumentParser(description="Databar enrichment helper")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Company enrichment
    company_parser = subparsers.add_parser("company", help="Enrich a company")
    company_parser.add_argument("--domain", required=True, help="Company domain (e.g., stripe.com)")
    company_parser.add_argument("--name", help="Company name (optional, for some enrichments)")
    company_parser.add_argument("--enrichment-id", type=int, help="Specific enrichment ID (skip waterfall)")
    company_parser.set_defaults(func=enrich_company)

    # Person enrichment
    person_parser = subparsers.add_parser("person", help="Enrich a person")
    person_parser.add_argument("--email", help="Person's email")
    person_parser.add_argument("--linkedin", help="Person's LinkedIn URL")
    person_parser.add_argument("--name", help="Person's full name")
    person_parser.add_argument("--company", help="Company domain (used with --name)")
    person_parser.add_argument("--enrichment-id", type=int, help="Specific enrichment ID")
    person_parser.set_defaults(func=enrich_person)

    # Discover enrichments
    discover_parser = subparsers.add_parser("discover", help="Search available enrichments")
    discover_parser.add_argument("--query", required=True, help="Search query")
    discover_parser.set_defaults(func=discover)

    # Balance check
    balance_parser = subparsers.add_parser("balance", help="Check credit balance")
    balance_parser.set_defaults(func=show_balance)

    # List waterfalls
    waterfall_parser = subparsers.add_parser("waterfalls", help="List available waterfalls")
    waterfall_parser.set_defaults(func=show_waterfalls)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
