import type { BattleListener, BattleState, BattleTransport } from "@poke-deck/ui";

// Browser transport over Server-Sent Events. EventSource auto-reconnects on drop.
export function sseTransport(url = "/events"): BattleTransport {
  return {
    subscribe(listener: BattleListener) {
      const es = new EventSource(url);
      es.onmessage = (e) => {
        try {
          listener(JSON.parse(e.data) as BattleState);
        } catch {
          /* ignore malformed frame */
        }
      };
      return () => es.close();
    },
  };
}
