// Shared payload contract — must match pokedeck/payload.py (single source of truth in Python).

export interface Move {
  id: number;
  name: string;
  type: string | null;
  category: string | null; // "physical" | "special" | "status"
  power: number | null; // 0 for status moves
  accuracy: number | null; // 0 = bypasses the accuracy check (always hits)
  priority: number | null;
  pp_max: number | null;
  pp: number | null; // live remaining PP; null when read off-RAM (bench mons)
}

export interface Mon {
  species_id: number;
  dex?: number | null; // National-Dex number (sprite + generation); differs from species_id for Gen-9/forms
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

export interface PartyMon {
  species_id: number;
  dex?: number | null;
  species: string;
  level: number;
  hp: number;
  max_hp: number;
  shiny: boolean;
  item: string | null;
  moves: Move[];
}

export interface BattleState {
  connected: boolean;
  in_battle: boolean;
  player?: Mon;
  opponent?: Mon;
  party?: PartyMon[];
  opponent_party?: PartyMon[];
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
