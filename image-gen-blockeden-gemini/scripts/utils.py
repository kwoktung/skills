#!/usr/bin/env python3
"""Shared utilities for BlockEden Gemini image generation."""

import os
import sys
import base64
import time


def get_api_key():
    """Read BLOCKEDEN_GEMINI_API_KEY from environment or exit with an error."""
    api_key = os.environ.get("BLOCKEDEN_ACCESS_KEY")
    if not api_key:
        print("Error: BLOCKEDEN_ACCESS_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return api_key


def get_base_url():
    """Return the BlockEden Gemini proxy base URL."""
    return f"https://api.blockeden.xyz/gemini/{get_api_key()}"


def save_image(b64_data, output_dir="."):
    """Decode base64 image data and save it as a timestamped PNG file."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = int(time.time())
    filename = f"image_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "wb") as f:
        f.write(base64.b64decode(b64_data))
    return filepath
