export interface PptxTheme {
  id: string;
  name: string;
  colors: {
    bg: string;
    card: string;
    accent: string;
    text: string;
    muted: string;
  };
}

export const THEMES: readonly PptxTheme[] = [
  {
    id: "navy",
    name: "네이비 블루",
    colors: { bg: "#0F172A", card: "#16203A", accent: "#06B6D4", text: "#FAFAFA", muted: "#A1A1AA" },
  },
  {
    id: "dark",
    name: "다크 모드",
    colors: { bg: "#18181B", card: "#27272A", accent: "#8B5CF6", text: "#FAFAFA", muted: "#A1A1AA" },
  },
  {
    id: "forest",
    name: "포레스트 그린",
    colors: { bg: "#14291E", card: "#1A3A28", accent: "#22C55E", text: "#FAFAFA", muted: "#A1A1AA" },
  },
  {
    id: "sunset",
    name: "선셋 오렌지",
    colors: { bg: "#1C1410", card: "#2A1E16", accent: "#F97316", text: "#FAFAFA", muted: "#A1A1AA" },
  },
  {
    id: "minimal",
    name: "미니멀 화이트",
    colors: { bg: "#FFFFFF", card: "#F4F4F5", accent: "#3B82F6", text: "#18181B", muted: "#71717A" },
  },
] as const;

export const DEFAULT_THEME = THEMES[0];
