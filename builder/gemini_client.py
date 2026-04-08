"""Call Supabase Edge Function (Gemini proxy) for slide content generation."""

import json
import time

import requests

from schemas.slide_schema import PresentationData

SYSTEM_PROMPT_TEMPLATE = """You are a professional presentation content generator.
Given the source document content below, produce a JSON object with a "slides" array.

Each slide object must have:
- "type": one of "cover", "content", "twoColumn", "threeCards", "table", "quote", "section", "closing"
- "title": string (slide title)
- "subtitle": string (optional, for cover/section slides)
- "description": string (optional, body text or paragraph)
- "bullets": string[] (optional, bullet points, max 6 items, max 15 words each)
- "notes": string (optional, speaker notes)
- "tableHeaders": string[] (optional, for table type)
- "tableRows": string[][] (optional, for table type)

Rules:
- First slide MUST be type "cover" with title and subtitle
- Last slide MUST be type "closing"
- Total number of slides: exactly {slide_count}
- Language: match the source document language (Korean if Korean, English if English)
- Be concise: max 6 bullets per slide, max 15 words per bullet
- Use varied slide types for visual interest (don't repeat the same type)
- Include speaker notes that expand on each slide's content

Return ONLY a valid JSON object: {{"slides": [...]}}"""


def generate_slides(
    content: str,
    slide_count: int,
    supabase_url: str,
    supabase_key: str,
    max_retries: int = 3,
) -> PresentationData:
    """Call Gemini via Supabase Edge Function and return structured slide data."""
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(slide_count=slide_count)

    # Truncate content if too long (Gemini context limit)
    max_content_chars = 30000
    if len(content) > max_content_chars:
        content = content[:max_content_chars] + "\n\n[... 이하 생략됨]"

    url = f"{supabase_url}/functions/v1/gemini-proxy"
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "content": content,
        "settings": {"slideCount": slide_count},
        "systemPrompt": system_prompt,
    }

    last_error = None
    for attempt in range(max_retries):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=60)

            if resp.status_code == 429 or resp.status_code >= 500:
                wait = (3 ** attempt)
                time.sleep(wait)
                last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
                continue

            resp.raise_for_status()
            data = resp.json()

            # Extract the slides JSON from the Gemini response
            slides_json = _extract_slides_json(data)
            return PresentationData.model_validate(slides_json)

        except requests.RequestException as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                time.sleep(3 ** attempt)

    raise RuntimeError(f"Gemini API 호출 실패 ({max_retries}회 시도): {last_error}")


def _extract_slides_json(gemini_response: dict) -> dict:
    """Extract slides JSON from Gemini API response."""
    # Try direct response (when responseMimeType is application/json)
    if "slides" in gemini_response:
        return gemini_response

    # Try Gemini REST API response format
    candidates = gemini_response.get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        if parts:
            text = parts[0].get("text", "")
            # Clean up markdown code blocks if present
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            return json.loads(text.strip())

    raise ValueError(f"Gemini 응답에서 슬라이드 데이터를 추출할 수 없습니다: {json.dumps(gemini_response)[:500]}")
