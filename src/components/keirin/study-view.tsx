import { Cell, Pie, PieChart, Tooltip } from "recharts";
import { pct } from "@/lib/keirin/analytics";
import { SITES, type DashModel, type SiteKey } from "@/lib/keirin/types";
import { cn } from "@/lib/cn";

const SITE_COLOR: Record<SiteKey, string> = {
  B: "var(--color-site-b)",
  Y: "var(--color-site-y)",
  N: "var(--color-site-n)",
};

export function StudyView({ model }: { model: DashModel }) {
  return (
    <div className="space-y-4">
      <section className="panel p-4 md:p-5">
        <p className="kicker">万車の1着</p>
        <h2 className="mt-2 text-xl font-semibold">当てたとき、どの車番が先頭だったか</h2>
        <p className="mt-2 text-sm text-muted">
          万車は {model.manshaCount} 件。各サイトの円は、そのサイトが的中にした万車だけです。横棒は全体の1着割合との差で、プラスならその車番を多く引いています。
        </p>
      </section>
      <div className="grid gap-4 lg:grid-cols-3">
        {SITES.map((site) => (
          <SiteCut key={site} site={site} rows={model.manshaBySite[site]} hits={model.manshaHits[site]} />
        ))}
      </div>
    </div>
  );
}

function SiteCut({
  site,
  rows,
  hits,
}: {
  site: SiteKey;
  rows: DashModel["manshaBySite"][SiteKey];
  hits: number;
}) {
  const lead = rows[0];
  const edge = [...rows].sort((a, b) => b.pct - b.fieldPct - (a.pct - a.fieldPct))[0];
  return (
    <article className="panel p-4">
      <div className="flex items-end justify-between">
        <h3 className={cn("num text-5xl", site === "B" && "text-site-b", site === "Y" && "text-site-y", site === "N" && "text-site-n")}>
          {site}
        </h3>
        <p className="text-sm text-muted">万車的中 {hits}</p>
      </div>
      {rows.length === 0 ? (
        <p className="py-16 text-center text-sm text-muted">的中した万車がありません。</p>
      ) : (
        <>
          <div className="mx-auto flex h-52 w-full max-w-xs items-center justify-center">
            <PieChart width={240} height={200}>
                <Pie data={rows} dataKey="count" nameKey="car" innerRadius={48} outerRadius={72} paddingAngle={2} stroke="none" cx={120} cy={96}>
                  {rows.map((row, index) => (
                    <Cell key={row.car} fill={SITE_COLOR[site]} fillOpacity={Math.max(0.28, 1 - index * 0.16)} />
                  ))}
                </Pie>
                <Tooltip
                  content={({ active, payload }) => {
                    const row = payload?.[0]?.payload as (typeof rows)[number] | undefined;
                    if (!active || !row) return null;
                    return (
                      <div className="rounded-md border border-line bg-ink-2 px-3 py-2 text-sm">
                        <p className="font-semibold">{row.car}番</p>
                        <p>
                          {row.count}回 / {pct(row.pct)}
                        </p>
                      </div>
                    );
                  }}
                />
            </PieChart>
          </div>
          <ul className="space-y-3">
            {rows.map((row) => {
              const delta = row.pct - row.fieldPct;
              return (
                <li key={row.car}>
                  <div className="flex items-baseline justify-between text-sm">
                    <span className="font-semibold">{row.car}番</span>
                    <span>
                      {pct(row.pct)}
                      <span className={cn("ml-2", delta >= 8 ? "text-heat" : "text-muted")}>
                        {delta >= 0 ? "+" : ""}
                        {Math.round(delta)}pt
                      </span>
                    </span>
                  </div>
                  <div className="mt-1 h-2 overflow-hidden rounded-full bg-ink">
                    <div className="h-full rounded-full" style={{ width: `${row.pct}%`, background: SITE_COLOR[site] }} />
                  </div>
                </li>
              );
            })}
          </ul>
          {lead ? (
            <p className="mt-4 text-sm text-muted">
              最多は {lead.car}番（{lead.count}回）。
              {edge && edge.pct - edge.fieldPct >= 8
                ? ` 全体より濃いのは ${edge.car}番（${Math.round(edge.pct - edge.fieldPct)}ポイント）。`
                : " 全体と比べた偏りはまだ小さいです。"}
            </p>
          ) : null}
        </>
      )}
    </article>
  );
}
