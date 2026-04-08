"use client";

import { useState, useRef, useEffect } from "react";
import { LinkIcon, X, Check, AlertTriangle } from "lucide-react";

interface NotebookLMButtonProps {
  url: string | null;
  onUrlChange: (url: string | null) => void;
  onContentPaste: (content: string) => void;
  disabled?: boolean;
}

export default function NotebookLMButton({
  url,
  onUrlChange,
  onContentPaste,
  disabled,
}: NotebookLMButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState(url ?? "");
  const [pasteContent, setPasteContent] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setInputValue(url ?? "");
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen, url]);

  const handleSave = () => {
    const trimmedUrl = inputValue.trim();
    onUrlChange(trimmedUrl || null);

    // If content was pasted, pass it along
    if (pasteContent.trim()) {
      onContentPaste(pasteContent.trim());
    }

    setIsOpen(false);
  };

  const handleRemove = () => {
    onUrlChange(null);
    setInputValue("");
    setPasteContent("");
    setIsOpen(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) handleSave();
    if (e.key === "Escape") setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-xs font-medium transition-colors disabled:opacity-50 ${
          url
            ? "border-emerald-500/50 bg-emerald-500/20 text-emerald-300"
            : "border-emerald-500/30 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20"
        }`}
      >
        <LinkIcon className="h-3 w-3" />
        {url ? "NotebookLM 연결됨" : "NotebookLM 연결"}
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          <div className="absolute right-0 top-full z-50 mt-2 w-96 rounded-xl border border-zinc-700 bg-zinc-800 p-4 shadow-xl">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm font-medium text-zinc-200">
                NotebookLM 소스 연결
              </span>
              <button
                onClick={() => setIsOpen(false)}
                className="rounded p-1 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>

            {/* URL input */}
            <input
              ref={inputRef}
              type="url"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="https://notebooklm.google.com/notebook/..."
              className="w-full rounded-lg border border-zinc-600 bg-zinc-900 px-3 py-2 text-sm text-zinc-200 outline-none placeholder:text-zinc-500 focus:border-emerald-500"
            />

            {/* Warning + Content paste */}
            <div className="mt-3 rounded-lg border border-amber-500/20 bg-amber-500/5 p-2.5">
              <div className="flex items-start gap-2">
                <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-400" />
                <div className="text-[11px] leading-relaxed text-amber-300/80">
                  NotebookLM 노트북은 비공개라 AI가 직접 읽을 수 없습니다.
                  <strong className="text-amber-300"> 아래에 노트북 내용을 붙여넣어주세요.</strong>
                </div>
              </div>
              <textarea
                value={pasteContent}
                onChange={(e) => setPasteContent(e.target.value)}
                placeholder="NotebookLM에서 내용을 복사(Ctrl+A → Ctrl+C)하여 여기에 붙여넣기(Ctrl+V)"
                className="mt-2 h-32 w-full resize-none rounded-md border border-zinc-600 bg-zinc-900 px-2.5 py-2 text-xs text-zinc-200 outline-none placeholder:text-zinc-500 focus:border-emerald-500"
              />
            </div>

            <div className="mt-3 flex items-center gap-2">
              <button
                onClick={handleSave}
                disabled={!inputValue.trim() && !pasteContent.trim()}
                className="flex flex-1 items-center justify-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-medium text-white transition-colors hover:bg-emerald-500 disabled:opacity-50"
              >
                <Check className="h-3 w-3" />
                연결
              </button>
              {url && (
                <button
                  onClick={handleRemove}
                  className="rounded-lg border border-zinc-600 px-3 py-1.5 text-xs text-zinc-400 transition-colors hover:bg-zinc-700 hover:text-zinc-200"
                >
                  해제
                </button>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
