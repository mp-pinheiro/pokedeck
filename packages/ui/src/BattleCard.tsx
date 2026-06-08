import type { ReactNode } from "react";
import type { Mon } from "./types";
import { Pressable } from "./Pressable";
import { Sprite } from "./Sprite";
import { Pill } from "./Pill";
import { HpBar } from "./HpBar";
import { MoveList } from "./MoveList";
import { typeColor, statusInfo, HUD_LABEL } from "./theme";

// Aligned label/value row — every field hangs off the same label column so the
// type / weakness / immunity / ability / item blocks read as a clean table
// instead of a cluster of pills.
function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div style={{ display: "flex", gap: 9, alignItems: "baseline", marginTop: 7 }}>
      <span style={{ ...HUD_LABEL, width: 52, flexShrink: 0, opacity: 0.5, textAlign: "right" }}>{label}</span>
      <div style={{ flex: 1, minWidth: 0, display: "flex", flexWrap: "wrap", gap: 5, alignItems: "baseline" }}>
        {children}
      </div>
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
      <div style={{ display: "flex", gap: 11, alignItems: "center" }}>
        <Sprite id={dex} size={50} alt={mon.species} />
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
        </div>
      </div>

      <div style={{ marginTop: 4 }}>
        <Field label="Type">
          {mon.types.map((t) => (
            <Pill key={t} bg={typeColor(t)}>
              {t}
            </Pill>
          ))}
        </Field>
        {mon.weak.length > 0 && (
          <Field label="Weak">
            {mon.weak.map(([t, m]) => (
              <Pill key={t} bg={typeColor(t)}>
                {t}
                {m >= 4 ? " ×4" : ""}
              </Pill>
            ))}
          </Field>
        )}
        {mon.immune.length > 0 && (
          <Field label="Immune">
            {mon.immune.map((t) => (
              <Pill key={t} bg={typeColor(t)}>
                {t}
              </Pill>
            ))}
          </Field>
        )}
        {mon.ability && (
          <Field label="Ability">
            <span style={{ fontWeight: 700, fontSize: "0.9em" }}>{mon.ability}</span>
            {mon.ability_desc && <span style={{ fontSize: "0.82em", opacity: 0.6 }}>{mon.ability_desc}</span>}
          </Field>
        )}
        {mon.item && (
          <Field label="Item">
            <span style={{ fontWeight: 700, fontSize: "0.9em" }}>◈ {mon.item}</span>
            {mon.item_desc && <span style={{ fontSize: "0.82em", opacity: 0.6 }}>{mon.item_desc}</span>}
          </Field>
        )}
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 10 }}>
        <div style={{ flex: 1 }}>
          <HpBar hp={mon.hp} max={mon.max_hp} />
        </div>
        <span style={{ fontSize: "0.78em", opacity: 0.85, fontVariantNumeric: "tabular-nums" }}>
          {mon.hp}/{mon.max_hp}
        </span>
      </div>

      <MoveList moves={mon.moves} />
    </Pressable>
  );
}
