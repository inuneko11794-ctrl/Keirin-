import { useEffect, useState, type ReactElement, type ReactNode } from "react";
import {
  Bar,
  CartesianGrid,
  Cell,
  ComposedChart,
  Legend,
  Line,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { buildInsights, pct, yen } from "@/lib/keirin/analytics";
import type { DashModel, Heat } from "@/lib/keirin/types";
import { cn } from "@/lib/cn";

const TICK = { fill: "var(--color-muted)", fontSize: 11 };
const AXIS = { width: 32 };
const GRID = "var(--color-line)";

function FitChart({ children }: { children: ReactElement }) {
  const [on, setOn] = useState(false);
  useEffect(() => {
    setOn(true);
  }, []);
  return (
    <div className="h-72 w-full min-w-0">
      {on ? (
        <ResponsiveContainer width="100%" height="100%">
          {children}
        </ResponsiveContainer>
      ) : null}
    </div>
  );
}

function Tip({
  active,
  payload,
  label,
  moneyKeys,
}: {
  active?: boolean;
  payload?: { name?: string; value?: number | string; color?: string }[];
  label?: string | number;
  moneyKeys?: string[];
}) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rounded-md border border-line bg-ink-2 px-3 py-2 text-sm text-paper">
      {label != null && String(label) !== "" ? <p className="mb-1 font-semibold">{label}</p> : null}
      {payload
        .filter((item) => item.value != null && item.value !== "")
        .map((item) => {
          const numeric = typeof item.value === "number" ? item.value : Number(item.value);
          const text =
            moneyKeys?.includes(String(item.name)) && Number.isFinite(numeric) ? yen(numeric) : item.value;
          return (
            <p key={`${item.name}-${item.value}`} style={{ color: item.color }}>
              {item.name}: {text}
            </p>
          );
        })}
    </div>
  );
}

function Panel({
  title,
  hint,
  children,
  className,
}: {
  title: string;
  hint?: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={cn("panel p-4 md:p-5", className)}>
      <h3 className="text-base font-semibold">{title}</h3>
      {hint ? <p className="mt-1 text-sm text-muted">{hint}</p> : null}
      <div className="mt-4">{children}</div>
    </section>
  );
}

function Empty({ label }: { label: string }) {
  return <p className="grid h-64 place-items-center text-sm text-muted">{label}</p>;
}

function HeatGrid({ heat }: { heat: Heat }) {
  const cars = Array.from({ length: heat.maxCar }, (_, index) => index + 1);
  return (
    <div className="min-w-0">
      <table className="w-full table-fixed border-collapse text-center">
        <thead>
          <tr>
            <th className="p-0.5 text-[10px] text-faint">1＼2</th>
            {cars.map((car) => (
              <th key={car} className="p-1 text-sm text-muted">
                {car}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {cars.map((row) => (
            <tr key={row}>
              <th className="p-1 text-sm text-muted">{row}</th>
              {cars.map((col) => {
                if (row === col) {
                  return (
                    <td key={col} className="p-1">
                      <div className="heat-cell text-faint" style={{ ["--p" as string]: 0 }} />
                    </td>
                  );
                }
                const value = heat.matrix[row - 1]?.[col - 1] ?? 0;
                const intensity = heat.max ? value / heat.max : 0;
                return (
                  <td key={col} className="p-1">
                    <div
                      className={cn("heat-cell", intensity > 0.55 ? "text-ink" : "text-paper")}
                      style={{ ["--p" as string]: intensity.toFixed(3) }}
                      title={`${row}-${col} : ${value}回`}
                    >
                      {value > 0 ? value : ""}
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ZoneBar({ label, 内, 中, 外 }: { label: string; 内: number; 中: number; 外: number }) {
  const total = 内 + 中 + 外 || 1;
  const parts = [
    { name: "内1-3", value: 内, className: "bg-site-b text-ink" },
    { name: "中4-6", value: 中, className: "bg-site-y text-ink" },
    { name: "外7-", value: 外, className: "bg-heat text-paper" },
  ];
  return (
    <div>
      <p className="mb-2 text-sm text-muted">{label}</p>
      <div className="flex h-11 overflow-hidden rounded-md">
        {parts.map((part) => (
          <div
            key={part.name}
            className={cn("min-w-0 overflow-hidden", part.className)}
            style={{ width: `${(part.value / total) * 100}%` }}
          />
        ))}
      </div>
      <p className="mt-1 flex flex-wrap gap-x-3 gap-y-1 text-xs text-muted">
        {parts.map((part) => (
          <span key={part.name}>
            {part.name} {Math.round((part.value / total) * 100)}%
          </span>
        ))}
      </p>
    </div>
  );
}

function CondTable({ rows }: { rows: { key: string; count: number; manshaRate: number; avgP3: number; peak: number }[] }) {
  if (!rows.length) return <p className="text-sm text-muted">まだありません。</p>;
  return (
    <table className="w-full text-sm">
      <thead className="text-left text-xs text-faint">
        <tr>
          <th className="py-2 font-semibold">条件</th>
          <th className="py-2 font-semibold">件数</th>
          <th className="py-2 font-semibold">万車率</th>
          <th className="py-2 font-semibold">平均3連</th>
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.key} className="border-t border-line">
            <td className="py-2 font-medium">{row.key}</td>
            <td className="py-2">{row.count}</td>
            <td className="py-2">{pct(row.manshaRate)}</td>
            <td className="py-2">{yen(row.avgP3)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export function BoardView({ model, sample }: { model: DashModel; sample: boolean }) {
  const [heatMode, setHeatMode] = useState<"all" | "man">("all");
  const [pair, setPair] = useState("");
  const [logScale, setLogScale] = useState(false);
  const insights = buildInsights(model, sample);
  const heat = heatMode === "man" ? model.heatMan : model.heatAll;
  const thirds = pair ? (model.thirds[pair] ?? []) : [];

  useEffect(() => {
    if (pair && !model.pairs.includes(pair)) setPair("");
  }, [model.pairs, pair]);

  const series = logScale
    ? model.series.map((row) => ({
        ...row,
        payout3: row.payout3 >= 100 ? row.payout3 : null,
        mark: row.mark != null && row.mark >= 100 ? row.mark : null,
      }))
    : model.series;

  return (
    <div className="space-y-4">
      <section className="panel wash p-4 md:p-5">
        <p className="kicker">読み</p>
        <ul className="mt-3 space-y-2">
          {insights.map((line) => (
            <li key={line} className="border-l-2 border-heat pl-3 text-sm md:text-base">
              {line}
            </li>
          ))}
        </ul>
      </section>

      <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        <Kpi label="レース" value={String(model.total)} unit="R" />
        <Kpi label="万車率" value={String(Math.round(model.manshaRate))} unit="%" note={`${model.manshaCount}件`} />
        <Kpi label="最高3連単" value={model.peakP3 ? model.peakP3.toLocaleString("ja-JP") : "—"} unit={model.peakP3 ? "円" : ""} note={model.peakOrder} />
        <Kpi
          label="万車からの間隔"
          value={model.gap == null ? "—" : model.gap === 0 ? "今" : String(model.gap)}
          unit={model.gap ? "R前" : ""}
          note={`直近10Rで ${model.recentMansha}`}
        />
      </section>

      <section className="grid gap-3 lg:grid-cols-3">
        {model.sites.map((site) => (
          <article key={site.site} className="panel p-4">
            <div className="flex items-baseline justify-between">
              <h3 className={cn("num text-5xl", site.site === "B" && "text-site-b", site.site === "Y" && "text-site-y", site.site === "N" && "text-site-n")}>
                {site.site}
              </h3>
              <p className="text-right">
                <span className="num text-4xl">{Math.round(site.index)}</span>
                <span className="ml-1 text-xs text-faint">指数</span>
              </p>
            </div>
            <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <Metric label="的中率" value={pct(site.hitRate)} note={`${site.hit}/${site.bet || 0}`} />
              <Metric label="万車率" value={pct(site.manRate)} note={`予想のうち ${site.man}`} />
              <Metric label="捕捉率" value={pct(site.capture)} note="全万車のうち" />
              <Metric label="的中時3連" value={site.hit ? yen(site.avgP3) : "—"} note={site.hit ? `2連 ${yen(site.avgP2)}` : "的中なし"} />
            </dl>
          </article>
        ))}
      </section>
      <p className="text-xs text-faint">
        指数は的中率35、予想内の万車率25、全万車の捕捉率25、配当力15。配当力は的中時平均3連単を、3サイト中の最大を100にした相対値です。
      </p>

      <section className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
        {model.agreement.map((row) => (
          <article key={row.bets} className="panel p-4">
            <p className="kicker">{row.bets === 0 ? "予想なし" : `${row.bets}サイト`}</p>
            <p className="num mt-3 text-5xl">
              {row.count ? Math.round(row.manshaRate) : "—"}
              {row.count ? <span className="text-2xl text-muted">%</span> : null}
            </p>
            <p className="mt-1 text-xs text-muted">{row.count}R の万車率</p>
            <p className="mt-3 text-sm">平均 {row.count ? yen(row.avgP3) : "—"}</p>
            <p className="text-sm text-muted">誰かが的中 {row.count ? pct(row.hitRate) : "—"}</p>
            <p className="text-sm text-muted">その時 {row.avgP3OnHit ? yen(row.avgP3OnHit) : "—"}</p>
          </article>
        ))}
      </section>

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="実力の形" hint="同じ100点満点。配当力だけ相対です。">
          {model.total === 0 ? (
            <Empty label="記録がありません" />
          ) : (
            <FitChart>
                <RadarChart data={model.radar} cx="50%" cy="46%" outerRadius="68%">
                  <PolarGrid stroke={GRID} />
                  <PolarAngleAxis dataKey="axis" tick={TICK} />
                  <PolarRadiusAxis domain={[0, 100]} tick={false} axisLine={false} />
                  <Radar name="B" dataKey="B" stroke="var(--color-site-b)" fill="var(--color-site-b)" fillOpacity={0.2} />
                  <Radar name="Y" dataKey="Y" stroke="var(--color-site-y)" fill="var(--color-site-y)" fillOpacity={0.16} />
                  <Radar name="N" dataKey="N" stroke="var(--color-site-n)" fill="var(--color-site-n)" fillOpacity={0.16} />
                  <Legend wrapperStyle={{ color: "var(--color-paper)" }} />
                  <Tooltip content={<Tip />} />
                </RadarChart>
            </FitChart>
          )}
        </Panel>

        <Panel title="万車の1着" hint="回数と、その車番が1着のときの平均3連単。">
          {model.winCars.length === 0 ? (
            <Empty label="万車の着順がまだありません" />
          ) : (
            <FitChart>
                <ComposedChart data={model.winCars} margin={{ top: 8, right: 4, left: 0, bottom: 0 }}>
                  <CartesianGrid stroke={GRID} vertical={false} />
                  <XAxis dataKey="car" tick={TICK} axisLine={false} tickLine={false} />
                  <YAxis yAxisId="n" width={AXIS.width} tick={TICK} axisLine={false} tickLine={false} allowDecimals={false} />
                  <YAxis yAxisId="yen" orientation="right" width={AXIS.width} tick={TICK} axisLine={false} tickLine={false} />
                  <Tooltip content={<Tip moneyKeys={["平均3連単"]} />} />
                  <Legend wrapperStyle={{ color: "var(--color-paper)" }} />
                  <Bar yAxisId="n" dataKey="count" name="回数" fill="var(--color-heat)" radius={[4, 4, 0, 0]} />
                  <Line yAxisId="yen" dataKey="avgP3" name="平均3連単" stroke="var(--color-site-y)" strokeWidth={2} dot={{ r: 3, fill: "var(--color-site-y)" }} />
                </ComposedChart>
            </FitChart>
          )}
        </Panel>
      </div>

      <div className="grid gap-4 lg:grid-cols-5">
        <Panel className="lg:col-span-3" title="1着-2着の出目" hint="明るいほど回数が多い。万車だけに絞れます。">
          <div className="mb-3 flex gap-2">
            <button type="button" className={cn("btn", heatMode === "all" ? "btn-ink" : "btn-ghost")} onClick={() => setHeatMode("all")}>
              全体
            </button>
            <button type="button" className={cn("btn", heatMode === "man" ? "btn-ink" : "btn-ghost")} onClick={() => setHeatMode("man")}>
              万車だけ
            </button>
          </div>
          {heat.max === 0 ? <Empty label="連対がまだありません" /> : <HeatGrid heat={heat} />}
        </Panel>
        <Panel className="lg:col-span-2" title="厚い出目と高い出目" hint="回数が多い連対と、平均配当が高い連対は別です。">
          <p className="text-xs text-faint">回数</p>
          <PairList rows={model.topPairs} />
          <p className="mt-4 text-xs text-faint">平均3連単（2回以上）</p>
          <PairList rows={model.richPairs} />
        </Panel>
      </div>

      <Panel title="車番の合計" hint="棒が出る回数、線がその合計の平均3連単。出現と配当のズレを見ます。">
        {model.sums.length === 0 ? (
          <Empty label="3連単の着順がまだありません" />
        ) : (
          <FitChart>
              <ComposedChart data={model.sums} margin={{ top: 8, right: 4, left: 0, bottom: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis dataKey="sum" tick={TICK} axisLine={false} tickLine={false} />
                <YAxis yAxisId="n" width={AXIS.width} tick={TICK} axisLine={false} tickLine={false} allowDecimals={false} />
                <YAxis yAxisId="yen" orientation="right" width={AXIS.width} tick={TICK} axisLine={false} tickLine={false} />
                <Tooltip content={<Tip moneyKeys={["平均3連単"]} />} />
                <Legend wrapperStyle={{ color: "var(--color-paper)" }} />
                <Bar yAxisId="n" dataKey="count" name="出現" fill="var(--color-muted)" radius={[4, 4, 0, 0]} />
                <Bar yAxisId="n" dataKey="mansha" name="万車" fill="var(--color-heat)" radius={[4, 4, 0, 0]} />
                <Line yAxisId="yen" dataKey="avgP3" name="平均3連単" stroke="var(--color-site-n)" strokeWidth={2} dot={false} />
              </ComposedChart>
          </FitChart>
        )}
      </Panel>

      <Panel title="配当の流れ" hint="古いレースが左です。点は万車。対数にすると大万車に潰れにくくなります。">
        <div className="mb-3 flex gap-2">
          <button type="button" className={cn("btn", !logScale ? "btn-ink" : "btn-ghost")} onClick={() => setLogScale(false)}>
            線形
          </button>
          <button type="button" className={cn("btn", logScale ? "btn-ink" : "btn-ghost")} onClick={() => setLogScale(true)}>
            対数
          </button>
        </div>
        {model.series.length === 0 ? (
          <Empty label="記録がありません" />
        ) : (
          <FitChart>
              <ComposedChart data={series} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis dataKey="i" tick={TICK} axisLine={false} tickLine={false} />
                <YAxis
                  width={AXIS.width}
                  tick={TICK}
                  axisLine={false}
                  tickLine={false}
                  scale={logScale ? "log" : "linear"}
                  domain={logScale ? [100, "auto"] : [0, "auto"]}
                  allowDataOverflow
                />
                <Tooltip
                  content={({ active, payload }) => {
                    const row = payload?.[0]?.payload as { order?: string; payout3?: number } | undefined;
                    if (!active || !row) return null;
                    return (
                      <div className="rounded-md border border-line bg-ink-2 px-3 py-2 text-sm">
                        <p className="font-semibold">{row.order}</p>
                        <p>{yen(row.payout3 ?? 0)}</p>
                      </div>
                    );
                  }}
                />
                <ReferenceLine y={10000} stroke="var(--color-heat)" strokeDasharray="4 4" />
                <Line dataKey="payout3" name="3連単" stroke="var(--color-paper)" strokeWidth={1.5} dot={false} connectNulls={false} />
                <Line dataKey="mark" name="万車" stroke="none" dot={{ r: 4, fill: "var(--color-heat)" }} legendType="circle" />
              </ComposedChart>
          </FitChart>
        )}
      </Panel>

      <Panel title="配当帯と、誰が当てたか" hint="全体の件数と、各サイトが的中にした件数。万車の帯に誰が残るかを見ます。">
        {model.bands.every((band) => band.all === 0) ? (
          <Empty label="3連単の払戻がまだありません" />
        ) : (
          <FitChart>
              <ComposedChart data={model.bands} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis dataKey="band" tick={TICK} axisLine={false} tickLine={false} />
                <YAxis width={AXIS.width} tick={TICK} axisLine={false} tickLine={false} allowDecimals={false} />
                <Tooltip content={<Tip />} />
                <Legend wrapperStyle={{ color: "var(--color-paper)" }} />
                <Bar dataKey="all" name="全体" fill="var(--color-faint)" radius={[3, 3, 0, 0]} />
                <Bar dataKey="B" name="B" fill="var(--color-site-b)" radius={[3, 3, 0, 0]} />
                <Bar dataKey="Y" name="Y" fill="var(--color-site-y)" radius={[3, 3, 0, 0]} />
                <Bar dataKey="N" name="N" fill="var(--color-site-n)" radius={[3, 3, 0, 0]} />
              </ComposedChart>
          </FitChart>
        )}
      </Panel>

      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="1着ラインのリフト" hint="万車の割合 ÷ 全体の割合。1より大きいとそのラインが万車に濃い。">
          {model.lines.length === 0 ? (
            <Empty label="ラインがまだありません" />
          ) : (
            <table className="w-full text-sm">
              <thead className="text-left text-xs text-faint">
                <tr>
                  <th className="py-2">L</th>
                  <th className="py-2">全体</th>
                  <th className="py-2">万車</th>
                  <th className="py-2">リフト</th>
                </tr>
              </thead>
              <tbody>
                {model.lines.map((row) => (
                  <tr key={row.line} className="border-t border-line">
                    <td className="py-2 font-semibold">{row.line}</td>
                    <td className="py-2">{pct(row.allPct)}</td>
                    <td className="py-2">{pct(row.manPct)}</td>
                    <td className={cn("py-2 font-semibold", row.lift != null && row.lift >= 1.15 && "text-heat")}>
                      {row.lift == null ? "—" : row.lift.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Panel>
        <Panel title="1着の位置" hint="内は1-3、中は4-6、外は7番以降。万車で外が厚くなるかを見ます。">
          <div className="space-y-4">
            {model.zones.map((zone) => (
              <ZoneBar key={zone.scope} label={zone.scope} 内={zone.内} 中={zone.中} 外={zone.外} />
            ))}
          </div>
          <div className="mt-6 min-w-0">
            {model.siteLines.every((row) => row.B + row.Y + row.N === 0) ? (
              <p className="text-sm text-muted">万車的中時のラインはまだありません。</p>
            ) : (
                <FitChart>
                <ComposedChart data={model.siteLines} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                  <CartesianGrid stroke={GRID} vertical={false} />
                  <XAxis dataKey="line" tick={TICK} axisLine={false} tickLine={false} />
                  <YAxis width={AXIS.width} tick={TICK} axisLine={false} tickLine={false} allowDecimals={false} />
                  <Tooltip content={<Tip />} />
                  <Legend wrapperStyle={{ color: "var(--color-paper)" }} />
                  <Bar dataKey="B" name="B" fill="var(--color-site-b)" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="Y" name="Y" fill="var(--color-site-y)" radius={[3, 3, 0, 0]} />
                  <Bar dataKey="N" name="N" fill="var(--color-site-n)" radius={[3, 3, 0, 0]} />
                </ComposedChart>
                </FitChart>
            )}
          </div>
        </Panel>
      </div>

      <Panel title="2連単から3着" hint="連対を選ぶと、3着のシェアと平均配当が出ます。">
        <select className="field mb-4 w-full max-w-xs" value={pair} aria-label="2連単" onChange={(event) => setPair(event.target.value)}>
          <option value="">連対を選ぶ</option>
          {model.pairs.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
        {!pair ? (
          <p className="text-sm text-muted">上の一覧から選ぶと、3着候補が分かれます。</p>
        ) : thirds.length === 0 ? (
          <Empty label="この連対の3着がありません" />
        ) : (
          <FitChart>
              <ComposedChart data={thirds} margin={{ top: 8, right: 4, left: 0, bottom: 0 }}>
                <CartesianGrid stroke={GRID} vertical={false} />
                <XAxis dataKey="car" tick={TICK} axisLine={false} tickLine={false} />
                <YAxis yAxisId="n" width={AXIS.width} tick={TICK} axisLine={false} tickLine={false} allowDecimals={false} />
                <YAxis yAxisId="yen" orientation="right" width={AXIS.width} tick={TICK} axisLine={false} tickLine={false} />
                <Tooltip content={<Tip moneyKeys={["平均3連単"]} />} />
                <Legend wrapperStyle={{ color: "var(--color-paper)" }} />
                <Bar yAxisId="n" dataKey="count" name="回数" fill="var(--color-site-b)" radius={[4, 4, 0, 0]}>
                  {thirds.map((row) => (
                    <Cell key={row.car} fill={row.car === thirds[0]?.car ? "var(--color-site-b)" : "var(--color-faint)"} />
                  ))}
                </Bar>
                <Line yAxisId="yen" dataKey="avgP3" name="平均3連単" stroke="var(--color-heat)" strokeWidth={2} dot={false} />
              </ComposedChart>
          </FitChart>
        )}
        {thirds.length > 0 ? (
          <p className="mt-3 text-sm text-muted">
            最有力は {thirds[0]?.car}番。シェア {pct(thirds[0]?.share ?? 0)}、平均 {yen(thirds[0]?.avgP3 ?? 0)}。
          </p>
        ) : null}
      </Panel>

      <div className="grid gap-4 lg:grid-cols-3">
        <Panel title="戦型">
          <CondTable rows={model.battles} />
        </Panel>
        <Panel title="決まり手">
          <CondTable rows={model.techs} />
        </Panel>
        <Panel title="車立">
          <CondTable rows={model.fields} />
        </Panel>
      </div>

      <Panel title="サイトの重なり" hint="誰が予想を置いたかで分けた母数です。的中時の平均は、誰か一人でも的中したレースだけ。">
        <div className="overflow-x-auto">
          <table className="w-full min-w-full text-sm">
            <thead className="text-left text-xs text-faint">
              <tr>
                <th className="py-2 pr-3">組合せ</th>
                <th className="py-2 pr-3">件数</th>
                <th className="py-2 pr-3">万車</th>
                <th className="py-2 pr-3">万車率</th>
                <th className="py-2 pr-3">平均3連</th>
                <th className="py-2">的中時</th>
              </tr>
            </thead>
            <tbody>
              {model.overlap.map((row) => (
                <tr key={row.key} className="border-t border-line">
                  <td className="py-2 pr-3 font-semibold">{row.key}</td>
                  <td className="py-2 pr-3">{row.count}</td>
                  <td className="py-2 pr-3">{row.mansha}</td>
                  <td className="py-2 pr-3">{pct(row.manshaRate)}</td>
                  <td className="py-2 pr-3">{yen(row.avgP3)}</td>
                  <td className="py-2">{row.avgP3OnHit ? yen(row.avgP3OnHit) : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <Panel title="高配当の着順" hint="3連単の高い順です。">
        {model.topPayouts.length === 0 ? (
          <p className="text-sm text-muted">払戻がまだありません。</p>
        ) : (
          <ul className="divide-y divide-line">
            {model.topPayouts.map((row) => (
              <li key={`${row.order}-${row.payout3}`} className="flex items-baseline justify-between gap-3 py-2">
                <span className="num text-3xl">{row.order}</span>
                <span className="text-sm text-muted">L {row.line}</span>
                <span className="text-sm font-semibold text-heat">{yen(row.payout3)}</span>
              </li>
            ))}
          </ul>
        )}
      </Panel>
    </div>
  );
}

function Kpi({ label, value, unit, note }: { label: string; value: string; unit?: string; note?: string }) {
  return (
    <article className="panel p-4">
      <p className="kicker">{label}</p>
      <p className="mt-3 flex items-end gap-1">
        <span className="num min-w-0 text-4xl sm:text-5xl">{value}</span>
        {unit ? <span className="mb-1 text-sm text-muted">{unit}</span> : null}
      </p>
      {note ? <p className="mt-2 truncate text-xs text-faint">{note}</p> : null}
    </article>
  );
}

function Metric({ label, value, note }: { label: string; value: string; note: string }) {
  return (
    <div>
      <dt className="text-xs text-faint">{label}</dt>
      <dd className="font-semibold">{value}</dd>
      <dd className="text-xs text-muted">{note}</dd>
    </div>
  );
}

function PairList({ rows }: { rows: { pair: string; count: number; share: number; avgP3: number }[] }) {
  if (!rows.length) return <p className="mt-2 text-sm text-muted">まだありません。</p>;
  return (
    <ul className="mt-2 space-y-2">
      {rows.map((row) => (
        <li key={row.pair} className="flex items-baseline justify-between gap-3 text-sm">
          <span className="num text-2xl">{row.pair}</span>
          <span className="text-muted">{row.count}回</span>
          <span>{yen(row.avgP3)}</span>
        </li>
      ))}
    </ul>
  );
}
