// "dependencies": {
//   "bmp-js": "^0.1.0",
// }

const fs = require('fs');
const bmp = require('bmp-js');

let content = '';

for (let x = 0; x <= 9; x++) {
  const bmpBuffer = fs.readFileSync(`digit-${x}.bmp`);
  const bmpData = bmp.decode(bmpBuffer);

  const data = [...bmpData.data];

  const digit = [];
  const rowLength = 12;

  for (let i = 0; i < data.length; i += 4) {
    const index = i / 4;
    const row = Math.floor(index / rowLength);

    if (!digit[row]) {
      digit[row] = '';
    }

    const sum = data[i] + data[i + 1] + data[i + 2] + data[i + 3];

    const char = sum > 0 ? 'x' : '_';
    digit[row] += char;
  }

  const code = `digit${x} = [\n${digit
    .map((s) => `    "${s}",`)
    .join('\n')}\n]\n\n`;

  content += code;

  // fs.writeFileSync(`digit${x}.py`, code, { encoding: 'utf-8' });
}

fs.writeFileSync('digits.py', content, { encoding: 'utf-8' });
