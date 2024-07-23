import { useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import {
  EffectComposer,
  Bloom,
  ToneMapping,
} from '@react-three/postprocessing';
import { OrbitControls } from '@react-three/drei';
import { parseGIF, decompressFrames } from 'gifuct-js';
import { Box3, Color, Vector3 } from 'three';
// import Frame from './components/frame';
import { useControls } from 'leva';

import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

const FrameModel = () => {
  const [frame, setFrame] = useState(null);

  useEffect(() => {
    const gltfLoader = new GLTFLoader();

    gltfLoader.load('/frame.glb', (gltf) => {
      const model = gltf.scene;
      const box = new Box3().setFromObject(model);
      const center = box.getCenter(new Vector3());
      model.position.sub(center);
      model.position.z += 26;

      model.rotation.x = Math.PI;

      setFrame(model);
    });
  }, []);

  return frame ? <primitive object={frame} /> : null;
};

const getBlankImage = (w = 64, h = 64, size = 2, gap = 0.5) => {
  const width = w * (size + gap) - gap;
  const height = h * (size + gap) - gap;

  const image = [];
  for (let x = 0; x < w; x++) {
    const col = [];
    for (let y = 0; y < h; y++) {
      col.push({
        color: [0, 0, 0],
        size: size,
        intensity: 1,
        position: {
          x: x * (size + gap) - width / 2,
          y: y * (size + gap) - height / 2,
        },
      });
    }
    image.push(col);
  }

  return image;
};

const convertUint8Arr = (byteArray) => {
  let result = [];

  for (let i = byteArray.length - 1; i >= 0; i--) {
    result.push(byteArray[i] / 255);
  }

  return result.reverse();
};

const sRGBToLinear = (color) => {
  return color.clone().convertSRGBToLinear();
};

const normalizeColorIntensity = (color) => {
  let maxComponent = Math.max(color.r, color.g, color.b);
  if (maxComponent > 1) {
    color.multiplyScalar(1 / maxComponent);
  }
  // color.multiplyScalar(2);
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

const frameToImage = (frame) => {
  const image = getBlankImage();

  const colorTable = frame.colorTable.map((color) => convertUint8Arr(color));

  frame.pixels.forEach((pixel, i) => {
    const xOffset = Math.floor((image.length - frame.dims.width) / 2);
    const yOffset = Math.floor((image[0].length - frame.dims.height) / 2);
    const x = (i % frame.dims.width) + xOffset;
    const y =
      frame.dims.height - Math.floor(i / frame.dims.width) - 1 + yOffset;

    let color = new Color(...colorTable[pixel]);
    color = sRGBToLinear(color);

    // Normalize the color intensity
    color = normalizeColorIntensity(color);

    let emissiveIntensity = 7; // example emissive intensity
    emissiveIntensity = adjustEmissiveIntensity(color, emissiveIntensity);

    // Optionally, apply bloom threshold
    // color = applyBloomThreshold(color, 0.8);
    image[x][y].color = color;
    image[x][y].intensity = emissiveIntensity;

    // let color = new THREE.Color(0xabcdef); // example color in sRGB
    // color = sRGBToLinear(color);
  });

  return image;
};

export default function App() {
  const [image, setImage] = useState(getBlankImage());
  const [animation, setAnimation] = useState(null);
  const { intensity, levels, gifURL } = useControls({
    intensity: { value: 5, min: 0, max: 20, step: 1 },
    levels: { value: 3, min: 0, max: 10, step: 0.5 },
    gifURL: {
      options: [
        'mario-chase-saturation.gif',
        'mario-jump-black.gif',
        'totoro.gif',
        'tutur.gif',
        'tmnt-rafael.gif',
        'wc-footman.gif',
        'zero.gif',
        'bear-black.gif',
        'knight.gif',
        'jim.gif',
        'megaman.gif',
        'hex-radial-pulsar.gif',
        'totk.gif',
      ],
    },
  });

  useEffect(() => {
    fetch(`/gif/${gifURL}`)
      .then((response) => response.arrayBuffer())
      .then((buffer) => {
        const gif = parseGIF(buffer);
        const frames = decompressFrames(gif, true);

        setAnimation(frames.map(frameToImage));
      });
  }, [gifURL]);

  useEffect(() => {
    if (animation) {
      let i = 0;
      const interval = setInterval(() => {
        setImage(animation[i]);
        i = (i + 1) % animation.length;
      }, 100);

      return () => clearInterval(interval);
    }
  }, [animation]);

  return (
    <Canvas camera={{ position: [0, 0, 200], far: 2000 }}>
      <OrbitControls />

      <ambientLight />
      <hemisphereLight intensity={0.3} />
      <directionalLight
        position={[0.2, 0.2, 1]}
        intensity={0.02}
        color="#fff"
      />

      <EffectComposer disableNormalPass>
        <Bloom
          mipmapBlur
          luminanceThreshold={0}
          levels={levels}
          intensity={intensity}
        />
        <ToneMapping />
      </EffectComposer>

      {image.map((col, x) =>
        col.map((cell, y) => (
          <Pixel
            key={`${x}-${y}`}
            color={cell.color}
            intensity={cell.intensity}
            position={[cell.position.x, cell.position.y, -6.2]}
          >
            <planeGeometry args={[cell.size, cell.size]} />
          </Pixel>
        ))
      )}

      <FrameModel />

      <mesh position={[0, 0, -6.0001]}>
        <boxGeometry args={[200, 200, 3]} />
        <meshPhysicalMaterial
          roughness={0.16}
          color="black"
          opacity={0.92}
          transparent
          reflectivity={0.5} // Higher reflectivity for a more reflective surface
          clearcoat={0.4} // Clearcoat for additional reflectivity and shine
          clearcoatRoughness={1} // Make the clearcoat smooth
        />
      </mesh>

      <mesh position={[0, 0, -35]}>
        <boxGeometry args={[236, 236, 1]} />
        <meshPhysicalMaterial roughness={0.5} color="#3a1101" />
      </mesh>
    </Canvas>
  );
}

function Pixel({ children, color, intensity, ...props }) {
  const isBlack =
    color.isColor && color.r === 0 && color.g === 0 && color.b === 0;
  return (
    <mesh {...props}>
      {children}
      <meshStandardMaterial
        color={color}
        emissive={isBlack ? null : color}
        emissiveIntensity={isBlack ? null : intensity}
        toneMapped={false}
      />
    </mesh>
  );
}
