import { ingestShot, type ShotReading } from "./read-shot";

type Job = { id: string; width: number; height: number; buffer: ArrayBuffer };

self.onmessage = (event: MessageEvent<Job>) => {
  const { id, width, height, buffer } = event.data;
  const reading: ShotReading = ingestShot({
    width,
    height,
    data: new Uint8ClampedArray(buffer),
  });
  self.postMessage({ id, reading });
};
