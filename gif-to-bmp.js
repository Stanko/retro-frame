const fs = require('fs');
const extractFrames = require('gif-extract-frames');
const mergeImg = require('merge-img');
const sharp = require('sharp');
const { exec } = require('child_process');
// const getPixels = require('get-pixels');

async function main(gifPath, resize, color, fit) {
  const results = await extractFrames({
    input: gifPath,
    output: './output/frame-%d.png',
  });

  const pngPath =
    './output/' + gifPath.split('/').pop().replace('.gif', '.png');
  const bmpPath = pngPath.replace('.png', '.bmp');

  const numberOfFrames = results.shape[0];
  const width = results.shape[1];
  const height = results.shape[2];

  const size = resize || 64;

  const images = [];
  for (let i = 0; i < numberOfFrames; i++) {
    const imagePath = `./output/frame-64-${i}.png`;
    images.push(imagePath);

    await sharp(`./output/frame-${i}.png`)
      .resize({
        width: width > 64 || resize ? size : width,
        height: height > 64 || resize ? size : height,
        kernel: sharp.kernel.nearest,
        fit,
        background: color,
      })
      .removeAlpha()
      .toFile(imagePath);
  }

  // Merge images into vertical strip
  mergeImg(images, { direction: true }).then((img) => {
    img.write(pngPath, async () => {
      for (let i = 0; i < numberOfFrames; i++) {
        fs.unlinkSync(`./output/frame-${i}.png`);
        fs.unlinkSync(`./output/frame-64-${i}.png`);
      }

      // getPixels(pngPath, async (err, ndarray) => {
      //   if (err) {
      //     console.log('Bad image path!');
      //     return;
      //   }

      //   const uintArr = new Uint8Array(ndarray.data);
      //   const regularArr = [];
      //   const colors = [];

      //   for (let i = 0, l = uintArr.length / 4; i < l; i++) {
      //     regularArr.push([
      //       uintArr[4 * i],
      //       uintArr[4 * i + 1],
      //       uintArr[4 * i + 2],
      //       // uintArr[4 * i + 3],
      //     ]);
      //   }

      //   for (let i = 0, l = regularArr.length; i < l; i++) {
      //     let currentValString = JSON.stringify(regularArr[i]);

      //     if (!colors.includes(currentValString)) {
      //       colors.push(currentValString);
      //     }
      //   }

      //   let colorsCount = 64;

      //   if (colors.length <= 4) {
      //     colorsCount = 4;
      //   } else if (colors.length <= 8) {
      //     colorsCount = 8;
      //   } else if (colors.length <= 16) {
      //     colorsCount = 16;
      //   } else if (colors.length <= 32) {
      //     colorsCount = 32;
      //   }

      //   console.log(colors);
      //   console.log(colors.length, colorsCount);
      // });

      // `-colors ${colorsCount}`;

      const command = `convert ${pngPath} -compress none -type palette -alpha off ${bmpPath}`;

      // Run imagemagick to convert png to bmp
      const convertProcess = await exec(command);

      convertProcess.stdout.on('data', function (data) {
        console.log(data);
      });
    });
  });
}

const args = process.argv.slice(2);

if (args[0] && args[0].length > 2) {
  let resize = 0;
  if (args[1] && parseInt(args[1], 10)) {
    resize = parseInt(args[1], 10);
  }
  const color = args[2] || '#000';
  const fit = (args[3] && sharp.fit[args[3]]) || sharp.fit.contain;

  main(args[0], resize, color, fit);
} else {
  console.warn('Please provide path to a gif file');
}
