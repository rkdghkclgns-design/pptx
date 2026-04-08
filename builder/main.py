"""PPT Builder - Main entry point for GitHub Actions."""

import json
import os
import sys

from file_parser import parse_all_files
from gemini_client import generate_slides
from image_generator import generate_slide_images
from notebook_fetcher import fetch_notebook_content
from slide_builder import build_pptx
from supabase_client import download_source_files, get_gemini_api_key, get_session, update_session_status


def main() -> None:
    session_id = os.environ.get("SESSION_ID")
    settings_json = os.environ.get("SETTINGS", "{}")
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

    if not session_id:
        print("ERROR: SESSION_ID is required")
        sys.exit(1)

    if not supabase_url or not supabase_key:
        print("ERROR: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")
        sys.exit(1)

    settings = json.loads(settings_json)
    slide_count = settings.get("slideCount", 5)

    # Fetch Gemini API key from Supabase DB (paid key) if not in env
    if not os.environ.get("GEMINI_API_KEY"):
        db_key = get_gemini_api_key(supabase_url, supabase_key)
        if db_key:
            os.environ["GEMINI_API_KEY"] = db_key
            print("Using Gemini API key from Supabase DB")

    try:
        # 1. Update status to building
        update_session_status(session_id, "building", supabase_url, supabase_key)
        print(f"Session {session_id}: status -> building")

        # 2. Fetch session to get notebook_url
        session = get_session(session_id, supabase_url, supabase_key)
        notebook_url = session.get("notebook_url")
        print(f"Notebook URL: {notebook_url or 'none'}")

        # 3. Download source files (may be empty if only NotebookLM)
        tmp_dir = download_source_files(session_id, supabase_url, supabase_key)

        # 4. Parse all source files
        content_parts: list[str] = []

        file_content = parse_all_files(tmp_dir)
        if file_content.strip():
            content_parts.append(file_content)
            print(f"Parsed file content: {len(file_content)} characters")

        # 5. Fetch NotebookLM content if URL provided
        has_notebook = False
        if notebook_url and notebook_url.startswith("http"):
            nb_content = fetch_notebook_content(notebook_url)
            if nb_content.strip():
                content_parts.append(f"=== NotebookLM Source ===\n{nb_content}")
                print(f"Fetched NotebookLM content: {len(nb_content)} characters")
            else:
                # JS-rendered page — Gemini will use Google Search grounding
                has_notebook = True
                print(f"NotebookLM is JS-rendered, Gemini will use Search grounding")

        content = "\n\n".join(content_parts)
        if not content.strip() and not has_notebook:
            raise RuntimeError("소스 데이터에서 텍스트를 추출할 수 없습니다. 파일을 업로드하거나 NotebookLM URL을 확인하세요.")
        if not content.strip() and has_notebook:
            content = f"Please create a presentation based on the content at this URL: {notebook_url}"
        print(f"Total content: {len(content)} characters")

        # 6. Generate slides via Gemini
        update_session_status(session_id, "generating", supabase_url, supabase_key)
        print("Calling Gemini API for slide generation...")
        presentation = generate_slides(
            content, slide_count, supabase_url, supabase_key,
            notebook_url=notebook_url,
        )
        print(f"Generated {len(presentation.slides)} slides")

        # 7. Generate images for slides
        print("Generating slide images...")
        slides_with_images = generate_slide_images(
            presentation.slides, supabase_url, supabase_key
        )
        print(f"Images generated for {sum(1 for s in slides_with_images if s.imageUrl)} slides")

        # 8. Save slide data to session for preview
        slide_data_json = [s.model_dump() for s in slides_with_images]
        update_session_status(
            session_id, "generating", supabase_url, supabase_key,
            slide_data=slide_data_json
        )

        # 9. Build PPTX
        os.makedirs("output", exist_ok=True)
        output_path = "output/presentation.pptx"
        build_pptx(slides_with_images, output_path)
        print(f"PPTX saved to {output_path}")

        # 9. Update status to complete
        update_session_status(session_id, "complete", supabase_url, supabase_key)
        print("Build complete!")

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        update_session_status(
            session_id, "error", supabase_url, supabase_key,
            error_message=str(e)
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
