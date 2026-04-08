"""Call Gemini API directly for slide content generation."""

import json
import os
import time
from typing import Optional

import requests

from schemas.slide_schema import PresentationData

SYSTEM_PROMPT_TEMPLATE = """You are a professional presentation content generator.
Your task: Analyze the source document thoroughly and create a presentation that accurately represents its content.

CRITICAL RULES:
1. Every slide MUST be based on actual information from the source document
2. Do NOT invent facts, statistics, or claims not present in the source
3. Organize the source content logically into a compelling narrative flow
4. Extract key points, data, and insights directly from the source

Each slide object must have:
- "type": one of "cover", "content", "twoColumn", "threeCards", "table", "quote", "section", "closing"
- "title": string (slide title)
- "subtitle": string (optional, for cover/section slides)
- "description": string (optional, body text paragraph from source)
- "bullets": string[] (optional, key points from source, max 6 items, max 20 words each)
- "notes": string (speaker notes with additional context from source)
- "tableHeaders": string[] (optional, for table type)
- "tableRows": string[][] (optional, for table type)
- "imagePrompt": string (a detailed English prompt to generate a relevant illustration for this slide, describing the visual concept)

Slide structure:
- Slide 1: MUST be type "cover" — derive title from the source topic
- Slides 2 to {last_slide}: Mix of content, twoColumn, quote, section types — each covering a distinct aspect from the source
- Last slide: MUST be type "closing" — summarize the key takeaway

Total slides: exactly {slide_count}
Language: match the source document language (Korean if Korean, English if English)
imagePrompt: ALWAYS in English, describe a professional illustration concept

Return ONLY a valid JSON object: {{"slides": [...]}}"""


def generate_slides(
    content: str,
    slide_count: int,
    supabase_url: str,
    supabase_key: str,
    max_retries: int = 3,
    notebook_url: str | None = None,
) -> PresentationData:
    """Call Gemini API directly and return structured slide data."""
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        slide_count=slide_count,
        last_slide=slide_count - 1,
    )

    max_content_chars = 30000
    if len(content) > max_content_chars:
        content = content[:max_content_chars] + "\n\n[... 이하 생략됨]"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"

    # Build the prompt text
    prompt_text = f"{system_prompt}\n\n--- SOURCE CONTENT ---\n\n{content}"

    # If we have a notebook URL, add it for Gemini to reference via grounding
    if notebook_url and notebook_url.startswith("http"):
        prompt_text += f"\n\n--- ADDITIONAL REFERENCE URL ---\nPlease also analyze the content at this URL for the presentation: {notebook_url}"

    payload: dict = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 8192,
        },
    }

    # Enable Google Search grounding when we have a URL
    # This lets Gemini actually fetch and read the URL content
    if notebook_url and notebook_url.startswith("http"):
        payload["tools"] = [
            {"googleSearch": {}}
        ]

    last_error: Optional[str] = None
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=120,
            )

            if resp.status_code == 429 or resp.status_code >= 500:
                wait = 3 ** attempt
                print(f"Gemini API retry {attempt + 1}/{max_retries} (HTTP {resp.status_code}), waiting {wait}s...")
                time.sleep(wait)
                last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
                continue

            if resp.status_code == 400:
                # If grounding fails, retry without it
                if "tools" in payload:
                    print("Google Search grounding failed, retrying without it...")
                    del payload["tools"]
                    continue
                last_error = f"HTTP 400: {resp.text[:300]}"
                time.sleep(1)
                continue

            resp.raise_for_status()
            data = resp.json()

            slides_json = _extract_slides_json(data)
            return PresentationData.model_validate(slides_json)

        except requests.RequestException as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                time.sleep(3 ** attempt)

    raise RuntimeError(f"Gemini API 호출 실패 ({max_retries}회 시도): {last_error}")


def _extract_slides_json(gemini_response: dict) -> dict:
    """Extract slides JSON from Gemini API response."""
    if "slides" in gemini_response:
        return gemini_response

    candidates = gemini_response.get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        for part in parts:
            text = part.get("text", "")
            if not text:
                continue
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            if text.startswith("{"):
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    continue

    raise ValueError(
        f"Gemini 응답에서 슬라이드 데이터를 추출할 수 없습니다: {json.dumps(gemini_response)[:500]}"
    )
