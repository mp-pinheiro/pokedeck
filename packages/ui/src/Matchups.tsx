import type { ReactNode } from "react";
import { Pill } from "./Pill";
import { typeColor, HUD_LABEL } from "./theme";

const RESIST_LABEL: Record<string, string> = { "0.5": "×½", "0.25": "×¼" };

// Subtitle on its own line, pills wrapping full-width below — so a mon with many
// resists (6+) stays readable instead of cramming label + pills on one row.
function Group({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div style={{ marginTop: 7 }}>
      <div style={{ ...HUD_LABEL, opacity: 0.5, marginBottom: 4 }}>{label}</div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>{children}</div>
    </div>
  );
}

export function Matchups({
  weak,
  resist,
  immune,
}: {
  weak: [string, number][];
  resist: [string, number][];
  immune: string[];
}) {
  if (weak.length === 0 && resist.length === 0 && immune.length === 0) return null;
  return (
    <>
      {weak.length > 0 && (
        <Group label="Weak">
          {weak.map(([t, m]) => (
            <Pill key={t} bg={typeColor(t)}>
              {t} {m >= 4 ? "×4" : "×2"}
            </Pill>
          ))}
        </Group>
      )}
      {resist.length > 0 && (
        <Group label="Resist">
          {resist.map(([t, m]) => (
            <Pill key={t} bg={typeColor(t)}>
              {t} {RESIST_LABEL[String(m)] ?? `×${m}`}
            </Pill>
          ))}
        </Group>
      )}
      {immune.length > 0 && (
        <Group label="Immune">
          {immune.map((t) => (
            <Pill key={t} bg={typeColor(t)}>
              {t} ×0
            </Pill>
          ))}
        </Group>
      )}
    </>
  );
}
