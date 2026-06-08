import type { Mon } from "./types";
import { Pressable } from "./Pressable";
import { Sprite } from "./Sprite";
import { Pill } from "./Pill";
import { HpBar } from "./HpBar";
import { typeColor, statusInfo, HUD_LABEL } from "./theme";

// Big, glanceable "what beats this mon" tile — the primary thing you read mid-battle.
function Tile({ t, m }: { t: string; m: number }) {
  const c = typeColor(t);
  const quad = m >= 4;
  return (
    <div
      style={{
        display: "flex",
        alignItems: "baseline",
        gap: 6,
        padding: "8px 14px",
        borderRadius: 12,
        background: c,
        color: "#0e1117",
        fontWeight: 800,
        fontSize: quad ? "1.1em" : "1em",
        letterSpacing: 0.3,
        boxShadow: quad ? `0 0 18px ${c}` : `0 4px 12px -5px ${c}`,
      }}
    >
      {t}
      <span style={{ fontSize: "0.76em", opacity: 0.85 }}>×{quad ? 4 : 2}</span>
    </div>
  );
}

export function WeaknessHero({ mon, label, onOpen }: { mon: Mon; label: string; onOpen?: () => void }) {
  const accent = typeColor(mon.types[0]);
  const dex = mon.dex ?? mon.species_id;
  const status = statusInfo(mon.status);
  return (
    <Pressable
      onPress={onOpen}
      style={{
        padding: 13,
        borderRadius: 16,
        background: `linear-gradient(180deg, ${accent}22, #ffffff06)`,
        border: "1px solid #ffffff14",
        borderLeft: `4px solid ${accent}`,
        boxShadow: `0 14px 34px -20px ${accent}`,
      }}
    >
      <div style={{ ...HUD_LABEL, color: accent, opacity: 0.95 }}>{label}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 11, marginTop: 4 }}>
        <Sprite id={dex} size={54} alt={mon.species} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "baseline", gap: 7, flexWrap: "wrap" }}>
            <span style={{ fontWeight: 800, fontSize: "1.18em" }}>
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
          <div style={{ display: "flex", gap: 5, marginTop: 4, flexWrap: "wrap" }}>
            {mon.types.map((t) => (
              <Pill key={t} bg={typeColor(t)}>
                {t}
              </Pill>
            ))}
          </div>
        </div>
      </div>

      <div style={{ ...HUD_LABEL, marginTop: 12, marginBottom: 7 }}>Hit with</div>
      {mon.weak.length > 0 ? (
        <div style={{ display: "flex", flexWrap: "wrap", gap: 7 }}>
          {mon.weak.map(([t, m]) => (
            <Tile key={t} t={t} m={m} />
          ))}
        </div>
      ) : (
        <div style={{ opacity: 0.5, fontSize: "0.9em" }}>No type weaknesses</div>
      )}

      <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 12 }}>
        <div style={{ flex: 1 }}>
          <HpBar hp={mon.hp} max={mon.max_hp} />
        </div>
        <span style={{ fontSize: "0.76em", opacity: 0.8, fontVariantNumeric: "tabular-nums" }}>
          {mon.hp}/{mon.max_hp}
        </span>
      </div>
    </Pressable>
  );
}
