"""Generate real images for slides using Imagen 3 API."""

import base64
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

        # Rate limit protection
        time.sleep(5)

    return updated


def _generate_image(prompt: str, api_key: str) -> Optional[str]:
    """Generate image using Imagen 3 via Gemini API.

    Returns a data:image/png;base64,... URI or None on failure.
    """
    # Try Imagen 3 first
    result = _try_imagen3(prompt, api_key)
    if result:
        return result

    # Fallback: Gemini Flash with image output
    result = _try_gemini_flash_image(prompt, api_key)
    if result:
        return result

    return None


def _try_imagen3(prompt: str, api_key: str) -> Optional[str]:
    """Try Imagen 3 model for image generation."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
        payload = {
            "instances": [
                {
                    "prompt": (
                        f"Professional presentation slide illustration: {prompt}. "
                        f"Clean modern flat design, minimal style, no text, 16:9 aspect ratio."
                    )
                }
            ],
            "parameters": {
                "sampleCount": 1,
                "aspectRatio": "16:9",
            },
        }

        resp = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30,
        )

        if resp.status_code == 200:
            data = resp.json()
            predictions = data.get("predictions", [])
            if predictions:
                b64 = predictions[0].get("bytesBase64Encoded", "")
                if b64:
                    return f"data:image/png;base64,{b64}"

        print(f"    Imagen 3 returned {resp.status_code}: {resp.text[:100]}")
        return None

    except Exception as e:
        print(f"    Imagen 3 failed: {e}")
        return None


def _try_gemini_flash_image(prompt: str, api_key: str) -> Optional[str]:
    """Try Gemini 2.0 Flash with image generation capability."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                f"Generate an image: Professional presentation slide illustration about {prompt}. "
                                f"Clean modern flat design, minimal style, no text."
                            )
                        }
                    ]
                }
            ],
            "generationConfig": {
                "responseModalities": ["TEXT", "IMAGE"],
            },
        }

        resp = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60,
        )

        if resp.status_code != 200:
            print(f"    Gemini Flash image returned {resp.status_code}: {resp.text[:100]}")
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

        print(f"    Gemini Flash returned no image in response")
        return None

    except Exception as e:
        print(f"    Gemini Flash image failed: {e}")
        return None
