"""Generate images for slides using Gemini Imagen API via Supabase image-gen edge function."""

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
    """Generate images for slides that have imagePrompt.

    Uses the existing image-gen edge function on Supabase, or falls back
    to a placeholder if unavailable.
    """
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
    updated: list[SlideData] = []

    for i, slide in enumerate(slides):
        if not slide.imagePrompt or slide.type in ("closing",):
            updated.append(slide)
            continue

        print(f"  Generating image for slide {i + 1}: {slide.imagePrompt[:50]}...")
        image_url = _generate_image(slide.imagePrompt, gemini_api_key)

        if image_url:
            updated.append(slide.model_copy(update={"imageUrl": image_url}))
        else:
            updated.append(slide)

        # Rate limit protection
        time.sleep(1)

    return updated


def _generate_image(prompt: str, api_key: str) -> Optional[str]:
    """Generate image using Gemini Imagen API and return URL.

    Uses the Gemini imagen model to generate an image, then uploads
    to a free image host or returns a data URI.
    """
    if not api_key:
        return None

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
        payload = {
            "instances": [
                {"prompt": f"Professional presentation slide illustration: {prompt}. Clean, modern, minimal style."}
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
                image_bytes = predictions[0].get("bytesBase64Encoded", "")
                if image_bytes:
                    return f"data:image/png;base64,{image_bytes}"

        # If Imagen fails, try with Gemini Flash image generation
        return _generate_with_gemini_flash(prompt, api_key)

    except Exception as e:
        print(f"  Image generation failed: {e}")
        return None


def _generate_with_gemini_flash(prompt: str, api_key: str) -> Optional[str]:
    """Fallback: Use Gemini Flash to generate a simple SVG-based illustration."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"""Generate a simple, clean SVG illustration for a presentation slide about: {prompt}

Requirements:
- Return ONLY the SVG code, no explanation
- Use a 800x450 viewBox (16:9 ratio)
- Use modern, flat design style
- Maximum 5-6 shapes
- Use colors: #06B6D4 (cyan), #3B82F6 (blue), #8B5CF6 (purple)
- Transparent or dark (#0F172A) background
- Simple geometric shapes and icons"""
                        }
                    ]
                }
            ],
            "generationConfig": {"temperature": 0.5, "maxOutputTokens": 2048},
        }

        resp = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        if resp.status_code != 200:
            return None

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return None

        text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")

        # Extract SVG from response
        svg_start = text.find("<svg")
        svg_end = text.find("</svg>")
        if svg_start >= 0 and svg_end > svg_start:
            svg = text[svg_start : svg_end + 6]
            import base64
            encoded = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
            return f"data:image/svg+xml;base64,{encoded}"

        return None

    except Exception as e:
        print(f"  SVG generation fallback failed: {e}")
        return None
