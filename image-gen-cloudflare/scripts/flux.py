#!/usr/bin/env python3
import json
import sys
import urllib.request
import urllib.error

from utils import get_base_url, get_auth_headers, save_image

MODEL = "@cf/black-forest-labs/flux-1-schnell"


def generate(prompt, steps=4, output_dir="."):
    endpoint = f"{get_base_url()}/{MODEL}"
    payload = {"prompt": prompt, "steps": steps}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(endpoint, data=data, headers=get_auth_headers())

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"API Error {e.code}: {e.read().decode('utf-8')}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)

    if not result.get("success"):
        print(f"Error: API returned success=false: {json.dumps(result)}", file=sys.stderr)
        sys.exit(1)

    b64_data = result.get("result", {}).get("image")
    if not b64_data:
        print(f"Error: no image in response: {json.dumps(result)}", file=sys.stderr)
        sys.exit(1)

    filepath = save_image(b64_data, output_dir, is_base64=True)
    return {"filepath": filepath, "model": MODEL, "prompt": prompt}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--steps", type=int, default=4)
    parser.add_argument("--output-dir", default=".")
    args = parser.parse_args()
    print(json.dumps(generate(args.prompt, steps=args.steps, output_dir=args.output_dir)))
