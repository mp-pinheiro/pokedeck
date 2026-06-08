import { Pill } from "./Pill";
import { typeColor, HUD_LABEL } from "./theme";

// Compact "Weak to" row — small pills that wrap, so 4+ weaknesses stay readable.
// ×4 is marked; ×2 is implied.
export function WeakPills({ weak, label = "Weak to" }: { weak: [string, number][]; label?: string }) {
  if (!weak || weak.length === 0) return null;
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 4, alignItems: "center", marginTop: 7 }}>
      <span style={{ ...HUD_LABEL, opacity: 0.55 }}>{label}</span>
      {weak.map(([t, m]) => (
        <Pill key={t} bg={typeColor(t)}>
          {t}
          {m >= 4 ? " ×4" : ""}
        </Pill>
      ))}
    </div>
  );
}
