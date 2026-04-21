---
name: crypto-tweet
description: >
  Researches crypto news and drafts Twitter/X post candidates in a casual
  crypto-community voice, crafts a landscape editorial image prompt, then
  saves draft.json. Use whenever the user wants to write a crypto tweet, post
  about crypto news, create Twitter/X content about cryptocurrency, or generate
  crypto social media content. Trigger on phrases like "write a crypto tweet",
  "post about crypto", "crypto twitter post", "tweet about [coin/topic]",
  "crypto content for twitter", or "help me tweet about crypto news".
argument-hint: "[optional topic, e.g. 'Bitcoin ETF' — omit for auto-trending]"
allowed-tools: WebSearch, Bash(mkdir:*), Write
---

# Crypto Tweet Generator

Creates a Twitter/X post + editorial image prompt based on current crypto news.

## Step 1 — Research

**If user specified a topic** (e.g. "Bitcoin ETF", "Solana"), run 2 searches:
```
<topic> crypto news discussion
<topic> crypto community reaction reddit twitter
```

**If no topic specified**, run 2 searches to find what's trending:
```
crypto news most discussed today
trending crypto twitter community
```

Collect: headline summary, key numbers/events, community sentiment (bullish/bearish/mixed).

## Step 2 — Draft Tweet Candidates

Write **3 to 5** candidate tweets. Rules:
- Voice: regular crypto user reacting naturally — casual, not corporate
- Allowed: crypto slang ("ser", "wen", "ngmi/wagmi", "gm", "lfg"), relevant emojis
- Mix styles: one analytical/factual, one excited/bullish, one skeptical/cautious
- Max **280 characters** each
- Max **2 hashtags** per tweet (or zero — don't force them)
- No self-promotion, no "just my opinion" disclaimers

Number them clearly:
```
1. [tweet text]
2. [tweet text]
...
```

## Step 3 — User Selection

After presenting candidates, ask:
> "Which tweet would you like to use? Reply with a number (1–5), or describe changes."

If the user requests edits, revise and re-present before continuing.
If the user picks one, proceed to Step 4.

## Step 4 — Craft Image Prompt

Based on the selected tweet and news context, write a descriptive image prompt suitable for any image generation skill.

**Requirements — always include all of these:**
- **Landscape:** wide 16:9 composition, horizontal orientation
- **Editorial style:** `editorial news-style illustration for a financial and technology publication`
- **No padding:** `full-bleed, edge-to-edge composition, no borders, no margins, no letterboxing`
- **Social media ready:** clean focal point, uncluttered background, strong visual hierarchy
- **Graceful and clean layout:** minimal elements, generous negative space, elegant color palette (muted tones with one or two accent colors), balanced composition
- **No text/logos:** do NOT include readable text, brand logos, watermarks, or chart labels in the prompt

**Prompt structure:**
```
[Specific subject for the news topic], editorial news-style illustration for a financial and technology publication, wide 16:9 landscape, full-bleed edge-to-edge composition, no borders, no padding, clean minimal layout, generous negative space, elegant muted color palette with [relevant accent color] accents, strong visual hierarchy, social media optimized, professional studio lighting, no text, no logos
```

**Also always provide a negative prompt:**
```
text, watermark, logo, signature, border, padding, margin, letterbox, black bars, busy background, cluttered, low quality, blurry, distorted, cropped
```

Present both prompts to the user and ask which image generation skill they want to use.
Do NOT run image generation yourself — let the user invoke their preferred skill with this prompt.

## Step 5 — Create Output Folder

Before image generation, create a dedicated output folder under `/tmp/crypto-tweet/`:

```bash
mkdir -p /tmp/crypto-tweet/<slug>
```

Where `<slug>` is a lowercase, hyphen-separated version of the topic + Unix timestamp, e.g.:
- topic "Bitcoin ETF" → `/tmp/crypto-tweet/bitcoin-etf-1745000000`
- topic "Kelp DAO exploit" → `/tmp/crypto-tweet/kelp-dao-exploit-1745000000`

Tell the user the output folder path, then pass it as `--output-dir` when invoking the image generation skill.

## Step 6 — Save draft.json

After the user has generated the image with their preferred skill, write `draft.json` into the same output folder. Schema: `references/draft-schema.json`.

Example output at `/tmp/crypto-tweet/bitcoin-etf-1745000000/draft.json`:
```json
{
  "version": "1.0",
  "generated_at": "2026-04-21T10:00:00Z",
  "topic": "Bitcoin ETF",
  "tweet": "BlackRock just added another 1,200 BTC to their ETF holdings. Institutions aren't leaving ser — they're stacking. 🟠",
  "image": {
    "filepath": "/tmp/crypto-tweet/bitcoin-etf-1745000000/image_1745000000.png",
    "prompt": "Bitcoin gold coin on digital circuit board, institutional traders in background, editorial news-style digital illustration...",
    "width": 1344,
    "height": 768
  }
}
```

After writing the file, tell the user:
- The selected tweet text (ready to copy)
- The full output folder path containing the image and `draft.json`
