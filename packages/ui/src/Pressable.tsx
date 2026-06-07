import { createContext, useContext } from "react";
import type { CSSProperties, ReactNode } from "react";
import { openProps } from "./interactive";

// On the Steam Deck, only @decky/ui <Focusable> elements join Steam's gamepad
// navigation tree — plain tabIndex divs are unreachable by the d-pad. The Decky
// shell injects a Focusable-backed renderer here; the browser falls back to a
// DOM-focusable div. This keeps packages/ui free of any @decky/* import.
export type PressableRenderer = (props: {
  onPress: () => void;
  children: ReactNode;
  style?: CSSProperties;
}) => ReactNode;

const Ctx = createContext<PressableRenderer | null>(null);
export const InteractiveProvider = Ctx.Provider;

export function Pressable({
  onPress,
  children,
  style,
}: {
  onPress?: () => void;
  children: ReactNode;
  style?: CSSProperties;
}) {
  const render = useContext(Ctx);
  if (!onPress) return <div style={style}>{children}</div>;
  if (render) return <>{render({ onPress, children, style })}</>;
  return (
    <div {...openProps(onPress)} style={{ ...style, cursor: "pointer" }}>
      {children}
    </div>
  );
}
