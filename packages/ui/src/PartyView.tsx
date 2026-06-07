import type { PartyMon } from "./types";

export function PartyView({ party, label }: { party?: PartyMon[]; label?: string }) {
  if (!party || party.length === 0) return null;
  return (
    <div style={{ marginTop: 12 }}>
      {label && (
        <div style={{ opacity: 0.6, fontSize: "0.8em", textTransform: "uppercase", marginBottom: 4 }}>{label}</div>
      )}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
        {party.map((m, i) => {
          const pct = m.max_hp ? Math.round((m.hp / m.max_hp) * 100) : 0;
          return (
            <div
              key={i}
              style={{ border: "1px solid #333", borderRadius: 6, padding: "4px 8px", fontSize: "0.8em", minWidth: 92 }}
            >
              <div style={{ fontWeight: "bold" }}>
                {m.shiny ? "★ " : ""}
                {m.species}
              </div>
              <div style={{ opacity: 0.85 }}>
                Lv{m.level} · {m.hp}/{m.max_hp} ({pct}%)
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
