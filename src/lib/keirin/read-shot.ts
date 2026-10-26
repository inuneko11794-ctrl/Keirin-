import { DIGIT_BITS, DIGIT_H, DIGIT_W, TECH_BITS, TECH_H, TECH_W } from "./glyphs";
import { blankRace, type Race } from "./types";

export type Raster = {
  width: number;
  height: number;
  data: Uint8ClampedArray;
};

export type OrderRow = { cars: [number, number, number]; techs: [string, string] };
export type PayoutRow = {
  nirentan: number;
  niPop: number | null;
  sanrentan: number;
  sanPop: number | null;
};
export type ShotReading = {
  kind: "order" | "payout" | "unknown";
  order: OrderRow[];
  payout: PayoutRow[];
};

type Comp = {
  x: number;
  y: number;
  x1: number;
  y1: number;
  n: number;
  pts: [number, number][];
};

function unpack(bits: string, w: number, h: number) {
  const grid: number[][] = [];
  for (let y = 0; y < h; y++) {
    grid.push(
      bits
        .slice(y * w, y * w + w)
        .split("")
        .map((cell) => (cell === "1" ? 1 : 0)),
    );
  }
  return grid;
}

const DIGIT_TEMPLATES = Object.entries(DIGIT_BITS).map(([ch, bits]) => ({
  ch,
  grid: unpack(bits, DIGIT_W, DIGIT_H),
}));
const TECH_TEMPLATES = Object.entries(TECH_BITS).map(([ch, bits]) => ({
  ch,
  grid: unpack(bits, TECH_W, TECH_H),
}));

function at(img: Raster, x: number, y: number) {
  const i = (y * img.width + x) * 4;
  return [img.data[i] ?? 0, img.data[i + 1] ?? 0, img.data[i + 2] ?? 0];
}

function rowBands(img: Raster) {
  const { width: w, height: h } = img;
  const ys: number[] = [];
  const step = Math.max(4, Math.floor(w / 140));
  for (let y = 0; y < h; y++) {
    let close = 0;
    let sum = 0;
    let n = 0;
    for (let x = Math.floor(w * 0.08); x < Math.floor(w * 0.92); x += step) {
      const [r, g, b] = at(img, x, y);
      n += 1;
      sum += r;
      if (Math.abs(r - g) < 28 && Math.abs(g - b) < 28 && r >= 198 && r <= 250) close += 1;
    }
    const avg = sum / Math.max(1, n);
    if (close > n * 0.86 && avg > 210 && avg < 249) ys.push(y);
  }
  const groups: number[][] = [];
  for (const y of ys) {
    const last = groups[groups.length - 1];
    if (last && y - last[last.length - 1]! <= Math.max(3, Math.floor(h / 600))) last.push(y);
    else groups.push([y]);
  }
  const lines = groups
    .filter((group) => group[group.length - 1]! - group[0]! <= 8 && group[0]! > h * 0.16)
    .map((group) => group[Math.floor(group.length / 2)]!);
  const bands: [number, number][] = [];
  for (let i = 0; i < lines.length - 1; i++) {
    const gap = lines[i + 1]! - lines[i]!;
    if (gap > h * 0.03 && gap < h * 0.12) bands.push([lines[i]! + 2, lines[i + 1]! - 2]);
  }
  return bands;
}

function components(img: Raster, x0: number, x1: number, y0: number, y1: number, dark: number) {
  const w = x1 - x0;
  const h = y1 - y0;
  if (w <= 0 || h <= 0) return [];
  const mask = new Uint8Array(w * h);
  const seen = new Uint8Array(w * h);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const [r, g, b] = at(img, x0 + x, y0 + y);
      if (r < dark && g < dark && b < dark + 15) mask[y * w + x] = 1;
    }
  }
  const comps: Comp[] = [];
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const start = y * w + x;
      if (!mask[start] || seen[start]) continue;
      const stack: [number, number][] = [[x, y]];
      seen[start] = 1;
      const pts: [number, number][] = [];
      while (stack.length) {
        const [cx, cy] = stack.pop()!;
        pts.push([cx, cy]);
        for (const [dx, dy] of [
          [1, 0],
          [-1, 0],
          [0, 1],
          [0, -1],
        ] as const) {
          const nx = cx + dx;
          const ny = cy + dy;
          if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
          const ni = ny * w + nx;
          if (mask[ni] && !seen[ni]) {
            seen[ni] = 1;
            stack.push([nx, ny]);
          }
        }
      }
      let minX = pts[0]![0];
      let maxX = pts[0]![0];
      let minY = pts[0]![1];
      let maxY = pts[0]![1];
      for (const [px, py] of pts) {
        if (px < minX) minX = px;
        if (px > maxX) maxX = px;
        if (py < minY) minY = py;
        if (py > maxY) maxY = py;
      }
      comps.push({
        x: minX + x0,
        y: minY + y0,
        x1: maxX + x0,
        y1: maxY + y0,
        n: pts.length,
        pts: pts.map(([px, py]) => [px + x0, py + y0]),
      });
    }
  }
  return comps;
}

function normalize(comp: Comp, w: number, h: number) {
  const bw = Math.max(1, comp.x1 - comp.x + 1);
  const bh = Math.max(1, comp.y1 - comp.y + 1);
  const pts = new Set(comp.pts.map(([x, y]) => `${x},${y}`));
  const grid: number[][] = [];
  for (let gy = 0; gy < h; gy++) {
    const row: number[] = [];
    for (let gx = 0; gx < w; gx++) {
      const sx = comp.x + Math.floor(((gx + 0.5) * bw) / w);
      const sy = comp.y + Math.floor(((gy + 0.5) * bh) / h);
      row.push(pts.has(`${sx},${sy}`) ? 1 : 0);
    }
    grid.push(row);
  }
  return grid;
}

function hamming(a: number[][], b: number[][]) {
  let dist = 0;
  for (let y = 0; y < a.length; y++) {
    for (let x = 0; x < a[0]!.length; x++) if (a[y]![x] !== b[y]![x]) dist += 1;
  }
  return dist;
}

function readDigit(comp: Comp) {
  const grid = normalize(comp, DIGIT_W, DIGIT_H);
  let best = "0";
  let dist = 1e9;
  for (const template of DIGIT_TEMPLATES) {
    const next = hamming(grid, template.grid);
    if (next < dist) {
      dist = next;
      best = template.ch;
    }
  }
  return { ch: best, dist };
}

function payoutGroups(img: Raster, y0: number, y1: number) {
  const w = img.width;
  const rh = y1 - y0;
  const comps = components(
    img,
    Math.floor(w * 0.28),
    w - 2,
    y0 + Math.floor(rh * 0.12),
    y0 + Math.floor(rh * 0.9),
    155,
  ).filter((comp) => comp.n > 18 && comp.y1 - comp.y > rh * 0.12);
  if (!comps.length) return [];
  const heights = comps.map((comp) => comp.y1 - comp.y).sort((a, b) => a - b);
  const med = heights[Math.floor(heights.length / 2)] ?? 0;
  const kept = comps.filter((comp) => {
    const bw = comp.x1 - comp.x + 1;
    const bh = comp.y1 - comp.y + 1;
    if (bh > med * 1.15 && bw < bh * 0.5) return false;
    if (bw > med * 1.05) return false;
    return true;
  });
  kept.sort((a, b) => a.x - b.x);
  const groups: Comp[][] = [];
  for (const comp of kept) {
    const last = groups[groups.length - 1];
    if (!last || comp.x - last[last.length - 1]!.x1 > w * 0.035) groups.push([comp]);
    else last.push(comp);
  }
  return groups;
}

function groupValue(group: Comp[]) {
  if (!group.length || group.length > 6) return null;
  let text = "";
  let dist = 0;
  for (const comp of group) {
    const digit = readDigit(comp);
    text += digit.ch;
    dist = Math.max(dist, digit.dist);
  }
  const value = Number(text);
  if (!Number.isFinite(value)) return null;
  return { value, dist };
}

function readPayout(img: Raster) {
  const rows: PayoutRow[] = [];
  for (const [y0, y1] of rowBands(img)) {
    const groups = payoutGroups(img, y0, y1);
    if (groups.length < 4) continue;
    const ni = groupValue(groups[0] ?? []);
    const nip = groupValue(groups[1] ?? []);
    const san = groupValue(groups[2] ?? []);
    const sanp = groupValue(groups[3] ?? []);
    if (!ni || !san || ni.value < 100 || san.value < 100) continue;
    if (ni.dist > 90 || san.dist > 90) continue;
    rows.push({
      nirentan: ni.value,
      niPop: nip && nip.dist <= 90 && nip.value >= 1 && nip.value <= 999 ? nip.value : null,
      sanrentan: san.value,
      sanPop: sanp && sanp.dist <= 90 && sanp.value >= 1 && sanp.value <= 999 ? sanp.value : null,
    });
  }
  return rows;
}

function isBg(rgb: number[]) {
  return rgb[0]! > 248 && rgb[1]! > 248 && rgb[2]! > 248;
}

function plateColor(rgb: number[]) {
  const r = rgb[0] ?? 0;
  const g = rgb[1] ?? 0;
  const b = rgb[2] ?? 0;
  const mx = Math.max(r, g, b);
  const mn = Math.min(r, g, b);
  const sat = mx - mn;
  if (mn > 190 && sat < 40) return 1;
  if (mx < 110 && sat < 40) return 2;
  if (r > 200 && g > 160 && b < 140 && g > b + 40 && r > b + 60) return 5;
  if (g > 120 && g > r + 30 && g >= b && b < 180 && r < 180) return 6;
  if (r > 180 && g < 50 && b > 60 && b < 160 && r > b + 40) return 8;
  if (b > 140 && r > 100 && g < 50 && Math.abs(r - b) < 80) return 9;
  if (b > 150 && r < 90 && b > g + 20) return 4;
  if (r > 180 && g > 80 && g < 200 && b < 140 && r > g + 20 && g > b) return 7;
  if (r > 150 && g < 90 && b < 90 && r > g + 60) return 3;
  return 0;
}

function readCars(img: Raster, y0: number, y1: number) {
  const w = img.width;
  const rh = y1 - y0;
  const band0 = y0 + Math.floor(rh * 0.18);
  const band1 = y0 + Math.floor(rh * 0.82);
  const col = new Array<number>(w).fill(0);
  for (let x2 = 0; x2 < w; x2++) {
    let count = 0;
    for (let y = band0; y < band1; y++) if (!isBg(at(img, x2, y))) count += 1;
    col[x2] = count;
  }
  const thresh = Math.floor((band1 - band0) * 0.42);
  const runs: [number, number][] = [];
  let x = 0;
  while (x < w) {
    if (col[x]! >= thresh) {
      const x0 = x;
      while (x < w && col[x]! >= thresh) x += 1;
      if (x - x0 >= 16 && x - x0 <= Math.floor(w * 0.09)) runs.push([x0, x - 1]);
    } else x += 1;
  }
  const cars: number[] = [];
  for (const [x0, x1] of runs) {
    const cx = (x0 + x1) / 2;
    if (cx <= w * 0.16 || cx >= w * 0.8) continue;
    const samples: number[][] = [];
    const yy0 = band0 + Math.floor((band1 - band0) * 0.25);
    const yy1 = band0 + Math.floor((band1 - band0) * 0.75);
    for (let yy = yy0; yy < yy1; yy++) {
      for (const xx of [x0 + 2, x0 + 3, x0 + 4, x1 - 2, x1 - 3, x1 - 4]) {
        if (xx >= 0 && xx < w) samples.push(at(img, xx, yy));
      }
    }
    if (!samples.length) continue;
    const med = [0, 1, 2].map((channel) => {
      const vals = samples.map((sample) => sample[channel] ?? 0).sort((a, b) => a - b);
      return vals[Math.floor(vals.length / 2)] ?? 0;
    });
    const car = plateColor(med);
    if (car) cars.push(car);
  }
  if (cars.length !== 3) return null;
  return [cars[0]!, cars[1]!, cars[2]!] as [number, number, number];
}

function readTechs(img: Raster, y0: number, y1: number): [string, string] {
  const w = img.width;
  const rh = y1 - y0;
  const xStart = Math.floor(w * 0.7);
  const ww = w - xStart;
  const mask = new Uint8Array(ww * rh);
  const seen = new Uint8Array(ww * rh);
  for (let y = 0; y < rh; y++) {
    for (let x = 0; x < ww; x++) {
      const [r, g, b] = at(img, xStart + x, y0 + y);
      if (Math.abs(r - g) < 12 && Math.abs(g - b) < 12 && r >= 225 && r <= 246) mask[y * ww + x] = 1;
    }
  }
  const chips: [number, number, number, number][] = [];
  for (let y = 0; y < rh; y++) {
    for (let x = 0; x < ww; x++) {
      const start = y * ww + x;
      if (!mask[start] || seen[start]) continue;
      const stack: [number, number][] = [[x, y]];
      seen[start] = 1;
      const pts: [number, number][] = [];
      while (stack.length) {
        const [cx, cy] = stack.pop()!;
        pts.push([cx, cy]);
        for (const [dx, dy] of [
          [1, 0],
          [-1, 0],
          [0, 1],
          [0, -1],
        ] as const) {
          const nx = cx + dx;
          const ny = cy + dy;
          if (nx < 0 || ny < 0 || nx >= ww || ny >= rh) continue;
          const ni = ny * ww + nx;
          if (mask[ni] && !seen[ni]) {
            seen[ni] = 1;
            stack.push([nx, ny]);
          }
        }
      }
      if (pts.length < 40) continue;
      let minX = pts[0]![0];
      let maxX = pts[0]![0];
      let minY = pts[0]![1];
      let maxY = pts[0]![1];
      for (const [px, py] of pts) {
        if (px < minX) minX = px;
        if (px > maxX) maxX = px;
        if (py < minY) minY = py;
        if (py > maxY) maxY = py;
      }
      chips.push([minX + xStart, minY + y0, maxX + xStart, maxY + y0]);
    }
  }
  chips.sort((a, b) => a[0] - b[0]);
  const techs: string[] = [];
  for (const [x0, cy0, x1, cy1] of chips) {
    const ink: [number, number][] = [];
    for (let y = cy0; y <= cy1; y++) {
      for (let x = x0; x <= x1; x++) {
        const [r, g, b] = at(img, x, y);
        if (r < 80 && g < 80 && b < 80) ink.push([x, y]);
      }
    }
    if (ink.length < 8) continue;
    let minX = ink[0]![0];
    let maxX = ink[0]![0];
    let minY = ink[0]![1];
    let maxY = ink[0]![1];
    for (const [px, py] of ink) {
      if (px < minX) minX = px;
      if (px > maxX) maxX = px;
      if (py < minY) minY = py;
      if (py > maxY) maxY = py;
    }
    const grid = normalize({ x: minX, y: minY, x1: maxX, y1: maxY, n: ink.length, pts: ink }, TECH_W, TECH_H);
    let best = "";
    let dist = 1e9;
    for (const template of TECH_TEMPLATES) {
      const next = hamming(grid, template.grid);
      if (next < dist) {
        dist = next;
        best = template.ch;
      }
    }
    techs.push(dist <= 100 ? best : "");
  }
  return [techs[0] ?? "", techs[1] ?? ""];
}

function readOrder(img: Raster) {
  const rows: OrderRow[] = [];
  for (const [y0, y1] of rowBands(img)) {
    const cars = readCars(img, y0, y1);
    if (!cars) continue;
    rows.push({ cars, techs: readTechs(img, y0, y1) });
  }
  return rows;
}

export function ingestShot(img: Raster): ShotReading {
  const order = readOrder(img);
  const payout = readPayout(img);
  let kind: ShotReading["kind"] = "unknown";
  if (order.length >= 4 && order.length >= payout.length) kind = "order";
  else if (payout.length >= 4) kind = "payout";
  return { kind, order, payout };
}

export async function rasterOf(file: Blob): Promise<Raster> {
  const bitmap = await createImageBitmap(file);
  const maxW = 1600;
  const scale = bitmap.width > maxW ? maxW / bitmap.width : 1;
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(bitmap.width * scale);
  canvas.height = Math.round(bitmap.height * scale);
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  if (!ctx) throw new Error("canvas");
  ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);
  bitmap.close();
  const image = ctx.getImageData(0, 0, canvas.width, canvas.height);
  return { width: image.width, height: image.height, data: image.data };
}

export function racesFromReading(order: OrderRow[], payout: PayoutRow[]): Race[] {
  const count = Math.max(order.length, payout.length);
  const races: Race[] = [];
  for (let i = 0; i < count; i++) {
    const row = order[i];
    const pay = payout[i];
    if (!row && !pay) continue;
    races.push(
      blankRace({
        order: row ? `${row.cars[0]}-${row.cars[1]}-${row.cars[2]}` : "",
        tech1: row?.techs[0] ?? "",
        tech2: row?.techs[1] ?? "",
        payout2: pay ? String(pay.nirentan) : "",
        payout3: pay ? String(pay.sanrentan) : "",
      }),
    );
  }
  return races;
}
