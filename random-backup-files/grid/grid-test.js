const fit = 0.2;
const nothing = 0.00001;

const defaultParams = {
  cornerOnly: true,
};

/** @typedef { typeof import("replicad") } replicadLib */
/** @type {function(replicadLib, typeof defaultParams): any} */
const main = ({ makeBaseBox }, { cornerOnly }) => {
  const height = 2;
  const ledSize = 2.5;
  const wall = 0.45;
  const outerWall = 3;
  const outerWallHeight = 6;

  const gapMagicNumber = wall * 0.98;

  const getGrid = (w, h) => {
    const matrixW = ledSize * w + fit * 2;
    const matrixH = ledSize * h + fit * 2;
    const hole = makeBaseBox(matrixW, matrixH, outerWallHeight + 10).translateZ(
      -5
    );
    const gridW = matrixW + outerWall * 2;
    const gridH = matrixH + outerWall * 2;
    let grid = makeBaseBox(gridW, gridH, outerWallHeight).cut(hole);

    let cols;
    let rows;

    for (let x = 0; x < w; x++) {
      const isFirstRow = x === 0;
      const isLastRow = x === w - 1;

      const d1 =
        (isFirstRow || isLastRow
          ? ledSize - wall * 0.5 + fit * 2
          : ledSize - wall) + gapMagicNumber;

      let d1offset = 0;

      if (isFirstRow) {
        d1offset = wall * -0.25 - fit;
      } else if (isLastRow) {
        d1offset = wall * 0.25 + fit;
      }

      for (let y = 0; y < h; y++) {
        const isFirstCol = y === 0;
        const isLastCol = y === h - 1;

        const wall1 = makeBaseBox(d1, wall, height)
          .translateX(ledSize * x + d1offset)
          .translateY(ledSize * y);

        const d2 =
          (isFirstCol || isLastCol
            ? ledSize - wall * 0.5 + fit * 2
            : ledSize - wall) +
          wall * 0.7;

        let d2offset = 0;

        if (isFirstCol) {
          d2offset = wall * -0.25 - fit;
        } else if (isLastCol) {
          d2offset = wall * 0.25 + fit;
        }

        const wall2 = makeBaseBox(wall, d2, height)
          .translateY(ledSize * y + d2offset)
          .translateX(ledSize * x);

        if (cols) {
          if (!isLastRow) {
            cols = cols.fuse(wall2);
          }
        } else {
          cols = wall2;
        }

        if (rows) {
          if (!isLastCol) {
            rows = rows.fuse(wall1);
          }
        } else {
          rows = wall1;
        }
      }
    }

    const walls = rows
      .translateX(ledSize / 2)
      .translateY(ledSize)
      .fuse(cols.translateX(ledSize).translateY(ledSize / 2));

    return grid
      .translateX(matrixW / 2 - fit)
      .translateY(matrixH / 2 - fit)
      .fuse(walls);
  };

  let grid = getGrid(6, 6);

  if (cornerOnly) {
    grid = grid
      .cut(
        makeBaseBox(outerWall * 2, 500, outerWallHeight * 2).translate(
          -outerWall,
          250 - outerWall * 2,
          -1
        )
      )
      .cut(
        makeBaseBox(500, outerWall * 2, outerWallHeight * 2).translate(
          250 - outerWall * 2,
          -outerWall,
          -1
        )
      );
  }

  return [
    {
      color: '#36e',
      shape: grid,
      name: `grid-${gapMagicNumber}`,
    },
  ];
};
