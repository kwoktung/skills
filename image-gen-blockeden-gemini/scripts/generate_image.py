#!/usr/bin/env python3
"""Main CLI entry point for BlockEden Gemini image generation.

Delegates to the appropriate backend:
  - imagen3.py     — text-to-image via Imagen 3 (default)
  - gemini_flash.py — text-to-image or image editing via Gemini Flash
                      (auto-selected when --reference-image is given, or
                       when --model gemini-2.0-flash-preview-image-generation)
"""

import argparse
import json
import sys
import os

# Ensure sibling scripts are importable when run directly
sys.path.insert(0, os.path.dirname(__file__))

import imagen3
import gemini_flash


def main():
    parser = argparse.ArgumentParser(
        description="Generate or edit an image via BlockEden Gemini proxy"
    )
    parser.add_argument("prompt", help="Image description or editing instruction")
    parser.add_argument(
        "--reference-image", default=None,
        help="Path to a local image file to use as reference for editing "
             "(automatically uses Gemini Flash)",
    )
    parser.add_argument(
        "--model", default="imagen-3.0-generate-002",
        choices=["imagen-3.0-generate-002", "gemini-2.0-flash-preview-image-generation"],
        help="Model for text-only generation (default: imagen-3.0-generate-002). "
             "Ignored when --reference-image is set.",
    )
    parser.add_argument(
        "--aspect-ratio", default="1:1",
        choices=["1:1", "16:9", "9:16", "4:3", "3:4"],
        help="Aspect ratio for Imagen 3 (default: 1:1)",
    )
    parser.add_argument(
        "--output-dir", default=".",
        help="Directory to save the output image (default: current dir)",
    )
    args = parser.parse_args()

    if args.reference_image:
        # Editing / reference-based generation always uses Gemini Flash
        result = gemini_flash.generate(
            prompt=args.prompt,
            reference_image_path=args.reference_image,
            output_dir=args.output_dir,
        )
    elif args.model == "gemini-2.0-flash-preview-image-generation":
        result = gemini_flash.generate(
            prompt=args.prompt,
            output_dir=args.output_dir,
        )
    else:
        result = imagen3.generate(
            prompt=args.prompt,
            aspect_ratio=args.aspect_ratio,
            output_dir=args.output_dir,
        )

    print(json.dumps(result))


if __name__ == "__main__":
    main()
