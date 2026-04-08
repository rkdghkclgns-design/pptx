"""Generate real images for slides using Gemini 2.5 Flash native image generation."""

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
        image_data_uri = _generate_image_gemini(slide.imagePrompt, gemini_api_key)

        if image_data_uri:
            # Upload to Supabase Storage for persistent URL
            public_url = _upload_to_storage(
                image_data_uri, f"slide-{i}", supabase_url, supabase_key
            )
            updated.append(slide.model_copy(update={"imageUrl": public_url or image_data_uri}))
            print(f"  ✓ Image generated for slide {i + 1}")
        else:
            updated.append(slide)
            print(f"  ✗ Image generation failed for slide {i + 1}")

        # Rate limit: 10 RPM for free tier
        time.sleep(7)

    return updated


def _generate_image_gemini(prompt: str, api_key: str) -> Optional[str]:
    """Generate image using Gemini 2.5 Flash native image generation.

    Returns a data:image/png;base64,... URI or None on failure.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            f"Generate a professional, clean illustration image for a presentation slide. "
                            f"The image should visually represent: {prompt}. "
                            f"Style: modern flat design, minimal, corporate, 16:9 aspect ratio. "
                            f"No text in the image."
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
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
            print(f"    Gemini image API error: {resp.status_code} - {resp.text[:150]}")
            return None

        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return None

        parts = candidates[0].get("content", {}).get("parts", [])
        for part in parts:
            inline_data = part.get("inlineData", {})
            if inline_data.get("mimeType", "").startswith("image/"):
                b64 = inline_data["data"]
                mime = inline_data["mimeType"]
                return f"data:{mime};base64,{b64}"

        return None

    except Exception as e:
        print(f"    Image generation exception: {e}")
        return None


def _upload_to_storage(
    data_uri: str,
    filename: str,
    supabase_url: str,
    supabase_key: str,
) -> Optional[str]:
    """Upload a data URI image to Supabase Storage and return public URL."""
    try:
        # Parse data URI
        header, b64data = data_uri.split(",", 1)
        mime = header.split(":")[1].split(";")[0]
        ext = "png" if "png" in mime else "jpeg"
        image_bytes = base64.b64decode(b64data)

        path = f"generated/{filename}.{ext}"
        upload_url = f"{supabase_url}/storage/v1/object/source-files/{path}"

        resp = requests.post(
            upload_url,
            data=image_bytes,
            headers={
                "Authorization": f"Bearer {supabase_key}",
                "Content-Type": mime,
            },
            timeout=30,
        )

        if resp.status_code in (200, 201):
            return f"{supabase_url}/storage/v1/object/public/source-files/{path}"

        return None

    except Exception as e:
        print(f"    Upload failed: {e}")
        return None
