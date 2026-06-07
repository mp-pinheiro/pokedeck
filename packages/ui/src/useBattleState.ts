import { useEffect, useState } from "react";
import type { BattleState, BattleTransport } from "./types";

// Subscribes to a host-supplied transport and returns the latest battle state.
// `transport` must be stable across renders (wrap in useMemo in the host shell).
export function useBattleState(transport: BattleTransport): BattleState | null {
  const [state, setState] = useState<BattleState | null>(null);
  useEffect(() => transport.subscribe(setState), [transport]);
  return state;
}
