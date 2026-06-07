import { useState } from "react";
import { spriteUrl } from "./theme";

// PokeAPI sprite with graceful fallback (Decky/CEF may be offline or block external img).
export function Sprite({ id, size = 76, alt }: { id: number; size?: number; alt?: string }) {
  const [failed, setFailed] = useState(false);
  const usable = id > 0 && id <= 1025 && !failed;
  return (
    <div
      style={{
        width: size,
        height: size,
        flexShrink: 0,
        display: "grid",
        placeItems: "center",
        borderRadius: 12,
        background: "radial-gradient(circle at 50% 38%, #ffffff12, #ffffff03)",
        border: "1px solid #ffffff10",
      }}
    >
      {usable ? (
        <img
          src={spriteUrl(id)}
          alt={alt ?? ""}
          width={size}
          height={size}
          onError={() => setFailed(true)}
          style={{
            width: size,
            height: size,
            objectFit: "contain",
            imageRendering: "pixelated",
            filter: "drop-shadow(0 2px 3px #0009)",
          }}
        />
      ) : (
        <span style={{ fontSize: size * 0.34, fontWeight: 800, opacity: 0.22 }}>?</span>
      )}
    </div>
  );
}
