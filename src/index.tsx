import { PanelSection, PanelSectionRow, staticClasses } from "@decky/ui";
import { addEventListener, removeEventListener, call, definePlugin } from "@decky/api";
import { useEffect, useState } from "react";
import { FaBolt } from "react-icons/fa";

interface Mon {
  species_id: number;
  species: string;
  level: number;
  hp: number;
  max_hp: number;
  status: number;
  stats: Record<string, number>;
  types: string[];
  weak: [string, number][];
  resist: [string, number][];
  immune: string[];
  moves: { id: number; name: string; type: string | null; category: string | null }[];
}

interface BattleState {
  connected: boolean;
  in_battle: boolean;
  player?: Mon;
  opponent?: Mon;
}

const mult = (m: number) => (m === 0 ? "immune" : `x${m}`);

function MonView({ mon }: { mon: Mon }) {
  const pct = mon.max_hp ? Math.round((mon.hp / mon.max_hp) * 100) : 0;
  return (
    <div style={{ fontSize: "0.85em", lineHeight: 1.45 }}>
      <div style={{ fontWeight: "bold" }}>
        {mon.species} · Lv{mon.level}
      </div>
      <div>
        HP {mon.hp}/{mon.max_hp} ({pct}%) · {mon.types.join(" / ")}
      </div>
      {mon.weak.length > 0 && (
        <div style={{ color: "#ff6b6b" }}>
          Weak: {mon.weak.map(([t, m]) => `${t} ${mult(m)}`).join(", ")}
        </div>
      )}
      {mon.immune.length > 0 && <div>Immune: {mon.immune.join(", ")}</div>}
      <div>Moves: {mon.moves.map((mv) => mv.name).join(", ") || "—"}</div>
    </div>
  );
}

function Content() {
  const [state, setState] = useState<BattleState | null>(null);

  useEffect(() => {
    const listener = addEventListener<[BattleState]>("battle_update", (s) => setState(s));
    call<[], BattleState>("get_snapshot")
      .then((s) => setState(s))
      .catch(() => undefined);
    return () => removeEventListener("battle_update", listener);
  }, []);

  if (!state || !state.connected) {
    return (
      <PanelSection title="Poke Deck">
        <PanelSectionRow>RetroArch not connected.</PanelSectionRow>
      </PanelSection>
    );
  }
  if (!state.in_battle) {
    return (
      <PanelSection title="Poke Deck">
        <PanelSectionRow>Not in a battle.</PanelSectionRow>
      </PanelSection>
    );
  }
  return (
    <>
      <PanelSection title="Opponent">
        <PanelSectionRow>{state.opponent && <MonView mon={state.opponent} />}</PanelSectionRow>
      </PanelSection>
      <PanelSection title="Your Pokémon">
        <PanelSectionRow>{state.player && <MonView mon={state.player} />}</PanelSectionRow>
      </PanelSection>
    </>
  );
}

export default definePlugin(() => ({
  name: "Poke Deck",
  titleView: <div className={staticClasses.Title}>Poke Deck</div>,
  content: <Content />,
  icon: <FaBolt />,
}));
