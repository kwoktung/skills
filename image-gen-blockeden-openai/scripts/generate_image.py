#!/usr/bin/env python3
"""Generate an image using BlockEden OpenAI proxy (DALL-E compatible)."""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
import base64
import time


def generate_image(prompt, size="1024x1024", quality="standard", model="dall-e-3", style="vivid", output_dir="."):
    api_key = os.environ.get("BLOCKEDEN_ACCESS_KEY")
    if not api_key:
        print("Error: BLOCKEDEN_ACCESS_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    base_url = f"https://api.blockeden.xyz/openai/{api_key}"
    endpoint = f"{base_url}/v1/images/generations"

    payload = {
        "model": model,
        "prompt": prompt,
        "size": size,
        "quality": quality,
        "n": 1,
        "response_format": "b64_json",
    }
    if model == "dall-e-3":
        payload["style"] = style

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
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

    image_data = result["data"][0]["b64_json"]
    revised_prompt = result["data"][0].get("revised_prompt", prompt)

    os.makedirs(output_dir, exist_ok=True)
    timestamp = int(time.time())
    filename = f"image_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "wb") as f:
        f.write(base64.b64decode(image_data))

    print(json.dumps({
        "filepath": filepath,
        "revised_prompt": revised_prompt,
        "model": model,
        "size": size,
        "quality": quality,
        "style": style if model == "dall-e-3" else None,
    }))


def generate_image_with_reference(prompt, reference_image_url, size="1024x1024", output_dir="."):
    """Generate an image using a reference image URI via /v1/responses with gpt-image-1."""
    api_key = os.environ.get("BLOCKEDEN_ACCESS_KEY")
    if not api_key:
        print("Error: BLOCKEDEN_ACCESS_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    base_url = f"https://api.blockeden.xyz/openai/{api_key}"
    endpoint = f"{base_url}/v1/responses"

    payload = {
        "model": "gpt-image-1",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": reference_image_url,
                    },
                    {
                        "type": "input_text",
                        "text": prompt,
                    },
                ],
            }
        ],
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
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

    # Find the image_generation_call output item
    image_b64 = None
    for item in result.get("output", []):
        if item.get("type") == "image_generation_call":
            image_b64 = item.get("result")
            break

    if not image_b64:
        print(f"Error: no image found in response: {json.dumps(result)}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)
    timestamp = int(time.time())
    filename = f"image_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "wb") as f:
        f.write(base64.b64decode(image_b64))

    print(json.dumps({
        "filepath": filepath,
        "model": "gpt-image-1",
        "reference_image": reference_image_url,
        "prompt": prompt,
    }))


def main():
    parser = argparse.ArgumentParser(description="Generate an image via BlockEden OpenAI proxy")
    parser.add_argument("prompt", help="Image description / prompt")
    parser.add_argument("--reference-image", default=None,
                        help="URI of a reference image to base generation on (uses gpt-image-1 via /v1/responses)")
    parser.add_argument("--size", default="1024x1024",
                        choices=["1024x1024", "1792x1024", "1024x1792"],
                        help="Image size (default: 1024x1024)")
    parser.add_argument("--quality", default="standard", choices=["standard", "hd"],
                        help="Image quality (default: standard)")
    parser.add_argument("--model", default="dall-e-3", choices=["dall-e-3", "dall-e-2"],
                        help="Model to use for text-only generation (default: dall-e-3)")
    parser.add_argument("--style", default="vivid", choices=["vivid", "natural"],
                        help="Image style for dall-e-3 (default: vivid)")
    parser.add_argument("--output-dir", default=".", help="Directory to save the image (default: current dir)")
    args = parser.parse_args()

    if args.reference_image:
        generate_image_with_reference(
            prompt=args.prompt,
            reference_image_url=args.reference_image,
            size=args.size,
            output_dir=args.output_dir,
        )
    else:
        generate_image(
            prompt=args.prompt,
            size=args.size,
            quality=args.quality,
            model=args.model,
            style=args.style,
            output_dir=args.output_dir,
        )


if __name__ == "__main__":
    main()
