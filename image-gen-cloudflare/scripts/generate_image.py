#!/usr/bin/env python3
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import flux
import sdxl
import img2img

FLUX_MODEL = "@cf/black-forest-labs/flux-1-schnell"
SDXL_MODEL = "@cf/stabilityai/stable-diffusion-xl-base-1.0"


def main():
    parser = argparse.ArgumentParser(description="Generate or edit an image via Cloudflare Workers AI")
    parser.add_argument("prompt", help="Image description or editing instruction")
    parser.add_argument("--reference-image", default=None,
                        help="Path to a local image file for editing (uses SD v1.5 img2img)")
    parser.add_argument("--model", default=FLUX_MODEL,
                        choices=[FLUX_MODEL, SDXL_MODEL],
                        help=f"Model for text-only generation (default: {FLUX_MODEL})")
    parser.add_argument("--width", type=int, default=1024,
                        help="Image width in pixels for SDXL (default: 1024)")
    parser.add_argument("--height", type=int, default=1024,
                        help="Image height in pixels for SDXL (default: 1024)")
    parser.add_argument("--negative-prompt", default="",
                        help="Things to avoid in the image (SDXL only)")
    parser.add_argument("--strength", type=float, default=0.75,
                        help="Transformation strength 0.0–1.0 for img2img (default: 0.75)")
    parser.add_argument("--output-dir", default=".",
                        help="Directory to save the output image (default: current dir)")
    args = parser.parse_args()

    if args.reference_image:
        result = img2img.generate(
            prompt=args.prompt,
            reference_image_path=args.reference_image,
            strength=args.strength,
            output_dir=args.output_dir,
        )
    elif args.model == SDXL_MODEL:
        result = sdxl.generate(
            prompt=args.prompt,
            negative_prompt=args.negative_prompt,
            width=args.width,
            height=args.height,
            output_dir=args.output_dir,
        )
    else:
        result = flux.generate(
            prompt=args.prompt,
            output_dir=args.output_dir,
        )

    print(json.dumps(result))


if __name__ == "__main__":
    main()
