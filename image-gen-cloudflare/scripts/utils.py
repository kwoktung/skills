#!/usr/bin/env python3
import os
import sys
import base64
import time


def get_api_token():
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        print("Error: CLOUDFLARE_API_TOKEN environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return token


def get_account_id():
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    if not account_id:
        print("Error: CLOUDFLARE_ACCOUNT_ID environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return account_id


def get_base_url():
    account_id = get_account_id()
    return f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run"


def get_auth_headers():
    return {
        "Authorization": f"Bearer {get_api_token()}",
        "Content-Type": "application/json",
    }


def save_image(data, output_dir=".", is_base64=True):
    os.makedirs(output_dir, exist_ok=True)
    timestamp = int(time.time())
    filepath = os.path.join(output_dir, f"image_{timestamp}.png")
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(data) if is_base64 else data)
    return filepath
