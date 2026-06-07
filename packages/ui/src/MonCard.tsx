import type { Mon } from "./types";
import { Pill } from "./Pill";
import { Sprite } from "./Sprite";
import { HpBar } from "./HpBar";
import { MoveList } from "./MoveList";
import { typeColor, statusInfo, genInfo } from "./theme";

const HUD_LABEL = {
  fontSize: "0.62em",
  fontWeight: 700,
  letterSpacing: 1.5,
  textTransform: "uppercase",
  opacity: 0.45,
} as const;

export function MonCard({ mon, label }: { mon: Mon; label?: string }) {
  const accent = typeColor(mon.types[0]);
  const status = statusInfo(mon.status);
  const dex = mon.dex ?? mon.species_id;
  const gen = genInfo(dex);
  return (
    <div
      style={{
        display: "flex",
        gap: 12,
        padding: 12,
        borderRadius: 16,
        background: `linear-gradient(180deg, ${accent}16, #ffffff05)`,
        border: "1px solid #ffffff12",
        borderLeft: `3px solid ${accent}`,
        boxShadow: `0 12px 30px -18px ${accent}, inset 0 1px 0 #ffffff0a`,
      }}
    >
      <Sprite id={dex} size={76} alt={mon.species} />
      <div style={{ flex: 1, minWidth: 0 }}>
        {label && <div style={HUD_LABEL}>{label}</div>}
        <div style={{ display: "flex", alignItems: "baseline", gap: 7, flexWrap: "wrap" }}>
          <span style={{ fontWeight: 800, fontSize: "1.08em" }}>
            {mon.shiny ? "✦ " : ""}
            {mon.species}
          </span>
          <span style={{ opacity: 0.55, fontSize: "0.82em" }}>Lv{mon.level}</span>
          {gen && (
            <Pill bg="#ffffff12" color="#9fb1c6" title={`#${dex} · National Dex`}>
              {gen.label}
            </Pill>
          )}
          {status && (
            <Pill bg={status.color} color="#15171c">
              {status.label}
            </Pill>
          )}
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 5, margin: "6px 0" }}>
          {mon.types.map((t) => (
            <Pill key={t} bg={typeColor(t)}>
              {t}
            </Pill>
          ))}
          {mon.ability && (
            <Pill bg="#ffffff14" color="#cfe0ee">
              {mon.ability}
            </Pill>
          )}
          {mon.item && (
            <Pill bg="#ffffff14" color="#cfe0ee">
              ◈ {mon.item}
            </Pill>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 9 }}>
          <div style={{ flex: 1 }}>
            <HpBar hp={mon.hp} max={mon.max_hp} />
          </div>
          <span style={{ fontSize: "0.78em", fontVariantNumeric: "tabular-nums", opacity: 0.85 }}>
            {mon.hp}/{mon.max_hp}
          </span>
        </div>
        {mon.weak.length > 0 && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginTop: 7, alignItems: "center" }}>
            <span style={HUD_LABEL}>Weak</span>
            {mon.weak.map(([t, m]) => (
              <Pill key={t} bg={typeColor(t)}>
                {t} {m >= 4 ? "×4" : "×2"}
              </Pill>
            ))}
          </div>
        )}
        <MoveList moves={mon.moves} />
      </div>
    </div>
  );
}
