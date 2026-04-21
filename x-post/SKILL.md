---
name: x-post
description: >
  Posts a prepared draft to X.com (Twitter) using the browser. Reads tweet text
  and image path from a draft.json file in the specified folder, strips image
  metadata with exiftool, then composes and submits the post via chrome-devtools.
  Use whenever the user wants to post, publish, or share content to X.com or
  Twitter from a draft folder. Trigger on phrases like "post [folder] to x.com",
  "publish my draft to twitter", "share this to X", "post the crypto tweet",
  "post content from [folder]", "tweet this", "submit to x.com", or any request
  to push prepared content to X / Twitter. Also trigger when the user refers to
  a folder containing draft.json and asks to post it.
argument-hint: "<path-to-draft-folder>"
allowed-tools: Read, Bash(exiftool:*), mcp__chrome-devtools__list_pages, mcp__chrome-devtools__new_page, mcp__chrome-devtools__select_page, mcp__chrome-devtools__navigate_page, mcp__chrome-devtools__take_screenshot, mcp__chrome-devtools__click, mcp__chrome-devtools__type_text, mcp__chrome-devtools__fill, mcp__chrome-devtools__wait_for, mcp__chrome-devtools__upload_file, mcp__chrome-devtools__press_key, mcp__chrome-devtools__handle_dialog
---

# X Post Publisher

Posts prepared content to X.com from a local draft folder.

## Step 1 — Locate the Draft Folder

The user will provide a folder path (absolute or relative) or a folder name under `/tmp/`.

- If an absolute path is given, use it directly.
- If a bare name like `bitcoin-etf-1745000000` is given, look for it under `/tmp/crypto-tweet/`.
- Read `draft.json` from that folder. It has this shape:

```json
{
  "version": "1.0",
  "generated_at": "...",
  "topic": "...",
  "tweet": "tweet text up to 280 chars",
  "image": {
    "filepath": "/absolute/path/to/image.png",
    "prompt": "...",
    "width": 1344,
    "height": 768
  }
}
```

Extract `tweet` (the post text) and `image.filepath` (the image to attach).

## Step 2 — Strip Image Metadata

Before uploading, remove all EXIF/XMP/IPTC metadata from the image. This prevents accidental location or device info from being embedded in the post.

```bash
exiftool -all= "<image.filepath>"
```

`exiftool -all=` overwrites the file in place. Confirm it exits with code 0 before continuing. If it fails (e.g., `exiftool` not installed), warn the user and ask whether to proceed without stripping.

## Step 3 — Open X.com in the Browser

Use chrome-devtools to find or open X.com:

1. Call `list_pages` to see what tabs are already open.
2. If an X.com tab already exists, select it with `select_page`.
3. Otherwise, open a new tab and navigate to `https://x.com/home`.
4. Wait for the page to load — look for the compose area or "What is happening?!" placeholder text.
5. Take a screenshot to confirm the page state before proceeding.

If the page shows a login screen instead of the home feed, pause and tell the user: "X.com is not logged in. Please log in to X.com in the browser and then let me know when you're ready to continue." Do not attempt to fill in login credentials.

## Step 4 — Compose the Post

Once the home feed is visible:

1. Click the "Post" compose button or the "What is happening?!" text area to focus it.
2. Type the tweet text using `type_text`. Do not use `fill` for the compose box — X.com's rich text editor requires simulated keystrokes, not a direct value injection.
3. Wait briefly after typing for the character counter to update.
4. Take a screenshot to verify the text appears correctly in the compose area.

## Step 5 — Attach the Image

1. Look for the image/media attachment icon in the compose toolbar (camera icon, usually).
2. Click it — this triggers a file picker dialog.
3. Use `upload_file` to supply the cleaned image path. Pass the absolute path from `image.filepath`.
4. Wait for the image thumbnail to appear in the compose preview — this confirms the upload succeeded.
5. Take a screenshot to confirm the image is attached.

## Step 6 — Submit the Post

1. Click the "Post" submit button (the blue button, distinct from the compose area).
2. Wait for the success indicator — typically the compose modal closes or a "Your post was sent" toast appears.
3. Take a final screenshot as a confirmation receipt.

Report back to the user:
- The tweet text that was posted
- The image that was attached
- The confirmation screenshot (describe what it shows)

## Edge Cases

- **Image file missing:** If `image.filepath` doesn't exist on disk, stop and tell the user. Don't post without the intended image unless the user explicitly says to skip it.
- **draft.json missing or malformed:** Stop and tell the user the exact parse error. Don't guess at content.
- **Post button disabled after typing:** X.com sometimes disables the submit button if the text is empty or over 280 chars. Take a screenshot and report the state to the user.
- **Rate limit / "Something went wrong":** Take a screenshot, report it, and suggest the user try again shortly.
