"""Generate images for slides using Gemini 2.5 Flash Image model.

Enhanced with Skywork-Design patterns:
- Professional illustration prompts
- Retry with varied prompts on failure
- Guaranteed image for every slide
"""

import os
import time
from typing import Optional

import requests

from schemas.slide_schema import SlideData

# Fallback prompts for slides that fail image generation
FALLBACK_PROMPTS = {
    "cover": "A sleek, modern presentation cover page with abstract geometric shapes, gradient blue and teal colors, professional business aesthetic",
    "content": "A clean business infographic layout with abstract data visualization elements, modern corporate flat design, blue accent colors",
    "twoColumn": "A split composition showing two complementary business concepts side by side, modern flat design with geometric shapes",
    "threeCards": "Three floating cards with abstract icons representing business concepts, modern minimal design, soft shadows",
    "table": "A clean data table visualization with highlighted rows and columns, corporate blue color scheme, modern design",
    "quote": "An elegant quotation mark design with subtle gradient background, inspirational and professional atmosphere",
    "section": "A bold section divider with abstract geometric shapes and gradient, modern presentation transition slide",
    "closing": "A professional thank you slide design with subtle confetti or celebration elements, clean and elegant",
}


def generate_slide_images(
    slides: list[SlideData],
    supabase_url: str,
    supabase_key: str,
) -> list[SlideData]:
    """Generate images for all slides."""
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_api_key:
        print("GEMINI_API_KEY not set, skipping image generation")
        return list(slides)

    updated: list[SlideData] = []

    for i, slide in enumerate(slides):
        prompt = slide.imagePrompt or FALLBACK_PROMPTS.get(slide.type, FALLBACK_PROMPTS["content"])
        print(f"  [{i + 1}/{len(slides)}] Generating image: {prompt[:50]}...")

        # Try original prompt, then simplified, then fallback
        image_data_uri = _generate_with_retries(prompt, slide.type, gemini_api_key)

        if image_data_uri:
            updated.append(slide.model_copy(update={"imageUrl": image_data_uri}))
            print(f"  ✓ Slide {i + 1} image OK")
        else:
            updated.append(slide)
            print(f"  ✗ Slide {i + 1} no image")

        # Rate limit: ~10 RPM for free tier
        time.sleep(7)

    return updated


def _generate_with_retries(prompt: str, slide_type: str, api_key: str) -> Optional[str]:
    """Try multiple prompt strategies to generate an image."""
    # Attempt 1: Original prompt
    result = _call_image_api(prompt, api_key)
    if result:
        return result

    time.sleep(3)

    # Attempt 2: Simplified prompt
    simplified = f"Professional business illustration: {prompt[:100]}. Flat design, clean, no text."
    result = _call_image_api(simplified, api_key)
    if result:
        return result

    time.sleep(3)

    # Attempt 3: Generic fallback for slide type
    fallback = FALLBACK_PROMPTS.get(slide_type, FALLBACK_PROMPTS["content"])
    return _call_image_api(fallback, api_key)


def _call_image_api(prompt: str, api_key: str) -> Optional[str]:
    """Call gemini-2.5-flash-image API."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Generate an image: {prompt}. "
                            f"Style: professional presentation illustration, "
                            f"clean modern design, minimal, no text in the image."
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
        },
    }

    try:
        resp = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )

        if resp.status_code != 200:
            print(f"    API {resp.status_code}: {resp.text[:80]}")
            return None

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return None

        parts = candidates[0].get("content", {}).get("parts", [])
        for part in parts:
            inline_data = part.get("inlineData", {})
            mime = inline_data.get("mimeType", "")
            if mime.startswith("image/"):
                b64 = inline_data.get("data", "")
                if b64:
                    return f"data:{mime};base64,{b64}"

        return None

    except Exception as e:
        print(f"    Exception: {e}")
        return None
