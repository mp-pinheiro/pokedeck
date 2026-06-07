import type { BattleState } from "./types";
import { MonCard } from "./MonCard";

export function BattleView({ state }: { state: BattleState | null }) {
  if (!state || !state.connected) {
    return <div>RetroArch not connected.</div>;
  }
  if (!state.in_battle) {
    return <div>Not in a battle.</div>;
  }
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {state.opponent && <MonCard mon={state.opponent} label="Opponent" />}
      {state.player && <MonCard mon={state.player} label="Your Pokémon" />}
    </div>
  );
}
