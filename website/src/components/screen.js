import {
  MeshStandardMaterial,
  Mesh,
  Color,
  PlaneGeometry,
  BoxGeometry,
  Group,
} from 'three';
import { getGif } from './gif';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

class Screen {
  intensity = 1;

  constructor(w = 64, h = 64, size = 2, gap = 0.5) {
    this.w = w;
    this.h = h;

    const width = w * (size + gap) - gap;
    const height = h * (size + gap) - gap;

    const pixels = [];
    const geometry = new PlaneGeometry(size, size, 1, 1);

    for (let x = 0; x < w; x++) {
      const col = [];

      for (let y = 0; y < h; y++) {
        const material = new MeshStandardMaterial({
          color: new Color(0, 0, 0),
          emissive: new Color(0, 0, 0),
          emissiveIntensity: 1,
        });

        const pixel = new Mesh(geometry, material);
        pixel.position.set(
          x * (size + gap) - width / 2,
          y * (size + gap) - height / 2,
          0
        );
        col.push(pixel);
      }
      pixels.push(col);
    }

    this.pixels = pixels;

    // Diffuser
    const diffuserThickness = 3;
    const diffuserGeometry = new BoxGeometry(200, 200, diffuserThickness);
    const diffuserMaterial = new MeshStandardMaterial({
      roughness: 0.1,
      color: 'black',
      opacity: 0.92,
      transparent: true,
      reflectivity: 0.5,
      clearcoat: 0.4,
      clearcoatRoughness: 1,
    });
    this.diffuser = new Mesh(diffuserGeometry, diffuserMaterial);
    this.diffuser.position.set(0, 0, diffuserThickness);

    // Group
    this.group = new Group();

    // this.group.add(this.diffuser);
    this.pixels.forEach((col) => col.forEach((pixel) => this.group.add(pixel)));

    // this.loadFrame();
  }

  async loadFrame() {
    const loader = new GLTFLoader();
    const gltf = await loader.loadAsync('/frame.glb');

    this.frame = gltf.scene;
    this.group.add(this.frame);
  }

  async loadGif(url) {
    const gif = await getGif(url, this.w, this.h);
    this.update(gif[0]);
    this.gif = gif;
  }

  getEmissiveColor = (color, intensity = 1, factor = 0.5) => {
    // Calculate perceived brightness
    const brightness = 0.299 * color.r + 0.587 * color.g + 0.114 * color.b;
    const scaleFactor = Math.min(1 / brightness, 5) / 1 - brightness;
    console.log(brightness, scaleFactor);
    intensity *= scaleFactor;

    return color.clone().multiplyScalar(2 - brightness * 2);
  };

  update(image) {
    image.forEach((pixelData) => {
      const { x, y, color, intensity } = pixelData;

      const pixel = this.pixels[x][y];
      // pixel.material.color.set(color);

      pixel.material.emissive.set(this.getEmissiveColor(color));
      pixel.material.emissiveIntensity = intensity;
    });
  }
}

export default Screen;
