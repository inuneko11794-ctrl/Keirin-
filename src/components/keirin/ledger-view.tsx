import { useEffect, useMemo, useRef, useState } from "react";
import { RaceTable } from "@/components/keirin/race-table";
import { downloadText, parseImport, toCsv } from "@/lib/keirin/parse";
import { ingestShot, racesFromReading, rasterOf, type Raster, type ShotReading } from "@/lib/keirin/read-shot";
import { useKeirin } from "@/lib/keirin/store";
import type { Race } from "@/lib/keirin/types";

type Shot = {
  id: string;
  url: string;
  name: string;
  status: "reading" | "done" | "error";
  reading: ShotReading | null;
  error: string | null;
  paired: string | null;
};

export function LedgerView() {
  const races = useKeirin((s) => s.races);
  const staging = useKeirin((s) => s.staging);
  const sample = useKeirin((s) => s.sample);
  const update = useKeirin((s) => s.update);
  const toggleSite = useKeirin((s) => s.toggleSite);
  const remove = useKeirin((s) => s.remove);
  const stage = useKeirin((s) => s.stage);
  const commitStaging = useKeirin((s) => s.commitStaging);
  const clearStaging = useKeirin((s) => s.clearStaging);
  const replaceAll = useKeirin((s) => s.replaceAll);
  const addSaved = useKeirin((s) => s.addSaved);
  const clearAll = useKeirin((s) => s.clearAll);
  const loadSample = useKeirin((s) => s.loadSample);
  const say = useKeirin((s) => s.say);

  const [draft, setDraft] = useState("");
  const [query, setQuery] = useState("");
  const [shots, setShots] = useState<Shot[]>([]);
  const [pending, setPending] = useState<Race[] | null>(null);
  const [armedClear, setArmedClear] = useState(false);

  const shotsRef = useRef<Shot[]>([]);
  shotsRef.current = shots;
  const stageRef = useRef(stage);
  stageRef.current = stage;
  const sayRef = useRef(say);
  sayRef.current = say;

  const pairedKey = useRef("");

  useEffect(() => {
    const order = shots.find((shot) => shot.reading?.kind === "order");
    const pay = shots.find((shot) => shot.reading?.kind === "payout");
    if (!order?.reading || !pay?.reading || order.paired === pay.id) return;
    const key = `${order.id}:${pay.id}`;
    if (pairedKey.current === key) return;
    pairedKey.current = key;
    const races = racesFromReading(order.reading.order, pay.reading.payout);
    if (!races.length) return;
    stageRef.current(races);
    const mismatch =
      order.reading.order.length === pay.reading.payout.length
        ? ""
        : ` 行数が違うので、上から順に合わせ、余った ${Math.abs(order.reading.order.length - pay.reading.payout.length)} 行は片方だけです。`;
    sayRef.current(`${races.length}レースを下書きに入れました。${mismatch}`);
    setShots((curr) =>
      curr.map((shot) => {
        if (shot.id === order.id) return { ...shot, paired: pay.id };
        if (shot.id === pay.id) return { ...shot, paired: order.id };
        return shot;
      }),
    );
  }, [shots]);

  useEffect(() => {
    function onPaste(event: ClipboardEvent) {
      const items = event.clipboardData?.items;
      if (!items) return;
      const files: File[] = [];
      for (const item of items) {
        if (item.type.startsWith("image/")) {
          const file = item.getAsFile();
          if (file) files.push(file);
        }
      }
      if (!files.length) return;
      event.preventDefault();
      addShots(files);
    }
    window.addEventListener("paste", onPaste);
    return () => window.removeEventListener("paste", onPaste);
  }, []);

  useEffect(() => {
    return () => {
      for (const shot of shotsRef.current) URL.revokeObjectURL(shot.url);
    };
  }, []);

  const shown = useMemo(() => {
    const q = query.trim();
    if (!q) return races;
    return races.filter((race) =>
      [race.order, race.battle, race.tech1, race.tech2, race.winLine, String(race.raceNo ?? "")].some((value) =>
        value.includes(q),
      ),
    );
  }, [races, query]);

  async function addShots(files: File[]) {
    const images = files.filter((file) => file.type.startsWith("image/"));
    if (!images.length) return;
    const next: Shot[] = images.map((file) => ({
      id: crypto.randomUUID(),
      url: URL.createObjectURL(file),
      name: file.name || "画像",
      status: "reading",
      reading: null,
      error: null,
      paired: null,
    }));
    setShots((curr) => {
      const merged = [...next, ...curr].slice(0, 6);
      const keep = new Set(merged.map((shot) => shot.id));
      for (const shot of [...next, ...curr]) {
        if (!keep.has(shot.id)) URL.revokeObjectURL(shot.url);
      }
      return merged;
    });
    await new Promise((resolve) => window.setTimeout(resolve, 40));
    const read = await Promise.all(
      next.map(async (shot, index) => {
        const file = images[index];
        if (!file) return { id: shot.id, reading: null, error: "画像がありません" };
        try {
          const raster = await rasterOf(file);
          return { id: shot.id, reading: await readShot(raster), error: null };
        } catch {
          return { id: shot.id, reading: null, error: "画像を開けません" };
        }
      }),
    );
    setShots((curr) =>
      curr.map((shot) => {
        const found = read.find((item) => item.id === shot.id);
        if (!found) return shot;
        return {
          ...shot,
          status: found.error ? "error" : "done",
          reading: found.reading,
          error: found.error,
        };
      }),
    );
  }

  function ingest(text: string) {
    const parsed = parseImport(text);
    if (parsed.error || !parsed.races.length) {
      say(parsed.error ?? "読めませんでした");
      return;
    }
    stage(parsed.races);
    setDraft("");
    const skip = parsed.skipped ? ` ${parsed.skipped}行は飛ばしました。` : "";
    say(`${parsed.races.length}件を下書きに入れました。${skip}`);
  }

  function onRestoreFile(file: File | undefined) {
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      const parsed = parseImport(String(reader.result ?? ""));
      if (parsed.error || !parsed.races.length) {
        say(parsed.error ?? "ファイルを読めません");
        return;
      }
      setPending(parsed.races);
      say(`${parsed.races.length}件を読みました。置き換えるか、上に足すか選んでください。`);
    };
    reader.readAsText(file);
  }

  const day = new Date().toISOString().slice(0, 10);

  return (
    <div className="space-y-4">
      {sample ? (
        <section className="panel panel-alert p-4">
          <p className="text-sm">
            今見ているのは見本の {races.length} レースです。手を入れると、その内容がこのブラウザに残ります。見本のまま閉じると、次は空で開きます。
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              type="button"
              className="btn btn-heat"
              onClick={() => {
                clearAll();
                say("見本を空にしました。");
              }}
            >
              見本を空にする
            </button>
          </div>
        </section>
      ) : null}

      <section
        className="panel p-4 md:p-5"
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          addShots([...event.dataTransfer.files]);
        }}
      >
        <h2 className="text-lg font-semibold">ここに足す</h2>
        <p className="mt-1 text-sm text-muted">
          1行でも、着順表と払戻表のスクショでも、同じ場所から下書きに入ります。書いた内容と下書きは、このブラウザにその場で残ります。
        </p>
        <textarea
          className="field mt-3 min-h-28 w-full"
          value={draft}
          placeholder={"4-1-5  4200  26800  7車  4分戦  2  差  Y*\n1-2-3  430  1280  B* N*"}
          onChange={(event) => setDraft(event.target.value)}
        />
        <div className="mt-3 flex flex-wrap gap-2">
          <button type="button" className="btn btn-ink" onClick={() => ingest(draft)}>
            下書きに入れる
          </button>
          <button type="button" className="btn btn-ghost" onClick={() => setDraft("")}>
            クリア
          </button>
          <label className="btn btn-ghost text-center">
            画像を選ぶ
            <input
              className="sr-only"
              type="file"
              accept="image/*"
              multiple
              onChange={(event) => {
                addShots([...(event.target.files ?? [])]);
                event.target.value = "";
              }}
            />
          </label>
        </div>
        {shots.length > 0 ? (
          <ul className="mt-4 flex gap-3 overflow-x-auto">
            {shots.map((shot) => (
              <li key={shot.id} className="w-36 shrink-0 overflow-hidden rounded-lg border border-line">
                <img src={shot.url} alt={shot.name} className="h-24 w-full object-contain bg-ink" />
                <div className="space-y-2 p-2">
                  <p className="text-xs font-semibold">{shotSummary(shot)}</p>
                  <button
                    type="button"
                    className="btn btn-ghost w-full px-2"
                    onClick={() => {
                      URL.revokeObjectURL(shot.url);
                      setShots((curr) => curr.filter((item) => item.id !== shot.id));
                    }}
                  >
                    閉じる
                  </button>
                </div>
              </li>
            ))}
          </ul>
        ) : null}
      </section>

      {staging.length > 0 ? (
        <section className="panel overflow-hidden">
          <div className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
            <h2 className="font-semibold">下書き {staging.length}件</h2>
            <div className="flex flex-wrap gap-2">
              <button
                type="button"
                className="btn btn-ink"
                onClick={() => {
                  const count = staging.length;
                  commitStaging();
                  say(`${count}件を記録へ入れました。`);
                }}
              >
                記録へ反映
              </button>
              <button type="button" className="btn btn-ghost" onClick={clearStaging}>
                下書きを捨てる
              </button>
            </div>
          </div>
          <RaceTable
            rows={staging}
            onChange={(id, patch) => update("stg", id, patch)}
            onSite={(id, site, field) => toggleSite("stg", id, site, field)}
            onDelete={(id) => remove("stg", id)}
          />
        </section>
      ) : null}

      <section className="panel p-4">
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => downloadText(`byn3_backup_pro_${day}.json`, JSON.stringify(races, null, 2), "application/json")}
          >
            JSONを保存
          </button>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={() => downloadText(`byn3_${day}.csv`, toCsv(races), "text/csv")}
          >
            CSVを保存
          </button>
          <label className="btn btn-ghost text-center">
            JSON / CSVを読む
            <input
              className="sr-only"
              type="file"
              accept=".json,.csv,.txt,application/json,text/csv,text/plain"
              onChange={(event) => {
                onRestoreFile(event.target.files?.[0]);
                event.target.value = "";
              }}
            />
          </label>
          <button type="button" className="btn btn-ghost" onClick={loadSample}>
            見本を読み直す
          </button>
          {armedClear ? (
            <>
              <button
                type="button"
                className="btn btn-heat"
                onClick={() => {
                  clearAll();
                  setArmedClear(false);
                  say("記録を空にしました。");
                }}
              >
                本当に消す
              </button>
              <button type="button" className="btn btn-ghost" onClick={() => setArmedClear(false)}>
                やめる
              </button>
            </>
          ) : (
            <button type="button" className="btn btn-ghost" onClick={() => setArmedClear(true)}>
              全消去
            </button>
          )}
        </div>
        {pending ? (
          <div className="mt-4 rounded-lg border border-line p-3">
            <p className="text-sm">{pending.length}件の読み込みが待っています。今の記録は {races.length}件です。</p>
            <div className="mt-3 flex flex-wrap gap-2">
              <button
                type="button"
                className="btn btn-heat"
                onClick={() => {
                  replaceAll(pending);
                  setPending(null);
                  say("読み込んだ内容で置き換えました。");
                }}
              >
                置き換える
              </button>
              <button
                type="button"
                className="btn btn-ink"
                onClick={() => {
                  addSaved(pending);
                  setPending(null);
                  say("上に足しました。");
                }}
              >
                上に足す
              </button>
              <button type="button" className="btn btn-ghost" onClick={() => setPending(null)}>
                やめる
              </button>
            </div>
          </div>
        ) : null}
      </section>

      <section className="panel overflow-hidden">
        <div className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="font-semibold">記録 {shown.length}件</h2>
          <input
            className="field w-full sm:max-w-xs"
            value={query}
            placeholder="着順・戦型・決まり手"
            aria-label="記録を絞り込む"
            onChange={(event) => setQuery(event.target.value)}
          />
        </div>
        <RaceTable
          rows={shown}
          onChange={(id, patch) => update("sv", id, patch)}
          onSite={(id, site, field) => toggleSite("sv", id, site, field)}
          onDelete={(id) => remove("sv", id)}
        />
      </section>
    </div>
  );
}

function readShot(raster: Raster): Promise<ShotReading> {
  return new Promise((resolve) => {
    let worker: Worker;
    try {
      worker = new Worker(new URL("../../lib/keirin/read-shot.worker.ts", import.meta.url), { type: "module" });
    } catch {
      resolve(ingestShot(raster));
      return;
    }
    const pixels = raster.data.slice();
    const timer = window.setTimeout(() => {
      worker.terminate();
      resolve(ingestShot(raster));
    }, 20000);
    worker.onmessage = (event: MessageEvent<{ reading: ShotReading }>) => {
      window.clearTimeout(timer);
      worker.terminate();
      resolve(event.data.reading);
    };
    worker.onerror = () => {
      window.clearTimeout(timer);
      worker.terminate();
      resolve(ingestShot(raster));
    };
    worker.postMessage({ id: "shot", width: raster.width, height: raster.height, buffer: pixels.buffer }, [
      pixels.buffer,
    ]);
  });
}

function shotSummary(shot: Shot) {
  if (shot.status === "reading") return "読んでいます";
  if (shot.error) return shot.error;
  if (!shot.reading || shot.reading.kind === "unknown") return "着順表でも払戻表でもありません";
  if (shot.reading.kind === "order") return `着順 ${shot.reading.order.length}行`;
  return `払戻 ${shot.reading.payout.length}行`;
}
