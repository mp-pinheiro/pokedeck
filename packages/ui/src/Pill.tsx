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
        fontSize: "0.74em",
        fontWeight: 700,
        lineHeight: 1.6,
        letterSpacing: 0.2,
        background: bg,
        color: color ?? "#fff",
        whiteSpace: "nowrap",
        // 1px all-around black outline at ~70% (no blur) keeps white text readable
        // on every type color, including bright ones (Electric/Ice). Explicit-color
        // pills (status badges) are already dark-on-light, so they skip it.
        textShadow: color
          ? undefined
          : "1px 1px 0 #000000b3, -1px -1px 0 #000000b3, 1px -1px 0 #000000b3, -1px 1px 0 #000000b3",
      }}
    >
      {children}
    </span>
  );
}
