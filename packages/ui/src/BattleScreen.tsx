import { useState } from "react";
import type { BattleState, FetchSpecies, Mon, PartyMon } from "./types";
import { BattleView } from "./BattleView";
import { PartyView } from "./PartyView";
import { MonDetail } from "./MonDetail";

type Sel =
  | { group: "active"; side: "player" | "opponent" }
  | { group: "party"; i: number }
  | { group: "oppparty"; i: number };

// Re-resolve the selection against the latest state every render, so an open
// detail page keeps updating live (HP/status/PP) and auto-closes if its mon
// disappears (battle ends, party reorders).
function resolve(
  state: BattleState | null,
  sel: Sel,
): { mon: Mon | PartyMon; active: boolean; subtitle: string } | null {
  if (!state) return null;
  if (sel.group === "active") {
    if (!state.in_battle) return null;
    const mon = sel.side === "player" ? state.player : state.opponent;
    return mon ? { mon, active: true, subtitle: sel.side === "player" ? "Your active" : "Opponent active" } : null;
  }
  const list = sel.group === "party" ? state.party : state.opponent_party;
  const mon = list?.[sel.i];
  return mon ? { mon, active: false, subtitle: sel.group === "party" ? "Your team" : "Opponent team" } : null;
}

export function BattleScreen({
  state,
  fetchSpecies,
}: {
  state: BattleState | null;
  fetchSpecies?: FetchSpecies;
}) {
  const [sel, setSel] = useState<Sel | null>(null);
  const picked = sel ? resolve(state, sel) : null;

  if (picked) {
    return (
      <MonDetail
        mon={picked.mon}
        active={picked.active}
        subtitle={picked.subtitle}
        onBack={() => setSel(null)}
        fetchSpecies={fetchSpecies}
      />
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <BattleView state={state} onSelect={(side) => setSel({ group: "active", side })} />
      <PartyView party={state?.opponent_party} label="Opponent team" onSelect={(i) => setSel({ group: "oppparty", i })} />
      <PartyView party={state?.party} label="Your team" onSelect={(i) => setSel({ group: "party", i })} />
    </div>
  );
}
