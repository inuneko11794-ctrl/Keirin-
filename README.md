# BYN3サイト寄れば文殊超え

B・Y・N、三つの競輪予想を一つの盤で比べる記録帳。ブラウザの localStorage に保存する。サーバーには送らない。

## 起動

```bash
npm install
npm run dev
```

http://localhost:8080

## 使い方

- 記録タブに `7-3-1 2分戦 7車 単 逃-差 *B` のように1行で入れる。
- 結果画面のスクショは、着順表と払戻表を2枚落とすと下書きになる。予・的の印は手で付ける。
- JSON / CSV で書き出し、GitHub以外のバックアップにも使える。

## 中身

アプリ本体は `src/components/keirin` と `src/lib/keirin`。盤面の集計は `src/lib/keirin/analytics.ts`、スクショ読み取りは `src/lib/keirin/read-shot.ts` と `src/lib/keirin/glyphs.ts`。
