import type { Move } from "./types";
import { typeColor } from "./theme";

// Damage category -> dot color (physical/special/status).
const CAT_COLOR: Record<string, string> = {
  physical: "#e5673f",
  special: "#4f86c6",
  status: "#9aa0aa",
};

function cap(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function Stat({ label, value, title }: { label: string; value: string; title: string }) {
  return (
    <span title={title} style={{ display: "inline-flex", gap: 3, alignItems: "baseline" }}>
      <span style={{ opacity: 0.45, fontSize: "0.82em" }}>{label}</span>
      <span>{value}</span>
    </span>
  );
}

// Compact: name gets priority, only power/accuracy alongside (PP/desc would crowd
// the name and truncate it). Detailed (detail page): + PP + effect text.
function Row({ mv, detailed }: { mv: Move; detailed?: boolean }) {
  const c = typeColor(mv.type);
  const status = mv.category === "status";
  const meta =
    (mv.category ? cap(mv.category) : "") +
    (mv.priority ? `${mv.category ? " · " : ""}Prio ${mv.priority > 0 ? "+" : ""}${mv.priority}` : "");
  return (
    <div style={{ padding: "4px 8px", borderRadius: 8, background: `${c}20`, borderLeft: `3px solid ${c}` }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span
          title={mv.category ?? undefined}
          style={{ width: 6, height: 6, borderRadius: "50%", flexShrink: 0, background: CAT_COLOR[mv.category ?? "status"] ?? "#9aa0aa" }}
        />
        <span style={{ fontWeight: 700, fontSize: "0.85em", flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
          {mv.name}
        </span>
        <span style={{ fontSize: "0.72em", opacity: 0.85, fontVariantNumeric: "tabular-nums", display: "flex", gap: 9, flexShrink: 0 }}>
          <Stat label="P" value={status || !mv.power ? "—" : String(mv.power)} title="power" />
          <Stat label="A" value={mv.accuracy ? `${mv.accuracy}` : "—"} title="accuracy (— = always hits)" />
          {detailed && mv.pp_max != null && (
            <Stat label="" value={mv.pp != null ? `${mv.pp}/${mv.pp_max}` : `${mv.pp_max}`} title="PP" />
          )}
        </span>
      </div>
      {detailed && (mv.desc || meta) && (
        <div style={{ fontSize: "0.72em", opacity: 0.68, marginTop: 3, paddingLeft: 14, lineHeight: 1.35 }}>
          {meta}
          {meta && mv.desc ? " — " : ""}
          {mv.desc}
        </div>
      )}
    </div>
  );
}

export function MoveList({ moves, detailed = false }: { moves: Move[]; detailed?: boolean }) {
  if (!moves || moves.length === 0) return null;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: detailed ? 5 : 3, marginTop: 7 }}>
      {moves.map((mv, i) => (
        <Row key={i} mv={mv} detailed={detailed} />
      ))}
    </div>
  );
}
