#!/usr/bin/env python3
"""Text-to-image and image editing using Gemini Flash via BlockEden Gemini proxy."""

import base64
import json
import os
import sys
import urllib.request
import urllib.error

from utils import get_base_url, save_image

MODEL = "gemini-2.5-flash-image"

MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def _load_image_as_inline_data(image_path):
    """Read a local image file and return an inlineData part for the Gemini API."""
    ext = os.path.splitext(image_path)[1].lower()
    mime_type = MIME_TYPES.get(ext, "image/png")
    with open(image_path, "rb") as f:
        b64_data = base64.b64encode(f.read()).decode("utf-8")
    return {"inlineData": {"mimeType": mime_type, "data": b64_data}}


def generate(prompt, reference_image_path=None, output_dir="."):
    """Generate or edit an image using Gemini Flash.

    When reference_image_path is provided the model edits/transforms that image
    according to the prompt. Without it, the model generates from text alone.

    Args:
        prompt: Text description or editing instruction.
        reference_image_path: Optional path to a local image file.
        output_dir: Directory to save the output PNG.

    Returns:
        dict with filepath, model, prompt, and optionally reference_image.
    """
    endpoint = f"{get_base_url()}/v1beta/models/{MODEL}:generateContent"

    parts = []
    if reference_image_path:
        parts.append(_load_image_as_inline_data(reference_image_path))
    parts.append({"text": prompt})

    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"responseModalities": ["IMAGE", "TEXT"]},
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"API Error {e.code}: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    # Walk candidates -> content -> parts to find the image
    b64_data = None
    for candidate in result.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            inline = part.get("inlineData", {})
            if inline.get("mimeType", "").startswith("image/"):
                b64_data = inline.get("data")
                break
        if b64_data:
            break

    if not b64_data:
        print(f"Error: no image found in response: {json.dumps(result)}", file=sys.stderr)
        sys.exit(1)

    filepath = save_image(b64_data, output_dir)
    output = {"filepath": filepath, "model": MODEL, "prompt": prompt}
    if reference_image_path:
        output["reference_image"] = reference_image_path
    return output


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=f"Generate or edit images using {MODEL}")
    parser.add_argument("prompt", help="Text description or editing instruction")
    parser.add_argument("--reference-image", default=None,
                        help="Path to a local image file to edit/transform")
    parser.add_argument("--output-dir", default=".", help="Output directory (default: current dir)")
    args = parser.parse_args()

    result = generate(args.prompt, reference_image_path=args.reference_image, output_dir=args.output_dir)
    print(json.dumps(result))
