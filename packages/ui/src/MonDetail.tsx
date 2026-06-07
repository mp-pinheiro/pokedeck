import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import type { FetchSpecies, Mon, PartyMon, SpeciesExtra } from "./types";
import { Pokedex } from "./Pokedex";
import { Pill } from "./Pill";
import { Sprite } from "./Sprite";
import { HpBar } from "./HpBar";
import { MoveList } from "./MoveList";
import { StatBars } from "./StatBars";
import { typeColor, statusInfo, genInfo, HUD_LABEL } from "./theme";

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div style={{ marginTop: 14 }}>
      <div style={{ ...HUD_LABEL, marginBottom: 7 }}>{title}</div>
      {children}
    </div>
  );
}

const RESIST_LABEL: Record<string, string> = { "0.5": "×½", "0.25": "×¼" };

function Matchups({ mon }: { mon: Mon | PartyMon }) {
  const row = (label: string, pills: ReactNode) => (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 4, alignItems: "center", marginBottom: 5 }}>
      <span style={{ ...HUD_LABEL, width: 52, opacity: 0.5 }}>{label}</span>
      {pills}
    </div>
  );
  return (
    <div>
      {mon.weak.length > 0 &&
        row(
          "Weak",
          mon.weak.map(([t, m]) => (
            <Pill key={t} bg={typeColor(t)}>
              {t} {m >= 4 ? "×4" : "×2"}
            </Pill>
          )),
        )}
      {mon.resist.length > 0 &&
        row(
          "Resist",
          mon.resist.map(([t, m]) => (
            <Pill key={t} bg={typeColor(t)}>
              {t} {RESIST_LABEL[String(m)] ?? `×${m}`}
            </Pill>
          )),
        )}
      {mon.immune.length > 0 &&
        row(
          "Immune",
          mon.immune.map((t) => (
            <Pill key={t} bg={typeColor(t)}>
              {t} ×0
            </Pill>
          )),
        )}
    </div>
  );
}

export function MonDetail({
  mon,
  active,
  subtitle,
  onBack,
  fetchSpecies,
}: {
  mon: Mon | PartyMon;
  active: boolean;
  subtitle?: string;
  onBack: () => void;
  fetchSpecies?: FetchSpecies;
}) {
  const a = mon as Partial<Mon>; // active-only fields read optionally
  const dex = mon.dex ?? mon.species_id;
  const gen = genInfo(dex);

  // Reference layer (PokeAPI) — undefined = loading, null = unavailable/offline.
  const [extra, setExtra] = useState<SpeciesExtra | null | undefined>(undefined);
  useEffect(() => {
    if (!fetchSpecies) return;
    let live = true;
    setExtra(undefined);
    fetchSpecies(dex)
      .then((d) => live && setExtra(d))
      .catch(() => live && setExtra(null));
    return () => {
      live = false;
    };
  }, [dex, fetchSpecies]);
  const accent = typeColor(mon.types[0]);
  const status = active ? statusInfo(a.status ?? 0) : null;
  const abilityText = active ? a.ability : mon.abilities.join(" / ") || null;

  return (
    <div>
      <button
        onClick={onBack}
        style={{
          appearance: "none",
          background: "#ffffff10",
          border: "1px solid #ffffff1a",
          color: "inherit",
          borderRadius: 9,
          padding: "5px 12px",
          fontSize: "0.82em",
          fontWeight: 700,
          cursor: "pointer",
          marginBottom: 12,
        }}
      >
        ‹ Back
      </button>

      <div
        style={{
          display: "flex",
          gap: 12,
          padding: 12,
          borderRadius: 16,
          background: `linear-gradient(180deg, ${accent}1f, #ffffff05)`,
          border: "1px solid #ffffff14",
          borderLeft: `3px solid ${accent}`,
        }}
      >
        <Sprite id={dex} size={92} alt={mon.species} />
        <div style={{ flex: 1, minWidth: 0 }}>
          {subtitle && <div style={HUD_LABEL}>{subtitle}</div>}
          <div style={{ display: "flex", alignItems: "baseline", gap: 7, flexWrap: "wrap" }}>
            <span style={{ fontWeight: 800, fontSize: "1.2em" }}>
              {mon.shiny ? "✦ " : ""}
              {mon.species}
            </span>
            <span style={{ opacity: 0.45, fontSize: "0.8em" }}>#{dex}</span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 7, flexWrap: "wrap", margin: "3px 0 7px" }}>
            <span style={{ opacity: 0.6, fontSize: "0.82em" }}>Lv{mon.level}</span>
            {gen && <span style={{ ...HUD_LABEL, opacity: 0.4 }}>{gen.label}</span>}
            {status && (
              <Pill bg={status.color} color="#15171c">
                {status.label}
              </Pill>
            )}
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
            {mon.types.map((t) => (
              <Pill key={t} bg={typeColor(t)}>
                {t}
              </Pill>
            ))}
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 8 }}>
            <div style={{ flex: 1 }}>
              <HpBar hp={mon.hp} max={mon.max_hp} />
            </div>
            <span style={{ fontSize: "0.76em", opacity: 0.85, fontVariantNumeric: "tabular-nums" }}>
              {mon.hp}/{mon.max_hp}
            </span>
          </div>
        </div>
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginTop: 12, fontSize: "0.86em" }}>
        {abilityText && (
          <div>
            <span style={{ ...HUD_LABEL, marginRight: 6 }}>{active ? "Ability" : "Abilities"}</span>
            {abilityText}
          </div>
        )}
        {mon.item && (
          <div>
            <span style={{ ...HUD_LABEL, marginRight: 6 }}>Item</span>◈ {mon.item}
          </div>
        )}
        {active && a.friendship != null && (
          <div>
            <span style={{ ...HUD_LABEL, marginRight: 6 }}>Friendship</span>
            {a.friendship}
          </div>
        )}
      </div>

      {mon.base && (
        <Section title={active ? "Base stats" : "Base stats"}>
          <StatBars stats={mon.base} max={180} />
        </Section>
      )}
      {active && a.ivs && (
        <Section title="IVs">
          <StatBars stats={a.ivs} max={31} showTotal={false} />
        </Section>
      )}

      <Section title="Type matchups">
        <Matchups mon={mon} />
      </Section>

      {mon.moves.length > 0 && (
        <Section title="Moves">
          <MoveList moves={mon.moves} tooltips />
        </Section>
      )}

      {fetchSpecies && <Pokedex extra={extra} species={mon.species} accent={accent} />}
    </div>
  );
}
