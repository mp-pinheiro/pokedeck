import { hpColor } from "./theme";

export function HpBar({ hp, max }: { hp: number; max: number }) {
  const pct = max ? Math.max(0, Math.min(100, (hp / max) * 100)) : 0;
  const c = hpColor(pct);
  return (
    <div
      style={{
        height: 8,
        borderRadius: 999,
        background: "#00000055",
        border: "1px solid #ffffff12",
        overflow: "hidden",
      }}
    >
      <div
        style={{
          width: `${pct}%`,
          height: "100%",
          borderRadius: 999,
          background: `linear-gradient(180deg, ${c}, ${c}bb)`,
          boxShadow: `0 0 8px ${c}66`,
          transition: "width .35s ease, background .35s ease",
        }}
      />
    </div>
  );
}
