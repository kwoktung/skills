---
name: image-gen-cloudflare
description: Generates and edits AI images using the Cloudflare Workers AI REST API (FLUX.1-schnell / Stable Diffusion XL / SD v1.5 img2img). Use this skill whenever the user wants to generate, create, draw, make, or produce an image, picture, photo, illustration, artwork, or visual using Cloudflare AI models. Also use when the user wants to edit an existing image or generate a new image based on a reference image/photo. Trigger on phrases like "generate an image of", "create a picture of", "make me an illustration", "draw a scene", "visualize this", "I want an image", "edit this image", "modify this photo", "use this as reference", or "generate based on this image". Requires CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID environment variables.
argument-hint: |
  Describe the image you want to generate, e.g. "a sunset over mountains in watercolor style".
  Optionally provide a local image path for editing, e.g. "edit ./photo.jpg to look like an oil painting".
requirement: |
  CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID environment variables must be set.
---

# Generate / Edit an Image via Cloudflare Workers AI

## Prerequisites

Both environment variables must be set:
- `CLOUDFLARE_API_TOKEN` — Cloudflare API token with Workers AI permission
- `CLOUDFLARE_ACCOUNT_ID` — your Cloudflare account ID

If either is missing, tell the user to set them before continuing.

## How to generate or edit an image

Run the script at `scripts/generate_image.py` (relative to this SKILL.md):

```bash
python <skill_dir>/scripts/generate_image.py "<prompt>" [options]
```

## Options

| Flag | Default | Notes |
|------|---------|-------|
| `--reference-image` | None | Local image path to edit. Automatically uses SD v1.5 img2img. |
| `--model` | `@cf/black-forest-labs/flux-1-schnell` | Choices: `@cf/black-forest-labs/flux-1-schnell`, `@cf/stability-ai/stable-diffusion-xl-base-1.0` |
| `--width` | 1024 | Image width in pixels (SDXL only) |
| `--height` | 1024 | Image height in pixels (SDXL only) |
| `--negative-prompt` | `""` | Things to exclude from the image (SDXL only) |
| `--strength` | 0.75 | Transformation intensity 0.0–1.0 (img2img only) |
| `--output-dir` | `.` | Directory to save the PNG |

## Examples

### Text-to-image with FLUX (default, fastest)

```bash
python /path/to/skill/scripts/generate_image.py \
  "a cozy coffee shop on a rainy day, impressionist painting style" \
  --output-dir ~/Desktop
```

### Text-to-image with Stable Diffusion XL (landscape)

```bash
python /path/to/skill/scripts/generate_image.py \
  "a futuristic cityscape at dusk, digital art" \
  --model "@cf/stability-ai/stable-diffusion-xl-base-1.0" \
  --width 1344 --height 768 \
  --negative-prompt "blurry, low quality, distorted, watermark" \
  --output-dir ~/Desktop
```

### Image editing with SD v1.5 img2img

```bash
python /path/to/skill/scripts/generate_image.py \
  "transform into an oil painting with warm golden tones" \
  --reference-image ./my-photo.jpg \
  --strength 0.8 \
  --output-dir ~/Desktop
```

## Output format

### FLUX text-to-image
```json
{"filepath": "/path/to/image_1234567890.png", "model": "@cf/black-forest-labs/flux-1-schnell", "prompt": "..."}
```

### SDXL text-to-image
```json
{"filepath": "/path/to/image_1234567890.png", "model": "@cf/stability-ai/stable-diffusion-xl-base-1.0", "prompt": "...", "width": 1024, "height": 1024}
```

### SD img2img editing
```json
{"filepath": "/path/to/image_1234567890.png", "model": "@cf/runwayml/stable-diffusion-v1-5-img2img", "prompt": "...", "reference_image": "./my-photo.jpg", "strength": 0.75}
```

## After image generation

Tell the user the file path and offer to regenerate with different parameters if they want to iterate.

## Interpreting user requests

- Extract the core visual description as the prompt.
- If the user provides a local image file path to edit, pass it via `--reference-image` — this automatically uses the img2img model.
- For "wide", "landscape", "horizontal" with SDXL: use `--width 1344 --height 768`.
- For "tall", "portrait", "vertical" with SDXL: use `--width 768 --height 1344`.
- If the user mentions "Stable Diffusion" or "SDXL", use `--model "@cf/stability-ai/stable-diffusion-xl-base-1.0"`.
- Default to FLUX for all other cases (fastest, best for quick generation).
- Reference images must be local file paths. If the user gives a URL, download it first: `curl -L -o /tmp/ref_image.jpg "<url>"`.
- For `--strength`: 0.3–0.5 for subtle changes; 0.7–0.9 for strong transformations.

## Prompt crafting tips

- Add a medium/style if none given (e.g., "digital art", "watercolor", "photorealistic").
- Add lighting or atmosphere if vague (e.g., "golden hour lighting", "moody atmosphere").
- For SDXL, use `--negative-prompt "blurry, low quality, distorted, watermark"` to avoid common artifacts.
- Keep the user's intent central — don't over-engineer the prompt.
