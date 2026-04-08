import { NextResponse } from "next/server";

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_OWNER = process.env.GITHUB_OWNER ?? "rkdghkclgns-design";
const GITHUB_REPO = process.env.GITHUB_REPO ?? "pptx";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ runId: string }> }
) {
  const { runId } = await params;

  if (!GITHUB_TOKEN) {
    return NextResponse.json(
      { error: "GITHUB_TOKEN이 설정되지 않았습니다." },
      { status: 500 }
    );
  }

  // 1. Get artifacts for the run
  const artifactsUrl = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runs/${runId}/artifacts`;

  const artifactsRes = await fetch(artifactsUrl, {
    headers: {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      Accept: "application/vnd.github.v3+json",
    },
  });

  if (!artifactsRes.ok) {
    return NextResponse.json(
      { error: "아티팩트 조회에 실패했습니다." },
      { status: artifactsRes.status }
    );
  }

  const { artifacts } = await artifactsRes.json();

  if (!artifacts || artifacts.length === 0) {
    return NextResponse.json(
      { error: "아티팩트가 아직 준비되지 않았습니다." },
      { status: 404 }
    );
  }

  // 2. Get download URL for the first (PPTX) artifact
  const artifact = artifacts[0];
  const downloadUrl = `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/artifacts/${artifact.id}/zip`;

  // 3. Proxy the download (GitHub requires auth)
  const downloadRes = await fetch(downloadUrl, {
    headers: {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      Accept: "application/vnd.github.v3+json",
    },
    redirect: "follow",
  });

  if (!downloadRes.ok) {
    return NextResponse.json(
      { error: "다운로드에 실패했습니다." },
      { status: downloadRes.status }
    );
  }

  const blob = await downloadRes.blob();

  return new NextResponse(blob, {
    headers: {
      "Content-Type": "application/zip",
      "Content-Disposition": `attachment; filename="presentation-${runId}.zip"`,
    },
  });
}
