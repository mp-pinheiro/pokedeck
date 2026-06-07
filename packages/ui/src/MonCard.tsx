import type { Mon } from "./types";

const mult = (m: number) => (m === 0 ? "immune" : `x${m}`);

export function MonCard({ mon, label }: { mon: Mon; label?: string }) {
  const pct = mon.max_hp ? Math.round((mon.hp / mon.max_hp) * 100) : 0;
  return (
    <div style={{ fontSize: "0.9em", lineHeight: 1.45 }}>
      {label && <div style={{ opacity: 0.6, fontSize: "0.8em", textTransform: "uppercase" }}>{label}</div>}
      <div style={{ fontWeight: "bold" }}>
        {mon.shiny ? "★ " : ""}
        {mon.species} · Lv{mon.level}
      </div>
      <div>
        HP {mon.hp}/{mon.max_hp} ({pct}%) · {mon.types.join(" / ")}
      </div>
      {mon.ability && (
        <div>
          Ability: {mon.ability}
          {mon.item ? ` · Item: ${mon.item}` : ""}
        </div>
      )}
      {mon.weak.length > 0 && (
        <div style={{ color: "#ff6b6b" }}>Weak: {mon.weak.map(([t, m]) => `${t} ${mult(m)}`).join(", ")}</div>
      )}
      {mon.immune.length > 0 && <div>Immune: {mon.immune.join(", ")}</div>}
      <div>Moves: {mon.moves.map((mv) => (mv.pp != null ? `${mv.name} (${mv.pp})` : mv.name)).join(", ") || "—"}</div>
    </div>
  );
}
