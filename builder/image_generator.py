"""Generate images via Supabase Edge Function (pptx-image-gen)."""

import time
from typing import Optional

import requests

from schemas.slide_schema import SlideData

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
    """Generate images for all slides via Edge Function."""
    updated: list[SlideData] = []

    for i, slide in enumerate(slides):
        prompt = slide.imagePrompt or FALLBACK_PROMPTS.get(slide.type, FALLBACK_PROMPTS["content"])
        print(f"  [{i + 1}/{len(slides)}] Generating image: {prompt[:50]}...")

        image_data_uri = _generate_with_retries(prompt, slide.type, supabase_url, supabase_key)

        if image_data_uri:
            updated.append(slide.model_copy(update={"imageUrl": image_data_uri}))
            print(f"  OK Slide {i + 1} image ready")
        else:
            updated.append(slide)
            print(f"  FAIL Slide {i + 1} no image")

        time.sleep(3)

    return updated


def _generate_with_retries(
    prompt: str,
    slide_type: str,
    supabase_url: str,
    supabase_key: str,
) -> Optional[str]:
    """Try multiple strategies to generate an image."""
    result = _call_edge_function(prompt, supabase_url, supabase_key)
    if result:
        return result

    time.sleep(2)

    simplified = f"Professional business illustration: {prompt[:100]}. Flat design, clean, no text."
    result = _call_edge_function(simplified, supabase_url, supabase_key)
    if result:
        return result

    time.sleep(2)

    fallback = FALLBACK_PROMPTS.get(slide_type, FALLBACK_PROMPTS["content"])
    return _call_edge_function(fallback, supabase_url, supabase_key)


def _call_edge_function(
    prompt: str,
    supabase_url: str,
    supabase_key: str,
) -> Optional[str]:
    """Call pptx-image-gen Edge Function."""
    url = f"{supabase_url}/functions/v1/pptx-image-gen"
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(url, json={"prompt": prompt}, headers=headers, timeout=60)

        if resp.status_code != 200:
            print(f"    Edge Function {resp.status_code}: {resp.text[:100]}")
            return None

        data = resp.json()
        return data.get("imageUrl")

    except Exception as e:
        print(f"    Exception: {e}")
        return None
