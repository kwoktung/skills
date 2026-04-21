#!/usr/bin/env python3
import json
import sys
import urllib.request
import urllib.error

from utils import get_base_url, get_auth_headers, save_image

MODEL = "@cf/stabilityai/stable-diffusion-xl-base-1.0"


def generate(prompt, negative_prompt="", num_steps=20, width=1024, height=1024, output_dir="."):
    endpoint = f"{get_base_url()}/{MODEL}"
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "num_steps": num_steps,
        "width": width,
        "height": height,
    }
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
    return {"filepath": filepath, "model": MODEL, "prompt": prompt, "width": width, "height": height}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--negative-prompt", default="")
    parser.add_argument("--num-steps", type=int, default=20)
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--output-dir", default=".")
    args = parser.parse_args()
    print(json.dumps(generate(
        args.prompt,
        negative_prompt=args.negative_prompt,
        num_steps=args.num_steps,
        width=args.width,
        height=args.height,
        output_dir=args.output_dir,
    )))
