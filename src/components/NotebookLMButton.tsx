"use client";

import { useState, useRef, useEffect } from "react";
import { LinkIcon, X, Check } from "lucide-react";

interface NotebookLMButtonProps {
  url: string | null;
  onUrlChange: (url: string | null) => void;
  disabled?: boolean;
}

export default function NotebookLMButton({
  url,
  onUrlChange,
  disabled,
}: NotebookLMButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [inputValue, setInputValue] = useState(url ?? "");
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setInputValue(url ?? "");
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen, url]);

  const handleSave = () => {
    const trimmed = inputValue.trim();
    onUrlChange(trimmed || null);
    setIsOpen(false);
  };

  const handleRemove = () => {
    onUrlChange(null);
    setInputValue("");
    setIsOpen(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSave();
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
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* Dropdown */}
          <div className="absolute right-0 top-full z-50 mt-2 w-80 rounded-xl border border-zinc-700 bg-zinc-800 p-4 shadow-xl">
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm font-medium text-zinc-200">
                NotebookLM 공유 URL
              </span>
              <button
                onClick={() => setIsOpen(false)}
                className="rounded p-1 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>

            <input
              ref={inputRef}
              type="url"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="https://notebooklm.google.com/notebook/..."
              className="w-full rounded-lg border border-zinc-600 bg-zinc-900 px-3 py-2 text-sm text-zinc-200 outline-none placeholder:text-zinc-500 focus:border-emerald-500"
            />

            <div className="mt-3 flex items-center gap-2">
              <button
                onClick={handleSave}
                disabled={!inputValue.trim()}
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
