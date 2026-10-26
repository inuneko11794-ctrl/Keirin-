import { create } from "zustand";
import { autoHit, isMansha } from "./analytics";
import { makeSample } from "./sample";
import { normalizeRace } from "./parse";
import { LS_KEY, SAMPLE_KEY, STAGING_KEY, type Race, type SiteKey } from "./types";

export type ViewId = "board" | "book" | "study" | "desk";

type State = {
  hydrated: boolean;
  sample: boolean;
  races: Race[];
  staging: Race[];
  view: ViewId;
  filter: string;
  flash: string | null;
  hydrate: () => void;
  setView: (view: ViewId) => void;
  setFilter: (filter: string) => void;
  say: (message: string) => void;
  update: (scope: "sv" | "stg", id: string, patch: Partial<Race>) => void;
  toggleSite: (scope: "sv" | "stg", id: string, site: SiteKey, field: "bet" | "hit") => void;
  remove: (scope: "sv" | "stg", id: string) => void;
  stage: (rows: Race[]) => void;
  commitStaging: () => void;
  clearStaging: () => void;
  addSaved: (rows: Race[]) => void;
  replaceAll: (rows: Race[]) => void;
  clearAll: () => void;
  loadSample: () => void;
};

let flashToken = 0;

function persist(races: Race[], sample: boolean) {
  localStorage.setItem(LS_KEY, JSON.stringify(races));
  localStorage.setItem(SAMPLE_KEY, sample ? "1" : "0");
}

function persistStaging(staging: Race[]) {
  localStorage.setItem(STAGING_KEY, JSON.stringify(staging));
}

function readRaces(raw: string | null) {
  if (raw == null) return [];
  const data = JSON.parse(raw) as unknown;
  const used = new Set<string>();
  return Array.isArray(data)
    ? data.map((row, index) => normalizeRace(row, index, used)).filter((row): row is Race => row !== null)
    : [];
}

function untouchedSample(races: Race[]) {
  const sample = makeSample();
  if (races.length !== sample.length) return false;
  return races.every((race, index) => {
    const origin = sample[index];
    return (
      origin !== undefined &&
      race.id === origin.id &&
      race.order === origin.order &&
      race.payout2 === origin.payout2 &&
      race.payout3 === origin.payout3
    );
  });
}

function applyPatch(race: Race, patch: Partial<Race>) {
  const next: Race = {
    ...race,
    ...patch,
    sites: patch.sites
      ? {
          B: { ...race.sites.B, ...patch.sites.B },
          Y: { ...race.sites.Y, ...patch.sites.Y },
          N: { ...race.sites.N, ...patch.sites.N },
        }
      : race.sites,
  };
  if (patch.payout2 !== undefined || patch.payout3 !== undefined) return autoHit(next);
  return next;
}

export const useKeirin = create<State>((set, get) => ({
  hydrated: true,
  sample: false,
  races: [],
  staging: [],
  view: "board",
  filter: "all",
  flash: null,
  hydrate: () => {
    if (typeof window === "undefined") return;
    try {
      let races = readRaces(localStorage.getItem(LS_KEY));
      let sample = localStorage.getItem(SAMPLE_KEY) === "1";
      if (sample && untouchedSample(races)) {
        races = [];
        sample = false;
        persist(races, false);
      }
      const staging = readRaces(localStorage.getItem(STAGING_KEY));
      set({ races, staging, sample });
    } catch {
      set({ races: [], staging: [], sample: false });
    }
  },
  setView: (view) => set({ view }),
  setFilter: (filter) => set({ filter }),
  say: (message) => {
    const token = ++flashToken;
    set({ flash: message });
    window.setTimeout(() => {
      if (token === flashToken) set({ flash: null });
    }, 4200);
  },
  update: (scope, id, patch) => {
    if (scope === "stg") {
      const staging = get().staging.map((race) => (race.id === id ? applyPatch(race, patch) : race));
      persistStaging(staging);
      set({ staging });
      return;
    }
    const races = get().races.map((race) => (race.id === id ? applyPatch(race, patch) : race));
    persist(races, false);
    set({ races, sample: false });
  },
  toggleSite: (scope, id, site, field) => {
    const flip = (race: Race) => {
      if (race.id !== id) return race;
      const cell = { ...race.sites[site], [field]: !race.sites[site][field] };
      if (field === "bet" && cell.bet && isMansha(race)) cell.hit = true;
      return { ...race, sites: { ...race.sites, [site]: cell } };
    };
    if (scope === "stg") {
      const staging = get().staging.map(flip);
      persistStaging(staging);
      set({ staging });
      return;
    }
    const races = get().races.map(flip);
    persist(races, false);
    set({ races, sample: false });
  },
  remove: (scope, id) => {
    if (scope === "stg") {
      const staging = get().staging.filter((race) => race.id !== id);
      persistStaging(staging);
      set({ staging });
      return;
    }
    const races = get().races.filter((race) => race.id !== id);
    persist(races, false);
    set({ races, sample: false });
  },
  stage: (rows) => {
    const staging = [...rows, ...get().staging];
    persistStaging(staging);
    set({ staging });
  },
  commitStaging: () => {
    if (!get().staging.length) return;
    const races = [...get().staging.map((race) => ({ ...race, sites: { ...race.sites } })), ...get().races];
    persist(races, false);
    persistStaging([]);
    set({ races, staging: [], sample: false });
  },
  clearStaging: () => {
    persistStaging([]);
    set({ staging: [] });
  },
  addSaved: (rows) => {
    const races = [...rows, ...get().races];
    persist(races, false);
    set({ races, sample: false });
  },
  replaceAll: (rows) => {
    persist(rows, false);
    persistStaging([]);
    set({ races: rows, sample: false, staging: [] });
  },
  clearAll: () => {
    persist([], false);
    persistStaging([]);
    set({ races: [], sample: false, staging: [] });
  },
  loadSample: () => {
    const races = makeSample();
    persist(races, true);
    persistStaging([]);
    set({ races, sample: true, staging: [] });
  },
}));
