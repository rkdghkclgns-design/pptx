export type SlideType =
  | "cover"
  | "content"
  | "twoColumn"
  | "threeCards"
  | "table"
  | "quote"
  | "section"
  | "closing";

export interface SlideData {
  type: SlideType;
  title: string;
  subtitle?: string;
  description?: string;
  bullets?: string[];
  notes?: string;
  tableHeaders?: string[];
  tableRows?: string[][];
}

export interface SessionSettings {
  slideCount: number;
  duration: number;
  aiEngine: string;
}

export type SessionStatus =
  | "pending"
  | "uploading"
  | "triggered"
  | "building"
  | "generating"
  | "complete"
  | "error";

export interface Session {
  id: string;
  created_at: string;
  status: SessionStatus;
  settings: SessionSettings;
  file_paths: string[];
  github_run_id: number | null;
  artifact_url: string | null;
  error_message: string | null;
  slide_data: SlideData[] | null;
  updated_at: string;
}

export interface UploadedFile {
  file: File;
  name: string;
  size: number;
  type: string;
}
