export const MAX_FILES = 20;
export const ACCEPTED_FILE_TYPES = [".md", ".txt", ".pdf", ".pptx"];
export const MAX_FILE_SIZE_MB = 50;
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

export const POLL_INTERVAL_MS = 3000;

export const AI_ENGINE = {
  value: "gemini-2.5-pro",
  label: "Google Gemini 2.5 Pro",
} as const;

export const SESSION_STATUS_STEPS = [
  { key: "uploading", label: "파일 업로드 중..." },
  { key: "triggered", label: "빌드 트리거 중..." },
  { key: "building", label: "콘텐츠 생성 중..." },
  { key: "generating", label: "PPTX 생성 중..." },
  { key: "complete", label: "완료!" },
] as const;

export const STORAGE_BUCKET = "source-files";
