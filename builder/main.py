"""PPT Builder - Main entry point for GitHub Actions."""

import json
import os
import sys

from file_parser import parse_all_files
from gemini_client import generate_slides
from slide_builder import build_pptx
from supabase_client import download_source_files, update_session_status


def main():
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

    try:
        # 1. Update status to building
        update_session_status(session_id, "building", supabase_url, supabase_key)
        print(f"Session {session_id}: status -> building")

        # 2. Download source files
        tmp_dir = download_source_files(session_id, supabase_url, supabase_key)
        print(f"Downloaded source files to {tmp_dir}")

        # 3. Parse all source files
        content = parse_all_files(tmp_dir)
        if not content.strip():
            raise RuntimeError("소스 파일에서 텍스트를 추출할 수 없습니다.")
        print(f"Parsed content: {len(content)} characters")

        # 4. Generate slides via Gemini
        update_session_status(session_id, "generating", supabase_url, supabase_key)
        print("Calling Gemini API for slide generation...")
        presentation = generate_slides(content, slide_count, supabase_url, supabase_key)
        print(f"Generated {len(presentation.slides)} slides")

        # 5. Build PPTX
        os.makedirs("builder/output", exist_ok=True)
        output_path = "builder/output/presentation.pptx"
        build_pptx(presentation.slides, output_path)
        print(f"PPTX saved to {output_path}")

        # 6. Update status to complete
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
