import type { Move } from "./types";
import { typeColor } from "./theme";

// Damage category -> dot color (physical/special/status).
const CAT_COLOR: Record<string, string> = {
  physical: "#e5673f",
  special: "#4f86c6",
  status: "#9aa0aa",
};

function Stat({ label, value, title }: { label: string; value: string; title: string }) {
  return (
    <span title={title} style={{ display: "inline-flex", gap: 3, alignItems: "baseline" }}>
      <span style={{ opacity: 0.45, fontSize: "0.82em" }}>{label}</span>
      <span>{value}</span>
    </span>
  );
}

export function MoveList({ moves }: { moves: Move[] }) {
  if (!moves || moves.length === 0) return null;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 3, marginTop: 7 }}>
      {moves.map((mv, i) => {
        const c = typeColor(mv.type);
        const status = mv.category === "status";
        return (
          <div
            key={i}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 7,
              padding: "3px 8px",
              borderRadius: 8,
              background: `${c}20`,
              borderLeft: `3px solid ${c}`,
            }}
          >
            <span
              title={mv.category ?? undefined}
              style={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                flexShrink: 0,
                background: CAT_COLOR[mv.category ?? "status"] ?? "#9aa0aa",
              }}
            />
            <span
              style={{
                fontWeight: 700,
                fontSize: "0.82em",
                flex: 1,
                minWidth: 0,
                overflow: "hidden",
                textOverflow: "ellipsis",
                whiteSpace: "nowrap",
              }}
            >
              {mv.name}
            </span>
            <span
              style={{
                fontSize: "0.72em",
                opacity: 0.9,
                fontVariantNumeric: "tabular-nums",
                display: "flex",
                gap: 9,
                flexShrink: 0,
              }}
            >
              <Stat label="P" value={status || !mv.power ? "—" : String(mv.power)} title="power" />
              <Stat label="A" value={mv.accuracy ? `${mv.accuracy}` : "—"} title="accuracy (— = always hits)" />
              {mv.pp_max != null && (
                <Stat label="" value={mv.pp != null ? `${mv.pp}/${mv.pp_max}` : `${mv.pp_max}`} title="PP" />
              )}
            </span>
          </div>
        );
      })}
    </div>
  );
}
