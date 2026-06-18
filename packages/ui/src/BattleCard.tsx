import type { Mon } from "./types";
import { Pressable } from "./Pressable";
import { Sprite } from "./Sprite";
import { Pill } from "./Pill";
import { HpBar } from "./HpBar";
import { Matchups } from "./Matchups";
import { typeColor, statusInfo, HUD_LABEL } from "./theme";

function Attr({ label, name, desc }: { label: string; name: string; desc: string | null }) {
  return (
    <div style={{ marginTop: 7, fontSize: "0.86em", lineHeight: 1.4 }}>
      <span style={{ ...HUD_LABEL, marginRight: 6, opacity: 0.5 }}>{label}</span>
      <span style={{ fontWeight: 700 }}>{name}</span>
      {desc && <span style={{ opacity: 0.62 }}> — {desc}</span>}
    </div>
  );
}

export function BattleCard({ mon, label, onOpen }: { mon: Mon; label: string; onOpen?: () => void }) {
  const accent = typeColor(mon.types[0]);
  const dex = mon.dex ?? mon.species_id;
  const status = statusInfo(mon.status);
  return (
    <Pressable
      onPress={onOpen}
      style={{
        padding: 12,
        borderRadius: 15,
        background: `linear-gradient(180deg, ${accent}1c, #ffffff05)`,
        border: "1px solid #ffffff12",
        borderLeft: `3px solid ${accent}`,
        boxShadow: `0 12px 30px -20px ${accent}`,
      }}
    >
      <div style={{ display: "flex", gap: 11 }}>
        <Sprite id={dex} size={58} alt={mon.species} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ ...HUD_LABEL, color: accent, opacity: 0.95 }}>{label}</div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 7, flexWrap: "wrap", marginTop: 2 }}>
            <span style={{ fontWeight: 800, fontSize: "1.12em" }}>
              {mon.shiny ? "✦ " : ""}
              {mon.species}
            </span>
            <span style={{ opacity: 0.55, fontSize: "0.82em" }}>Lv{mon.level}</span>
            {status && (
              <Pill bg={status.color} color="#15171c">
                {status.label}
              </Pill>
            )}
          </div>
          <div style={{ display: "flex", gap: 5, marginTop: 5, flexWrap: "wrap" }}>
            {mon.types.map((t) => (
              <Pill key={t} bg={typeColor(t)}>
                {t}
              </Pill>
            ))}
          </div>
        </div>
      </div>

      <Matchups weak={mon.weak} resist={mon.resist} immune={mon.immune} />

      {mon.ability && <Attr label="Ability" name={mon.ability} desc={mon.ability_desc} />}
      {mon.item && <Attr label="Item" name={`◈ ${mon.item}`} desc={mon.item_desc} />}

      <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 10 }}>
        <div style={{ flex: 1 }}>
          <HpBar hp={mon.hp} max={mon.max_hp} />
        </div>
        <span style={{ fontSize: "0.78em", opacity: 0.85, fontVariantNumeric: "tabular-nums" }}>
          {mon.hp}/{mon.max_hp}
        </span>
      </div>
    </Pressable>
  );
}
