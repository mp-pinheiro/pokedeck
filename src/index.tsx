import { PanelSection, PanelSectionRow, staticClasses } from "@decky/ui";
import { addEventListener, removeEventListener, call, definePlugin } from "@decky/api";
import { useMemo } from "react";
import { FaBolt } from "react-icons/fa";
import { BattleView, PartyView, useBattleState } from "@poke-deck/ui";
import type { BattleListener, BattleState, BattleTransport } from "@poke-deck/ui";

// Decky transport: the Python backend pushes via decky.emit("battle_update");
// pull a snapshot once on open so the panel isn't empty.
function deckyTransport(): BattleTransport {
  return {
    subscribe(listener: BattleListener) {
      const handler = addEventListener<[BattleState]>("battle_update", (s) => listener(s));
      call<[], BattleState>("get_snapshot").then(listener).catch(() => undefined);
      return () => removeEventListener("battle_update", handler);
    },
  };
}

function Content() {
  const transport = useMemo(deckyTransport, []);
  const state = useBattleState(transport);
  return (
    <PanelSection title="Poke Deck">
      <PanelSectionRow>
        <BattleView state={state} />
      </PanelSectionRow>
      {state?.opponent_party && state.opponent_party.length > 0 && (
        <PanelSectionRow>
          <PartyView party={state.opponent_party} label="Opponent team" />
        </PanelSectionRow>
      )}
      {state?.party && state.party.length > 0 && (
        <PanelSectionRow>
          <PartyView party={state.party} label="Your team" />
        </PanelSectionRow>
      )}
    </PanelSection>
  );
}

export default definePlugin(() => ({
  name: "Poke Deck",
  titleView: <div className={staticClasses.Title}>Poke Deck</div>,
  content: <Content />,
  icon: <FaBolt />,
}));
