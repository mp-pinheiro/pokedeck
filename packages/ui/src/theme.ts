// Shared visual tokens. Pure functions + constants, no host deps.

export const TYPE_COLORS: Record<string, string> = {
  Normal: "#A8A878", Fire: "#F08030", Water: "#6890F0", Electric: "#F8D030",
  Grass: "#78C850", Ice: "#98D8D8", Fighting: "#C03028", Poison: "#A040A0",
  Ground: "#E0C068", Flying: "#A890F0", Psychic: "#F85888", Bug: "#A8B820",
  Rock: "#B8A038", Ghost: "#705898", Dragon: "#7038F8", Dark: "#705848",
  Steel: "#B8B8D0", Fairy: "#EE99AC", "???": "#68A090", Stellar: "#9DB7C8",
};

export function typeColor(t: string | null | undefined): string {
  return (t && TYPE_COLORS[t]) || "#6b7280";
}

// Small uppercase section label used across cards/detail.
export const HUD_LABEL = {
  fontSize: "0.6em",
  fontWeight: 700,
  letterSpacing: 1.5,
  textTransform: "uppercase",
  opacity: 0.45,
} as const;

export function hpColor(pct: number): string {
  return pct > 50 ? "#46c66a" : pct > 20 ? "#f0b73c" : "#e8533f";
}

// status1 bitfield -> short badge label + color
const _STATUS: [number, string, string][] = [
  [0x80, "TOX", "#b552c0"],
  [0x40, "PAR", "#e6cf45"],
  [0x20, "FRZ", "#7fd2ee"],
  [0x10, "BRN", "#ef7d3a"],
  [0x08, "PSN", "#a855c7"],
];

export function statusInfo(status: number): { label: string; color: string } | null {
  if (!status) return null;
  for (const [mask, label, color] of _STATUS) {
    if (status & mask) return { label, color };
  }
  if (status & 0x07) return { label: "SLP", color: "#9aa3b2" };
  return null;
}

// PokeAPI pixel sprite (National-Dex id; forms above 1025 won't resolve -> fallback)
export function spriteUrl(id: number): string {
  return `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${id}.png`;
}

// Generation from National-Dex number (last dex id of each gen).
const _GEN_LAST = [151, 251, 386, 493, 649, 721, 809, 905, 1025];
const _ROMAN = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX"];

export function genInfo(dex: number | null | undefined): { num: number; label: string } | null {
  if (!dex || dex < 1) return null;
  for (let i = 0; i < _GEN_LAST.length; i++) {
    if (dex <= _GEN_LAST[i]) return { num: i + 1, label: `GEN ${_ROMAN[i]}` };
  }
  return null;
}
