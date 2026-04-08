"use client";

import { THEMES, type PptxTheme } from "@/lib/themes";
import type { SlideData } from "@/lib/types";

interface SlidePreviewProps {
  slides: SlideData[];
  themeId: string;
}

export default function SlidePreview({ slides, themeId }: SlidePreviewProps) {
  const theme = THEMES.find((t) => t.id === themeId) ?? THEMES[0];

  return (
    <div className="grid grid-cols-2 gap-3">
      {slides.map((slide, i) => (
        <SlideCard key={i} slide={slide} index={i} theme={theme} />
      ))}
    </div>
  );
}

function SlideCard({
  slide,
  index,
  theme,
}: {
  slide: SlideData;
  index: number;
  theme: PptxTheme;
}) {
  const { colors } = theme;

  return (
    <div
      className="relative overflow-hidden rounded-lg border border-zinc-700/50 shadow-sm"
      style={{ backgroundColor: colors.bg, aspectRatio: "16/9" }}
    >
      <div className="flex h-full flex-col justify-center px-4 py-3">
        {slide.type === "cover" ? (
          <>
            <div
              className="mb-1 h-0.5 w-8 rounded-full"
              style={{ backgroundColor: colors.accent }}
            />
            <h3
              className="text-[11px] font-bold leading-tight"
              style={{ color: colors.text }}
            >
              {slide.title}
            </h3>
            {slide.subtitle && (
              <p
                className="mt-0.5 text-[8px]"
                style={{ color: colors.muted }}
              >
                {slide.subtitle}
              </p>
            )}
          </>
        ) : slide.type === "closing" ? (
          <div className="text-center">
            <h3
              className="text-[11px] font-bold"
              style={{ color: colors.text }}
            >
              {slide.title}
            </h3>
            <div
              className="mx-auto mt-1 h-0.5 w-6 rounded-full"
              style={{ backgroundColor: colors.accent }}
            />
          </div>
        ) : (
          <>
            <h3
              className="mb-1 text-[9px] font-bold"
              style={{ color: colors.text }}
            >
              {slide.title}
            </h3>
            {slide.bullets && (
              <ul className="space-y-0.5">
                {slide.bullets.slice(0, 4).map((b, j) => (
                  <li
                    key={j}
                    className="flex items-start gap-1 text-[7px] leading-tight"
                    style={{ color: colors.muted }}
                  >
                    <span
                      className="mt-[3px] h-1 w-1 shrink-0 rounded-full"
                      style={{ backgroundColor: colors.accent }}
                    />
                    {b}
                  </li>
                ))}
                {(slide.bullets.length ?? 0) > 4 && (
                  <li
                    className="text-[7px]"
                    style={{ color: colors.muted }}
                  >
                    +{slide.bullets.length - 4} more...
                  </li>
                )}
              </ul>
            )}
            {slide.description && !slide.bullets && (
              <p
                className="text-[7px] leading-tight"
                style={{ color: colors.muted }}
              >
                {slide.description.slice(0, 80)}
                {slide.description.length > 80 ? "..." : ""}
              </p>
            )}
          </>
        )}
      </div>
      {/* Slide number */}
      <span
        className="absolute bottom-1 right-2 text-[7px]"
        style={{ color: colors.muted }}
      >
        {index + 1}
      </span>
    </div>
  );
}
