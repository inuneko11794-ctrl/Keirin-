const LINKS = [
  {
    title: "B.Y.N ANALYZER",
    body: "GitHubに置いた分析ページ。このアプリの記録とは別です。",
    href: "https://inuneko11794-ctrl.github.io/-B-notameni.../",
  },
  {
    title: "万車ノート",
    body: "レース前の読みをここに残す。",
    href: "https://brook-beam-sunny-arch.grok.me",
  },
];

export function DeskView() {
  return (
    <div className="space-y-4">
      <section className="panel p-4 md:p-5">
        <p className="kicker">控室</p>
        <h2 className="mt-2 text-xl font-semibold">読む場所と、残す場所を分けない</h2>
        <p className="mt-2 text-sm text-muted">埋め込みが空白なら、相手側が画面内表示を拒んでいます。そのときは別のタブで開いてください。</p>
      </section>
      {LINKS.map((link) => (
        <section key={link.href} className="panel overflow-hidden">
          <div className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 className="font-semibold">{link.title}</h3>
              <p className="text-sm text-muted">{link.body}</p>
            </div>
            <a className="btn btn-ghost text-center" href={link.href} target="_blank" rel="noreferrer">
              別のタブで開く
            </a>
          </div>
          <iframe title={link.title} src={link.href} className="h-[70vh] min-h-96 w-full border-t border-line bg-ink" />
        </section>
      ))}
    </div>
  );
}
