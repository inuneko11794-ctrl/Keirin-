export const SITES = ["B", "Y", "N"] as const;
export type SiteKey = (typeof SITES)[number];

export const LINES = ["単", "0", "1", "2", "3", "4"] as const;
export const BATTLES = ["2分戦", "3分戦", "4分戦", "単騎戦"] as const;
export const FIELDS = ["9", "8", "7", "6", "5"] as const;

export const LS_KEY = "byn3_data";
export const STAGING_KEY = "byn3_staging";
export const SAMPLE_KEY = "byn3_sample";

export type SiteMark = { bet: boolean; hit: boolean };

export type Race = {
  id: string;
  raceNo?: number;
  order: string;
  payout2: string;
  payout3: string;
  racers: string;
  battle: string;
  winLine: string;
  tech1: string;
  tech2: string;
  sites: Record<SiteKey, SiteMark>;
};

export type SiteStat = {
  site: SiteKey;
  bet: number;
  hit: number;
  man: number;
  hitRate: number;
  manRate: number;
  capture: number;
  avgP2: number;
  avgP3: number;
  payoutPower: number;
  index: number;
};

export type AgreeRow = {
  bets: number;
  count: number;
  manshaRate: number;
  avgP3: number;
  hitRate: number;
  avgP3OnHit: number;
};

export type OverlapRow = {
  key: string;
  count: number;
  mansha: number;
  manshaRate: number;
  avgP2: number;
  avgP3: number;
  avgP3OnHit: number;
};

export type CondRow = {
  key: string;
  count: number;
  manshaRate: number;
  avgP3: number;
  peak: number;
};

export type Heat = {
  maxCar: number;
  matrix: number[][];
  max: number;
};

export type PairRow = {
  pair: string;
  count: number;
  share: number;
  avgP3: number;
};

export type ThirdRow = {
  car: string;
  count: number;
  share: number;
  avgP3: number;
};

export type OverlapCar = { car: string; count: number; share: number };

export type RoundRow = {
  raceNo: number;
  count: number;
  mansha: number;
  manshaRate: number;
  avgP3: number;
};

export type CarLineCell = {
  car: string;
  total: number;
  top: string;
  topCount: number;
  byLine: { line: string; count: number }[];
};

export type DashModel = {
  total: number;
  manshaCount: number;
  manshaRate: number;
  peakP3: number;
  peakOrder: string;
  recentMansha: number;
  gap: number | null;
  sites: SiteStat[];
  radar: { axis: string; B: number; Y: number; N: number }[];
  agreement: AgreeRow[];
  overlap: OverlapRow[];
  winCars: { car: string; count: number; avgP3: number }[];
  zones: { scope: "全体" | "万車"; 内: number; 中: number; 外: number }[];
  lines: {
    line: string;
    all: number;
    mansha: number;
    allPct: number;
    manPct: number;
    lift: number | null;
  }[];
  carLines: { all: CarLineCell[]; man: CarLineCell[] };
  rounds: RoundRow[];
  overlapWinCars: Record<SiteKey, { count: number; cars: OverlapCar[] }>;
  siteLines: { line: string; B: number; Y: number; N: number }[];
  sums: { sum: number; count: number; avgP3: number; mansha: number }[];
  pairSums: { sum: number; count: number; avgP2: number; mansha: number }[];
  pairs: string[];
  thirds: Record<string, ThirdRow[]>;
  topPairs: PairRow[];
  richPairs: PairRow[];
  topPayouts: { order: string; payout2: number; payout3: number; line: string }[];
  heatAll: Heat;
  heatMan: Heat;
  series: { i: number; order: string; payout3: number; mark: number | null }[];
  bands: { band: string; all: number; B: number; Y: number; N: number }[];
  battles: CondRow[];
  techs: CondRow[];
  fields: CondRow[];
  manshaBySite: Record<SiteKey, { car: string; count: number; pct: number; fieldPct: number }[]>;
  manshaHits: Record<SiteKey, number>;
};

export function emptySites(): Record<SiteKey, SiteMark> {
  return {
    B: { bet: false, hit: false },
    Y: { bet: false, hit: false },
    N: { bet: false, hit: false },
  };
}

export function blankRace(partial: Partial<Race> = {}): Race {
  return {
    id: crypto.randomUUID(),
    order: "",
    payout2: "",
    payout3: "",
    racers: "7",
    battle: "",
    winLine: "単",
    tech1: "",
    tech2: "",
    ...partial,
    sites: {
      ...emptySites(),
      ...(partial.sites ?? {}),
    },
  };
}
