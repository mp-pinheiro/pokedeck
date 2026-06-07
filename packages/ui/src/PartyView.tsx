import type { PartyMon } from "./types";
import { Sprite } from "./Sprite";
import { HpBar } from "./HpBar";
import { genInfo } from "./theme";

export function PartyView({ party, label }: { party?: PartyMon[]; label?: string }) {
  if (!party || party.length === 0) return null;
  return (
    <div style={{ marginTop: 14 }}>
      {label && (
        <div
          style={{
            fontSize: "0.62em",
            fontWeight: 700,
            letterSpacing: 1.5,
            textTransform: "uppercase",
            opacity: 0.45,
            marginBottom: 6,
          }}
        >
          {label}
        </div>
      )}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
        {party.map((m, i) => {
          const dex = m.dex ?? m.species_id;
          const gen = genInfo(dex);
          return (
            <div
              key={i}
              style={{
                width: 88,
                padding: "8px 6px",
                borderRadius: 12,
                background: "#ffffff07",
                border: "1px solid #ffffff10",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: 3,
              }}
            >
              <Sprite id={dex} size={50} alt={m.species} />
              <div
                style={{
                  fontSize: "0.76em",
                  fontWeight: 700,
                  maxWidth: "100%",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                }}
              >
                {m.shiny ? "✦ " : ""}
                {m.species}
              </div>
              <div style={{ fontSize: "0.66em", opacity: 0.55, display: "flex", gap: 5 }}>
                <span>Lv{m.level}</span>
                {gen && <span style={{ opacity: 0.8, letterSpacing: 0.5 }}>{gen.label}</span>}
              </div>
              <div style={{ width: "100%" }}>
                <HpBar hp={m.hp} max={m.max_hp} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
