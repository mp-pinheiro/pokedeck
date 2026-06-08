import type { ReactNode } from "react";
import { Pill } from "./Pill";
import { typeColor, HUD_LABEL } from "./theme";

function Line({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 4, alignItems: "center", marginTop: 6 }}>
      <span style={{ ...HUD_LABEL, opacity: 0.55, minWidth: 48 }}>{label}</span>
      {children}
    </div>
  );
}

// Compact, labeled matchup rows for the battle/bench cards: what beats this mon
// (Weak to) and what can't touch it (Immune). Pills wrap, so 4+ entries stay tidy.
export function MatchupRows({ weak, immune }: { weak: [string, number][]; immune: string[] }) {
  if ((!weak || weak.length === 0) && (!immune || immune.length === 0)) return null;
  return (
    <div>
      {weak.length > 0 && (
        <Line label="Weak to">
          {weak.map(([t, m]) => (
            <Pill key={t} bg={typeColor(t)}>
              {t}
              {m >= 4 ? " ×4" : ""}
            </Pill>
          ))}
        </Line>
      )}
      {immune.length > 0 && (
        <Line label="Immune">
          {immune.map((t) => (
            <Pill key={t} bg={typeColor(t)}>
              {t}
            </Pill>
          ))}
        </Line>
      )}
    </div>
  );
}
