"""Final status updater - runs in the 'if: always()' step of GitHub Actions."""

import os
import sys

from supabase_client import update_session_status


def main():
    session_id = os.environ.get("SESSION_ID")
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    build_status = os.environ.get("BUILD_STATUS", "failure")
    run_id = os.environ.get("RUN_ID")

    if not session_id or not supabase_url or not supabase_key:
        print("Missing required environment variables")
        sys.exit(1)

    github_run_id = int(run_id) if run_id else None

    if build_status == "success":
        update_session_status(
            session_id, "complete", supabase_url, supabase_key,
            github_run_id=github_run_id
        )
    else:
        update_session_status(
            session_id, "error", supabase_url, supabase_key,
            error_message=f"GitHub Actions 빌드 실패: {build_status}",
            github_run_id=github_run_id
        )

    print(f"Session {session_id}: final status -> {build_status}, run_id -> {run_id}")


if __name__ == "__main__":
    main()
