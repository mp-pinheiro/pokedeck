import { createContext, useContext, useEffect } from "react";
import type { CSSProperties, ReactNode } from "react";
import { openProps } from "./interactive";

// On the Steam Deck, only @decky/ui <Focusable> elements join Steam's gamepad
// navigation tree — plain divs are unreachable by the d-pad and the panel won't
// scroll to them. The Decky shell injects Focusable-backed renderers for three
// roles; the browser falls back to plain DOM. Keeps packages/ui free of @decky/*.
//  - pressable: an activatable element (gamepad A)
//  - focusItem: a focus stop so the d-pad can land on / scroll read-only content
//  - cancelZone: a boundary where gamepad B runs onCancel (e.g. go Back)
export type PressableRenderer = (p: { onPress: () => void; children: ReactNode; style?: CSSProperties }) => ReactNode;
export type FocusRenderer = (p: { children: ReactNode; style?: CSSProperties }) => ReactNode;
export type CancelRenderer = (p: { onCancel: () => void; children: ReactNode }) => ReactNode;

export interface InteractiveImpl {
  pressable?: PressableRenderer;
  focusItem?: FocusRenderer;
  cancelZone?: CancelRenderer;
}

const Ctx = createContext<InteractiveImpl>({});
export const InteractiveProvider = Ctx.Provider;

export function Pressable({ onPress, children, style }: { onPress?: () => void; children: ReactNode; style?: CSSProperties }) {
  const impl = useContext(Ctx);
  if (!onPress) return <div style={style}>{children}</div>;
  if (impl.pressable) return <>{impl.pressable({ onPress, children, style })}</>;
  return (
    <div {...openProps(onPress)} style={{ ...style, cursor: "pointer" }}>
      {children}
    </div>
  );
}

export function FocusItem({ children, style }: { children: ReactNode; style?: CSSProperties }) {
  const impl = useContext(Ctx);
  if (impl.focusItem) return <>{impl.focusItem({ children, style })}</>;
  return <div style={style}>{children}</div>;
}

export function CancelZone({ onCancel, children }: { onCancel: () => void; children: ReactNode }) {
  const impl = useContext(Ctx);
  useEffect(() => {
    if (impl.cancelZone) return; // gamepad B handled by the host
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onCancel();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [impl.cancelZone, onCancel]);
  if (impl.cancelZone) return <>{impl.cancelZone({ onCancel, children })}</>;
  return <>{children}</>;
}
