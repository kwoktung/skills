---
name: image-gen-blockeden-gemini
description: Generates AI images using the BlockEden Gemini proxy (Imagen 3 / Gemini Flash). Use this skill whenever the user wants to generate, create, draw, make, or produce an image, picture, photo, illustration, artwork, or visual using Gemini or Imagen models — even if they don't say "Gemini" or "BlockEden". Also use when the user wants to edit an existing image or generate a new image based on a reference image/photo. Trigger on phrases like "generate an image of", "create a picture of", "make me an illustration", "draw a scene", "visualize this", "I want an image", "edit this image", "modify this photo", "use this as reference", or "generate based on this image". Requires the BLOCKEDEN_ACCESS_KEY environment variable to be set.
argument-hint: [describe the image you want, optionally with a local reference image path, e.g. "a sunset over mountains in watercolor style" or "edit ./photo.jpg to add a dragon in the background"]
---

# Generate / Edit an Image via BlockEden Gemini Proxy

You are helping the user generate or edit an AI image using the BlockEden Gemini proxy, which is compatible with the Google Gemini API (Imagen 3 and Gemini Flash image generation).

## Prerequisites

The `BLOCKEDEN_ACCESS_KEY` environment variable must be set. If it's missing, tell the user:
> Please set the `BLOCKEDEN_ACCESS_KEY` environment variable before using this skill.

## How to generate or edit an image

Use the bundled script at `scripts/generate_image.py` (relative to this SKILL.md):

```bash
python <skill_dir>/scripts/generate_image.py "<prompt>" [options]
```

### Options

| Flag | Default | Notes |
|------|---------|-------|
| `--reference-image` | `None` | Path to a local image file to use as reference/base for editing. Switches to `gemini-2.0-flash-preview-image-generation`. |
| `--model` | `imagen-3.0-generate-002` | Model for text-only generation. Choices: `imagen-3.0-generate-002`, `gemini-2.0-flash-preview-image-generation` |
| `--aspect-ratio` | `1:1` | For Imagen 3. Choices: `1:1`, `16:9`, `9:16`, `4:3`, `3:4` |
| `--output-dir` | `.` | Directory where the PNG will be saved |

### Example: text-only generation (Imagen 3)

```bash
python /path/to/skill/scripts/generate_image.py \
  "a cozy coffee shop on a rainy day, impressionist painting style" \
  --aspect-ratio 16:9 \
  --output-dir ~/Desktop
```

### Example: reference image / editing (Gemini Flash)

```bash
python /path/to/skill/scripts/generate_image.py \
  "add a dragon flying in the background" \
  --reference-image ./my-photo.jpg \
  --output-dir ~/Desktop
```

### Example: text-to-image with Gemini Flash

```bash
python /path/to/skill/scripts/generate_image.py \
  "a futuristic cityscape at dusk" \
  --model gemini-2.0-flash-preview-image-generation \
  --output-dir ~/Desktop
```

## After generation

### Text-only (Imagen 3) output
```json
{
  "filepath": "/path/to/image_1234567890.png",
  "model": "imagen-3.0-generate-002",
  "aspect_ratio": "1:1",
  "prompt": "..."
}
```

### Reference image / edit (Gemini Flash) output
```json
{
  "filepath": "/path/to/image_1234567890.png",
  "model": "gemini-2.0-flash-preview-image-generation",
  "reference_image": "./my-photo.jpg",
  "prompt": "add a dragon flying in the background"
}
```

Once the image is saved:
1. Tell the user the file path so they can open it.
2. Offer to regenerate with different parameters if the user wants to iterate.

## Interpreting the user's request

- Extract the core visual description from what the user says and use it as the prompt.
- If the user provides a local image file path to edit or use as reference, pass it via `--reference-image`. This automatically uses Gemini Flash for editing.
- If the user specifies a wide/landscape aspect, map to `--aspect-ratio 16:9`. Tall/portrait → `9:16`. Square → `1:1`.
- If the user mentions "Gemini" explicitly, use `--model gemini-2.0-flash-preview-image-generation`.
- If no output location is given, save to the current working directory.
- The reference image must be a local file path (not a URL). If the user gives a URL, download it first with `curl -L -o /tmp/ref_image.jpg "<url>"`.

## Prompt crafting tips

Good image prompts are specific and visual. If the user's request is vague, enhance it slightly:
- Add a medium/style if none given (e.g., "digital art", "watercolor", "photorealistic")
- Add lighting or atmosphere if it feels generic (e.g., "golden hour lighting", "moody atmosphere")
- Don't over-engineer — keep the user's intent central
