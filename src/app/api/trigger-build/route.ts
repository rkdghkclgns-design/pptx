import { NextResponse } from "next/server";

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_OWNER = process.env.GITHUB_OWNER ?? "rkdghkclgns-design";
const GITHUB_REPO = process.env.GITHUB_REPO ?? "pptx";

export async function POST(req: Request) {
  if (!GITHUB_TOKEN) {
    return NextResponse.json(
      { success: false, error: "GITHUB_TOKEN이 설정되지 않았습니다." },
      { status: 500 }
    );
  }

  const { sessionId, settings } = await req.json();

  if (!sessionId || !settings) {
    return NextResponse.json(
      { success: false, error: "sessionId와 settings가 필요합니다." },
      { status: 400 }
    );
  }

  const dispatchUrl = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/build-pptx.yml/dispatches`;

  const res = await fetch(dispatchUrl, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      Accept: "application/vnd.github.v3+json",
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ref: "main",
      inputs: {
        session_id: sessionId,
        settings: JSON.stringify(settings),
      },
    }),
  });

  if (!res.ok) {
    const errorText = await res.text();
    return NextResponse.json(
      { success: false, error: `GitHub API 오류: ${res.status} - ${errorText}` },
      { status: res.status }
    );
  }

  return NextResponse.json({ success: true });
}
