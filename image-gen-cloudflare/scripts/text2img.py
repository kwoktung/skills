#!/usr/bin/env python3
"""Text-to-image generation for all Cloudflare Workers AI image models."""

import json
import sys
import uuid
import urllib.request
import urllib.error

from utils import get_base_url, get_auth_headers, save_image

# Models that require multipart/form-data instead of JSON body
MULTIPART_MODELS = {
    "@cf/black-forest-labs/flux-2-dev",
    "@cf/black-forest-labs/flux-2-klein-4b",
    "@cf/black-forest-labs/flux-2-klein-9b",
}

# Models whose response is a JSON envelope with base64 image (vs raw binary PNG)
JSON_RESPONSE_MODELS = {
    "@cf/black-forest-labs/flux-1-schnell",
    "@cf/black-forest-labs/flux-2-dev",
    "@cf/black-forest-labs/flux-2-klein-4b",
    "@cf/black-forest-labs/flux-2-klein-9b",
    "@cf/leonardo/lucid-origin",
}

ALL_MODELS = [
    "@cf/black-forest-labs/flux-1-schnell",
    "@cf/black-forest-labs/flux-2-dev",
    "@cf/black-forest-labs/flux-2-klein-4b",
    "@cf/black-forest-labs/flux-2-klein-9b",
    "@cf/bytedance/stable-diffusion-xl-lightning",
    "@cf/leonardo/lucid-origin",
    "@cf/leonardo/phoenix-1.0",
    "@cf/lykon/dreamshaper-8-lcm",
    "@cf/stabilityai/stable-diffusion-xl-base-1.0",
]

DEFAULT_MODEL = "@cf/black-forest-labs/flux-1-schnell"


def _build_multipart(fields):
    """Build multipart/form-data body. Returns (body_bytes, content_type_header)."""
    boundary = uuid.uuid4().hex
    parts = []
    for name, value in fields.items():
        if value is None:
            continue
        parts.append(
            f"--{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"{name}\"\r\n\r\n"
            f"{value}\r\n"
        )
    parts.append(f"--{boundary}--\r\n")
    body = "".join(parts).encode("utf-8")
    content_type = f"multipart/form-data; boundary={boundary}"
    return body, content_type


def generate(prompt, model=DEFAULT_MODEL, steps=None, width=None, height=None,
             negative_prompt="", output_dir="."):
    endpoint = f"{get_base_url()}/{model}"

    if model in MULTIPART_MODELS:
        fields = {"prompt": prompt}
        if steps is not None:
            fields["steps"] = str(steps)
        if width is not None:
            fields["width"] = str(width)
        if height is not None:
            fields["height"] = str(height)
        body, content_type = _build_multipart(fields)
        headers = {**get_auth_headers(), "Content-Type": content_type}
    else:
        payload = {"prompt": prompt}
        if steps is not None:
            payload["num_steps"] = steps
        if width is not None:
            payload["width"] = width
        if height is not None:
            payload["height"] = height
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        body = json.dumps(payload).encode("utf-8")
        headers = get_auth_headers()

    req = urllib.request.Request(endpoint, data=body, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            raw = response.read()
    except urllib.error.HTTPError as e:
        print(f"API Error {e.code}: {e.read().decode('utf-8')}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    if model in JSON_RESPONSE_MODELS:
        result = json.loads(raw.decode("utf-8"))
        if not result.get("success", True) and result.get("errors"):
            print(f"Error: {json.dumps(result['errors'])}", file=sys.stderr)
            sys.exit(1)
        b64 = result.get("result", {}).get("image")
        if not b64:
            print(f"Error: no image in response: {raw.decode()}", file=sys.stderr)
            sys.exit(1)
        filepath = save_image(b64, output_dir, is_base64=True)
    else:
        filepath = save_image(raw, output_dir, is_base64=False)

    out = {"filepath": filepath, "model": model, "prompt": prompt}
    if width:
        out["width"] = width
    if height:
        out["height"] = height
    return out


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--model", default=DEFAULT_MODEL, choices=ALL_MODELS)
    parser.add_argument("--steps", type=int, default=None)
    parser.add_argument("--width", type=int, default=None)
    parser.add_argument("--height", type=int, default=None)
    parser.add_argument("--negative-prompt", default="")
    parser.add_argument("--output-dir", default=".")
    args = parser.parse_args()
    print(json.dumps(generate(
        args.prompt, model=args.model, steps=args.steps,
        width=args.width, height=args.height,
        negative_prompt=args.negative_prompt, output_dir=args.output_dir,
    )))
