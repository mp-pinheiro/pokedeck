import "./styles.css";
import { createRoot } from "react-dom/client";
import { BattleView, PartyView } from "@poke-deck/ui";
import type { Mon, PartyMon } from "@poke-deck/ui";

// Static mock so the design is viewable without RetroArch: open /preview.html.
const mon = (o: Partial<Mon> & Pick<Mon, "species_id" | "species" | "level" | "hp" | "max_hp">): Mon => ({
  status: 0, shiny: false, ability: null, item: null, friendship: 0, ivs: null,
  stats: {}, types: [], weak: [], resist: [], immune: [], moves: [], ...o,
});
const pm = (o: Partial<PartyMon> & Pick<PartyMon, "species_id" | "species" | "level" | "hp" | "max_hp">): PartyMon => ({
  shiny: false, item: null, moves: [], ...o,
});

const opponent = mon({
  species_id: 248, species: "Tyranitar", level: 45, hp: 96, max_hp: 160, status: 0x10,
  types: ["Rock", "Dark"], ability: "Sand Stream", item: "Leftovers",
  weak: [["Fighting", 4], ["Water", 2], ["Grass", 2], ["Ground", 2], ["Bug", 2], ["Steel", 2], ["Fairy", 2]],
  moves: [
    { id: 1, name: "Crunch", type: "Dark", category: "physical", pp: 15 },
    { id: 2, name: "Earthquake", type: "Ground", category: "physical", pp: 10 },
    { id: 3, name: "Rock Slide", type: "Rock", category: "physical", pp: 10 },
    { id: 4, name: "Ice Beam", type: "Ice", category: "special", pp: 10 },
  ],
});

const player = mon({
  species_id: 729, species: "Brionne", level: 22, hp: 21, max_hp: 61, status: 0x40, shiny: true,
  types: ["Water"], ability: "Torrent", friendship: 142,
  weak: [["Electric", 2], ["Grass", 2]],
  moves: [
    { id: 1, name: "Encore", type: "Normal", category: "status", pp: 3 },
    { id: 2, name: "Bubble Beam", type: "Water", category: "special", pp: 20 },
    { id: 3, name: "Icy Wind", type: "Ice", category: "special", pp: 11 },
    { id: 4, name: "Disarming Voice", type: "Fairy", category: "special", pp: 13 },
  ],
});

createRoot(document.getElementById("root")!).render(
  <div style={{ maxWidth: 560, margin: "0 auto", padding: 22 }}>
    <h1 style={{ fontFamily: "'Pixelify Sans', system-ui", fontSize: "1.6em", marginTop: 0 }}>POKé DECK — preview</h1>
    <BattleView state={{ connected: true, in_battle: true, opponent, player }} />
    <PartyView
      party={[
        pm({ species_id: 248, species: "Tyranitar", level: 45, hp: 96, max_hp: 160 }),
        pm({ species_id: 282, species: "Gardevoir", level: 43, hp: 130, max_hp: 130 }),
        pm({ species_id: 460, species: "Abomasnow", level: 44, hp: 0, max_hp: 170 }),
        // Gen-9 mon: internal id 1336 but Pokédex #948 -> sprite/gen come from dex
        pm({ species_id: 1336, dex: 948, species: "Toedscool", level: 41, hp: 70, max_hp: 95 }),
        // Paldean form: dex 128 -> base Tauros sprite, Gen I
        pm({ species_id: 1402, dex: 128, species: "Tauros", level: 42, hp: 88, max_hp: 130 }),
      ]}
      label="Opponent team"
    />
    <PartyView
      party={[
        pm({ species_id: 729, species: "Brionne", level: 22, hp: 21, max_hp: 61, shiny: true }),
        pm({ species_id: 1291, dex: 908, species: "Meowscarada", level: 24, hp: 60, max_hp: 78 }),
      ]}
      label="Your team"
    />
  </div>,
);
