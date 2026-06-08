import type { Mon } from "./types";
import { Pressable } from "./Pressable";
import { Sprite } from "./Sprite";
import { Pill } from "./Pill";
import { HpBar } from "./HpBar";
import { WeakPills } from "./WeakPills";
import { MoveList } from "./MoveList";
import { typeColor, statusInfo, HUD_LABEL } from "./theme";

// Full active-battler card — identical layout for your mon and the opponent's:
// types, Weak to, HP (with numbers), and the move list. Tap (A) for full detail.
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
        <Sprite id={dex} size={50} alt={mon.species} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ ...HUD_LABEL, color: accent, opacity: 0.95 }}>{label}</div>
          <div style={{ display: "flex", alignItems: "baseline", gap: 7, flexWrap: "wrap", marginTop: 2 }}>
            <span style={{ fontWeight: 800, fontSize: "1.08em" }}>
              {mon.shiny ? "✦ " : ""}
              {mon.species}
            </span>
            <span style={{ opacity: 0.55, fontSize: "0.8em" }}>Lv{mon.level}</span>
            {status && (
              <Pill bg={status.color} color="#15171c">
                {status.label}
              </Pill>
            )}
            {mon.types.map((t) => (
              <Pill key={t} bg={typeColor(t)}>
                {t}
              </Pill>
            ))}
          </div>
        </div>
      </div>

      <WeakPills weak={mon.weak} />

      <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 8 }}>
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
