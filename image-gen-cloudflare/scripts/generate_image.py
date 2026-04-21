#!/usr/bin/env python3
"""Main CLI entry point for Cloudflare Workers AI image generation.

Backends:
  text2img.py   — all text-to-image models (FLUX, SDXL, Leonardo, Dreamshaper…)
  img2img.py    — SD v1.5 image-to-image editing (--reference-image)
  inpainting.py — SD v1.5 inpainting (--image + --mask)
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import text2img
import img2img
import inpainting


def main():
    parser = argparse.ArgumentParser(description="Generate or edit images via Cloudflare Workers AI")
    parser.add_argument("prompt", help="Image description or editing instruction")

    # routing flags
    parser.add_argument("--reference-image", default=None,
                        help="Source image for editing (uses SD v1.5 img2img)")
    parser.add_argument("--image", default=None,
                        help="Source image for inpainting (requires --mask)")
    parser.add_argument("--mask", default=None,
                        help="Mask image for inpainting (white=edit region, black=preserve)")

    # text-to-image options
    parser.add_argument("--model", default=text2img.DEFAULT_MODEL,
                        choices=text2img.ALL_MODELS,
                        help=f"Model for text-to-image (default: {text2img.DEFAULT_MODEL})")
    parser.add_argument("--steps", type=int, default=None,
                        help="Diffusion steps (model-dependent)")
    parser.add_argument("--width", type=int, default=None,
                        help="Image width in pixels")
    parser.add_argument("--height", type=int, default=None,
                        help="Image height in pixels")
    parser.add_argument("--negative-prompt", default="",
                        help="Elements to exclude (SD-family models)")

    # img2img / inpainting options
    parser.add_argument("--strength", type=float, default=0.75,
                        help="Transformation strength 0.0–1.0 (img2img/inpainting)")

    parser.add_argument("--output-dir", default=".",
                        help="Directory to save the output PNG")

    args = parser.parse_args()

    if args.image and args.mask:
        result = inpainting.generate(
            prompt=args.prompt,
            image_path=args.image,
            mask_path=args.mask,
            strength=args.strength,
            output_dir=args.output_dir,
        )
    elif args.reference_image:
        result = img2img.generate(
            prompt=args.prompt,
            reference_image_path=args.reference_image,
            strength=args.strength,
            output_dir=args.output_dir,
        )
    else:
        result = text2img.generate(
            prompt=args.prompt,
            model=args.model,
            steps=args.steps,
            width=args.width,
            height=args.height,
            negative_prompt=args.negative_prompt,
            output_dir=args.output_dir,
        )

    print(json.dumps(result))


if __name__ == "__main__":
    main()
