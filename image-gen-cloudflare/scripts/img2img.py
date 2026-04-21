#!/usr/bin/env python3
import base64
import json
import os
import sys
import urllib.request
import urllib.error

from utils import get_base_url, get_auth_headers, save_image

MODEL = "@cf/runwayml/stable-diffusion-v1-5-img2img"


def generate(prompt, reference_image_path, strength=0.75, output_dir="."):
    if not os.path.isfile(reference_image_path):
        print(f"Error: reference image not found: {reference_image_path}", file=sys.stderr)
        sys.exit(1)

    with open(reference_image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    endpoint = f"{get_base_url()}/{MODEL}"
    payload = {"prompt": prompt, "image_b64": image_b64, "strength": strength}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data, headers=get_auth_headers())

    try:
        with urllib.request.urlopen(req) as response:
            raw_bytes = response.read()
    except urllib.error.HTTPError as e:
        print(f"API Error {e.code}: {e.read().decode('utf-8')}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    filepath = save_image(raw_bytes, output_dir, is_base64=False)
    return {
        "filepath": filepath,
        "model": MODEL,
        "prompt": prompt,
        "reference_image": reference_image_path,
        "strength": strength,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--reference-image", required=True)
    parser.add_argument("--strength", type=float, default=0.75)
    parser.add_argument("--output-dir", default=".")
    args = parser.parse_args()
    print(json.dumps(generate(
        args.prompt,
        reference_image_path=args.reference_image,
        strength=args.strength,
        output_dir=args.output_dir,
    )))
