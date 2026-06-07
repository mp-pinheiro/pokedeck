import { useEffect, useMemo, useState } from "react";
import { BattleScreen, GamePicker, useBattleState } from "@poke-deck/ui";
import type { Game } from "@poke-deck/ui";
import { sseTransport } from "./sseTransport";

export function App() {
  const transport = useMemo(() => sseTransport("/events"), []);
  const state = useBattleState(transport);
  const [info, setInfo] = useState<{ game?: string; games: Game[] }>({ games: [] });

  useEffect(() => {
    fetch("/api/info")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => setInfo({ game: d.game, games: Array.isArray(d.games) ? d.games : [] }))
      .catch(() => undefined);
  }, []);

  const selectGame = (id: string) => {
    fetch("/api/game", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ game: id }),
    })
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((d) => setInfo((prev) => ({ ...prev, game: d.game })))
      .catch(() => undefined);
  };

  const status = !state ? "connecting" : !state.connected ? "offline" : state.in_battle ? "in battle" : "idle";
  const dot = !state || !state.connected ? "#6b7280" : state.in_battle ? "#46c66a" : "#f0b73c";

  return (
    <div style={{ maxWidth: 560, margin: "0 auto", padding: "22px 18px 44px" }}>
      <header style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
        <h1
          style={{
            fontFamily: "'Pixelify Sans', system-ui",
            fontSize: "1.75em",
            fontWeight: 700,
            margin: 0,
            letterSpacing: 0.5,
            background: "linear-gradient(180deg, #ffffff, #9fc6ff)",
            WebkitBackgroundClip: "text",
            backgroundClip: "text",
            color: "transparent",
            textShadow: "0 0 26px #5aa0ff33",
          }}
        >
          POKé DECK
        </h1>
        <span style={{ width: 9, height: 9, borderRadius: "50%", background: dot, boxShadow: `0 0 8px ${dot}` }} />
        <span style={{ opacity: 0.6, fontSize: "0.82em", letterSpacing: 0.5 }}>{status}</span>
        <span style={{ flex: 1 }} />
        <GamePicker games={info.games} current={info.game} onSelect={selectGame} />
      </header>
      <BattleScreen state={state} />
    </div>
  );
}
