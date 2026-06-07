import { Focusable, PanelSection, PanelSectionRow, staticClasses } from "@decky/ui";
import { addEventListener, removeEventListener, call, definePlugin } from "@decky/api";
import { useMemo } from "react";
import { FaBolt } from "react-icons/fa";
import { BattleScreen, InteractiveProvider, useBattleState } from "@poke-deck/ui";
import type { BattleListener, BattleState, BattleTransport, PressableRenderer, SpeciesExtra } from "@poke-deck/ui";

// Make shared cards/rows/Back reachable by the Steam gamepad: render them as
// @decky/ui <Focusable> (onActivate = the A button) instead of plain divs.
const deckyPressable: PressableRenderer = ({ onPress, children, style }) => (
  <Focusable onActivate={() => onPress()} onClick={() => onPress()} style={style}>
    {children}
  </Focusable>
);

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
        <InteractiveProvider value={deckyPressable}>
          <BattleScreen state={state} fetchSpecies={fetchSpecies} />
        </InteractiveProvider>
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
