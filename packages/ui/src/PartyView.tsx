import type { PartyMon } from "./types";
import { MonRow } from "./MonRow";
import { SectionHeader } from "./SectionHeader";

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
    <div>
      {label && <SectionHeader title={label} />}
      <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
        {party.map((m, i) => (
          <MonRow key={i} mon={m} onOpen={onSelect && (() => onSelect(i))} />
        ))}
      </div>
    </div>
  );
}
