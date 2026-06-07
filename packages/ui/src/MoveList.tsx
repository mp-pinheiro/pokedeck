import type { Move } from "./types";
import { Tooltip } from "./Tooltip";
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

function Row({ mv }: { mv: Move }) {
  const c = typeColor(mv.type);
  const status = mv.category === "status";
  return (
    <div
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
        style={{ width: 6, height: 6, borderRadius: "50%", flexShrink: 0, background: CAT_COLOR[mv.category ?? "status"] ?? "#9aa0aa" }}
      />
      <span style={{ fontWeight: 700, fontSize: "0.82em", flex: 1, minWidth: 0, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
        {mv.name}
      </span>
      <span style={{ fontSize: "0.72em", opacity: 0.9, fontVariantNumeric: "tabular-nums", display: "flex", gap: 9, flexShrink: 0 }}>
        <Stat label="P" value={status || !mv.power ? "—" : String(mv.power)} title="power" />
        <Stat label="A" value={mv.accuracy ? `${mv.accuracy}` : "—"} title="accuracy (— = always hits)" />
        {mv.pp_max != null && <Stat label="" value={mv.pp != null ? `${mv.pp}/${mv.pp_max}` : `${mv.pp_max}`} title="PP" />}
      </span>
    </div>
  );
}

function cap(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

function MoveTip({ mv }: { mv: Move }) {
  return (
    <div>
      <div style={{ fontWeight: 800, marginBottom: 2 }}>{mv.name}</div>
      <div style={{ opacity: 0.85 }}>
        {mv.type ?? "—"}
        {mv.category ? ` · ${cap(mv.category)}` : ""}
      </div>
      <div style={{ opacity: 0.7, marginTop: 2, fontVariantNumeric: "tabular-nums" }}>
        Power {mv.power || "—"} · Acc {mv.accuracy ? `${mv.accuracy}%` : "—"} · PP {mv.pp_max ?? "—"}
        {mv.priority ? ` · Prio ${mv.priority > 0 ? "+" : ""}${mv.priority}` : ""}
      </div>
      {mv.desc && <div style={{ marginTop: 5, opacity: 0.85 }}>{mv.desc}</div>}
    </div>
  );
}

export function MoveList({ moves, tooltips = false }: { moves: Move[]; tooltips?: boolean }) {
  if (!moves || moves.length === 0) return null;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 3, marginTop: 7 }}>
      {moves.map((mv, i) =>
        tooltips ? (
          <Tooltip key={i} content={<MoveTip mv={mv} />} width={240}>
            <Row mv={mv} />
          </Tooltip>
        ) : (
          <Row key={i} mv={mv} />
        ),
      )}
    </div>
  );
}
