import type { ReactNode } from "react";
import type { SpeciesExtra } from "./types";
import { HUD_LABEL } from "./theme";

function pretty(name: string): string {
  return name
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

function genderText(rate: number): string {
  if (rate < 0) return "Genderless";
  const f = (rate / 8) * 100;
  return `♀ ${f}%  ♂ ${100 - f}%`;
}

function Meta({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div>
      <span style={{ ...HUD_LABEL, marginRight: 6 }}>{label}</span>
      {value}
    </div>
  );
}

export function Pokedex({
  extra,
  species,
  accent,
}: {
  extra?: SpeciesExtra | null;
  species: string;
  accent: string;
}) {
  if (extra === undefined) {
    return <div style={{ ...HUD_LABEL, marginTop: 16, opacity: 0.4 }}>Loading Pokédex…</div>;
  }
  if (!extra) return null; // offline / unavailable — show ROM data only
  const cur = species.toLowerCase();
  return (
    <div style={{ marginTop: 16, paddingTop: 14, borderTop: "1px solid #ffffff12" }}>
      <div style={{ ...HUD_LABEL, marginBottom: 8 }}>Pokédex</div>
      <div style={{ display: "flex", gap: 12 }}>
        {extra.sprites.artwork && (
          <img
            src={extra.sprites.artwork}
            alt=""
            width={92}
            height={92}
            onError={(e) => {
              e.currentTarget.style.display = "none";
            }}
            style={{ width: 92, height: 92, objectFit: "contain", flexShrink: 0, filter: "drop-shadow(0 3px 6px #000a)" }}
          />
        )}
        <div style={{ flex: 1, minWidth: 0, fontSize: "0.86em" }}>
          {extra.genus && <div style={{ fontWeight: 700, opacity: 0.85 }}>{extra.genus}</div>}
          {extra.flavor && <div style={{ opacity: 0.7, marginTop: 4, lineHeight: 1.45 }}>{extra.flavor}</div>}
        </div>
      </div>

      {extra.evolution.length > 1 && (
        <div style={{ marginTop: 12 }}>
          <div style={{ ...HUD_LABEL, marginBottom: 5 }}>Evolution</div>
          <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: 6, fontSize: "0.88em" }}>
            {extra.evolution.map((n, i) => (
              <span key={n} style={{ display: "inline-flex", alignItems: "center", gap: 6 }}>
                {i > 0 && <span style={{ opacity: 0.4 }}>→</span>}
                <span
                  style={{
                    fontWeight: n.toLowerCase() === cur ? 800 : 400,
                    color: n.toLowerCase() === cur ? accent : undefined,
                  }}
                >
                  {pretty(n)}
                </span>
              </span>
            ))}
          </div>
        </div>
      )}

      <div style={{ display: "flex", flexWrap: "wrap", gap: 12, marginTop: 12, fontSize: "0.82em" }}>
        <Meta label="Height" value={`${extra.height_m} m`} />
        <Meta label="Weight" value={`${extra.weight_kg} kg`} />
        <Meta label="Gender" value={genderText(extra.gender_rate)} />
        {extra.egg_groups.length > 0 && <Meta label="Eggs" value={extra.egg_groups.map(pretty).join(", ")} />}
        {extra.capture_rate != null && <Meta label="Catch" value={String(extra.capture_rate)} />}
      </div>
    </div>
  );
}
