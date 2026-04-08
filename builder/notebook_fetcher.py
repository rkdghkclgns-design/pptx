"""Fetch content from a NotebookLM shared URL."""

import re

import requests


def fetch_notebook_content(url: str) -> str:
    """Attempt to fetch text content from a NotebookLM shared URL.

    NotebookLM pages are JavaScript-rendered, so direct HTTP fetch
    returns only boilerplate HTML. We extract meaningful text if possible,
    otherwise return a minimal reference for Gemini to use with Search grounding.
    """
    try:
        resp = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; PPTBuilder/1.0)",
            },
            timeout=30,
        )
        resp.raise_for_status()

        text = _extract_text_from_html(resp.text)

        # Check if extracted text is meaningful (not just boilerplate)
        if _is_meaningful_content(text):
            return text

        # Content is just boilerplate — return minimal reference
        # Gemini will use Google Search grounding to actually read the URL
        print(f"  NotebookLM page is JS-rendered, using Search grounding for: {url}")
        return ""

    except requests.RequestException as e:
        print(f"  NotebookLM fetch warning: {e}")
        return ""


def _extract_text_from_html(html: str) -> str:
    """Extract visible text from HTML, removing tags and scripts."""
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _is_meaningful_content(text: str) -> bool:
    """Check if extracted text has real content vs just page boilerplate."""
    if len(text) < 200:
        return False

    # Common boilerplate patterns from JS-rendered pages
    boilerplate_signals = [
        "sign in",
        "google account",
        "javascript",
        "enable javascript",
        "loading",
        "noscript",
        "NotebookLM",
        "__NEXT_DATA__",
        "window.__",
    ]

    lower = text.lower()
    boilerplate_count = sum(1 for s in boilerplate_signals if s.lower() in lower)

    # If more than 3 boilerplate signals, it's likely not real content
    if boilerplate_count >= 3:
        return False

    # If text is too short relative to unique words, likely boilerplate
    words = set(text.lower().split())
    if len(words) < 50:
        return False

    return True
