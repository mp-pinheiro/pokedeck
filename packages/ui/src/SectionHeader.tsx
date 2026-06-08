// Section divider with a label — used to break the panel into Battle / Opponent
// Team / My Team.
export function SectionHeader({ title, first }: { title: string; first?: boolean }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 9, margin: first ? "0 0 8px" : "16px 0 8px" }}>
      <span
        style={{
          fontWeight: 800,
          fontSize: "0.72em",
          letterSpacing: 1.6,
          textTransform: "uppercase",
          opacity: 0.7,
          whiteSpace: "nowrap",
        }}
      >
        {title}
      </span>
      <div style={{ flex: 1, height: 1, background: "linear-gradient(90deg, #ffffff22, #ffffff00)" }} />
    </div>
  );
}
