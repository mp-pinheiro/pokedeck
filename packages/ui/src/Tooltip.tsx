import { useState } from "react";
import type { ReactNode } from "react";

// Reveals `content` on mouse hover AND keyboard/controller focus AND tap-toggle,
// so it works on the Deck (no cursor) as well as in the browser. Inline-styled,
// no portals — the bubble is an absolutely-positioned child of the target.
export function Tooltip({
  content,
  children,
  width = 220,
  align = "left",
}: {
  content: ReactNode;
  children: ReactNode;
  width?: number;
  align?: "left" | "right";
}) {
  const [open, setOpen] = useState(false);
  if (!content) return <>{children}</>;
  return (
    <div
      style={{ position: "relative", outline: "none" }}
      tabIndex={0}
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onFocus={() => setOpen(true)}
      onBlur={() => setOpen(false)}
      onClick={() => setOpen((v) => !v)}
    >
      {children}
      {open && (
        <div
          role="tooltip"
          style={{
            position: "absolute",
            bottom: "calc(100% + 6px)",
            [align]: 0,
            zIndex: 50,
            width,
            maxWidth: "82vw",
            padding: "8px 10px",
            borderRadius: 10,
            background: "#0f131bf5",
            border: "1px solid #ffffff22",
            boxShadow: "0 12px 30px -8px #000c",
            fontSize: "0.82em",
            lineHeight: 1.45,
            color: "#e7eef6",
            textAlign: "left",
            whiteSpace: "normal",
            pointerEvents: "none",
          }}
        >
          {content}
        </div>
      )}
    </div>
  );
}
