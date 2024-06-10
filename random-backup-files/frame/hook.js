// Copy code here:
// https://studio.replicad.xyz/workbench
// and you'll be able to alter and download the model

const nothing = 0.00001;

/** @typedef { typeof import("replicad") } replicadLib */
/** @type {function(replicadLib, typeof defaultParams): any} */
const main = ({ draw, makeBaseBox, makeCylinder }, {}) => {
  const thickness = 3.5;
  const d = {
    base: {
      x: 10,
      y: 14,
      z: thickness,
    },
  };
  (d.screwHolder = {
    r: d.base.x / 2,
    h: 6.5,
    hole: 2,
  }),
    (d.hook = {
      x: d.base.x,
      y: thickness,
      z: 8.5,
      hole: 1.5,
      r: 5,
    });

  const triangleSide = d.base.y * 0.3;
  const triangle = draw([0, 0])
    .lineTo([0, triangleSide])
    .lineTo([triangleSide, 0])
    .close()
    .sketchOnPlane('YZ')
    .extrude(d.base.x)
    .translateX(d.base.x / -2)
    .translateY(d.base.y / -2 + thickness - nothing)
    .translateZ(thickness - nothing);

  const base = makeBaseBox(d.base.x, d.base.y, d.base.z);
  const screwHole = makeCylinder(d.screwHolder.hole, d.screwHolder.h * 2)
    .translateZ(d.screwHolder.h * -0.1)
    .translateY(d.base.y / 2);
  const screwHolder = makeCylinder(d.screwHolder.r, d.screwHolder.h).translateY(
    d.base.y / 2
  );
  const hookBase = makeBaseBox(d.hook.x, d.hook.y, d.hook.z).translateY(
    (d.base.y - d.hook.y) / -2
  );
  const hookHole = makeCylinder(d.hook.hole, d.hook.x * 2).translateZ(
    d.hook.x * -0.1
  );
  let hookOuter = makeCylinder(d.hook.r, d.hook.x)
    .cut(hookHole)
    .translateZ(d.hook.x / -2)
    .rotate(90, [0, 0, 0], [0, 1, 0]);

  const hookCut1 = makeBaseBox(20, 20, d.hook.r + 1)
    .translateZ(-(d.hook.r + 1))
    .translateY(-10);
  const hookCut2 = makeBaseBox(20, 20, d.hook.r + 1)
    .translateZ(-d.hook.r)
    .translateY(10);

  hookOuter = hookOuter
    .cut(hookCut1)
    .cut(hookCut2)
    .translateY(-(d.base.y / 2 - d.hook.r))
    .translateZ(d.hook.z - nothing);

  const hook = hookBase.fuse(hookOuter);

  // Nicer and flimsier cut
  // const outerCut1 = makeBaseBox(20,d.base.y,20).translateZ(-3).translateY(-d.base.y + d.hook.r)
  // const outerCut2 = makeCylinder(d.screwHolder.r, 25).translateZ(-2).translateY((d.base.y) / -2 +  d.hook.r)
  // const outerCut = outerCut1.cut(outerCut2);

  const outerCut1 = makeBaseBox(20, d.base.y, 20)
    .translateZ(-3)
    .translateY(-d.base.y + d.hook.r);
  const outerCut2 = makeCylinder(d.screwHolder.r * 1.2, 25)
    .translateZ(-2)
    .translateY(d.base.y / -2 + d.hook.r);
  const outerCut = outerCut1.cut(outerCut2);

  const part = base.fuse(screwHolder).cut(screwHole).fuse(hook).fuse(triangle);

  return [
    {
      shape: part.cut(outerCut),
      color: '#5c60d6',
    },
  ];
};
