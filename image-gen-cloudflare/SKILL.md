---
name: image-gen-cloudflare
description: Generates and edits AI images using the Cloudflare Workers AI REST API. Supports FLUX.1-schnell, FLUX.2 (dev/klein), Stable Diffusion XL, SDXL Lightning, Leonardo Phoenix/Lucid-Origin, Dreamshaper 8 LCM, SD v1.5 img2img, and SD v1.5 inpainting. Use this skill whenever the user wants to generate, create, draw, make, or produce an image, picture, photo, illustration, artwork, or visual. Also use when the user wants to edit an existing image, inpaint/replace a region, or generate based on a reference image. Trigger on phrases like "generate an image of", "create a picture of", "make me an illustration", "draw a scene", "visualize this", "I want an image", "edit this image", "modify this photo", "replace this region", "inpaint", "use this as reference", or "generate based on this image". Requires CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID environment variables.
argument-hint: |
  Describe the image you want, e.g. "a sunset over mountains in watercolor style".
  Optionally provide a local image path for editing ("edit ./photo.jpg to look like an oil painting")
  or a source + mask image for inpainting.
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

Run `scripts/generate_image.py` (relative to this SKILL.md):

```bash
python <skill_dir>/scripts/generate_image.py "<prompt>" [options]
```

## Available models

| Model ID | Style / strength |
|----------|-----------------|
| `@cf/black-forest-labs/flux-1-schnell` | Fast, high quality (default) |
| `@cf/black-forest-labs/flux-2-klein-4b` | FLUX 2 fast, 4B params |
| `@cf/black-forest-labs/flux-2-klein-9b` | FLUX 2 fast, 9B params |
| `@cf/black-forest-labs/flux-2-dev` | FLUX 2 high quality (may be unstable) |
| `@cf/leonardo/lucid-origin` | Best prompt adherence + text rendering |
| `@cf/leonardo/phoenix-1.0` | Excellent coherence + text generation |
| `@cf/stabilityai/stable-diffusion-xl-base-1.0` | Classic SDXL |
| `@cf/bytedance/stable-diffusion-xl-lightning` | Fast SDXL variant |
| `@cf/lykon/dreamshaper-8-lcm` | Photorealistic, fast LCM |

## Options

| Flag | Default | Notes |
|------|---------|-------|
| `--model` | `@cf/black-forest-labs/flux-1-schnell` | Any model from the table above |
| `--steps` | model default | Diffusion steps |
| `--width` | model default | Image width in pixels |
| `--height` | model default | Image height in pixels |
| `--negative-prompt` | `""` | Elements to exclude (SD-family models) |
| `--reference-image` | None | Local image for editing → uses SD v1.5 img2img |
| `--strength` | 0.75 | Transformation intensity 0.0–1.0 (img2img/inpainting) |
| `--image` | None | Source image for inpainting (requires `--mask`) |
| `--mask` | None | Mask image: white = edit region, black = preserve |
| `--output-dir` | `.` | Directory to save the PNG |

## Examples

### Text-to-image with FLUX (default, fastest)

```bash
python <skill_dir>/scripts/generate_image.py \
  "a cozy coffee shop on a rainy day, impressionist painting style" \
  --output-dir ~/Desktop
```

### FLUX 2 high-quality

```bash
python <skill_dir>/scripts/generate_image.py \
  "an epic mountain landscape at dawn" \
  --model "@cf/black-forest-labs/flux-2-klein-9b" \
  --output-dir ~/Desktop
```

### Leonardo Phoenix (great for text in image)

```bash
python <skill_dir>/scripts/generate_image.py \
  "a neon sign that reads OPEN, cyberpunk alley, photorealistic" \
  --model "@cf/leonardo/phoenix-1.0" \
  --output-dir ~/Desktop
```

### SDXL landscape

```bash
python <skill_dir>/scripts/generate_image.py \
  "a futuristic cityscape at dusk, digital art" \
  --model "@cf/stabilityai/stable-diffusion-xl-base-1.0" \
  --width 1344 --height 768 \
  --negative-prompt "blurry, low quality, distorted, watermark" \
  --output-dir ~/Desktop
```

### Image editing (img2img)

```bash
python <skill_dir>/scripts/generate_image.py \
  "transform into an oil painting with warm golden tones" \
  --reference-image ./my-photo.jpg \
  --strength 0.8 \
  --output-dir ~/Desktop
```

### Inpainting (replace a region)

```bash
python <skill_dir>/scripts/generate_image.py \
  "replace with a snowy mountain background" \
  --image ./my-photo.jpg \
  --mask ./my-mask.png \
  --strength 0.9 \
  --output-dir ~/Desktop
```

## Output format

All modes return JSON to stdout:

```json
{"filepath": "/path/to/image_1234567890.png", "model": "...", "prompt": "..."}
```

img2img additionally includes `reference_image` and `strength`.
Inpainting additionally includes `image`, `mask`, and `strength`.
SDXL/width-height models include `width` and `height` when specified.

## After image generation

Tell the user the file path and offer to regenerate with a different model or parameters.

## Interpreting user requests

- Extract the core visual description as the prompt.
- **Default model**: FLUX.1-schnell — fast and high quality for most use cases.
- **User mentions text in image** (signs, labels, logos): prefer `@cf/leonardo/phoenix-1.0` or `lucid-origin`.
- **User mentions "SDXL"** or "Stable Diffusion": use `@cf/stabilityai/stable-diffusion-xl-base-1.0`.
- **User mentions "FLUX 2"** or "high quality": use `@cf/black-forest-labs/flux-2-klein-9b`.
- **User mentions "fast"** or "quick": use `@cf/black-forest-labs/flux-1-schnell` or `flux-2-klein-4b`.
- **User provides a reference image to edit**: pass via `--reference-image` (img2img).
- **User wants to replace a region** (inpainting): need `--image` + `--mask`. Explain mask format if needed.
- **Wide/landscape**: `--width 1344 --height 768`. **Tall/portrait**: `--width 768 --height 1344`.
- Reference images must be local paths. Download URLs first: `curl -L -o /tmp/ref.jpg "<url>"`.
- `--strength`: 0.3–0.5 for subtle edits, 0.7–0.9 for strong transformations.

## Prompt crafting tips

- Add a medium/style if vague: "digital art", "watercolor", "photorealistic", "oil painting".
- Add lighting if generic: "golden hour", "dramatic studio lighting", "soft diffused light".
- For SDXL, add `--negative-prompt "blurry, low quality, distorted, watermark"`.
- Keep the user's intent central — don't over-engineer.
