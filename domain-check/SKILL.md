---
name: domain-check
description: >
  Suggests memorable domain name candidates based on user context and checks
  each one for real-time availability using whois and dig. Supports any TLD
  including country-codes (.us, .uk, .de, .co.uk, .com.au, etc.) and modern
  TLDs (.io, .ai, .co, .app, .dev, .xyz, and more). Use this skill whenever
  the user wants to find or check domain names — phrases like "find me a
  domain for my fish shop", "check if fishman.com is available", "suggest
  some domains for a coffee startup", "what .io domains are free for my app",
  "recommend domains with .us TLD", or any variation of "is X.Y taken /
  available / registered". Trigger even when the user mentions domain names
  in passing, e.g. "I'm building a site for my bakery" — proactively offer to
  check availability.
allowed-tools: Bash
---

# Domain Check

Suggest creative domain candidates and check their live availability.

## Step 1 — Clarify TLD if needed

If the user's message doesn't specify a TLD (top-level domain), ask before generating candidates:

> "Which TLD would you like? Common choices: `.com` (most trusted, default), `.io` (popular for tech), `.co` (short & modern), `.ai` (AI/tech startups), `.us` / `.uk` / `.de` (country-specific), or tell me any other TLD you have in mind."

If the user is clearly in a hurry or the context strongly implies `.com` (e.g. "find me a business domain"), default to `.com` and mention you did so.

If the user specifies a country or region (e.g. "UK domains", "US domains"), map it to the right TLD: UK → `.co.uk` and `.uk`, US → `.com` and `.us`, Australia → `.com.au`, Germany → `.de`, France → `.fr`, Canada → `.ca`, Japan → `.co.jp`, etc.

## Step 2 — Generate 6–10 domain candidates

Based on the user's topic, brainstorm memorable names. Aim for variety:

- **Direct**: the thing itself (fishmarket.com)
- **Descriptive**: what it does (freshcatch.com)
- **Portmanteau / blend**: combine two ideas (fishly.com, finco.io)
- **Action word**: verb-first names (getfreshfish.com, catchdaily.io)
- **Personality / brand feel**: evocative, memorable (oceanplate.co, reelfresh.ai)

Keep names short (ideally ≤ 15 characters before the TLD). Avoid hyphens unless the user asks for them. Don't suggest names that are obvious trademark risks (e.g. "Googly Fish").

List candidates like:
```
fishmanclothing.com
reelfresh.com
catchco.com
oceanplate.com
finmarket.com
freshcatch.com
fishly.com
theoceanshop.com
```

## Step 3 — Check availability for each candidate

Run the bundled script for every candidate. The script uses `whois` (primary) and `dig @1.1.1.1` (fallback) with a 10-second timeout per domain.

```bash
bash /Users/kwoktung/Projects/skills/domain-check/scripts/check_domain.sh <domain>
```

Run all checks sequentially — one per line. Each prints: `AVAILABLE`, `REGISTERED`, `UNKNOWN`, or `TIMEOUT`.

> **Tip for testing the script in isolation:**
> ```bash
> bash scripts/check_domain.sh google.com       # → REGISTERED
> bash scripts/check_domain.sh fishmanclothing.com  # → AVAILABLE
> ```

## Step 4 — Present results

Group by availability. Use a clean table or list:

```
✓ AVAILABLE
  fishmanclothing.com
  fishly.com
  catchco.com

✗ TAKEN
  freshcatch.com
  finmarket.com

? UNKNOWN
  oceanplate.com   (whois inconclusive, try registrar directly)
```

For TIMEOUT results, note that the whois server was slow — the user can try again or check via a registrar like Namecheap or Cloudflare Registrar.

## Step 5 — Offer next steps

After showing results, briefly offer:
- Check additional candidates if the available list is thin
- Try a different TLD for taken names (e.g. fishly.io if fishly.com is taken)
- Refine the naming style (shorter, catchier, more descriptive, etc.)

Keep it to one short sentence — don't over-explain.
