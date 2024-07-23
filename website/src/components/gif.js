import { decompressFrames, parseGIF } from 'gifuct-js';
import { Color } from 'three';

const sRGBToLinear = (color) => {
  return color.clone().convertSRGBToLinear();
};

const normalizeColorIntensity = (color) => {
  let maxComponent = Math.max(color.r, color.g, color.b);

  if (maxComponent > 1) {
    color.multiplyScalar(1 / maxComponent);
  }

  return color;
};

const adjustEmissiveIntensity = (
  color,
  intensity,
  factor = 0.5,
  threshold = 0.8
) => {
  // Calculate perceived brightness
  const brightness = 0.299 * color.r + 0.587 * color.g + 0.114 * color.b;

  if (brightness > threshold) {
    const scaleFactor = 1 - brightness * brightness * factor;
    intensity *= scaleFactor;
  }

  return intensity;
};

const convertFrame = (frame, w, h) => {
  const colorTable = frame.colorTable.map((color) => {
    const c = [];
    for (let i = 0; i < color.length; i++) {
      c.push(color[i] / 255);
    }
    return c;
  });

  const frames = frame.pixels.map((pixel, i) => {
    const xOffset = Math.floor((w - frame.dims.width) / 2);
    const yOffset = Math.floor((h - frame.dims.height) / 2);

    const x = (i % frame.dims.width) + xOffset;
    const y =
      frame.dims.height - Math.floor(i / frame.dims.width) - 1 + yOffset;

    let color = new Color(...colorTable[pixel]);
    color = sRGBToLinear(color);

    // Normalize the color intensity
    // I think this doesn't do anything ATM, as colors are coming from GIF
    color = normalizeColorIntensity(color);

    const intensity = adjustEmissiveIntensity(color, 1);

    // Optionally, apply bloom threshold
    return {
      x,
      y,
      color,
      intensity,
    };
  });

  return frames;
};

export const getGif = async (gifURL, screenW = 64, screenH = 64) => {
  const response = await fetch(gifURL);
  const buffer = await response.arrayBuffer();
  const gif = parseGIF(buffer);
  const frames = decompressFrames(gif, true);

  const convertedGif = frames.map((frame) =>
    convertFrame(frame, screenW, screenH)
  );

  return convertedGif;
};
