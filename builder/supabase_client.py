"""Supabase client for downloading source files and updating session status."""

import os
from pathlib import Path
from typing import Any

import requests


def get_session(
    session_id: str,
    supabase_url: str,
    supabase_key: str,
) -> dict[str, Any]:
    """Fetch session record from Supabase database."""
    url = f"{supabase_url}/rest/v1/sessions?id=eq.{session_id}&select=*"
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "apikey": supabase_key,
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    rows = resp.json()
    if not rows:
        raise RuntimeError(f"세션 {session_id}을(를) 찾을 수 없습니다.")
    return rows[0]


def download_source_files(
    session_id: str,
    supabase_url: str,
    supabase_key: str,
    output_dir: str = "./tmp",
) -> str:
    """Download all source files for a session from Supabase Storage.
    Returns the output directory. If no files exist, returns the empty directory.
    """
    os.makedirs(output_dir, exist_ok=True)

    # List objects in the session folder
    list_url = f"{supabase_url}/storage/v1/object/list/source-files"
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
    }

    resp = requests.post(
        list_url,
        json={"prefix": f"{session_id}/", "limit": 100},
        headers=headers,
        timeout=30,
    )
    resp.raise_for_status()
    objects = resp.json()

    if not objects:
        print(f"세션 {session_id}에 업로드된 파일이 없습니다. (NotebookLM만 사용 가능)")
        return output_dir

    # Download each file
    for obj in objects:
        name = obj.get("name", "")
        if not name:
            continue

        file_path = f"{session_id}/{name}"
        download_url = f"{supabase_url}/storage/v1/object/source-files/{file_path}"
        file_resp = requests.get(download_url, headers=headers, timeout=60)
        file_resp.raise_for_status()

        local_path = os.path.join(output_dir, name)
        Path(local_path).write_bytes(file_resp.content)

    return output_dir


def update_session_status(
    session_id: str,
    status: str,
    supabase_url: str,
    supabase_key: str,
    error_message: str | None = None,
    github_run_id: int | None = None,
) -> None:
    """Update session status in Supabase database."""
    url = f"{supabase_url}/rest/v1/sessions?id=eq.{session_id}"
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "apikey": supabase_key,
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    body: dict[str, Any] = {"status": status}
    if error_message is not None:
        body["error_message"] = error_message
    if github_run_id is not None:
        body["github_run_id"] = github_run_id

    resp = requests.patch(url, json=body, headers=headers, timeout=15)
    resp.raise_for_status()
