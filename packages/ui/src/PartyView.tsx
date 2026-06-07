import type { PartyMon } from "./types";
import { Pill } from "./Pill";
import { Sprite } from "./Sprite";
import { HpBar } from "./HpBar";
import { typeColor, genInfo } from "./theme";

const HUD_LABEL = {
  fontSize: "0.6em",
  fontWeight: 700,
  letterSpacing: 1.5,
  textTransform: "uppercase",
  opacity: 0.45,
} as const;

function PartyRow({ m }: { m: PartyMon }) {
  const dex = m.dex ?? m.species_id;
  const gen = genInfo(dex);
  const accent = typeColor(m.types[0]);
  const fainted = m.hp <= 0;
  return (
    <div
      style={{
        display: "flex",
        gap: 10,
        padding: "8px 10px",
        borderRadius: 12,
        background: `linear-gradient(180deg, ${accent}12, #ffffff04)`,
        border: "1px solid #ffffff10",
        borderLeft: `3px solid ${accent}`,
        opacity: fainted ? 0.5 : 1,
      }}
    >
      <Sprite id={dex} size={46} alt={m.species} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 6 }}>
          <span style={{ fontWeight: 800, fontSize: "0.95em", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {m.shiny ? "✦ " : ""}
            {m.species}
          </span>
          <span style={{ flex: 1 }} />
          <span style={{ opacity: 0.55, fontSize: "0.78em" }}>Lv{m.level}</span>
          {gen && <span style={{ ...HUD_LABEL, opacity: 0.4 }}>{gen.label}</span>}
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 4, margin: "4px 0" }}>
          {m.types.map((t) => (
            <Pill key={t} bg={typeColor(t)}>
              {t}
            </Pill>
          ))}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ flex: 1 }}>
            <HpBar hp={m.hp} max={m.max_hp} />
          </div>
          <span style={{ fontSize: "0.72em", opacity: 0.8, fontVariantNumeric: "tabular-nums" }}>
            {m.hp}/{m.max_hp}
          </span>
        </div>
        {m.weak.length > 0 && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 5, alignItems: "center" }}>
            <span style={HUD_LABEL}>Weak</span>
            {m.weak.map(([t, mult]) => (
              <Pill key={t} bg={typeColor(t)}>
                {t} {mult >= 4 ? "×4" : "×2"}
              </Pill>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export function PartyView({ party, label }: { party?: PartyMon[]; label?: string }) {
  if (!party || party.length === 0) return null;
  return (
    <div style={{ marginTop: 14 }}>
      {label && <div style={{ ...HUD_LABEL, marginBottom: 6 }}>{label}</div>}
      <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
        {party.map((m, i) => (
          <PartyRow key={i} m={m} />
        ))}
      </div>
    </div>
  );
}
