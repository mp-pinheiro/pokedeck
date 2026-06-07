import { useMemo } from "react";
import { BattleView, useBattleState } from "@poke-deck/ui";
import { sseTransport } from "./sseTransport";

export function App() {
  const transport = useMemo(() => sseTransport("/events"), []);
  const state = useBattleState(transport);
  const status = !state
    ? "connecting…"
    : !state.connected
      ? "RetroArch offline"
      : state.in_battle
        ? "in battle"
        : "idle";
  const dot = !state || !state.connected ? "#888" : state.in_battle ? "#4caf50" : "#e0a000";

  return (
    <div
      style={{
        fontFamily: "system-ui, sans-serif",
        color: "#e8e8e8",
        background: "#16181d",
        minHeight: "100vh",
        padding: 20,
        boxSizing: "border-box",
      }}
    >
      <header style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 18 }}>
        <h1 style={{ fontSize: "1.4em", margin: 0 }}>Poke Deck</h1>
        <span style={{ width: 9, height: 9, borderRadius: "50%", background: dot, display: "inline-block" }} />
        <span style={{ opacity: 0.7 }}>{status}</span>
      </header>
      <BattleView state={state} />
    </div>
  );
}
