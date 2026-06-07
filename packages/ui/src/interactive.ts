import type { KeyboardEvent } from "react";

// Spread onto any element to make it a focusable, keyboard/controller-activatable
// button (Enter/Space). Returns nothing when onOpen is absent, so the element
// stays a plain, non-interactive container.
export function openProps(onOpen?: () => void) {
  if (!onOpen) return {};
  return {
    role: "button" as const,
    tabIndex: 0,
    onClick: onOpen,
    onKeyDown: (e: KeyboardEvent<HTMLElement>) => {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        onOpen();
      }
    },
  };
}
