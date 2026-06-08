import type { BattleState } from "./types";
import { WeaknessHero } from "./WeaknessHero";
import { MonRow } from "./MonRow";

function Hint({ text }: { text: string }) {
  return (
    <div
      style={{
        padding: "30px 16px",
        textAlign: "center",
        opacity: 0.5,
        fontSize: "0.9em",
        border: "1px dashed #ffffff1f",
        borderRadius: 14,
      }}
    >
      {text}
    </div>
  );
}

export function BattleView({
  state,
  onSelect,
}: {
  state: BattleState | null;
  onSelect?: (side: "player" | "opponent") => void;
}) {
  if (!state || !state.connected) return <Hint text="Waiting for RetroArch…" />;
  if (!state.in_battle) return <Hint text="Not in a battle." />;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 9 }}>
      {state.opponent && (
        <WeaknessHero mon={state.opponent} label="Opponent" onOpen={onSelect && (() => onSelect("opponent"))} />
      )}
      {state.player && <MonRow mon={state.player} label="You" onOpen={onSelect && (() => onSelect("player"))} />}
    </div>
  );
}
