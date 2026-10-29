import { useEffect, useMemo } from "react";
import { AppWindow, Crosshair, LayoutDashboard, NotebookPen } from "lucide-react";
import { BoardView } from "@/components/keirin/board-view";
import { DeskView } from "@/components/keirin/desk-view";
import { LedgerView } from "@/components/keirin/ledger-view";
import { StudyView } from "@/components/keirin/study-view";
import { buildDash, filterRaces } from "@/lib/keirin/analytics";
import { useKeirin, type ViewId } from "@/lib/keirin/store";
import { FIELDS } from "@/lib/keirin/types";
import { Bgm } from "@/components/keirin/bgm";
import { cn } from "@/lib/cn";

const SLICES = [
  { id: "all", label: "全体" },
  ...FIELDS.map((field) => ({ id: field, label: field })),
  { id: "単騎戦", label: "単騎戦" },
];

const NAV: { id: ViewId; label: string; icon: typeof LayoutDashboard }[] = [
  { id: "board", label: "分析", icon: LayoutDashboard },
  { id: "book", label: "記録", icon: NotebookPen },
  { id: "study", label: "万車", icon: Crosshair },
  { id: "desk", label: "ノート", icon: AppWindow },
];

export function Dashboard() {
  const hydrate = useKeirin((s) => s.hydrate);
  const view = useKeirin((s) => s.view);
  const setView = useKeirin((s) => s.setView);
  const races = useKeirin((s) => s.races);
  const filter = useKeirin((s) => s.filter);
  const setFilter = useKeirin((s) => s.setFilter);
  const sample = useKeirin((s) => s.sample);
  const flash = useKeirin((s) => s.flash);

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  const filtered = useMemo(() => filterRaces(races, filter), [races, filter]);
  const heavy = view === "board" || view === "study";
  const model = useMemo(() => (heavy ? buildDash(filtered) : null), [heavy, filtered]);

  return (
    <div className="min-h-screen lg:flex">
      <aside className="sticky top-0 hidden h-screen w-52 shrink-0 flex-col border-r border-line bg-ink px-4 py-6 lg:flex">
        <Wordmark />
        <nav className="mt-8 flex flex-col gap-1" aria-label="画面">
          {NAV.map((item) => (
            <NavButton key={item.id} item={item} current={view} onSelect={setView} />
          ))}
        </nav>
        <p className="mt-auto text-xs leading-relaxed text-faint">このブラウザに自動で残ります。機種を変えるときだけJSONを保存してください。</p>
        <div className="mt-4">
          <Bgm />
        </div>
      </aside>

      <div className="min-w-0 flex-1 overflow-x-hidden">
        <header className="sticky top-0 z-20 border-b border-line bg-ink lg:static">
          <div className="flex items-center justify-between gap-3 px-4 py-3 lg:hidden">
            <Wordmark />
            <div className="flex shrink-0 items-center gap-2">
              <Bgm />
              <p className="text-xs text-faint">{races.length}R</p>
            </div>
          </div>
          <nav className="grid grid-cols-4 gap-1 px-3 pb-3 lg:hidden" aria-label="画面">
            {NAV.map((item) => (
              <NavButton key={item.id} item={item} current={view} onSelect={setView} compact />
            ))}
          </nav>
        </header>

        <div className="mx-auto max-w-7xl px-4 py-5">
          <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="kicker">{view === "board" ? "三つの読み" : view === "study" ? "万車の解剖" : view === "book" ? "台帳" : "外部"}</p>
              <h1 className="mt-1 text-2xl font-semibold tracking-tight">
                {view === "board" ? "寄った数で、何が変わるか" : view === "study" ? "万車の1着は誰の癖か" : view === "book" ? "レースを残す" : "ノートを開く"}
              </h1>
            </div>
          </div>
          {view === "board" || view === "study" ? (
            <div className="mb-5">
              <div className="flex flex-wrap gap-2" role="group" aria-label="グラフの母数">
                {SLICES.map((slice) => (
                  <button
                    key={slice.id}
                    type="button"
                    className={cn("btn min-h-11 px-3", filter === slice.id ? "btn-ink" : "btn-ghost")}
                    aria-pressed={filter === slice.id}
                    onClick={() => setFilter(slice.id)}
                  >
                    {slice.label}
                  </button>
                ))}
              </div>
              <p className="mt-2 text-xs text-muted">この下のグラフは、選んだ {filtered.length}R だけです。</p>
            </div>
          ) : null}

          {view === "board" && model ? <BoardView model={model} sample={sample} /> : null}
          {view === "book" ? <LedgerView /> : null}
          {view === "study" && model ? <StudyView model={model} /> : null}
          {view === "desk" ? <DeskView /> : null}
        </div>
      </div>

      {flash ? (
        <div
          role="status"
          className="fixed inset-x-4 bottom-4 z-40 mx-auto max-w-lg rounded-lg border border-line bg-panel px-4 py-3 text-sm shadow-lg"
        >
          {flash}
        </div>
      ) : null}
    </div>
  );
}

function Wordmark() {
  return (
    <div className="min-w-0">
      <div className="flex items-center gap-2" aria-hidden="true">
        <span className="h-4 w-1.5 bg-site-b" />
        <span className="h-4 w-1.5 bg-site-y" />
        <span className="h-4 w-1.5 bg-site-n" />
      </div>
      <p className="mt-3 text-sm font-semibold leading-snug sm:text-base">BYN3サイト寄れば文殊超え</p>
      <p className="kicker mt-1">B · Y · N</p>
    </div>
  );
}

function NavButton({
  item,
  current,
  onSelect,
  compact,
}: {
  item: (typeof NAV)[number];
  current: ViewId;
  onSelect: (view: ViewId) => void;
  compact?: boolean;
}) {
  const Icon = item.icon;
  const on = current === item.id;
  return (
    <button
      type="button"
      aria-current={on ? "page" : undefined}
      className={cn(
        "flex items-center gap-2 rounded-md text-sm font-semibold",
        compact ? "min-h-11 w-full justify-center px-1 text-xs" : "min-h-11 px-3",
        on ? "bg-paper text-ink" : "text-muted hover:bg-panel-2 hover:text-paper",
      )}
      onClick={() => onSelect(item.id)}
    >
      <Icon className="size-4" aria-hidden="true" />
      {item.label}
    </button>
  );
}
