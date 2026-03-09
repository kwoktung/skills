#!/usr/bin/env python3
"""Text-to-image generation using Imagen 3 via BlockEden Gemini proxy."""

import json
import sys
import urllib.request
import urllib.error

from utils import get_base_url, save_image

MODEL = "imagen-3.0-generate-002"
ASPECT_RATIOS = ["1:1", "16:9", "9:16", "4:3", "3:4"]


def generate(prompt, aspect_ratio="1:1", output_dir="."):
    """Generate an image from a text prompt using Imagen 3.

    Args:
        prompt: Text description of the image to generate.
        aspect_ratio: One of 1:1, 16:9, 9:16, 4:3, 3:4.
        output_dir: Directory to save the output PNG.

    Returns:
        dict with filepath, model, aspect_ratio, and prompt.
    """
    endpoint = f"{get_base_url()}/v1beta/models/{MODEL}:predict"

    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": aspect_ratio,
        },
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

    predictions = result.get("predictions", [])
    if not predictions:
        print(f"Error: no predictions in response: {json.dumps(result)}", file=sys.stderr)
        sys.exit(1)

    b64_data = predictions[0].get("bytesBase64Encoded")
    if not b64_data:
        print(f"Error: no image data in prediction: {json.dumps(predictions[0])}", file=sys.stderr)
        sys.exit(1)

    filepath = save_image(b64_data, output_dir)
    return {
        "filepath": filepath,
        "model": MODEL,
        "aspect_ratio": aspect_ratio,
        "prompt": prompt,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=f"Generate an image using {MODEL}")
    parser.add_argument("prompt", help="Text description of the image")
    parser.add_argument("--aspect-ratio", default="1:1", choices=ASPECT_RATIOS,
                        help="Aspect ratio (default: 1:1)")
    parser.add_argument("--output-dir", default=".", help="Output directory (default: current dir)")
    args = parser.parse_args()

    result = generate(args.prompt, aspect_ratio=args.aspect_ratio, output_dir=args.output_dir)
    print(json.dumps(result))
