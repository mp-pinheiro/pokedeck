import type { Move } from "./types";
import { typeColor } from "./theme";

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

// Line 1: name + power/accuracy. Line 2: type · category (so you can read the
// move's typing and whether it's physical/special at a glance). Detailed adds
// PP, priority, and the effect text.
function Row({ mv, detailed }: { mv: Move; detailed?: boolean }) {
  const c = typeColor(mv.type);
  const status = mv.category === "status";
  return (
    <div style={{ padding: "5px 9px", borderRadius: 8, background: `${c}1e`, borderLeft: `3px solid ${c}` }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <span style={{ fontWeight: 700, fontSize: "0.86em", flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
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
      <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 2, fontSize: "0.68em" }}>
        <span style={{ color: c, fontWeight: 700 }}>{mv.type ?? "—"}</span>
        <span style={{ opacity: 0.35 }}>·</span>
        <span style={{ opacity: 0.7 }}>{mv.category ? cap(mv.category) : "—"}</span>
        {detailed && mv.priority ? (
          <>
            <span style={{ opacity: 0.35 }}>·</span>
            <span style={{ opacity: 0.7 }}>
              Prio {mv.priority > 0 ? "+" : ""}
              {mv.priority}
            </span>
          </>
        ) : null}
      </div>
      {detailed && mv.desc && (
        <div style={{ fontSize: "0.72em", opacity: 0.68, marginTop: 3, lineHeight: 1.35 }}>{mv.desc}</div>
      )}
    </div>
  );
}

export function MoveList({ moves, detailed = false }: { moves: Move[]; detailed?: boolean }) {
  if (!moves || moves.length === 0) return null;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4, marginTop: 7 }}>
      {moves.map((mv, i) => (
        <Row key={i} mv={mv} detailed={detailed} />
      ))}
    </div>
  );
}
