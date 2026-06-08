import { Focusable, PanelSection, PanelSectionRow, staticClasses } from "@decky/ui";
import { addEventListener, removeEventListener, call, definePlugin } from "@decky/api";
import { useMemo, useState } from "react";
import type { CSSProperties, ReactNode } from "react";
import { FaBolt } from "react-icons/fa";
import { BattleScreen, InteractiveProvider, useBattleState } from "@poke-deck/ui";
import type { BattleListener, BattleState, BattleTransport, InteractiveImpl, SpeciesExtra } from "@poke-deck/ui";

const RING = "0 0 0 2px #6cb4ff, 0 0 16px #6cb4ff66";

// A gamepad focus stop with a VISIBLE highlight. Steam's default ring is hard to
// see on our dark cards, so we draw an explicit blue ring via onGamepadFocus.
// onPress => activatable (A); no onPress => a plain focus stop (for scrolling).
function DeckFocusable({
  onPress,
  children,
  style,
}: {
  onPress?: () => void;
  children: ReactNode;
  style?: CSSProperties;
}) {
  const [focused, setFocused] = useState(false);
  return (
    <Focusable
      onActivate={onPress ? () => onPress() : undefined}
      onClick={onPress ? () => onPress() : undefined}
      onOKActionDescription={onPress ? "Select" : undefined}
      onGamepadFocus={() => setFocused(true)}
      onGamepadBlur={() => setFocused(false)}
      style={{
        ...style,
        ...(focused ? { boxShadow: style?.boxShadow ? `${style.boxShadow}, ${RING}` : RING } : {}),
      }}
    >
      {children}
    </Focusable>
  );
}

// Make shared cards/rows/sections reachable by the Steam gamepad. A activates,
// the d-pad lands on focus stops (visible ring) so the panel scrolls, and B
// (onCancel) goes Back from the detail view.
const interactive: InteractiveImpl = {
  pressable: ({ onPress, children, style }) => (
    <DeckFocusable onPress={onPress} style={style}>
      {children}
    </DeckFocusable>
  ),
  focusItem: ({ children, style }) => <DeckFocusable style={style}>{children}</DeckFocusable>,
  cancelZone: ({ onCancel, children }) => (
    <Focusable onCancel={() => onCancel()} onCancelActionDescription="Back">
      {children}
    </Focusable>
  ),
};

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
    <PanelSection>
      <PanelSectionRow>
        <InteractiveProvider value={interactive}>
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
