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
  desc: string | null; // effect text
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
  ability_desc: string | null; // the active ability's effect text
  abilities: string[]; // species' possible abilities (baseline)
  item: string | null;
  item_desc: string | null;
  friendship: number;
  ivs: Record<string, number> | null;
  stats: Record<string, number>; // live in-battle stats
  base: Record<string, number> | null; // species base stats
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
  item_desc: string | null;
  abilities: string[];
  base: Record<string, number> | null;
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
  party?: PartyMon[];
  opponent_party?: PartyMon[];
}

export interface Game {
  id: string;
  name: string;
}

// PokeAPI reference layer (from the backend /api/species proxy) — must match
// pokedeck/pokeapi.py species_extra().
export interface SpeciesExtra {
  dex: number;
  genus: string | null;
  flavor: string | null;
  height_m: number;
  weight_kg: number;
  base_exp: number | null;
  capture_rate: number | null;
  gender_rate: number; // -1 = genderless, else female eighths
  egg_groups: string[];
  evolution: string[];
  sprites: { front: string | null; shiny: string | null; artwork: string | null; home: string | null };
}

// Host-injected lookup: web hits the HTTP proxy, Decky calls the backend method.
export type FetchSpecies = (dex: number) => Promise<SpeciesExtra | null>;

export type BattleListener = (state: BattleState) => void;

// Host-supplied transport: browser implements it over SSE/WebSocket, Decky over @decky/api events.
export interface BattleTransport {
  subscribe(listener: BattleListener): () => void;
}
