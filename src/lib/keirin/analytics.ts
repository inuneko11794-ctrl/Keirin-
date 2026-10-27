import {
  LINES,
  SITES,
  type CarLineCell,
  type CondRow,
  type RoundRow,
  type DashModel,
  type Heat,
  type PairRow,
  type Race,
  type SiteKey,
  type SiteStat,
  type ThirdRow,
} from "./types";

export function money(value: unknown) {
  const n = Number.parseInt(String(value ?? "").replace(/[^0-9]/g, ""), 10);
  return Number.isFinite(n) ? n : 0;
}

export function yen(value: number) {
  return `${Math.round(value).toLocaleString("ja-JP")}円`;
}

export function pct(value: number) {
  if (!Number.isFinite(value)) return "—";
  return `${Math.round(value)}%`;
}

export function isMansha(race: Race) {
  return money(race.payout2) >= 10000 || money(race.payout3) >= 10000;
}

export function orderParts(order: string) {
  return order
    .split("-")
    .map((part) => part.trim())
    .filter(Boolean);
}

export function filterRaces(races: Race[], field: string) {
  if (field === "all") return races;
  return races.filter((race) => race.racers === field);
}

export function autoHit(race: Race): Race {
  if (!isMansha(race)) return race;
  let changed = false;
  const sites = { ...race.sites };
  for (const site of SITES) {
    const cell = sites[site];
    if (cell.bet && !cell.hit) {
      sites[site] = { ...cell, hit: true };
      changed = true;
    }
  }
  return changed ? { ...race, sites } : race;
}

function trioSum(order: string) {
  const parts = orderParts(order).map(Number);
  if (parts.length !== 3 || parts.some((n) => Number.isNaN(n))) return null;
  return (parts[0] ?? 0) + (parts[1] ?? 0) + (parts[2] ?? 0);
}

function zoneOf(car: string) {
  const n = Number(car);
  if (!Number.isFinite(n) || n <= 0) return null;
  if (n <= 3) return "内" as const;
  if (n <= 6) return "中" as const;
  return "外" as const;
}

function betNames(race: Race) {
  return SITES.filter((site) => race.sites[site]?.bet);
}

function anyHit(race: Race) {
  return SITES.some((site) => race.sites[site]?.hit);
}

function overlapWinCarsOf(races: Race[]): DashModel["overlapWinCars"] {
  const out = {
    B: { count: 0, cars: [] },
    Y: { count: 0, cars: [] },
    N: { count: 0, cars: [] },
  } as DashModel["overlapWinCars"];
  for (const site of SITES) {
    const counts = new Map<string, number>();
    let total = 0;
    for (const race of races) {
      if (!race.sites[site]?.bet) continue;
      if (betNames(race).length < 2) continue;
      const car = orderParts(race.order)[0] ?? "";
      if (!car) continue;
      total += 1;
      counts.set(car, (counts.get(car) ?? 0) + 1);
    }
    out[site] = {
      count: total,
      cars: [...counts.entries()]
        .map(([car, count]) => ({ car, count, share: total ? (count / total) * 100 : 0 }))
        .sort((a, b) => b.count - a.count || Number(a.car) - Number(b.car)),
    };
  }
  return out;
}

function roundsOf(races: Race[]): RoundRow[] {
  const bucket = new Map<number, { count: number; mansha: number; p3: number }>();
  for (const race of races) {
    const raceNo = race.raceNo;
    if (!raceNo || raceNo < 1 || raceNo > 12) continue;
    const cur = bucket.get(raceNo) ?? { count: 0, mansha: 0, p3: 0 };
    cur.count += 1;
    cur.p3 += money(race.payout3);
    if (isMansha(race)) cur.mansha += 1;
    bucket.set(raceNo, cur);
  }
  return [...bucket.entries()]
    .map(([raceNo, cell]) => ({
      raceNo,
      count: cell.count,
      mansha: cell.mansha,
      manshaRate: (cell.mansha / cell.count) * 100,
      avgP3: cell.p3 / cell.count,
    }))
    .sort((a, b) => a.raceNo - b.raceNo);
}

function carLineOf(races: Race[], lineKeys: string[]): CarLineCell[] {
  const bucket = new Map<string, Map<string, number>>();
  for (const race of races) {
    const car = orderParts(race.order)[0] ?? "";
    if (!car || !race.winLine) continue;
    const map = bucket.get(car) ?? new Map<string, number>();
    map.set(race.winLine, (map.get(race.winLine) ?? 0) + 1);
    bucket.set(car, map);
  }
  return [...bucket.entries()]
    .map(([car, map]) => {
      const byLine = lineKeys
        .map((line) => ({ line, count: map.get(line) ?? 0 }))
        .filter((row) => row.count > 0);
      const total = byLine.reduce((sum, row) => sum + row.count, 0);
      const top = [...byLine].sort((a, b) => b.count - a.count || a.line.localeCompare(b.line))[0];
      return {
        car,
        total,
        top: top?.line ?? "—",
        topCount: top?.count ?? 0,
        byLine,
      };
    })
    .filter((row) => row.total > 0)
    .sort((a, b) => Number(a.car) - Number(b.car));
}

function heatOf(races: Race[], take: (race: Race) => boolean): Heat {
  let maxCar = 7;
  for (const race of races) {
    maxCar = Math.max(maxCar, Number(race.racers) || 0);
    for (const part of orderParts(race.order)) maxCar = Math.max(maxCar, Number(part) || 0);
  }
  maxCar = Math.min(9, Math.max(5, maxCar));
  const matrix = Array.from({ length: maxCar }, () => Array<number>(maxCar).fill(0));
  let max = 0;
  for (const race of races) {
    if (!take(race)) continue;
    const [first, second] = orderParts(race.order);
    const row = Number(first);
    const col = Number(second);
    if (row >= 1 && row <= maxCar && col >= 1 && col <= maxCar && row !== col) {
      const next = (matrix[row - 1]?.[col - 1] ?? 0) + 1;
      matrix[row - 1]![col - 1] = next;
      max = Math.max(max, next);
    }
  }
  return { maxCar, matrix, max };
}

function pairsFrom(heat: Heat, races: Race[], take: (race: Race) => boolean): PairRow[] {
  const payout = new Map<string, { count: number; p3: number }>();
  let seen = 0;
  for (const race of races) {
    if (!take(race)) continue;
    const [first, second] = orderParts(race.order);
    const a = Number(first);
    const b = Number(second);
    if (!a || !b || a === b) continue;
    seen += 1;
    const key = `${a}-${b}`;
    const cur = payout.get(key) ?? { count: 0, p3: 0 };
    cur.count += 1;
    cur.p3 += money(race.payout3);
    payout.set(key, cur);
  }
  return [...payout.entries()]
    .map(([pair, cell]) => ({
      pair,
      count: cell.count,
      share: seen ? (cell.count / seen) * 100 : 0,
      avgP3: cell.count ? cell.p3 / cell.count : 0,
    }))
    .sort((a, b) => b.count - a.count || b.avgP3 - a.avgP3);
}

function condOf(races: Race[], keyFn: (race: Race) => string): CondRow[] {
  const groups = new Map<string, Race[]>();
  for (const race of races) {
    const key = keyFn(race).trim() || "未設定";
    const list = groups.get(key) ?? [];
    list.push(race);
    groups.set(key, list);
  }
  return [...groups.entries()]
    .map(([key, rows]) => {
      const pays = rows.map((race) => money(race.payout3));
      const mansha = rows.filter(isMansha).length;
      return {
        key,
        count: rows.length,
        manshaRate: (mansha / rows.length) * 100,
        avgP3: pays.reduce((sum, n) => sum + n, 0) / rows.length,
        peak: Math.max(0, ...pays),
      };
    })
    .sort((a, b) => b.count - a.count);
}

const BANDS: { band: string; test: (n: number) => boolean }[] = [
  { band: "〜999", test: (n) => n > 0 && n < 1000 },
  { band: "1千台", test: (n) => n >= 1000 && n < 3000 },
  { band: "3千〜万", test: (n) => n >= 3000 && n < 10000 },
  { band: "万車", test: (n) => n >= 10000 && n < 30000 },
  { band: "3万超", test: (n) => n >= 30000 && n < 100000 },
  { band: "10万超", test: (n) => n >= 100000 },
];

export function buildDash(races: Race[]): DashModel {
  const manshaRaces = races.filter(isMansha);
  const manshaCount = manshaRaces.length;
  let peakP3 = 0;
  let peakOrder = "—";
  for (const race of races) {
    const pay = money(race.payout3);
    if (pay > peakP3) {
      peakP3 = pay;
      peakOrder = race.order || "—";
    }
  }

  const recentMansha = races.slice(0, 10).filter(isMansha).length;
  const gapIndex = races.findIndex(isMansha);
  const gap = gapIndex < 0 ? null : gapIndex;

  const draft: Omit<SiteStat, "payoutPower" | "index">[] = SITES.map((site) => {
    let bet = 0;
    let hit = 0;
    let man = 0;
    let captured = 0;
    let p2 = 0;
    let p3 = 0;
    for (const race of races) {
      const cell = race.sites[site];
      if (!cell) continue;
      if (cell.bet) bet += 1;
      if (cell.bet && cell.hit) {
        hit += 1;
        p2 += money(race.payout2);
        p3 += money(race.payout3);
        if (isMansha(race)) man += 1;
      }
      if (cell.hit && isMansha(race)) captured += 1;
    }
    return {
      site,
      bet,
      hit,
      man,
      hitRate: bet ? (hit / bet) * 100 : 0,
      manRate: bet ? (man / bet) * 100 : 0,
      capture: manshaCount ? (captured / manshaCount) * 100 : 0,
      avgP2: hit ? p2 / hit : 0,
      avgP3: hit ? p3 / hit : 0,
    };
  });

  const maxAvg = Math.max(1, ...draft.map((site) => site.avgP3));
  const sites: SiteStat[] = draft.map((site) => {
    const payoutPower = (site.avgP3 / maxAvg) * 100;
    const index = site.hitRate * 0.35 + site.manRate * 0.25 + site.capture * 0.25 + payoutPower * 0.15;
    return { ...site, payoutPower, index };
  });

  const radar = [
    { axis: "的中率", B: sites[0]?.hitRate ?? 0, Y: sites[1]?.hitRate ?? 0, N: sites[2]?.hitRate ?? 0 },
    { axis: "万車率", B: sites[0]?.manRate ?? 0, Y: sites[1]?.manRate ?? 0, N: sites[2]?.manRate ?? 0 },
    { axis: "捕捉率", B: sites[0]?.capture ?? 0, Y: sites[1]?.capture ?? 0, N: sites[2]?.capture ?? 0 },
    { axis: "配当力", B: sites[0]?.payoutPower ?? 0, Y: sites[1]?.payoutPower ?? 0, N: sites[2]?.payoutPower ?? 0 },
  ];

  const agreement = [0, 1, 2, 3].map((bets) => {
    const rows = races.filter((race) => betNames(race).length === bets);
    const hits = rows.filter(anyHit);
    const mansha = rows.filter(isMansha).length;
    const avg = (list: Race[]) =>
      list.length ? list.reduce((sum, race) => sum + money(race.payout3), 0) / list.length : 0;
    return {
      bets,
      count: rows.length,
      manshaRate: rows.length ? (mansha / rows.length) * 100 : 0,
      avgP3: avg(rows),
      hitRate: rows.length ? (hits.length / rows.length) * 100 : 0,
      avgP3OnHit: avg(hits),
    };
  });

  const overlapMap = new Map<string, Race[]>();
  for (const race of races) {
    const names = betNames(race);
    const key = names.length ? names.join("+") : "なし";
    const list = overlapMap.get(key) ?? [];
    list.push(race);
    overlapMap.set(key, list);
  }
  const overlap = [...overlapMap.entries()]
    .map(([key, rows]) => {
      const hits = rows.filter(anyHit);
      const mansha = rows.filter(isMansha).length;
      const avg = (list: Race[]) =>
        list.length ? list.reduce((sum, race) => sum + money(race.payout3), 0) / list.length : 0;
      return {
        key,
        count: rows.length,
        mansha,
        manshaRate: (mansha / rows.length) * 100,
        avgP3: avg(rows),
        avgP3OnHit: avg(hits),
      };
    })
    .sort((a, b) => b.count - a.count);

  const manWithOrder = manshaRaces.filter((race) => orderParts(race.order)[0]);
  const carBucket = new Map<string, { count: number; p3: number }>();
  for (const race of manWithOrder) {
    const car = orderParts(race.order)[0] ?? "";
    const cur = carBucket.get(car) ?? { count: 0, p3: 0 };
    cur.count += 1;
    cur.p3 += money(race.payout3);
    carBucket.set(car, cur);
  }
  const winCars = [...carBucket.entries()]
    .map(([car, cell]) => ({ car, count: cell.count, avgP3: cell.p3 / cell.count }))
    .sort((a, b) => Number(a.car) - Number(b.car));

  const countZones = (rows: Race[]) => {
    const tally = { 内: 0, 中: 0, 外: 0 };
    for (const race of rows) {
      const zone = zoneOf(orderParts(race.order)[0] ?? "");
      if (zone) tally[zone] += 1;
    }
    return tally;
  };
  const zones = [
    { scope: "全体" as const, ...countZones(races) },
    { scope: "万車" as const, ...countZones(manWithOrder) },
  ];

  const lineAll = new Map<string, number>();
  const lineMan = new Map<string, number>();
  for (const race of races) {
    if (!race.winLine) continue;
    lineAll.set(race.winLine, (lineAll.get(race.winLine) ?? 0) + 1);
  }
  for (const race of manWithOrder) {
    if (!race.winLine) continue;
    lineMan.set(race.winLine, (lineMan.get(race.winLine) ?? 0) + 1);
  }
  const lineKeys = [...new Set([...LINES, ...lineAll.keys(), ...lineMan.keys()])];
  const allLineTotal = [...lineAll.values()].reduce((sum, n) => sum + n, 0);
  const manLineTotal = [...lineMan.values()].reduce((sum, n) => sum + n, 0);
  const lines = lineKeys
    .map((line) => {
      const all = lineAll.get(line) ?? 0;
      const mansha = lineMan.get(line) ?? 0;
      const allPct = allLineTotal ? (all / allLineTotal) * 100 : 0;
      const manPct = manLineTotal ? (mansha / manLineTotal) * 100 : 0;
      return {
        line,
        all,
        mansha,
        allPct,
        manPct,
        lift: allPct > 0 ? manPct / allPct : null,
      };
    })
    .filter((row) => row.all > 0 || row.mansha > 0);

  const carLines = {
    all: carLineOf(races, lineKeys),
    man: carLineOf(manWithOrder, lineKeys),
  };

  const siteLineMap: Record<SiteKey, Map<string, number>> = {
    B: new Map(),
    Y: new Map(),
    N: new Map(),
  };
  for (const race of manWithOrder) {
    if (!race.winLine) continue;
    for (const site of SITES) {
      if (!race.sites[site]?.hit) continue;
      const map = siteLineMap[site];
      map.set(race.winLine, (map.get(race.winLine) ?? 0) + 1);
    }
  }
  const siteLines = lineKeys.map((line) => ({
    line,
    B: siteLineMap.B.get(line) ?? 0,
    Y: siteLineMap.Y.get(line) ?? 0,
    N: siteLineMap.N.get(line) ?? 0,
  }));

  const sumMap = new Map<number, { count: number; p3: number; mansha: number }>();
  for (const race of races) {
    const sum = trioSum(race.order);
    if (sum == null) continue;
    const cur = sumMap.get(sum) ?? { count: 0, p3: 0, mansha: 0 };
    cur.count += 1;
    cur.p3 += money(race.payout3);
    if (isMansha(race)) cur.mansha += 1;
    sumMap.set(sum, cur);
  }
  const sums = [...sumMap.entries()]
    .map(([sum, cell]) => ({
      sum,
      count: cell.count,
      avgP3: cell.p3 / cell.count,
      mansha: cell.mansha,
    }))
    .sort((a, b) => a.sum - b.sum);

  const thirdBucket = new Map<string, Map<string, { count: number; p3: number }>>();
  for (const race of races) {
    const parts = orderParts(race.order);
    if (parts.length < 3) continue;
    const pair = `${parts[0]}-${parts[1]}`;
    const third = parts[2] ?? "";
    if (!third) continue;
    const map = thirdBucket.get(pair) ?? new Map();
    const cur = map.get(third) ?? { count: 0, p3: 0 };
    cur.count += 1;
    cur.p3 += money(race.payout3);
    map.set(third, cur);
    thirdBucket.set(pair, map);
  }
  const thirds: Record<string, ThirdRow[]> = {};
  for (const [pair, map] of thirdBucket) {
    const total = [...map.values()].reduce((sum, cell) => sum + cell.count, 0);
    thirds[pair] = [...map.entries()]
      .map(([car, cell]) => ({
        car,
        count: cell.count,
        share: total ? (cell.count / total) * 100 : 0,
        avgP3: cell.p3 / cell.count,
      }))
      .sort((a, b) => b.count - a.count || Number(a.car) - Number(b.car));
  }
  const pairs = Object.keys(thirds).sort();

  const heatAll = heatOf(races, (race) => orderParts(race.order).length >= 2);
  const heatMan = heatOf(races, (race) => isMansha(race) && orderParts(race.order).length >= 2);
  const rankedPairs = pairsFrom(heatAll, races, (race) => orderParts(race.order).length >= 2);
  const topPairs = rankedPairs.slice(0, 6);
  const richPairs = [...rankedPairs].filter((row) => row.count >= 2).sort((a, b) => b.avgP3 - a.avgP3).slice(0, 5);

  const topPayouts = [...races]
    .filter((race) => money(race.payout3) > 0 && race.order)
    .sort((a, b) => money(b.payout3) - money(a.payout3))
    .slice(0, 5)
    .map((race) => ({
      order: race.order,
      payout2: money(race.payout2),
      payout3: money(race.payout3),
      line: race.winLine || "—",
    }));

  const chrono = [...races].reverse();
  const series = chrono.map((race, index) => {
    const payout3 = money(race.payout3);
    const mansha = isMansha(race);
    return {
      i: index + 1,
      order: race.order || "—",
      payout3,
      mark: mansha ? Math.max(payout3, 1) : null,
    };
  });

  const bands = BANDS.map((band) => {
    const row = { band: band.band, all: 0, B: 0, Y: 0, N: 0 };
    for (const race of races) {
      const pay = money(race.payout3);
      if (!band.test(pay)) continue;
      row.all += 1;
      for (const site of SITES) {
        if (race.sites[site]?.hit) row[site] += 1;
      }
    }
    return row;
  });

  const fieldCars = new Map<string, number>();
  for (const race of manWithOrder) {
    const car = orderParts(race.order)[0] ?? "";
    fieldCars.set(car, (fieldCars.get(car) ?? 0) + 1);
  }
  const fieldTotal = manWithOrder.length || 1;
  const manshaBySite = { B: [], Y: [], N: [] } as DashModel["manshaBySite"];
  const manshaHits = { B: 0, Y: 0, N: 0 };
  for (const site of SITES) {
    const counts = new Map<string, number>();
    for (const race of manWithOrder) {
      if (!race.sites[site]?.hit) continue;
      manshaHits[site] += 1;
      const car = orderParts(race.order)[0] ?? "";
      counts.set(car, (counts.get(car) ?? 0) + 1);
    }
    const total = manshaHits[site] || 1;
    manshaBySite[site] = [...counts.entries()]
      .map(([car, count]) => ({
        car,
        count,
        pct: (count / total) * 100,
        fieldPct: ((fieldCars.get(car) ?? 0) / fieldTotal) * 100,
      }))
      .sort((a, b) => b.count - a.count || Number(a.car) - Number(b.car));
    manshaHits[site] = counts.size ? [...counts.values()].reduce((sum, n) => sum + n, 0) : 0;
  }

  return {
    total: races.length,
    manshaCount,
    manshaRate: races.length ? (manshaCount / races.length) * 100 : 0,
    peakP3,
    peakOrder,
    recentMansha,
    gap,
    sites,
    radar,
    agreement,
    overlap,
    winCars,
    zones,
    lines,
    carLines,
    rounds: roundsOf(races),
    overlapWinCars: overlapWinCarsOf(races),
    siteLines,
    sums,
    pairs,
    thirds,
    topPairs,
    richPairs,
    topPayouts,
    heatAll,
    heatMan,
    series,
    bands,
    battles: condOf(races, (race) => race.battle),
    techs: condOf(races, (race) => [race.tech1, race.tech2].filter(Boolean).join("-")),
    fields: condOf(races, (race) => (race.racers ? `${race.racers}車` : "")).sort(
      (a, b) => Number(b.key.replace("車", "")) - Number(a.key.replace("車", "")),
    ),
    manshaBySite,
    manshaHits,
  };
}

export function buildInsights(model: DashModel, sample: boolean) {
  if (model.total < 3) {
    return ["レースがまだ少ないです。20件を超えると、出目とサイトの偏りが言葉になります。"];
  }
  const lead = sample ? "見本では、" : "";
  const lines: string[] = [];
  const best = [...model.sites].sort((a, b) => b.index - a.index)[0];
  if (best && best.bet > 0) {
    lines.push(
      `${lead}${best.site}が総合指数で先頭。的中率 ${Math.round(best.hitRate)}%、万車の捕捉率 ${Math.round(best.capture)}%、的中時の平均3連単は ${yen(best.avgP3)}。`,
    );
  }
  const one = model.agreement.find((row) => row.bets === 1);
  const three = model.agreement.find((row) => row.bets === 3);
  if (one && three && one.count >= 3 && three.count >= 3) {
    const diff = Math.round(three.manshaRate - one.manshaRate);
    if (diff >= 8) {
      lines.push(
        `3サイトが揃った ${three.count}R の万車率は ${Math.round(three.manshaRate)}%。1サイトだけの ${Math.round(one.manshaRate)}% より ${diff} ポイント高い。`,
      );
    } else if (diff <= -8) {
      lines.push(
        `3サイトが揃った万車率は ${Math.round(three.manshaRate)}% で、1サイトだけの ${Math.round(one.manshaRate)}% を下回る。寄ったあとの過信は禁物。`,
      );
    } else {
      lines.push(
        `揃った数と万車率の差はまだ小さい。1サイト ${Math.round(one.manshaRate)}% / 3サイト ${Math.round(three.manshaRate)}%。`,
      );
    }
  }
  const busy = [...model.sums].sort((a, b) => b.count - a.count)[0];
  const rich = [...model.sums].filter((row) => row.count >= 2).sort((a, b) => b.avgP3 - a.avgP3)[0];
  if (busy && rich && busy.sum !== rich.sum) {
    lines.push(`よく出る合計は ${busy.sum}。平均配当が高いのは合計 ${rich.sum}（${yen(rich.avgP3)}）。`);
  } else if (model.topPairs[0] && model.topPairs[0].count >= 2) {
    const pair = model.topPairs[0];
    lines.push(`いちばん厚い連対は ${pair.pair}（${pair.count}回、平均3連単 ${yen(pair.avgP3)}）。`);
  }
  const allZone = model.zones[0];
  const manZone = model.zones[1];
  if (allZone && manZone && model.manshaCount >= 4) {
    const allTotal = allZone.内 + allZone.中 + allZone.外 || 1;
    const manTotal = manZone.内 + manZone.中 + manZone.外 || 1;
    const shift = (manZone.外 / manTotal) * 100 - (allZone.外 / allTotal) * 100;
    if (shift >= 12) {
      lines.push(`万車に限ると、1着が外（7番以降）へ ${Math.round(shift)} ポイント寄っている。`);
    }
  }
  return lines.slice(0, 4);
}
