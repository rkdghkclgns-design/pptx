"use client";

import { useCallback, useRef, useState } from "react";
import { Upload, X, FileText, Link2 } from "lucide-react";
import { MAX_FILES, ACCEPTED_FILE_TYPES, MAX_FILE_SIZE_BYTES } from "@/lib/constants";
import type { UploadedFile } from "@/lib/types";

interface SourceUploaderProps {
  files: UploadedFile[];
  onFilesChange: (files: UploadedFile[]) => void;
  notebookUrl?: string | null;
  disabled?: boolean;
}

function isAcceptedType(name: string): boolean {
  return ACCEPTED_FILE_TYPES.some((ext) => name.toLowerCase().endsWith(ext));
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function SourceUploader({
  files,
  onFilesChange,
  notebookUrl,
  disabled,
}: SourceUploaderProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const sourceCount = files.length + (notebookUrl ? 1 : 0);

  const addFiles = useCallback(
    (incoming: FileList | File[]) => {
      const newFiles: UploadedFile[] = [];
      const remaining = MAX_FILES - files.length;

      for (const file of Array.from(incoming).slice(0, remaining)) {
        if (!isAcceptedType(file.name)) continue;
        if (file.size > MAX_FILE_SIZE_BYTES) continue;
        if (files.some((f) => f.name === file.name)) continue;

        newFiles.push({ file, name: file.name, size: file.size, type: file.type });
      }

      if (newFiles.length > 0) {
        onFilesChange([...files, ...newFiles]);
      }
    },
    [files, onFilesChange]
  );

  const removeFile = (name: string) => {
    onFilesChange(files.filter((f) => f.name !== name));
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (!disabled) addFiles(e.dataTransfer.files);
  };

  const handleClick = () => {
    if (!disabled) inputRef.current?.click();
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) addFiles(e.target.files);
    e.target.value = "";
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 text-sm text-zinc-400">
        <span className="text-base">&#x1F4C2;</span>
        <span className="font-semibold text-zinc-200">소스 데이터</span>
        <span className="rounded-full bg-zinc-700 px-2 py-0.5 text-xs">
          {sourceCount}/{MAX_FILES}
        </span>
      </div>

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed p-8 transition-colors ${
          isDragging
            ? "border-cyan-400 bg-cyan-400/5"
            : "border-zinc-700 bg-zinc-800/50 hover:border-zinc-500"
        } ${disabled ? "pointer-events-none opacity-50" : ""}`}
      >
        <Upload className="mb-3 h-8 w-8 text-zinc-500" />
        <p className="text-sm font-medium text-zinc-300">
          클릭하거나 여러 파일을 드래그 앤 드롭하세요
        </p>
        <p className="mt-1 text-xs text-zinc-500">
          최대 {MAX_FILES}개 지원 ({ACCEPTED_FILE_TYPES.join(", ")})
        </p>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept={ACCEPTED_FILE_TYPES.join(",")}
          onChange={handleInputChange}
          className="hidden"
        />
      </div>

      {/* NotebookLM source */}
      {notebookUrl && (
        <div className="flex items-center justify-between rounded-lg border border-emerald-500/20 bg-emerald-500/5 px-3 py-2">
          <div className="flex items-center gap-2 overflow-hidden">
            <Link2 className="h-4 w-4 shrink-0 text-emerald-400" />
            <span className="text-sm font-medium text-emerald-300">NotebookLM</span>
            <span className="truncate text-xs text-zinc-500">{notebookUrl}</span>
          </div>
        </div>
      )}

      {/* File list */}
      {files.length > 0 && (
        <div className="space-y-1.5">
          {files.map((f) => (
            <div
              key={f.name}
              className="flex items-center justify-between rounded-lg bg-zinc-800/70 px-3 py-2"
            >
              <div className="flex items-center gap-2 overflow-hidden">
                <FileText className="h-4 w-4 shrink-0 text-zinc-400" />
                <span className="truncate text-sm text-zinc-300">{f.name}</span>
                <span className="shrink-0 text-xs text-zinc-500">
                  {formatSize(f.size)}
                </span>
              </div>
              {!disabled && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    removeFile(f.name);
                  }}
                  className="ml-2 rounded p-1 text-zinc-500 hover:bg-zinc-700 hover:text-zinc-300"
                >
                  <X className="h-3.5 w-3.5" />
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {sourceCount === 0 && (
        <div className="rounded-xl bg-zinc-800/30 px-4 py-6 text-center text-sm text-zinc-500">
          첨부된 소스 데이터가 없습니다.
        </div>
      )}
    </div>
  );
}
