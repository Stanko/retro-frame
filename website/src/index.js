import { AmbientLight, HemisphereLight, Vector2, Clock } from 'three';
import { renderer, scene } from './core/renderer';
import { fpsGraph, gui } from './core/gui';
import camera from './core/camera';
import { controls } from './core/orbit-control';
import Screen from './components/screen';

import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';

// ----- Lights ----- //
const ambientLight = new AmbientLight(0xffffff, 0.2);
scene.add(ambientLight);

const directionalLight = new HemisphereLight('#ffff00', 1);
// directionalLight.castShadow = true;
// directionalLight.shadow.mapSize.set(1024, 1024);
// directionalLight.shadow.camera.far = 15;
// directionalLight.shadow.normalBias = 0.05;
directionalLight.position.set(0, 0, 100);

scene.add(directionalLight);

const DirectionalLightFolder = gui.addFolder({
  title: 'Directional Light',
});

Object.keys(directionalLight.position).forEach((key) => {
  DirectionalLightFolder.addBinding(directionalLight.position, key, {
    min: -300,
    max: 300,
    step: 1,
  });
});

// ----- Retro Frame ----- //

const screen = new Screen();
scene.add(screen.group);
screen.loadGif('/gif/wc-footman.gif');

// Change pixel intensity through GUI
gui.addBinding(screen, 'intensity', {
  value: screen.intensity,
  min: 1,
  max: 20,
  step: 1,
  label: 'pixel intensity',
});

// Diffuser params
gui.addBinding(screen.diffuser, 'visible', {
  value: true,
  label: 'diffuser',
});
gui.addBinding(screen.diffuser.material, 'opacity', {
  value: screen.diffuser.material.opacity,
  label: 'opacity',
  min: 0,
  max: 1,
  step: 0.01,
});

// ----- Render loop ----- //

const renderScene = new RenderPass(scene, camera);

const bloomPass = new UnrealBloomPass(
  new Vector2(window.innerWidth, window.innerHeight),
  1.5,
  0.4,
  0.85
);

const BloomFolder = gui.addFolder({
  title: 'Bloom',
});
BloomFolder.addBinding(bloomPass, 'threshold', {
  value: bloomPass.threshold,
  min: 0,
  max: 1,
  step: 0.01,
  label: 'threshold',
});
BloomFolder.addBinding(bloomPass, 'strength', {
  value: bloomPass.strength,
  min: 0,
  max: 10,
  step: 0.1,
  label: 'strength',
});
BloomFolder.addBinding(bloomPass, 'radius', {
  value: bloomPass.radius,
  min: 0,
  max: 12,
  step: 0.5,
  label: 'radius',
});

const outputPass = new OutputPass();

const composer = new EffectComposer(renderer);
composer.addPass(renderScene);
composer.addPass(bloomPass);
composer.addPass(outputPass);

const clock = new Clock();

const loop = () => {
  const elapsedTime = clock.getElapsedTime();

  fpsGraph.begin();

  controls.update();
  // renderer.render(scene, camera);
  composer.render();

  fpsGraph.end();
  requestAnimationFrame(loop);
};

loop();
