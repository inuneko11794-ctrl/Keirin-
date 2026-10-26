import { blankRace, emptySites, type Race, type SiteKey, SITES } from "./types";

const ORDER_RE = /(\d{1,2})\s*[-ー−–—]\s*(\d{1,2})\s*[-ー−–—]\s*(\d{1,2})/;
const BATTLE_RE = /2分戦|3分戦|4分戦|単騎戦/;

function truthy(v: unknown) {
  return v === true || v === "true" || v === 1 || v === "1";
}

export function normalizeRace(raw: unknown, index: number, used: Set<string>): Race | null {
  if (!raw || typeof raw !== "object") return null;
  const r = raw as Record<string, unknown>;
  const sitesRaw =
    r.sites && typeof r.sites === "object" ? (r.sites as Record<string, unknown>) : {};
  const sites = emptySites();
  for (const key of SITES) {
    const cell = sitesRaw[key];
    if (!cell || typeof cell !== "object") continue;
    const o = cell as Record<string, unknown>;
    sites[key] = { bet: truthy(o.bet), hit: truthy(o.hit) };
  }
  let id = typeof r.id === "string" && r.id ? r.id : `legacy-${index + 1}`;
  while (used.has(id)) id = `${id}-x`;
  used.add(id);
  const tech = typeof r.tech === "string" ? r.tech : "";
  const [techFromCombo, techFromCombo2 = ""] = tech.split("-");
  return {
    id,
    raceNo: typeof r.raceNo === "number" ? r.raceNo : undefined,
    order: String(r.order ?? r.winCar ?? ""),
    payout2: String(r.payout2 ?? r.pay2 ?? ""),
    payout3: String(r.payout3 ?? r.pay3 ?? ""),
    racers: String(r.racers ?? "7"),
    battle: String(r.battle ?? ""),
    winLine: String(r.winLine ?? "単"),
    tech1: String(r.tech1 ?? techFromCombo ?? ""),
    tech2: String(r.tech2 ?? techFromCombo2 ?? ""),
    sites,
  };
}

export function digits(value: string) {
  return value.replace(/[^0-9]/g, "");
}

export function cleanOrder(value: string) {
  return value.replace(/[ー−–—]/g, "-").replace(/\s+/g, "");
}

export function joinTech(race: Pick<Race, "tech1" | "tech2">) {
  return [race.tech1, race.tech2].filter(Boolean).join("-");
}

export function splitTech(value: string) {
  const [tech1, ...rest] = value.split("-");
  return { tech1: (tech1 ?? "").trim(), tech2: rest.join("-").trim() };
}

function siteMark(mark: string | undefined): { bet: boolean; hit: boolean } {
  if (!mark || mark === "予") return { bet: true, hit: false };
  return { bet: true, hit: true };
}

export function parseLine(line: string): Race | null {
  const orderM = line.match(ORDER_RE);
  if (!orderM) return null;
  const order = `${orderM[1]}-${orderM[2]}-${orderM[3]}`;
  let rest = line.replace(orderM[0], " ");

  let battle = "";
  const battleM = rest.match(BATTLE_RE);
  if (battleM) {
    battle = battleM[0];
    rest = rest.replace(battleM[0], " ");
  }

  let winLine = "";
  const lineM = rest.match(/(?:ライン|1着L|L)\s*[:：]?\s*(単|[0-4])/);
  if (lineM) {
    winLine = lineM[1] ?? "";
    rest = rest.replace(lineM[0], " ");
  }

  let racers = "";
  const fieldM = rest.match(/([5-9])\s*車/);
  if (fieldM) {
    racers = fieldM[1] ?? "";
    rest = rest.replace(fieldM[0], " ");
  }

  const sites = emptySites();
  rest = rest.replace(/(?:^|[^A-Za-z])([BYN])\s*(\*|＊|予的|的中|的|予)?/g, (full, site: string, mark?: string) => {
    const key = site as SiteKey;
    if (key === "B" || key === "Y" || key === "N") sites[key] = siteMark(mark);
    const lead = full.startsWith(site) ? "" : full.slice(0, full.indexOf(site));
    return `${lead} `;
  });

  let tech1 = "";
  const techM = rest.match(/(逃げ|逃|捲り|捲|差し|差|マーク|マ|追込|追)/);
  if (techM) {
    const word = techM[1] ?? "";
    tech1 = word === "逃げ" ? "逃" : word === "捲り" ? "捲" : word === "差し" ? "差" : word === "マーク" ? "マ" : word === "追込" ? "追" : word;
    rest = rest.replace(techM[0], " ");
  }

  const amounts: number[] = [];
  const small: number[] = [];
  const tokenRe = /(\d+(?:\.\d+)?)\s*万|(\d{1,3}(?:,\d{3})+|\d+)/g;
  let token: RegExpExecArray | null;
  while ((token = tokenRe.exec(rest))) {
    if (token[1]) amounts.push(Math.round(Number.parseFloat(token[1]) * 10000));
    else if (token[2]) {
      const n = Number(token[2].replace(/,/g, ""));
      if (n >= 50) amounts.push(n);
      else small.push(n);
    }
  }

  if (!racers) {
    const found = small.find((n) => n >= 5 && n <= 9);
    if (found) racers = String(found);
  }
  if (!winLine && /単/.test(line)) winLine = "単";
  if (!winLine) {
    const found = small.find((n) => n <= 4 && String(n) !== racers);
    if (found !== undefined && racers) winLine = String(found);
  }
  if (!winLine) winLine = "単";
  if (!racers) racers = "7";

  let payout2 = "";
  let payout3 = "";
  if (amounts.length >= 2) {
    payout2 = String(amounts[0]);
    payout3 = String(amounts[1]);
  } else if (amounts.length === 1) {
    if ((amounts[0] ?? 0) >= 1000) payout3 = String(amounts[0]);
    else payout2 = String(amounts[0]);
  }

  return blankRace({
    order,
    payout2,
    payout3,
    racers,
    battle,
    winLine,
    tech1,
    sites,
  });
}

export function parseImport(text: string): { races: Race[]; skipped: number; error?: string } {
  const trimmed = text.trim();
  if (!trimmed) return { races: [], skipped: 0, error: "中身が空です" };

  if (trimmed.startsWith("[") || trimmed.startsWith("{")) {
    try {
      const data = JSON.parse(trimmed) as unknown;
      const arr = Array.isArray(data)
        ? data
        : data && typeof data === "object" && Array.isArray((data as { races?: unknown }).races)
          ? (data as { races: unknown[] }).races
          : null;
      if (!arr) return { races: [], skipped: 0, error: "JSONの形が違います" };
      const used = new Set<string>();
      const races = arr
        .map((row, i) => normalizeRace(row, i, used))
        .filter((row): row is Race => row !== null);
      if (!races.length) return { races: [], skipped: 0, error: "レースが1件もありません" };
      return { races, skipped: arr.length - races.length };
    } catch {
      return { races: [], skipped: 0, error: "JSONを読めません" };
    }
  }

  const lines = trimmed
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith("#"));
  if (lines[0]?.includes(",") && /order|着順/.test(lines[0])) {
    return parseCsv(lines);
  }

  const races: Race[] = [];
  let skipped = 0;
  for (const line of lines) {
    if (/着順|2連単/.test(line) && !ORDER_RE.test(line)) {
      skipped += 1;
      continue;
    }
    const race = parseLine(line);
    if (race) races.push(race);
    else skipped += 1;
  }
  if (!races.length) return { races: [], skipped, error: "着順（例 1-2-3）が見つかりません" };
  return { races, skipped };
}

function parseCsv(lines: string[]): { races: Race[]; skipped: number; error?: string } {
  const head = lines[0]?.split(",").map((cell) => cell.trim().replace(/^\uFEFF/, "")) ?? [];
  const col = (...names: string[]) => head.findIndex((cell) => names.includes(cell));
  const oi = col("order", "着順");
  if (oi < 0) return { races: [], skipped: 0, error: "CSVに着順列がありません" };
  const take = (cells: string[], index: number) => (index >= 0 ? (cells[index] ?? "").trim() : "");
  const races: Race[] = [];
  let skipped = 0;
  lines.slice(1).forEach((line, i) => {
    const cells = line.split(",");
    const order = cleanOrder(take(cells, oi));
    if (!ORDER_RE.test(order)) {
      skipped += 1;
      return;
    }
    const sites = emptySites();
    for (const site of SITES) {
      sites[site] = {
        bet: truthy(take(cells, col(`${site}_bet`, `${site}予`))),
        hit: truthy(take(cells, col(`${site}_hit`, `${site}的`))),
      };
    }
    const raceNo = Number(take(cells, col("raceNo", "R")));
    races.push(
      blankRace({
        id: `csv-${i + 1}-${order}`,
        raceNo: Number.isFinite(raceNo) && raceNo > 0 ? raceNo : undefined,
        order,
        payout2: digits(take(cells, col("payout2", "2連単"))),
        payout3: digits(take(cells, col("payout3", "3連単"))),
        racers: take(cells, col("racers", "車")) || "7",
        battle: take(cells, col("battle", "戦型")),
        winLine: take(cells, col("winLine", "1着L")) || "単",
        tech1: take(cells, col("tech1", "決まり手")),
        tech2: take(cells, col("tech2")),
        sites,
      }),
    );
  });
  if (!races.length) return { races: [], skipped, error: "CSVからレースを読めません" };
  return { races, skipped };
}

export function toCsv(races: Race[]) {
  const head = [
    "raceNo",
    "order",
    "tech1",
    "tech2",
    "payout2",
    "payout3",
    "racers",
    "battle",
    "winLine",
    "B_bet",
    "B_hit",
    "Y_bet",
    "Y_hit",
    "N_bet",
    "N_hit",
  ];
  const rows = races.map((race) =>
    [
      race.raceNo ?? "",
      race.order,
      race.tech1,
      race.tech2,
      digits(race.payout2),
      digits(race.payout3),
      race.racers,
      race.battle,
      race.winLine,
      race.sites.B.bet ? 1 : 0,
      race.sites.B.hit ? 1 : 0,
      race.sites.Y.bet ? 1 : 0,
      race.sites.Y.hit ? 1 : 0,
      race.sites.N.bet ? 1 : 0,
      race.sites.N.hit ? 1 : 0,
    ].join(","),
  );
  return `\uFEFF${[head.join(","), ...rows].join("\n")}`;
}

export function downloadText(filename: string, body: string, type: string) {
  const blob = new Blob([body], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}
