import type { Mon, PartyMon } from "./types";
import { Pressable } from "./Pressable";
import { Sprite } from "./Sprite";
import { Pill } from "./Pill";
import { HpBar } from "./HpBar";
import { typeColor, HUD_LABEL } from "./theme";

// Compact, glanceable row: sprite + name/Lv + types + weakness summary + HP.
// No moves/ability/stats — those live in the drill-in detail, so nothing truncates.
export function MonRow({ mon, label, onOpen }: { mon: Mon | PartyMon; label?: string; onOpen?: () => void }) {
  const accent = typeColor(mon.types[0]);
  const dex = mon.dex ?? mon.species_id;
  const fainted = mon.hp <= 0;
  return (
    <Pressable
      onPress={onOpen}
      style={{
        display: "flex",
        gap: 10,
        padding: "9px 11px",
        borderRadius: 13,
        background: `linear-gradient(180deg, ${accent}14, #ffffff04)`,
        border: "1px solid #ffffff10",
        borderLeft: `3px solid ${accent}`,
        opacity: fainted ? 0.5 : 1,
      }}
    >
      <Sprite id={dex} size={42} alt={mon.species} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: "flex", alignItems: "baseline", gap: 7, flexWrap: "wrap" }}>
          {label && <span style={{ ...HUD_LABEL, opacity: 0.55 }}>{label}</span>}
          <span style={{ fontWeight: 800, fontSize: "0.98em" }}>
            {mon.shiny ? "✦ " : ""}
            {mon.species}
          </span>
          <span style={{ opacity: 0.5, fontSize: "0.78em" }}>Lv{mon.level}</span>
          {mon.types.map((t) => (
            <Pill key={t} bg={typeColor(t)}>
              {t}
            </Pill>
          ))}
        </div>
        {mon.weak.length > 0 && (
          <div style={{ display: "flex", flexWrap: "wrap", gap: 4, alignItems: "center", margin: "5px 0" }}>
            <span style={{ ...HUD_LABEL, opacity: 0.5 }}>Weak</span>
            {mon.weak.map(([t, m]) => (
              <Pill key={t} bg={typeColor(t)}>
                {t}
                {m >= 4 ? " ×4" : ""}
              </Pill>
            ))}
          </div>
        )}
        <HpBar hp={mon.hp} max={mon.max_hp} />
      </div>
    </Pressable>
  );
}
