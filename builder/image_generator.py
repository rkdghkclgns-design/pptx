"""Generate real images for slides using Gemini 2.5 Flash Image model."""

import os
import time
from typing import Optional

import requests

from schemas.slide_schema import SlideData


def generate_slide_images(
    slides: list[SlideData],
    supabase_url: str,
    supabase_key: str,
) -> list[SlideData]:
    """Generate images for slides that have imagePrompt."""
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_api_key:
        print("GEMINI_API_KEY not set, skipping image generation")
        return list(slides)

    updated: list[SlideData] = []

    for i, slide in enumerate(slides):
        if not slide.imagePrompt or slide.type in ("closing",):
            updated.append(slide)
            continue

        print(f"  Generating image for slide {i + 1}: {slide.imagePrompt[:60]}...")
        image_data_uri = _generate_image(slide.imagePrompt, gemini_api_key)

        if image_data_uri:
            updated.append(slide.model_copy(update={"imageUrl": image_data_uri}))
            print(f"  ✓ Image generated for slide {i + 1}")
        else:
            updated.append(slide)
            print(f"  ✗ Image generation failed for slide {i + 1}")

        # Rate limit: ~10 RPM
        time.sleep(7)

    return updated


def _generate_image(prompt: str, api_key: str) -> Optional[str]:
    """Generate image using gemini-2.5-flash-image model.

    Returns a data:image/png;base64,... URI or None on failure.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Generate an image: Professional presentation slide illustration about: {prompt}. "
                            f"Style: clean modern flat design, minimal, corporate colors, no text in the image."
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
            print(f"    Image API error {resp.status_code}: {resp.text[:150]}")
            return None

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            print("    No candidates in image response")
            return None

        parts = candidates[0].get("content", {}).get("parts", [])
        for part in parts:
            inline_data = part.get("inlineData", {})
            mime = inline_data.get("mimeType", "")
            if mime.startswith("image/"):
                b64 = inline_data.get("data", "")
                if b64:
                    return f"data:{mime};base64,{b64}"

        print("    No image data in response parts")
        return None

    except Exception as e:
        print(f"    Image generation exception: {e}")
        return None
