// Pillars hero background. Original three.js scene: glass data towers on a
// reflective floor, with bloom, light beams, drifting motes, hover lift and
// ripples that follow the pointer, and a big blast on click.
//
// Usage:
//   import { createPillars } from "./pillars.js";
//   const pillars = createPillars(canvas, { palette: "cobalt", interactTarget: heroEl });
//   pillars.destroy();

import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";

export const PALETTES = {
  cobalt:   { base: "#0a1a52", glow: "#2f6bff", rim: "#7ec2ff", zenith: "#010209", horizon: "#0a1646", mote: "#8fc4ff" },
};

const DEFAULTS = {
  palette: "cobalt",
  grid: 15,             // pillars per side before the circular mask
  spacing: 2.4,         // world units between pillar centers
  maxHeight: 13,
  orbitSpeed: 0.03,     // camera orbit, radians per second
  motes: 1400,
  beams: 5,             // light beams above the tallest pillars
  bloom: 0.9,
  interactTarget: null, // element that receives hover/click (defaults to the canvas)
  maxPixelRatio: 2,
  startTime: 0,         // seconds into the animation to start at (skips the intro)
};

const GLSL_COMMON = /* glsl */ `
  uniform vec3 uFogColor;
  uniform float uFogDensity;
  float fogFactor(float d) { float f = uFogDensity * d; return clamp(1.0 - exp(-f * f), 0.0, 1.0); }
  float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
`;

const PILLAR_VERT = /* glsl */ `
  attribute vec4 aData;   // x seed, y heat, z height, w width
  varying vec3 vN;
  varying vec3 vWP;
  varying vec3 vLocal;
  varying vec4 vData;
  void main() {
    vLocal = position;
    vData = aData;
    vec4 wp = modelMatrix * instanceMatrix * vec4(position, 1.0);
    vWP = wp.xyz;
    vN = normalize(mat3(modelMatrix) * mat3(instanceMatrix) * normal);
    gl_Position = projectionMatrix * viewMatrix * wp;
  }
`;

const PILLAR_FRAG = /* glsl */ `
  ${GLSL_COMMON}
  uniform float uTime;
  uniform float uMirror;
  uniform vec3 uBase;
  uniform vec3 uGlow;
  uniform vec3 uRim;
  varying vec3 vN;
  varying vec3 vWP;
  varying vec3 vLocal;
  varying vec4 vData;

  void main() {
    vec3 N = normalize(vN);
    vec3 V = normalize(cameraPosition - vWP);
    float fres = pow(1.0 - abs(dot(N, V)), 3.0);

    float seed = vData.x, heat = vData.y, H = vData.z, W = vData.w;
    float y = vLocal.y;
    float h = y * H;
    bool cap = abs(N.y) > 0.5;

    // Glowing edges, kept a constant world width regardless of pillar size
    float ax = abs(vLocal.x), az = abs(vLocal.z);
    float s = (cap ? max(ax, az) : min(ax, az)) * W;
    float ew = 0.05;
    float edge = smoothstep(0.5 * W - ew - fwidth(s), 0.5 * W - ew * 0.25, s);
    float rimTop = cap ? 0.0 : smoothstep(H - 0.12, H, h);

    // Face coordinate along the current side, for cells and panel lines
    float u = (abs(N.x) > 0.5 ? vLocal.z : vLocal.x) * W;

    // Horizontal panel seams
    float lc = h / 1.1 + seed * 3.0;
    float ld = min(fract(lc), 1.0 - fract(lc));
    float seam = 1.0 - smoothstep(0.0, fwidth(lc) * 1.5, ld);

    // Lit data cells that flicker slowly
    vec2 cell = vec2(floor(u * 3.2), floor(h * 1.6));
    vec2 cf = vec2(fract(u * 3.2), fract(h * 1.6));
    float r = hash(cell + seed * 17.0 + (N.x > 0.5 ? 3.0 : 0.0) + (N.z > 0.5 ? 7.0 : 0.0));
    float inside = step(0.18, cf.x) * step(cf.x, 0.82) * step(0.25, cf.y) * step(cf.y, 0.75);
    float lit = step(0.86, r) * inside * (0.55 + 0.45 * sin(uTime * (0.4 + r * 1.8) + r * 60.0));
    lit *= smoothstep(0.1, 0.5, y);

    // Energy pulses climbing each tower
    float speed = 0.18 + hash(vec2(seed, 1.7)) * 0.22;
    float p = fract(h * 0.06 - uTime * speed + seed * 13.0);
    float pulse = pow(max(0.0, 1.0 - abs(p - 0.5) * 2.0), 28.0);

    vec3 col = uBase * (0.06 + 0.32 * pow(y, 1.8));
    col += uGlow * fres * 0.22;
    col += uGlow * edge * (0.25 + 0.75 * y);
    col += uGlow * seam * 0.18 * y;
    col += uGlow * lit * 0.9;
    col += uRim * pulse * (0.12 + edge * 1.8);
    col += mix(uGlow, uRim, 0.6) * rimTop * 1.1;
    if (cap) col = uBase * 0.25 + uGlow * edge * 1.8 + uGlow * 0.08;

    col *= 1.0 + heat * 1.4;
    col += uRim * heat * (edge + rimTop) * 1.4;

    if (uMirror > 0.5) col *= exp(-h * 0.3) * 0.55;

    col = mix(col, uFogColor, fogFactor(length(vWP - cameraPosition)));
    gl_FragColor = vec4(col, 1.0);
  }
`;

const FLOOR_VERT = /* glsl */ `
  varying vec3 vWP;
  void main() {
    vec4 wp = modelMatrix * vec4(position, 1.0);
    vWP = wp.xyz;
    gl_Position = projectionMatrix * viewMatrix * wp;
  }
`;

const FLOOR_FRAG = /* glsl */ `
  ${GLSL_COMMON}
  uniform float uTime;
  uniform float uSpacing;
  uniform vec3 uGlow;
  uniform vec3 uRim;
  #define MAX_WAVES 8
  uniform vec4 uWaves[MAX_WAVES];   // x, z, radius, strength
  uniform float uWaveW[MAX_WAVES];  // ring width
  varying vec3 vWP;
  void main() {
    vec2 p = vWP.xz;
    float d = length(p);
    vec2 c = p / uSpacing + 0.5;
    vec2 g = abs(fract(c - 0.5) - 0.5) / fwidth(c);
    float line = 1.0 - min(min(g.x, g.y), 1.0);

    vec3 col = uGlow * line * 0.28 * exp(-d * 0.035);
    col += uGlow * 0.06 * exp(-d * d * 0.003);

    // Ripple rings from the pointer, plus a filled flash for big blasts
    float ring = 0.0, flash = 0.0;
    for (int i = 0; i < MAX_WAVES; i++) {
      vec4 w = uWaves[i];
      if (w.w <= 0.0) continue;
      float wd = length(p - w.xy);
      ring += exp(-pow((wd - w.z) / uWaveW[i], 2.0)) * w.w;
      flash += step(2.0, uWaveW[i]) * smoothstep(w.z, 0.0, wd) * w.w;
    }
    col += uRim * ring * (0.35 + line * 1.5);
    col += uGlow * flash * (0.05 + line * 0.5);

    vec3 V = normalize(cameraPosition - vWP);
    float fres = pow(1.0 - abs(V.y), 4.0);
    float alpha = mix(0.72, 0.9, fres);

    col = mix(col, uFogColor, fogFactor(length(vWP - cameraPosition)));
    gl_FragColor = vec4(col, alpha);
  }
`;

const BEAM_VERT = /* glsl */ `
  attribute vec2 aBeam; // x seed, y intensity
  varying vec3 vN;
  varying vec3 vWP;
  varying float vY;
  varying vec2 vBeam;
  void main() {
    vY = position.y;
    vBeam = aBeam;
    vec4 wp = modelMatrix * instanceMatrix * vec4(position, 1.0);
    vWP = wp.xyz;
    vN = normalize(mat3(modelMatrix) * mat3(instanceMatrix) * normal);
    gl_Position = projectionMatrix * viewMatrix * wp;
  }
`;

const BEAM_FRAG = /* glsl */ `
  ${GLSL_COMMON}
  uniform float uTime;
  uniform vec3 uRim;
  varying vec3 vN;
  varying vec3 vWP;
  varying float vY;
  varying vec2 vBeam;
  void main() {
    vec3 V = normalize(cameraPosition - vWP);
    float core = pow(abs(dot(normalize(vN), V)), 4.0);
    float fall = pow(1.0 - vY, 2.5) * smoothstep(0.0, 0.02, vY);
    float s = vBeam.x;
    float flick = 0.8 + 0.2 * sin(uTime * 2.3 + s * 10.0) * sin(uTime * 1.3 + s * 4.0);
    float a = core * fall * flick * vBeam.y * 0.4;
    a *= 1.0 - fogFactor(length(vWP - cameraPosition));
    gl_FragColor = vec4(uRim * a, 1.0);
  }
`;

const MOTE_VERT = /* glsl */ `
  attribute float aSeed;
  uniform float uTime;
  uniform float uHeight;
  uniform float uScale;
  varying float vA;
  void main() {
    vec3 p = position;
    p.y = mod(p.y + uTime * (0.25 + aSeed * 0.6), uHeight);
    p.x += sin(uTime * 0.3 + aSeed * 20.0) * 0.8;
    p.z += cos(uTime * 0.23 + aSeed * 15.0) * 0.8;
    vec4 mv = modelViewMatrix * vec4(p, 1.0);
    gl_Position = projectionMatrix * mv;
    gl_PointSize = (1.2 + aSeed * 2.8) * uScale * (28.0 / -mv.z);
    float tw = 0.45 + 0.55 * sin(uTime * (0.8 + aSeed * 3.0) + aSeed * 50.0);
    vA = tw * smoothstep(0.0, 2.0, p.y) * smoothstep(uHeight, uHeight - 5.0, p.y) * exp(mv.z * 0.018);
  }
`;

const MOTE_FRAG = /* glsl */ `
  uniform vec3 uMote;
  varying float vA;
  void main() {
    float d = length(gl_PointCoord - 0.5);
    float a = smoothstep(0.5, 0.0, d);
    gl_FragColor = vec4(uMote * a * a * vA * 1.6, 1.0);
  }
`;

const SKY_VERT = /* glsl */ `
  varying vec3 vDir;
  void main() {
    vDir = position;
    vec4 p = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    gl_Position = p.xyww;
  }
`;

const SKY_FRAG = /* glsl */ `
  uniform float uTime;
  uniform vec3 uZenith;
  uniform vec3 uFogColor;
  varying vec3 vDir;
  float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
  void main() {
    vec3 d = normalize(vDir);
    float y = d.y;
    vec3 col = mix(uFogColor, uZenith, smoothstep(0.0, 0.5, y));

    vec2 uv = vec2(atan(d.z, d.x) * 90.0, asin(clamp(y, -1.0, 1.0)) * 90.0);
    vec2 id = floor(uv);
    float r = hash(id);
    float star = step(0.992, r) * smoothstep(0.35, 0.0, length(fract(uv) - 0.5));
    star *= smoothstep(0.08, 0.45, y) * (0.55 + 0.45 * sin(uTime * 1.5 + r * 100.0));
    col += vec3(0.8, 0.88, 1.0) * star * 0.7;
    gl_FragColor = vec4(col, 1.0);
  }
`;

const FINISH_SHADER = {
  uniforms: {
    tDiffuse: { value: null },
    uTime: { value: 0 },
    uRes: { value: new THREE.Vector2(1, 1) },
    uGrain: { value: 0.025 },
    uCA: { value: 0.004 },
  },
  vertexShader: /* glsl */ `
    varying vec2 vUv;
    void main() { vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }
  `,
  fragmentShader: /* glsl */ `
    uniform sampler2D tDiffuse;
    uniform float uTime;
    uniform vec2 uRes;
    uniform float uGrain;
    uniform float uCA;
    varying vec2 vUv;
    void main() {
      vec2 c = vUv - 0.5;
      float k = uCA * dot(c, c) * 4.0;
      vec3 col;
      col.r = texture2D(tDiffuse, vUv + c * k).r;
      col.g = texture2D(tDiffuse, vUv).g;
      col.b = texture2D(tDiffuse, vUv - c * k).b;
      float n = fract(sin(dot(floor(vUv * uRes) + fract(uTime) * 91.0, vec2(12.9898, 78.233))) * 43758.5453);
      col += (n - 0.5) * uGrain;
      gl_FragColor = vec4(col, 1.0);
    }
  `,
};

const easeOutCubic = (x) => 1 - Math.pow(1 - x, 3);
const easeInOutCubic = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
const clamp01 = (x) => Math.min(1, Math.max(0, x));
const lerp = (a, b, t) => a + (b - a) * t;

function seeded(seed) {
  let s = seed >>> 0;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 4294967296);
}

export function createPillars(canvas, options = {}) {
  const cfg = { ...DEFAULTS, ...options };

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: false, powerPreference: "high-performance" });
  } catch (err) {
    canvas.dataset.pillars = "unsupported";
    return { setPalette() {}, blast() {}, destroy() {}, supported: false };
  }
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.95;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, 1, 0.1, 400);

  // ---- Colors (lerped when the palette changes) ----
  const keys = ["base", "glow", "rim", "zenith", "horizon", "mote"];
  const colors = {};
  const targets = {};
  for (const k of keys) {
    colors[k] = new THREE.Color(PALETTES[cfg.palette][k]);
    targets[k] = colors[k].clone();
  }

  const fogColor = new THREE.Color();
  const fog = { uFogColor: { value: fogColor }, uFogDensity: { value: 0.02 } };
  const time = { value: 0 };

  // ---- Pillars ----
  const rand = seeded(47);
  const half = (cfg.grid - 1) / 2;
  const towers = [];
  for (let gx = 0; gx < cfg.grid; gx++) {
    for (let gz = 0; gz < cfg.grid; gz++) {
      const x = gx - half, z = gz - half;
      const d = Math.hypot(x, z) / half;
      if (d > 1.02) continue;
      const falloff = 0.22 + 0.78 * Math.exp(-(d * d) / (2 * 0.38 * 0.38));
      let base = falloff * (0.45 + rand() * 0.55);
      if (rand() < 0.06) base = Math.min(1.15, base * 1.6);
      towers.push({
        x: x * cfg.spacing, z: z * cfg.spacing, d, base,
        width: cfg.spacing * (0.42 + rand() * 0.2),
        seed: rand(), phase: rand() * Math.PI * 2,
        heat: 0, height: 0,
      });
    }
  }
  const count = towers.length;

  const boxGeo = new THREE.BoxGeometry(1, 1, 1);
  boxGeo.translate(0, 0.5, 0);
  const aData = new THREE.InstancedBufferAttribute(new Float32Array(count * 4), 4);
  aData.setUsage(THREE.DynamicDrawUsage);
  boxGeo.setAttribute("aData", aData);

  const pillarUniforms = (mirror) => ({
    ...fog, uTime: time, uMirror: { value: mirror },
    uBase: { value: colors.base }, uGlow: { value: colors.glow }, uRim: { value: colors.rim },
  });
  const pillarMat = new THREE.ShaderMaterial({
    uniforms: pillarUniforms(0), vertexShader: PILLAR_VERT, fragmentShader: PILLAR_FRAG,
  });
  const pillars = new THREE.InstancedMesh(boxGeo, pillarMat, count);
  pillars.instanceMatrix.setUsage(THREE.DynamicDrawUsage);
  pillars.frustumCulled = false;
  scene.add(pillars);

  // Reflection: the same instances drawn upside down under a translucent floor
  const mirrorMat = new THREE.ShaderMaterial({
    uniforms: pillarUniforms(1), vertexShader: PILLAR_VERT, fragmentShader: PILLAR_FRAG,
    side: THREE.BackSide,
  });
  const mirror = new THREE.InstancedMesh(boxGeo, mirrorMat, count);
  mirror.instanceMatrix = pillars.instanceMatrix;
  mirror.scale.y = -1;
  mirror.frustumCulled = false;
  scene.add(mirror);

  // ---- Floor ----
  const MAX_WAVES = 8;
  const waves = [];
  const waveUniform = Array.from({ length: MAX_WAVES }, () => new THREE.Vector4());
  const waveWidth = new Array(MAX_WAVES).fill(1);
  const floorMat = new THREE.ShaderMaterial({
    uniforms: {
      ...fog, uTime: time, uSpacing: { value: cfg.spacing },
      uGlow: { value: colors.glow }, uRim: { value: colors.rim },
      uWaves: { value: waveUniform }, uWaveW: { value: waveWidth },
    },
    vertexShader: FLOOR_VERT, fragmentShader: FLOOR_FRAG,
    transparent: true, depthWrite: false,
  });
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(600, 600), floorMat);
  floor.rotation.x = -Math.PI / 2;
  scene.add(floor);

  // ---- Light beams above the tallest towers ----
  const beamTowers = [...towers].sort((a, b) => b.base - a.base).slice(0, cfg.beams);
  const beamGeo = new THREE.CylinderGeometry(1, 1, 1, 24, 1, true);
  beamGeo.translate(0, 0.5, 0);
  const aBeam = new THREE.InstancedBufferAttribute(new Float32Array(cfg.beams * 2), 2);
  beamTowers.forEach((t, i) => aBeam.setXY(i, t.seed, 0));
  beamGeo.setAttribute("aBeam", aBeam);
  const beams = new THREE.InstancedMesh(beamGeo, new THREE.ShaderMaterial({
    uniforms: { ...fog, uTime: time, uRim: { value: colors.rim } },
    vertexShader: BEAM_VERT, fragmentShader: BEAM_FRAG,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  }), beamTowers.length);
  beams.frustumCulled = false;
  scene.add(beams);

  // ---- Motes ----
  const span = cfg.grid * cfg.spacing;
  const mPos = new Float32Array(cfg.motes * 3);
  const mSeed = new Float32Array(cfg.motes);
  for (let i = 0; i < cfg.motes; i++) {
    const a = rand() * Math.PI * 2, r = Math.sqrt(rand()) * span * 0.9;
    mPos.set([Math.cos(a) * r, rand() * cfg.maxHeight * 1.8, Math.sin(a) * r], i * 3);
    mSeed[i] = rand();
  }
  const moteGeo = new THREE.BufferGeometry();
  moteGeo.setAttribute("position", new THREE.BufferAttribute(mPos, 3));
  moteGeo.setAttribute("aSeed", new THREE.BufferAttribute(mSeed, 1));
  const moteUniforms = {
    uTime: time, uHeight: { value: cfg.maxHeight * 1.8 }, uScale: { value: 1 }, uMote: { value: colors.mote },
  };
  const motes = new THREE.Points(moteGeo, new THREE.ShaderMaterial({
    uniforms: moteUniforms, vertexShader: MOTE_VERT, fragmentShader: MOTE_FRAG,
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
  }));
  motes.frustumCulled = false;
  scene.add(motes);

  // ---- Sky ----
  const sky = new THREE.Mesh(new THREE.SphereGeometry(300, 32, 16), new THREE.ShaderMaterial({
    uniforms: { uTime: time, uZenith: { value: colors.zenith }, uFogColor: fog.uFogColor },
    vertexShader: SKY_VERT, fragmentShader: SKY_FRAG, side: THREE.BackSide, depthWrite: false,
  }));
  sky.renderOrder = -1;
  scene.add(sky);

  // ---- Post ----
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), cfg.bloom, 0.55, 0.28);
  composer.addPass(bloom);
  composer.addPass(new OutputPass());
  const finish = new ShaderPass(FINISH_SHADER);
  composer.addPass(finish);

  // ---- Sizing and adaptive quality ----
  let dpr = Math.min(devicePixelRatio || 1, cfg.maxPixelRatio);
  function resize() {
    const w = Math.max(1, canvas.clientWidth), h = Math.max(1, canvas.clientHeight);
    renderer.setPixelRatio(dpr);
    renderer.setSize(w, h, false);
    composer.setPixelRatio(dpr);
    composer.setSize(w, h);
    camera.aspect = w / h;
    // Keep the field framed on tall, narrow screens
    camera.fov = w / h < 1 ? 40 + (1 - w / h) * 28 : 40;
    camera.updateProjectionMatrix();
    finish.uniforms.uRes.value.set(w * dpr, h * dpr);
    moteUniforms.uScale.value = (h * dpr) / 900;
    if (!running) renderFrame();
  }
  const ro = new ResizeObserver(resize);
  ro.observe(canvas);

  // ---- Interaction ----
  const target = cfg.interactTarget || canvas;
  const ndc = new THREE.Vector2(0, 0);
  const parallax = new THREE.Vector2(0, 0);
  const hover = new THREE.Vector3();
  let hovering = false;
  const ray = new THREE.Raycaster();
  const ground = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);

  function toNdc(e) {
    const r = canvas.getBoundingClientRect();
    ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  }
  function groundPoint(out) {
    ray.setFromCamera(ndc, camera);
    return ray.ray.intersectPlane(ground, out);
  }
  const onMove = (e) => { toNdc(e); hovering = true; };
  const onLeave = () => { hovering = false; ndc.set(0, 0); };
  const lastRipple = new THREE.Vector3();
  let rippleTravel = 0;
  let hadHover = false;
  let kick = 0;

  // Small ripples trail the pointer; a click is a big area blast
  function spawnWave(x, z, big) {
    if (waves.length >= MAX_WAVES) {
      const small = waves.findIndex((w) => !w.big);
      waves.splice(small >= 0 ? small : 0, 1);
    }
    waves.push(big
      ? { x, z, big, age: 0, life: 2.8, speed: 24, width: 3.2, power: 2.1 }
      : { x, z, big, age: 0, life: 1.5, speed: 12, width: 1.2, power: 0.55 });
    if (big) kick = 1;
  }

  const onDown = (e) => {
    if (e.target.closest && e.target.closest("a, button, input, select, textarea, label")) return;
    toNdc(e);
    const p = new THREE.Vector3();
    if (groundPoint(p) && Math.hypot(p.x, p.z) < span) spawnWave(p.x, p.z, true);
  };
  target.addEventListener("pointermove", onMove);
  target.addEventListener("pointerleave", onLeave);
  target.addEventListener("pointerdown", onDown);

  // ---- Palette ----
  function setPalette(name) {
    const p = PALETTES[name];
    if (!p) return;
    for (const k of keys) targets[k].set(p[k]);
    if (!running) { for (const k of keys) colors[k].copy(targets[k]); renderFrame(); }
  }

  // ---- Animation ----
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const m = new THREE.Matrix4();
  const tmp = new THREE.Vector3();
  let t = reduced ? 12 : cfg.startTime;
  let last = performance.now();
  let raf = 0;
  let running = false;
  let visible = true, onscreen = true;
  let perfFrames = 0, perfTime = 0;

  function update(dt) {
    time.value = t;

    for (const k of keys) colors[k].lerp(targets[k], Math.min(1, dt * 2.5));
    fogColor.copy(colors.horizon).lerp(colors.glow, 0.12);

    // Camera: pull back from low and close, then a slow orbit with pointer parallax
    const intro = reduced ? 1 : easeInOutCubic(clamp01(t / 5));
    parallax.lerp(ndc, Math.min(1, dt * 2));
    const ang = t * cfg.orbitSpeed + 0.7 + parallax.x * 0.12;
    const radius = lerp(12, 40, intro);
    const camY = lerp(1.6, 7.5, intro) + parallax.y * 1.8;
    camera.position.set(Math.cos(ang) * radius, camY, Math.sin(ang) * radius);
    camera.lookAt(0, lerp(9, 10.5, intro), 0);

    const hoverHit = hovering && groundPoint(hover) && Math.hypot(hover.x, hover.z) < span * 0.75;
    if (hoverHit) {
      if (!hadHover) { lastRipple.copy(hover); spawnWave(hover.x, hover.z, false); }
      rippleTravel += hover.distanceTo(lastRipple);
      lastRipple.copy(hover);
      if (rippleTravel > 2.6) { rippleTravel = 0; spawnWave(hover.x, hover.z, false); }
    }
    hadHover = hoverHit;

    for (let w = waves.length - 1; w >= 0; w--) {
      const wv = waves[w];
      wv.age += dt;
      if (wv.age >= wv.life) waves.splice(w, 1);
    }
    for (let w = 0; w < MAX_WAVES; w++) {
      const wv = waves[w];
      if (!wv) { waveUniform[w].set(0, 0, 0, 0); continue; }
      wv.radius = wv.age * wv.speed;
      wv.fade = Math.pow(1 - wv.age / wv.life, 1.5);
      waveUniform[w].set(wv.x, wv.z, wv.radius, wv.fade * (wv.big ? 1.4 : 0.8));
      waveWidth[w] = wv.width;
    }

    // Big blasts shake the camera and swell the bloom for a moment
    kick *= Math.exp(-dt * 3.5);
    camera.position.y += Math.sin(t * 47) * kick * 0.22;
    camera.position.x += Math.sin(t * 39 + 1.3) * kick * 0.18;
    bloom.strength = cfg.bloom + kick * 0.7;

    for (let i = 0; i < count; i++) {
      const tw = towers[i];
      const rise = easeOutCubic(clamp01((t - 0.3 - tw.d * 1.6) / 1.8));
      const breathe = 0.9 + 0.1 * Math.sin(t * 0.5 + tw.phase);
      const swell = 0.5 + 0.5 * Math.sin(tw.x * 0.18 + tw.z * 0.11 - t * 0.6);

      let heatTarget = 0;
      if (hoverHit) {
        const dd = (tw.x - hover.x) ** 2 + (tw.z - hover.z) ** 2;
        heatTarget = Math.exp(-dd / (2 * 3.2 * 3.2));
      }
      let shock = 0;
      for (const wv of waves) {
        const wd = Math.hypot(tw.x - wv.x, tw.z - wv.z);
        shock += Math.exp(-(((wd - wv.radius) / (wv.width * 1.6)) ** 2)) * wv.power * wv.fade;
      }
      tw.heat = lerp(tw.heat, heatTarget, Math.min(1, dt * 5));
      const heat = Math.min(2.4, tw.heat + shock);

      const hTarget = (tw.base * breathe * cfg.maxHeight + swell * 1.4 + heat * 3.2) * rise;
      tw.height = Math.max(0.05, hTarget);

      m.makeScale(tw.width, tw.height, tw.width).setPosition(tw.x, 0, tw.z);
      pillars.setMatrixAt(i, m);
      aData.setXYZW(i, tw.seed, heat, tw.height, tw.width);
    }
    pillars.instanceMatrix.needsUpdate = true;
    aData.needsUpdate = true;

    const beamIn = reduced ? 1 : clamp01((t - 3.2) / 2);
    beamTowers.forEach((tw, i) => {
      const w = tw.width * 0.32;
      m.makeScale(w, 60, w).setPosition(tw.x, tw.height, tw.z);
      beams.setMatrixAt(i, m);
      aBeam.setY(i, beamIn);
    });
    beams.instanceMatrix.needsUpdate = true;
    aBeam.needsUpdate = true;

    finish.uniforms.uTime.value = t;
  }

  function renderFrame() { update(0.016); composer.render(); }

  function loop(now) {
    raf = requestAnimationFrame(loop);
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    t += dt;
    update(dt);
    composer.render();

    // Drop resolution if the device cannot keep up
    perfFrames++; perfTime += dt;
    if (perfFrames >= 90) {
      const avg = perfTime / perfFrames;
      if (avg > 1 / 45 && dpr > 0.75) { dpr = Math.max(0.75, dpr - 0.25); resize(); }
      perfFrames = 0; perfTime = 0;
    }
  }

  function setRunning() {
    const should = !reduced && visible && onscreen;
    if (should && !running) { running = true; last = performance.now(); raf = requestAnimationFrame(loop); }
    else if (!should && running) { running = false; cancelAnimationFrame(raf); }
  }
  const io = new IntersectionObserver(([e]) => { onscreen = e.isIntersecting; setRunning(); });
  io.observe(canvas);
  const onVis = () => { visible = document.visibilityState === "visible"; setRunning(); };
  document.addEventListener("visibilitychange", onVis);

  resize();
  if (reduced) renderFrame();
  setRunning();
  canvas.dataset.pillars = "ready";

  function destroy() {
    running = false;
    cancelAnimationFrame(raf);
    ro.disconnect(); io.disconnect();
    document.removeEventListener("visibilitychange", onVis);
    target.removeEventListener("pointermove", onMove);
    target.removeEventListener("pointerleave", onLeave);
    target.removeEventListener("pointerdown", onDown);
    scene.traverse((o) => { o.geometry?.dispose(); o.material?.dispose(); });
    composer.dispose?.();
    renderer.dispose();
  }

  // Big area blast from code (default: the center of the field)
  const blast = (x = 0, z = 0) => spawnWave(x, z, true);

  return { setPalette, blast, destroy, supported: true };
}
