import type { BattleState } from "./types";
import { MonCard } from "./MonCard";

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

export function BattleView({ state }: { state: BattleState | null }) {
  if (!state || !state.connected) return <Hint text="Waiting for RetroArch…" />;
  if (!state.in_battle) return <Hint text="Not in a battle." />;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {state.opponent && <MonCard mon={state.opponent} label="Opponent" />}
      {state.player && <MonCard mon={state.player} label="Your Pokémon" />}
    </div>
  );
}
