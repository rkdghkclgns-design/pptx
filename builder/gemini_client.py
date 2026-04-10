"""Call Gemini API via Supabase Edge Function for slide content generation."""

import json
import os
import time
from typing import Optional

import requests

from schemas.slide_schema import PresentationData

SYSTEM_PROMPT_TEMPLATE = """당신은 전문 프레젠테이션 콘텐츠 생성기입니다.

## 임무
제공된 소스 문서를 철저히 분석하여 소스 내용을 정확히 반영하는 프레젠테이션을 생성합니다.

## 핵심 원칙
1. 모든 슬라이드는 소스 문서의 실제 정보에 기반해야 합니다
2. 소스에 없는 사실, 통계, 주장을 만들어내지 마세요
3. 소스 콘텐츠를 논리적이고 설득력 있는 내러티브 흐름으로 구성하세요
4. 각 슬라이드는 소스의 서로 다른 핵심 주제를 다뤄야 합니다

## 슬라이드 JSON 스키마
각 슬라이드 객체:
- "type": "cover" | "content" | "twoColumn" | "threeCards" | "table" | "quote" | "section" | "closing"
- "title": string (한국어, 슬라이드 제목)
- "subtitle": string (선택, 한국어, cover/section/closing용)
- "description": string (선택, 한국어, 본문 단락)
- "bullets": string[] (선택, 한국어, 핵심 포인트, 최대 6개, 각 20단어 이내)
- "notes": string (한국어, 발표자 노트)
- "tableHeaders": string[] (선택, table 타입용)
- "tableRows": string[][] (선택, table 타입용)
- "imagePrompt": string (필수! 영어로, 일러스트레이션 프롬프트)

## 슬라이드 구성 규칙
- 슬라이드 1: 반드시 "cover"
- 슬라이드 2~{last_slide}: content, twoColumn, threeCards, table, quote, section을 다양하게 혼합
- 마지막 슬라이드: 반드시 "closing"

## 제약사항
- 총 슬라이드 수: 정확히 {slide_count}장
- 언어: 모든 텍스트는 반드시 한국어(Korean)로 작성
- imagePrompt: 반드시 영어(English)로

## 출력 형식
반드시 유효한 JSON만 반환: {{"slides": [...]}}"""


def generate_slides(
    content: str,
    slide_count: int,
    supabase_url: str,
    supabase_key: str,
    max_retries: int = 3,
    notebook_url: str | None = None,
) -> PresentationData:
    """Call Gemini API via Supabase Edge Function."""
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        slide_count=slide_count,
        last_slide=slide_count - 1,
    )

    max_content_chars = 30000
    if len(content) > max_content_chars:
        content = content[:max_content_chars] + "\n\n[... 이하 생략됨]"

    url = f"{supabase_url}/functions/v1/gemini-proxy"
    payload = {
        "content": content,
        "systemPrompt": system_prompt,
        "model": "gemini-2.5-flash",
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 32768,
            "thinkingConfig": {"thinkingBudget": 0},
        },
    }
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
    }

    last_error: Optional[str] = None
    for attempt in range(max_retries):
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=120)

            if resp.status_code == 429 or resp.status_code >= 500:
                wait = 3 ** attempt
                print(f"Edge Function retry {attempt + 1}/{max_retries} (HTTP {resp.status_code}), waiting {wait}s...")
                time.sleep(wait)
                last_error = f"HTTP {resp.status_code}: {resp.text[:200]}"
                continue

            if resp.status_code >= 400:
                last_error = f"HTTP {resp.status_code}: {resp.text[:300]}"
                print(f"Edge Function error: {resp.text[:200]}")
                time.sleep(1)
                continue

            data = resp.json()
            slides_json = _extract_slides_json(data)
            return PresentationData.model_validate(slides_json)

        except requests.RequestException as e:
            last_error = str(e)
            if attempt < max_retries - 1:
                time.sleep(3 ** attempt)

    raise RuntimeError(f"Edge Function 호출 실패 ({max_retries}회 시도): {last_error}")


def _extract_slides_json(gemini_response: dict) -> dict:
    """Extract slides JSON from Gemini response."""
    if "slides" in gemini_response:
        return gemini_response

    candidates = gemini_response.get("candidates", [])
    if candidates:
        finish_reason = candidates[0].get("finishReason", "")
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
                    pass

                repaired = _repair_truncated_json(text)
                if repaired:
                    try:
                        return json.loads(repaired)
                    except json.JSONDecodeError:
                        pass

        print(f"JSON 파싱 실패. finishReason: {finish_reason}")

    raise ValueError(
        f"Gemini 응답에서 슬라이드 데이터를 추출할 수 없습니다: {json.dumps(gemini_response)[:500]}"
    )


def _repair_truncated_json(text: str) -> Optional[str]:
    """Repair truncated JSON by closing at the last complete slide object."""
    slides_idx = text.find('"slides"')
    if slides_idx < 0:
        return None

    array_start = text.find("[", slides_idx)
    if array_start < 0:
        return None

    depth = 0
    in_string = False
    escape = False
    last_complete_end = -1

    for i in range(array_start + 1, len(text)):
        ch = text[i]

        if escape:
            escape = False
            continue

        if ch == "\\":
            escape = True
            continue

        if ch == '"':
            in_string = not in_string
            continue

        if in_string:
            continue

        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                last_complete_end = i

    if last_complete_end < 0:
        return None

    return text[: last_complete_end + 1] + "]}"
