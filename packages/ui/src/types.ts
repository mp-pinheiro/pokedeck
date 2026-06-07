// Shared payload contract — must match pokedeck/payload.py (single source of truth in Python).

export interface Move {
  id: number;
  name: string;
  type: string | null;
  category: string | null;
  pp: number | null;
}

export interface Mon {
  species_id: number;
  species: string;
  level: number;
  hp: number;
  max_hp: number;
  status: number;
  shiny: boolean;
  ability: string | null;
  item: string | null;
  friendship: number;
  ivs: Record<string, number> | null;
  stats: Record<string, number>;
  types: string[];
  weak: [string, number][];
  resist: [string, number][];
  immune: string[];
  moves: Move[];
}

export interface BattleState {
  connected: boolean;
  in_battle: boolean;
  player?: Mon;
  opponent?: Mon;
}

export interface Game {
  id: string;
  name: string;
}

export type BattleListener = (state: BattleState) => void;

// Host-supplied transport: browser implements it over SSE/WebSocket, Decky over @decky/api events.
export interface BattleTransport {
  subscribe(listener: BattleListener): () => void;
}
