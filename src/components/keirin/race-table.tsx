import { useState } from "react";
import { BATTLES, FIELDS, LINES, SITES, type Race, type SiteKey } from "@/lib/keirin/types";
import { cleanOrder, digits, joinTech, splitTech } from "@/lib/keirin/parse";
import { money } from "@/lib/keirin/analytics";
import { cn } from "@/lib/cn";

const MARK_ON: Record<SiteKey, string> = {
  B: "mark-on-b",
  Y: "mark-on-y",
  N: "mark-on-n",
};

type Props = {
  rows: Race[];
  onChange: (id: string, patch: Partial<Race>) => void;
  onSite: (id: string, site: SiteKey, field: "bet" | "hit") => void;
  onDelete: (id: string) => void;
};

export function RaceTable({ rows, onChange, onSite, onDelete }: Props) {
  const [armed, setArmed] = useState<string | null>(null);

  if (!rows.length) {
    return <p className="px-4 py-10 text-center text-sm text-muted">ここにレースが並びます。</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="sheet w-full border-collapse text-left text-sm">
        <thead className="text-xs text-faint">
          <tr className="border-b border-line">
            {["R", "着順", "決まり手", "2連単", "3連単", "車", "戦型", "1着L", "B", "Y", "N", ""].map((label) => (
              <th key={label || "del"} className="px-2 py-3 font-semibold">
                {label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((race, index) => (
            <tr key={race.id} className="border-b border-line align-middle">
              <td className="px-2 py-2 text-muted">{race.raceNo ?? index + 1}</td>
              <td className="px-2 py-2">
                <input
                  className="field w-24"
                  value={race.order}
                  aria-label="着順"
                  placeholder="1-2-3"
                  onChange={(event) => onChange(race.id, { order: cleanOrder(event.target.value) })}
                />
              </td>
              <td className="px-2 py-2">
                <input
                  className="field w-20"
                  value={joinTech(race)}
                  aria-label="決まり手"
                  placeholder="逃"
                  onChange={(event) => onChange(race.id, splitTech(event.target.value))}
                />
              </td>
              <td className="px-2 py-2">
                <input
                  className="field w-24"
                  inputMode="numeric"
                  value={race.payout2}
                  aria-label="2連単"
                  onChange={(event) => onChange(race.id, { payout2: digits(event.target.value) })}
                />
              </td>
              <td className="px-2 py-2">
                <div className="flex items-center gap-2">
                  <input
                    className="field w-28"
                    inputMode="numeric"
                    value={race.payout3}
                    aria-label="3連単"
                    onChange={(event) => onChange(race.id, { payout3: digits(event.target.value) })}
                  />
                  {money(race.payout3) >= 10000 || money(race.payout2) >= 10000 ? (
                    <span className="text-xs font-semibold text-heat">万</span>
                  ) : null}
                </div>
              </td>
              <td className="px-2 py-2">
                <select
                  className="field w-20"
                  value={race.racers}
                  aria-label="車立"
                  onChange={(event) => onChange(race.id, { racers: event.target.value })}
                >
                  {FIELDS.map((field) => (
                    <option key={field} value={field}>
                      {field}車
                    </option>
                  ))}
                </select>
              </td>
              <td className="px-2 py-2">
                <select
                  className="field w-28"
                  value={race.battle}
                  aria-label="戦型"
                  onChange={(event) => onChange(race.id, { battle: event.target.value })}
                >
                  <option value="">—</option>
                  {BATTLES.map((battle) => (
                    <option key={battle} value={battle}>
                      {battle}
                    </option>
                  ))}
                </select>
              </td>
              <td className="px-2 py-2">
                <select
                  className="field w-20"
                  value={race.winLine}
                  aria-label="1着ライン"
                  onChange={(event) => onChange(race.id, { winLine: event.target.value })}
                >
                  {LINES.map((line) => (
                    <option key={line} value={line}>
                      {line}
                    </option>
                  ))}
                </select>
              </td>
              {SITES.map((site) => (
                <td key={site} className="px-2 py-2">
                  <div className="flex gap-1">
                    <button
                      type="button"
                      className={cn("mark", race.sites[site].bet && MARK_ON[site])}
                      aria-pressed={race.sites[site].bet}
                      aria-label={`${site}の予想`}
                      onClick={() => onSite(race.id, site, "bet")}
                    >
                      予
                    </button>
                    <button
                      type="button"
                      className={cn("mark", race.sites[site].hit && "mark-hit")}
                      aria-pressed={race.sites[site].hit}
                      aria-label={`${site}の的中`}
                      onClick={() => onSite(race.id, site, "hit")}
                    >
                      的
                    </button>
                  </div>
                </td>
              ))}
              <td className="px-2 py-2">
                {armed === race.id ? (
                  <div className="flex gap-1">
                    <button type="button" className="btn btn-heat px-3" onClick={() => onDelete(race.id)}>
                      消す
                    </button>
                    <button type="button" className="btn btn-ghost px-3" onClick={() => setArmed(null)}>
                      戻す
                    </button>
                  </div>
                ) : (
                  <button type="button" className="btn btn-ghost px-3" onClick={() => setArmed(race.id)}>
                    削除
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
