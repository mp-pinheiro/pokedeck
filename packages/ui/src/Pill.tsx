import type { ReactNode } from "react";

export function Pill({
  children,
  bg,
  color,
  title,
}: {
  children: ReactNode;
  bg: string;
  color?: string;
  title?: string;
}) {
  return (
    <span
      title={title}
      style={{
        display: "inline-block",
        padding: "1px 7px",
        borderRadius: 999,
        fontSize: "0.72em",
        fontWeight: 700,
        lineHeight: 1.6,
        letterSpacing: 0.3,
        background: bg,
        color: color ?? "#fff",
        whiteSpace: "nowrap",
        textShadow: color ? undefined : "0 1px 1px #0006",
      }}
    >
      {children}
    </span>
  );
}
