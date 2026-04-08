"use client";

import { useState } from "react";
import { ChevronLeft, ChevronRight, Maximize2, Minimize2 } from "lucide-react";
import { THEMES, type PptxTheme } from "@/lib/themes";
import type { SlideData } from "@/lib/types";

interface SlidePreviewProps {
  slides: SlideData[];
  themeId: string;
}

export default function SlidePreview({ slides, themeId }: SlidePreviewProps) {
  const theme = THEMES.find((t) => t.id === themeId) ?? THEMES[0];
  const [current, setCurrent] = useState(0);
  const [fullscreen, setFullscreen] = useState(false);

  const prev = () => setCurrent((c) => Math.max(0, c - 1));
  const next = () => setCurrent((c) => Math.min(slides.length - 1, c + 1));

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowLeft") prev();
    if (e.key === "ArrowRight") next();
    if (e.key === "Escape") setFullscreen(false);
  };

  const slide = slides[current];
  if (!slide) return null;

  return (
    <div
      className={`flex flex-col ${fullscreen ? "fixed inset-0 z-50 bg-black" : "h-full"}`}
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      {/* Slide display */}
      <div className="relative flex flex-1 items-center justify-center overflow-hidden">
        <div
          className={`relative ${fullscreen ? "h-full w-full" : "w-full"}`}
          style={{ aspectRatio: fullscreen ? undefined : "16/9" }}
        >
          <SlideRenderer slide={slide} theme={theme} />
        </div>

        {/* Nav arrows */}
        {current > 0 && (
          <button
            onClick={prev}
            className="absolute left-2 top-1/2 -translate-y-1/2 rounded-full bg-black/50 p-2 text-white/80 backdrop-blur-sm transition-colors hover:bg-black/70"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
        )}
        {current < slides.length - 1 && (
          <button
            onClick={next}
            className="absolute right-2 top-1/2 -translate-y-1/2 rounded-full bg-black/50 p-2 text-white/80 backdrop-blur-sm transition-colors hover:bg-black/70"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Bottom bar */}
      <div className="flex items-center justify-between border-t border-zinc-800 bg-zinc-900/80 px-4 py-2">
        <span className="text-xs text-zinc-400">
          {current + 1} / {slides.length}
        </span>

        {/* Thumbnail strip */}
        <div className="flex gap-1">
          {slides.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrent(i)}
              className={`h-1.5 rounded-full transition-all ${
                i === current
                  ? "w-6 bg-cyan-400"
                  : "w-1.5 bg-zinc-600 hover:bg-zinc-400"
              }`}
            />
          ))}
        </div>

        <button
          onClick={() => setFullscreen((f) => !f)}
          className="rounded p-1 text-zinc-400 hover:bg-zinc-700 hover:text-zinc-200"
        >
          {fullscreen ? (
            <Minimize2 className="h-4 w-4" />
          ) : (
            <Maximize2 className="h-4 w-4" />
          )}
        </button>
      </div>
    </div>
  );
}

function SlideRenderer({
  slide,
  theme,
}: {
  slide: SlideData;
  theme: PptxTheme;
}) {
  const { colors } = theme;

  return (
    <div
      className="flex h-full w-full flex-col overflow-hidden rounded-lg"
      style={{ backgroundColor: colors.bg }}
    >
      {slide.type === "cover" ? (
        <CoverSlide slide={slide} colors={colors} />
      ) : slide.type === "closing" ? (
        <ClosingSlide slide={slide} colors={colors} />
      ) : slide.type === "quote" ? (
        <QuoteSlide slide={slide} colors={colors} />
      ) : slide.type === "section" ? (
        <SectionSlide slide={slide} colors={colors} />
      ) : slide.type === "twoColumn" ? (
        <TwoColumnSlide slide={slide} colors={colors} />
      ) : (
        <ContentSlide slide={slide} colors={colors} />
      )}
    </div>
  );
}

type ColorsProps = PptxTheme["colors"];

function CoverSlide({ slide, colors }: { slide: SlideData; colors: ColorsProps }) {
  return (
    <div className="flex h-full flex-col justify-center px-[8%]">
      <div
        className="mb-4 h-1 w-20 rounded-full"
        style={{ backgroundColor: colors.accent }}
      />
      <h1
        className="text-[2.5vw] font-bold leading-tight"
        style={{ color: colors.text }}
      >
        {slide.title}
      </h1>
      {slide.subtitle && (
        <p className="mt-3 text-[1.3vw]" style={{ color: colors.muted }}>
          {slide.subtitle}
        </p>
      )}
      {slide.imageUrl && (
        <img
          src={slide.imageUrl}
          alt=""
          className="mt-6 max-h-[30%] rounded-lg object-cover"
        />
      )}
    </div>
  );
}

function ContentSlide({ slide, colors }: { slide: SlideData; colors: ColorsProps }) {
  return (
    <div className="flex h-full flex-col px-[6%] py-[5%]">
      <h2
        className="mb-2 text-[1.8vw] font-bold"
        style={{ color: colors.text }}
      >
        {slide.title}
      </h2>
      <div className="mb-4 h-px w-full" style={{ backgroundColor: colors.muted + "33" }} />

      <div className="flex flex-1 gap-6">
        <div className={slide.imageUrl ? "flex-1" : "w-full"}>
          {slide.description && (
            <p className="mb-3 text-[1vw] leading-relaxed" style={{ color: colors.muted }}>
              {slide.description}
            </p>
          )}
          {slide.bullets && (
            <ul className="space-y-2">
              {slide.bullets.map((b, i) => (
                <li key={i} className="flex items-start gap-2 text-[1vw]">
                  <span
                    className="mt-[0.6em] h-1.5 w-1.5 shrink-0 rounded-full"
                    style={{ backgroundColor: colors.accent }}
                  />
                  <span style={{ color: colors.text }}>{b}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
        {slide.imageUrl && (
          <div className="flex w-[40%] items-center">
            <img
              src={slide.imageUrl}
              alt=""
              className="w-full rounded-lg object-cover"
            />
          </div>
        )}
      </div>
    </div>
  );
}

function TwoColumnSlide({ slide, colors }: { slide: SlideData; colors: ColorsProps }) {
  const bullets = slide.bullets ?? [];
  const mid = Math.ceil(bullets.length / 2);
  const left = bullets.slice(0, mid);
  const right = bullets.slice(mid);

  return (
    <div className="flex h-full flex-col px-[6%] py-[5%]">
      <h2 className="mb-4 text-[1.8vw] font-bold" style={{ color: colors.text }}>
        {slide.title}
      </h2>
      <div className="flex flex-1 gap-4">
        {[left, right].map((col, ci) => (
          <div
            key={ci}
            className="flex-1 rounded-xl p-4"
            style={{ backgroundColor: colors.card }}
          >
            <ul className="space-y-2">
              {col.map((b, i) => (
                <li key={i} className="flex items-start gap-2 text-[0.9vw]">
                  <span
                    className="mt-[0.5em] h-1.5 w-1.5 shrink-0 rounded-full"
                    style={{ backgroundColor: colors.accent }}
                  />
                  <span style={{ color: colors.text }}>{b}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}

function QuoteSlide({ slide, colors }: { slide: SlideData; colors: ColorsProps }) {
  return (
    <div className="flex h-full flex-col items-center justify-center px-[12%] text-center">
      <p className="text-[2vw] font-light italic leading-relaxed" style={{ color: colors.accent }}>
        &ldquo;{slide.description ?? slide.title}&rdquo;
      </p>
      {slide.subtitle && (
        <p className="mt-4 text-[1.1vw]" style={{ color: colors.muted }}>
          &mdash; {slide.subtitle}
        </p>
      )}
    </div>
  );
}

function SectionSlide({ slide, colors }: { slide: SlideData; colors: ColorsProps }) {
  return (
    <div className="flex h-full flex-col items-center justify-center text-center">
      <div className="mb-4 h-1 w-16 rounded-full" style={{ backgroundColor: colors.accent }} />
      <h2 className="text-[2.2vw] font-bold" style={{ color: colors.text }}>
        {slide.title}
      </h2>
      {slide.subtitle && (
        <p className="mt-2 text-[1.2vw]" style={{ color: colors.muted }}>
          {slide.subtitle}
        </p>
      )}
    </div>
  );
}

function ClosingSlide({ slide, colors }: { slide: SlideData; colors: ColorsProps }) {
  return (
    <div className="flex h-full flex-col items-center justify-center text-center">
      <h2 className="text-[2.5vw] font-bold" style={{ color: colors.text }}>
        {slide.title}
      </h2>
      {slide.subtitle && (
        <p className="mt-2 text-[1.2vw]" style={{ color: colors.muted }}>
          {slide.subtitle}
        </p>
      )}
      <div className="mt-6 h-1 w-16 rounded-full" style={{ backgroundColor: colors.accent }} />
    </div>
  );
}
