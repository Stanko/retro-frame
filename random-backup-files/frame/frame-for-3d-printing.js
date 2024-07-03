const { cos, sin, PI, SQRT2 } = Math;

const fit = 0.1;
const nothing = 0.00001;

const defaultParams = {
  drawAll: true,
  websiteVersion: false,
};

/** @typedef { typeof import("replicad") } replicadLib */
/** @type {function(replicadLib, typeof defaultParams): any} */
const main = ({ draw, makeBaseBox, makeCylinder }, { drawAll, websiteVersion }) => {
  const size = 250;
  const hole = 190;
  const wall = 6;
  const depth = 45;
  const frontWidth = (size - hole) * 0.5;

  const diagonal = 25;
  const connectionSize = 8;
  const position = (size - frontWidth) / -2;

  const getSide = () => {
    const b1 = draw([0, 0])
      .lineTo([frontWidth, frontWidth])
      .lineTo([frontWidth, hole + frontWidth])
      .lineTo([0, size])
      .close()
      .sketchOnPlane('XY')
      .extrude(wall);

    const b2 = draw([0, 0])
      .lineTo([diagonal, diagonal])
      .lineTo([wall, diagonal])
      .lineTo([wall, size - diagonal])
      .lineTo([diagonal, size - diagonal])
      .lineTo([0, size])
      .close()
      .sketchOnPlane('XY')
      .extrude(depth);

    const b3 = draw([0, 0])
      .lineTo([wall, wall])
      .lineTo([wall, size - wall])
      .lineTo([0, size])
      .close()
      .sketchOnPlane('XY')
      .extrude(depth);

    if (websiteVersion) {
      return b1
        .fuse(b3)
        .translateX(frontWidth / -2)
        .translateY(size / -2);
    }

    let side = b1
      .fuse(b2)
      .translateX(frontWidth / -2)
      .translateY(size / -2);

    return side;
  };

  const getConnectionDrawng = () => {
    const control = connectionSize * 0.1;
    return draw([0, connectionSize])
      .lineTo([connectionSize, 0])
      .cubicBezierCurveTo([0, -connectionSize], [control, 0], [0, -control])
      .lineTo([-connectionSize, 0])
      .cubicBezierCurveTo([0, connectionSize], [-control, 0], [0, control])
      .close();
  };

  const getConnection = (xDirection, yDirection) => {
    const connection = getConnectionDrawng(xDirection, yDirection);
    return connection.sketchOnPlane('XY').extrude(depth / 2 - fit);
  };

  const getConnectionHole = (xDirection, yDirection) => {
    let connection = getConnectionDrawng(xDirection, yDirection)
      .offset(fit)
      .sketchOnPlane('XY')
      .extrude(depth)
      .translateZ(depth / 2);

    const xMove = ((size - diagonal) / 2) * xDirection;
    const yMove = ((size - diagonal) / 2) * yDirection;

    if (xDirection === yDirection) {
      // Mirror it
      connection = connection.mirror();
    }

    return connection.translateX(xMove).translateY(yMove);
  };

  const side1 = getSide().translateX(position);
  const side2 = getSide().rotate(180).translateX(-position);
  const side3 = getSide().rotate(90).translateY(position);
  const side4 = getSide().rotate(-90).translateY(-position);

  const connectionHole1 = getConnectionHole(1, 1);
  const connectionHole2 = getConnectionHole(1, -1);
  const connectionHole3 = getConnectionHole(-1, -1);
  const connectionHole4 = getConnectionHole(-1, 1);

  const connection = getConnection();

  if (websiteVersion) {
    return [{
      color: '#36e',
      shape: getSide(),
    }];
  }

  if (!drawAll) {
    return [
      {
        color: '#36e',
        shape: connection,
      },
      {
        color: '#36e',
        shape: side1
          .cut(connectionHole3)
          .cut(connectionHole4)
          .translateX(position / -2),
      },
    ];
  }

  return [
    {
      color: '#36e',
      shape: connection,
    },
    {
      color: '#36e',
      shape: side1.cut(connectionHole3).cut(connectionHole4),
    },
    {
      color: '#36e',
      shape: side2.cut(connectionHole1).cut(connectionHole2),
    },
    {
      color: '#14c',
      shape: side3.cut(connectionHole2).cut(connectionHole3),
    },
    {
      color: '#14c',
      shape: side4.cut(connectionHole1).cut(connectionHole4),
    },
  ];
};
