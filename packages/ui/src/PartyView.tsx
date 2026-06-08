import type { PartyMon } from "./types";
import { MonRow } from "./MonRow";
import { HUD_LABEL } from "./theme";

export function PartyView({
  party,
  label,
  onSelect,
}: {
  party?: PartyMon[];
  label?: string;
  onSelect?: (index: number) => void;
}) {
  if (!party || party.length === 0) return null;
  return (
    <div style={{ marginTop: 13 }}>
      {label && <div style={{ ...HUD_LABEL, marginBottom: 6 }}>{label}</div>}
      <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
        {party.map((m, i) => (
          <MonRow key={i} mon={m} onOpen={onSelect && (() => onSelect(i))} />
        ))}
      </div>
    </div>
  );
}
