import { PanelSection, PanelSectionRow, staticClasses } from "@decky/ui";
import { addEventListener, removeEventListener, call, definePlugin } from "@decky/api";
import { useMemo } from "react";
import { FaBolt } from "react-icons/fa";
import { BattleScreen, useBattleState } from "@poke-deck/ui";
import type { BattleListener, BattleState, BattleTransport, SpeciesExtra } from "@poke-deck/ui";

// PokeAPI lookup via the backend (disk-cached). Backend returns {} when offline.
const fetchSpecies = (dex: number): Promise<SpeciesExtra | null> =>
  call<[number], SpeciesExtra | Record<string, never>>("get_species", dex)
    .then((d) => ((d as SpeciesExtra)?.dex ? (d as SpeciesExtra) : null))
    .catch(() => null);

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
        <BattleScreen state={state} fetchSpecies={fetchSpecies} />
      </PanelSectionRow>
    </PanelSection>
  );
}

export default definePlugin(() => ({
  name: "Poke Deck",
  titleView: <div className={staticClasses.Title}>Poke Deck</div>,
  content: <Content />,
  icon: <FaBolt />,
}));
