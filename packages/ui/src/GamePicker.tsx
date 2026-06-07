import type { Game } from "./types";

export function GamePicker({
  games,
  current,
  onSelect,
}: {
  games: Game[];
  current?: string;
  onSelect: (id: string) => void;
}) {
  if (games.length <= 1) return null;
  return (
    <select
      value={current ?? ""}
      onChange={(e) => onSelect(e.target.value)}
      style={{ background: "#222", color: "#eee", border: "1px solid #444", borderRadius: 4, padding: "2px 6px" }}
    >
      {games.map((g) => (
        <option key={g.id} value={g.id}>
          {g.name}
        </option>
      ))}
    </select>
  );
}
