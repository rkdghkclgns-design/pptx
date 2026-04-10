"""Call Gemini API for slide content generation.

Enhanced with Skywork-PPT workflow patterns:
- Multi-layer content structuring
- Source-faithful content extraction
- Professional presentation narrative flow
"""

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
- "notes": string (한국어, 발표자 노트 — 슬라이드 내용을 보충하는 상세 설명)
- "tableHeaders": string[] (선택, table 타입용)
- "tableRows": string[][] (선택, table 타입용)
- "imagePrompt": string (필수! 모든 슬라이드에 포함. 영어로 작성. 해당 슬라이드 주제를 시각적으로 표현하는 일러스트레이션 프롬프트)

## 슬라이드 구성 규칙
- 슬라이드 1: 반드시 "cover" — 소스 주제에서 제목과 부제 도출
- 슬라이드 2~{last_slide}: content, twoColumn, threeCards, table, quote, section을 다양하게 혼합
  - 각 슬라이드는 소스의 서로 다른 핵심 측면을 다룸
  - 연속으로 같은 type 사용 금지
  - table 타입은 비교/데이터가 있을 때 사용
  - quote 타입은 핵심 인사이트 강조용
  - section 타입은 주제 전환 구분용
- 마지막 슬라이드: 반드시 "closing" — 핵심 메시지 요약

## 제약사항
- 총 슬라이드 수: 정확히 {slide_count}장
- 언어: 모든 텍스트는 반드시 한국어(Korean)로 작성
- imagePrompt: 반드시 영어(English)로, 전문적인 일러스트레이션 컨셉 설명
- bullets는 간결하게 (각 항목 20단어 이내)
- description은 2~3문장으로 핵심만

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
    """Call Gemini API and return structured slide data."""
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

    prompt_text = f"{system_prompt}\n\n--- 소스 콘텐츠 ---\n\n{content}"

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
            "maxOutputTokens": 32768,
            "thinkingConfig": {
                "thinkingBudget": 0,
            },
        },
    }

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
                last_error = f"HTTP 400: {resp.text[:300]}"
                print(f"Gemini API 400 error: {resp.text[:200]}")
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
                # Try direct parse
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    pass

                # Try repairing truncated JSON
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
    """Attempt to repair truncated JSON by closing open brackets/braces.

    Strategy: find the last complete slide object in the slides array,
    truncate after it, and close the array and root object.
    """
    # Find "slides" array start
    slides_idx = text.find('"slides"')
    if slides_idx < 0:
        return None

    array_start = text.find("[", slides_idx)
    if array_start < 0:
        return None

    # Walk through characters tracking depth to find complete objects
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

    # Rebuild: text up to last complete object + close array + close root
    repaired = text[: last_complete_end + 1] + "]}"
    return repaired
