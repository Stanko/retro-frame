const fs = require('fs');
const extractFrames = require('gif-extract-frames');
const mergeImg = require('merge-img');
const sharp = require('sharp');
const { exec } = require('child_process');

async function main(gifPath, color, fit) {
  const results = await extractFrames({
    input: gifPath,
    output: './output/frame-%d.png',
  });

  const pngPath = 'output/' + gifPath.split('/').pop().replace('.gif', '.png');
  const bmpPath = pngPath.replace('.png', '.bmp');

  const numberOfFrames = results.shape[0];
  // const width = results.shape[1];
  // const height = results.shape[2];

  const images = [];
  for (let i = 0; i < numberOfFrames; i++) {
    const imagePath = `./output/frame-64-${i}.png`;
    images.push(imagePath);

    await sharp(`./output/frame-${i}.png`)
      .resize({
        width: 64,
        height: 64,
        kernel: sharp.kernel.nearest,
        fit,
        background: color,
      })
      .removeAlpha()
      .toFile(imagePath);
  }

  // Merge images into vertical strip
  mergeImg(images, { direction: true }).then(async (img) => {
    img.write(pngPath, () => {
      for (let i = 0; i < numberOfFrames; i++) {
        fs.unlinkSync(`./output/frame-${i}.png`);
        fs.unlinkSync(`./output/frame-64-${i}.png`);
      }
    });

    // Run imagemagick to convert png to 8 bit bmp
    await exec(`convert ${pngPath} -alpha off -type palette BMP3:${bmpPath}`);
  });
}

const args = process.argv.slice(2);

if (args[0] && args[0].length > 2) {
  const color = args[1] || '#000';
  const fit = (args[2] && sharp.fit[args[2]]) || sharp.fit.contain;

  main(args[0], color, fit);
} else {
  console.warn('Please provide path to a gif file');
}
