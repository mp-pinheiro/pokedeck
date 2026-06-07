import { HUD_LABEL } from "./theme";

const STAT_ORDER: [string, string][] = [
  ["hp", "HP"], ["atk", "Atk"], ["def", "Def"],
  ["spa", "SpA"], ["spd", "SpD"], ["spe", "Spe"],
];

// Color by fraction of the bar's max (works for base stats and IVs alike).
function barColor(pct: number): string {
  return pct >= 80 ? "#46c66a" : pct >= 50 ? "#8bcf3f" : pct >= 28 ? "#f0b73c" : "#e8835f";
}

export function StatBars({
  stats,
  max = 180,
  label,
  showTotal = true,
}: {
  stats: Record<string, number> | null | undefined;
  max?: number;
  label?: string;
  showTotal?: boolean;
}) {
  if (!stats) return null;
  const total = STAT_ORDER.reduce((s, [k]) => s + (stats[k] ?? 0), 0);
  return (
    <div>
      {label && <div style={{ ...HUD_LABEL, marginBottom: 6 }}>{label}</div>}
      <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
        {STAT_ORDER.map(([k, lbl]) => {
          const v = stats[k] ?? 0;
          const pct = Math.max(3, Math.min(100, (v / max) * 100));
          return (
            <div key={k} style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <span style={{ width: 30, fontSize: "0.68em", opacity: 0.55, letterSpacing: 0.5, textTransform: "uppercase" }}>
                {lbl}
              </span>
              <span style={{ width: 26, fontSize: "0.78em", textAlign: "right", fontVariantNumeric: "tabular-nums" }}>
                {v}
              </span>
              <div style={{ flex: 1, height: 7, borderRadius: 4, background: "#ffffff10", overflow: "hidden" }}>
                <div style={{ width: `${pct}%`, height: "100%", background: barColor(pct), borderRadius: 4, transition: "width .3s" }} />
              </div>
            </div>
          );
        })}
        {showTotal && (
          <div style={{ display: "flex", justifyContent: "flex-end", gap: 6, fontSize: "0.72em", marginTop: 2 }}>
            <span style={{ opacity: 0.5, letterSpacing: 1 }}>TOTAL</span>
            <span style={{ fontWeight: 800, fontVariantNumeric: "tabular-nums" }}>{total}</span>
          </div>
        )}
      </div>
    </div>
  );
}
