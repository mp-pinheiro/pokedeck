import type { Mon, PartyMon } from "./types";
import { Pressable } from "./Pressable";
import { Sprite } from "./Sprite";
import { Pill } from "./Pill";
import { HpBar } from "./HpBar";
import { Matchups } from "./Matchups";
import { typeColor, HUD_LABEL } from "./theme";

// Compact bench row: sprite + name/Lv + types + Weak to + HP (with numbers).
// No moves — benches are secondary; tap (A) for the full detail.
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
        <Matchups weak={mon.weak} resist={mon.resist} immune={mon.immune} />
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 6 }}>
          <div style={{ flex: 1 }}>
            <HpBar hp={mon.hp} max={mon.max_hp} />
          </div>
          <span style={{ fontSize: "0.72em", opacity: 0.8, fontVariantNumeric: "tabular-nums" }}>
            {mon.hp}/{mon.max_hp}
          </span>
        </div>
      </div>
    </Pressable>
  );
}
