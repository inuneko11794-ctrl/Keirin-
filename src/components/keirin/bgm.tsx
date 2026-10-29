import { useEffect, useRef, useState } from "react";

const BUILTIN = "/dopagaki.m4a";

export function Bgm() {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const urlRef = useRef<string | null>(null);
  const [on, setOn] = useState(false);

  useEffect(() => {
    return () => {
      audioRef.current?.pause();
      if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    };
  }, []);

  function audio() {
    const node = audioRef.current ?? new Audio();
    audioRef.current = node;
    node.loop = true;
    node.volume = 0.8;
    if (!node.src) node.src = BUILTIN;
    return node;
  }

  function choose(file: File | undefined) {
    if (!file) return;
    if (urlRef.current) URL.revokeObjectURL(urlRef.current);
    const url = URL.createObjectURL(file);
    urlRef.current = url;
    const node = audio();
    node.src = url;
    void node.play();
    setOn(true);
  }

  function toggle() {
    const node = audio();
    if (on) {
      node.pause();
      setOn(false);
      return;
    }
    void node.play();
    setOn(true);
  }

  return (
    <div className="flex items-center gap-1">
      <button type="button" className="btn btn-ghost shrink-0 px-3" aria-pressed={on} title="100倍ドパガキの狂気" onClick={toggle}>
        {on ? "停止" : "再生"}
      </button>
      <label className="btn btn-ghost shrink-0 cursor-pointer px-3">
        曲
        <input
          className="sr-only"
          type="file"
          accept="audio/*"
          onChange={(event) => {
            choose(event.target.files?.[0]);
            event.target.value = "";
          }}
        />
      </label>
    </div>
  );
}
