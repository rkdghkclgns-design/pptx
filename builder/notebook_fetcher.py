"""Fetch content from a NotebookLM shared URL."""

import requests


def fetch_notebook_content(url: str) -> str:
    """Attempt to fetch text content from a NotebookLM shared URL.

    NotebookLM shared pages are JavaScript-rendered, so direct HTTP fetch
    may not return full content. We extract whatever text is available
    from the HTML response and pass the URL as context to Gemini.
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

        # Extract text from HTML (basic extraction)
        html = resp.text
        text = _extract_text_from_html(html)

        if text.strip():
            return text

        # If we can't extract content, provide the URL as reference
        return f"NotebookLM 소스 URL: {url}\n이 URL의 내용을 기반으로 프레젠테이션을 생성해주세요."

    except requests.RequestException as e:
        print(f"NotebookLM fetch warning: {e}")
        return f"NotebookLM 소스 URL: {url}\n(콘텐츠를 직접 가져올 수 없습니다. URL 참조로 프레젠테이션을 생성해주세요.)"


def _extract_text_from_html(html: str) -> str:
    """Extract visible text from HTML, removing tags and scripts."""
    import re

    # Remove script and style blocks
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Decode HTML entities
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")
    text = text.replace("&nbsp;", " ")

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Filter out very short results (likely just boilerplate)
    if len(text) < 100:
        return ""

    return text
