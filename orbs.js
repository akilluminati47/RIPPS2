// Glowing orbs flying through twelve mathematical formations.
// Original three.js scene: haze background, circular glow, light trails, and
// morphs where orbs split off or merge back when the orb count changes.
//
// Usage:
//   import { createOrbs, FORMATIONS } from "./orbs.js";
//   const orbs = createOrbs(canvas, { onChange: (index, formation) => {} });
//   orbs.go(3); orbs.next(); orbs.prev(); orbs.toggleLines(); orbs.destroy();

import * as THREE from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

const TAU = Math.PI * 2;
const PHI = (1 + Math.sqrt(5)) / 2;
const lerp = THREE.MathUtils.lerp;

// Lorenz attractor state, integrated every frame so it is always warm
const LORENZ_COUNT = 24;
const lorenz = Array.from({ length: LORENZ_COUNT }, (_, i) =>
  new THREE.Vector3(0.1 + (i % 6) * 0.35, 0.2 * i - 2, 16 + (i % 5) * 1.8));
function stepLorenz(dt) {
  const s = 10, r = 28, b = 8 / 3;
  const steps = 4, h = Math.min(dt, 0.05) * 0.35 / steps;
  for (const p of lorenz) {
    for (let k = 0; k < steps; k++) {
      const dx = s * (p.y - p.x), dy = p.x * (r - p.z) - p.y, dz = p.x * p.y - b * p.z;
      p.x += dx * h; p.y += dy * h; p.z += dz * h;
    }
  }
}

// Star polygon {7/3}: vertex order around the star
const STAR = Array.from({ length: 7 }, (_, k) => (k * 3) % 7);

// Full icosahedron: 12 vertices on the unit sphere, and its 30 edges
const ICO = [];
for (const s1 of [-1, 1]) for (const s2 of [-1, 1]) {
  ICO.push([0, s1, s2 * PHI], [s1, s2 * PHI, 0], [s2 * PHI, 0, s1]);
}
const ICO_EDGES = [];
for (let p = 0; p < 12; p++) for (let q = p + 1; q < 12; q++) {
  const d = Math.hypot(ICO[p][0] - ICO[q][0], ICO[p][1] - ICO[q][1], ICO[p][2] - ICO[q][2]);
  if (Math.abs(d - 2) < 1e-6) ICO_EDGES.push([p, q]);
}
const ICO_R = Math.hypot(1, PHI);
const AX = new THREE.Vector3(1, 0, 0), AY = new THREE.Vector3(0, 1, 0);
function icoVertex(k, t, o) {
  const [x, y, z] = ICO[k];
  o.set(x, y, z).multiplyScalar(3.4 / ICO_R);
  o.applyAxisAngle(AX, t * 0.31);
  return o.applyAxisAngle(AY, t * 0.23);
}

// A long Lorenz run, drawn as the faint butterfly behind the attractor orbs
const LORENZ_PATH = (() => {
  const p = new THREE.Vector3(0.1, 0, 20), out = [];
  for (let k = 0; k < 9000; k++) {
    const h = 0.004;
    const dx = 10 * (p.y - p.x), dy = p.x * (28 - p.z) - p.y, dz = p.x * p.y - (8 / 3) * p.z;
    p.x += dx * h; p.y += dy * h; p.z += dz * h;
    if (k > 600 && k % 3 === 0) out.push(new THREE.Vector3(p.x, p.z - 25, p.y).multiplyScalar(0.17));
  }
  return out;
})();

// Guide helpers: a curve is sampled into a faint polyline that outlines the shape
const curve = (at, samples = 220, closed = true) => ({ at, samples, closed });
const guideTmp = new THREE.Vector3();
const segment = (p0, p1) => curve((u, t, o) => {
  p0(t, guideTmp);
  p1(t, o);
  return o.lerpVectors(guideTmp, o, u);
}, 2, false);

function mobius(s, v, o) {
  const R = 3.6 + v * Math.cos(s / 2);
  return o.set(R * Math.cos(s), v * Math.sin(s / 2), R * Math.sin(s));
}
// Classic bottle-shaped Klein immersion (neck curving back in through the side), u in [0, PI)
function klein(u, v, o) {
  const cu = Math.cos(u), su = Math.sin(u), cv = Math.cos(v), sv = Math.sin(v);
  const c2 = cu * cu, c4 = c2 * c2, c6 = c4 * c2;
  const x = -2 / 15 * cu * (3 * cv - 30 * su + 90 * c4 * su - 60 * c6 * su + 5 * cu * cv * su);
  const y = -1 / 15 * su * (3 * cv - 3 * c2 * cv - 48 * c4 * cv + 48 * c6 * cv - 60 * su
    + 5 * cu * cv * su - 5 * c2 * cu * cv * su - 80 * c4 * cu * cv * su + 80 * c6 * cu * cv * su);
  const z = 2 / 15 * (3 + 5 * cu * su) * sv;
  return o.set(x - 0.15, y - 2.1, z).multiplyScalar(1.55);
}
function helix(k, strand, t, o) {
  const s = k * TAU * 1.4 + t * 0.8 + strand * Math.PI;
  return o.set((k - 0.5) * 8.5, Math.cos(s) * 1.7, Math.sin(s) * 1.7);
}
// Orb k's orbit: a circle of its own radius, inclined, with its plane slowly precessing
function menuOrbit(k, a, t, o) {
  const r = (2.5 + (k % 4) * 0.55) * (1 + 0.06 * Math.sin(t * 0.4 + k));
  const incl = 0.3 + ((k * 0.61) % 1) * 1.0;
  const node = (k / 7) * TAU + t * 0.05;
  const x0 = Math.cos(a) * r, z0 = Math.sin(a) * r;
  const y1 = -z0 * Math.sin(incl), z1 = z0 * Math.cos(incl);
  return o.set(x0 * Math.cos(node) + z1 * Math.sin(node), y1, -x0 * Math.sin(node) + z1 * Math.cos(node));
}

function borromean(ring, s, o) {
  const a = 3.2 * Math.cos(s), b = 1.6 * Math.sin(s);
  if (ring === 0) return o.set(a, b, 0);
  if (ring === 1) return o.set(0, a, b);
  return o.set(b, 0, a);
}

// Each formation places orb i of n at time t, in its own frame. `tilt` (about X)
// and `spin` (about Y, per second) are applied after, so flat shapes face the camera.
// `guides()` returns the curves drawn as the faint outline.
const ALL = [
  {
    // PS2 system-menu style: seven orbs, each on its own tilted orbit around a shared
    // center, at its own pace, weaving in front of and behind one another
    name: "Browser Orbit", n: 7, hue: 0.61, spread: 0.06, tilt: 0.12,
    at(i, n, t, o) { return menuOrbit(i, t * (0.3 + ((i * 0.37) % 1) * 0.35) + i * 2.1, t, o); },
    guides() { return Array.from({ length: this.n }, (_, k) => curve((u, t, o) => menuOrbit(k, u * TAU, t, o), 140)); },
  },
  {
    name: "Trefoil Knot", n: 24, hue: 0.6, spread: 0.06, spin: 0.12,
    at(i, n, t, o) {
      const s = (i / n) * TAU + t * 0.2;
      return o.set(Math.sin(s) + 2 * Math.sin(2 * s), Math.cos(s) - 2 * Math.cos(2 * s), -Math.sin(3 * s)).multiplyScalar(1.45);
    },
    guides() { return [curve((u, t, o) => this.at(u * this.n, this.n, t, o), 300)]; },
  },
  {
    // Three lanes across the width of the strip, so the half twist reads
    name: "Möbius Strip", n: 27, hue: 0.62, spread: 0.05, tilt: 0.6, spin: 0.1,
    at(i, n, t, o) {
      const lanes = 3, per = n / lanes;
      const v = ((i % lanes) - 1) * 1.15;
      return mobius((Math.floor(i / lanes) / per) * TAU + t * 0.28, v, o);
    },
    guides() {
      const edge = curve((u, t, o) => mobius(u * 2 * TAU, 1.15, o), 320);
      const rungs = Array.from({ length: 14 }, (_, k) =>
        curve((u, t, o) => mobius((k / 14) * TAU, lerp(-1.15, 1.15, u), o), 2, false));
      return [edge, ...rungs];
    },
  },
  {
    // A 7 x 4 grid of orbs sliding down the bottle, through the neck and around again
    name: "Klein Bottle", n: 28, hue: 0.63, spread: 0.06, tilt: 0.15,
    at(i, n, t, o) {
      const rows = 4, per = n / rows;
      const uu = (Math.floor(i / rows) / per) * Math.PI + t * 0.12;
      const wraps = Math.floor(uu / Math.PI);
      let v = ((i % rows) / rows) * TAU + t * 0.5;
      // The u = PI rim meets the u = 0 rim mirrored, so flip v on odd laps to stay continuous
      if (wraps % 2) v = Math.PI - v;
      return klein(uu - wraps * Math.PI, v, o);
    },
    guides() {
      const rings = Array.from({ length: 16 }, (_, k) => curve((u, t, o) => klein(((k + 0.5) / 16) * Math.PI, u * TAU, o), 90));
      const profile = [0, Math.PI].map((v) => curve((u, t, o) => klein(u * Math.PI, v, o), 180, false));
      return [...rings, ...profile];
    },
  },
  {
    name: "Golden Spiral", n: 21, hue: 0.59, spread: 0.05, tilt: 1.15,
    at(i, n, t, o) {
      const k = i / (n - 1);
      const a = k * 3 * Math.PI;
      const r = 0.24 * Math.exp((Math.log(PHI) / (Math.PI / 2)) * a) * (1 + 0.06 * Math.sin(t * 1.1));
      const rot = a + t * 0.25;
      return o.set(Math.cos(rot) * r, (k - 0.5) * 1.2, Math.sin(rot) * r);
    },
    guides() { return [curve((u, t, o) => this.at(u * (this.n - 1), this.n, t, o), 260, false)]; },
  },
  {
    name: "Lissajous", n: 28, hue: 0.6, spread: 0.07, spin: 0.1,
    at(i, n, t, o) {
      const s = (i / n) * TAU + t * 0.25;
      return o.set(4.2 * Math.sin(3 * s + Math.PI / 2), 2.6 * Math.sin(2 * s), 2.4 * Math.sin(5 * s));
    },
    guides() { return [curve((u, t, o) => this.at(u * this.n, this.n, t, o), 360)]; },
  },
  {
    name: "Borromean Rings", n: 24, hue: 0.61, spread: 0.08, spin: 0.14, tilt: 0.35,
    at(i, n, t, o) {
      const per = n / 3;
      const ring = Math.floor(i / per), idx = i % per;
      return borromean(ring, (idx / per) * TAU + t * (0.4 + ring * 0.07) + ring * 1.1, o);
    },
    guides() { return [0, 1, 2].map((ring) => curve((u, t, o) => borromean(ring, u * TAU, o), 160)); },
  },
  {
    name: "Torus Orbit", n: 28, hue: 0.6, spread: 0.05, tilt: 0.75,
    at(i, n, t, o) {
      const u = (i / n) * TAU + t * 0.3;
      const v = (i / n) * TAU * 4 + t * 1.1;
      const R = 3.3, r = 1.25;
      return o.set((R + r * Math.cos(v)) * Math.cos(u), r * Math.sin(v), (R + r * Math.cos(v)) * Math.sin(u));
    },
    guides() {
      // The knot the orbs ride, plus the donut outline: inner, outer, top and bottom rims
      const R = 3.3, r = 1.25;
      const rim = (rad, y) => curve((u, t, o) => o.set(Math.cos(u * TAU) * rad, y, Math.sin(u * TAU) * rad), 120);
      return [curve((u, t, o) => this.at(u * this.n, this.n, t, o), 360), rim(R - r, 0), rim(R + r, 0), rim(R, r), rim(R, -r)];
    },
  },
  {
    // Three orbs per edge, all gliding along the {7/3} star path
    name: "Seven-Point Star", n: 21, hue: 0.61, spread: 0.04,
    at(i, n, t, o) {
      const p = ((i / n + t * 0.03) % 1 + 1) % 1 * 7;
      const seg = Math.floor(p), f = p - seg;
      const r = 4 * (1 + 0.1 * Math.sin(t * 1.2));
      const a0 = (STAR[seg] / 7) * TAU + t * 0.12 - Math.PI / 2;
      const a1 = (STAR[(seg + 1) % 7] / 7) * TAU + t * 0.12 - Math.PI / 2;
      return o.set(lerp(Math.cos(a0), Math.cos(a1), f) * r, lerp(Math.sin(a0), Math.sin(a1), f) * r, 0);
    },
    guides() { return [curve((u, t, o) => this.at(u * this.n, this.n, t, o), 280)]; },
  },
  {
    // All twelve vertices, with the thirty edges as the outline
    name: "Icosahedron", n: 12, hue: 0.6, spread: 0.06,
    at(i, n, t, o) { return icoVertex(i, t, o); },
    guides() { return ICO_EDGES.map(([p, q]) => segment((t, o) => icoVertex(p, t, o), (t, o) => icoVertex(q, t, o))); },
  },
  {
    name: "Double Helix", n: 20, hue: 0.6, spread: 0.07, tilt: 0.3,
    at(i, n, t, o) { return helix(Math.floor(i / 2) / (n / 2 - 1), i % 2, t, o); },
    guides() {
      const strands = [0, 1].map((s) => curve((u, t, o) => helix(u, s, t, o), 200, false));
      const rungs = Array.from({ length: 10 }, (_, k) =>
        segment((t, o) => helix(k / 9, 0, t, o), (t, o) => helix(k / 9, 1, t, o)));
      return [...strands, ...rungs];
    },
  },
  {
    name: "Strange Attractor", n: LORENZ_COUNT, hue: 0.62, spread: 0.08, spin: 0.08,
    at(i, n, t, o) {
      const p = lorenz[i];
      return o.set(p.x, p.z - 25, p.y).multiplyScalar(0.17);
    },
    guides() {
      const last = LORENZ_PATH.length - 1;
      return [curve((u, t, o) => o.copy(LORENZ_PATH[Math.min(last, Math.round(u * last))]), LORENZ_PATH.length, false)];
    },
  },
];

// Display order (drives the counter, the dots and ?f=)
const ORDER = [
  "Browser Orbit", "Borromean Rings", "Torus Orbit", "Icosahedron", "Double Helix", "Strange Attractor",
  "Trefoil Knot", "Möbius Strip", "Klein Bottle", "Golden Spiral", "Lissajous", "Seven-Point Star",
];
export const FORMATIONS = ORDER.map((name) => ALL.find((f) => f.name === name));

// Formation frame to world: tilt flat shapes toward the camera, then spin
function toWorld(f, t, o) {
  if (f.tilt) o.applyAxisAngle(AX, f.tilt);
  if (f.spin) o.applyAxisAngle(AY, t * f.spin);
  return o;
}

const MAX = Math.max(...FORMATIONS.map((f) => f.n));

const ORB_VERT = /* glsl */ `
  attribute vec3 aColor;
  attribute float aSize;
  attribute float aAlpha;
  uniform float uScale;
  varying vec3 vColor;
  varying float vAlpha;
  void main() {
    vColor = aColor;
    vec4 mv = modelViewMatrix * vec4(position, 1.0);
    // Nearer orbs brighter, far ones dimmer, so depth reads
    vAlpha = aAlpha * clamp(1.0 - (-mv.z - 12.0) / 9.0, 0.45, 1.0);
    gl_Position = projectionMatrix * mv;
    gl_PointSize = min(aSize * uScale * (260.0 / -mv.z), 256.0);
    if (aAlpha <= 0.001) gl_PointSize = 0.0;
  }
`;

// The whole glow lives in the sprite, so it is perfectly round at any size
const ORB_FRAG = /* glsl */ `
  varying vec3 vColor;
  varying float vAlpha;
  void main() {
    vec2 p = gl_PointCoord - 0.5;
    float d = length(p) * 2.0;
    if (d > 1.0) discard;
    float edge = smoothstep(1.0, 0.6, d);
    float core = exp(-d * d * 220.0);
    float inner = exp(-d * d * 34.0);
    float halo = exp(-d * d * 7.0) * edge;
    vec3 col = vec3(1.0) * core * 1.5 + mix(vColor, vec3(1.0), 0.25) * inner * 0.55 + vColor * halo * 0.2;
    gl_FragColor = vec4(col * vAlpha, 1.0);
  }
`;

const BG_VERT = /* glsl */ `
  varying vec2 vUv;
  void main() { vUv = uv; gl_Position = vec4(position.xy, 1.0, 1.0); }
`;

const BG_FRAG = /* glsl */ `
  uniform float uTime;
  uniform float uAspect;
  uniform vec3 uDeep;
  uniform vec3 uMist;
  varying vec2 vUv;
  float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
  float noise(vec2 p) {
    vec2 i = floor(p), f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);
    return mix(mix(hash(i), hash(i + vec2(1, 0)), u.x), mix(hash(i + vec2(0, 1)), hash(i + vec2(1, 1)), u.x), u.y);
  }
  float fbm(vec2 p) {
    float v = 0.0, a = 0.5;
    for (int i = 0; i < 5; i++) { v += a * noise(p); p = p * 2.03 + 17.0; a *= 0.5; }
    return v;
  }
  void main() {
    vec2 p = (vUv - 0.5) * vec2(uAspect, 1.0);
    float t = uTime * 0.02;
    float n = fbm(p * 1.4 + vec2(t, t * 0.6));
    float m = fbm(p * 2.6 - vec2(t * 0.7, -t) + n * 1.5);
    vec3 col = uDeep;
    col += uMist * smoothstep(0.35, 0.95, m) * 0.55;
    col += uMist * 0.35 * exp(-dot(p, p) * 2.2);
    col *= 1.0 - 0.55 * smoothstep(0.35, 0.95, length(p));
    gl_FragColor = vec4(col, 1.0);
  }
`;

const easeInOutCubic = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);

export function createOrbs(canvas, options = {}) {
  const cfg = {
    trail: 44,          // trail samples per orb
    morphSeconds: 2.4,
    orbSize: 3.2,       // sprite size for a 7-orb formation; busier shapes get smaller orbs
    bloom: 0.55,
    maxPixelRatio: 2,
    start: 0,
    startTime: 0,
    lines: true,        // outlines on at load; click or tap the scene to toggle
    onChange: () => {},
    ...options,
  };

  let renderer;
  try {
    renderer = new THREE.WebGLRenderer({ canvas, antialias: false, powerPreference: "high-performance" });
  } catch (err) {
    canvas.dataset.orbs = "unsupported";
    return { go() {}, next() {}, prev() {}, toggleLines() {}, setLines() {}, destroy() {}, supported: false };
  }
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 200);

  // ---- Background haze ----
  const bgUniforms = {
    uTime: { value: 0 }, uAspect: { value: 1 },
    uDeep: { value: new THREE.Color("#01030d") }, uMist: { value: new THREE.Color("#12357f") },
  };
  const bg = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), new THREE.ShaderMaterial({
    uniforms: bgUniforms, vertexShader: BG_VERT, fragmentShader: BG_FRAG, depthWrite: false, depthTest: false,
  }));
  bg.frustumCulled = false;
  bg.renderOrder = -1;
  scene.add(bg);

  // ---- Orbs and trails share one point cloud: slot 0 of each orb is the head ----
  const T = cfg.trail;
  const total = MAX * T;
  const pos = new Float32Array(total * 3);
  const col = new Float32Array(total * 3);
  const size = new Float32Array(total);
  const alpha = new Float32Array(total);
  const geo = new THREE.BufferGeometry();
  const attr = (arr, n) => new THREE.BufferAttribute(arr, n).setUsage(THREE.DynamicDrawUsage);
  const aPos = attr(pos, 3), aCol = attr(col, 3), aSize = attr(size, 1), aAlpha = attr(alpha, 1);
  geo.setAttribute("position", aPos);
  geo.setAttribute("aColor", aCol);
  geo.setAttribute("aSize", aSize);
  geo.setAttribute("aAlpha", aAlpha);
  const orbUniforms = { uScale: { value: 1 } };
  const cloud = new THREE.Points(geo, new THREE.ShaderMaterial({
    uniforms: orbUniforms, vertexShader: ORB_VERT, fragmentShader: ORB_FRAG,
    transparent: true, depthWrite: false, depthTest: false, blending: THREE.AdditiveBlending,
  }));
  cloud.frustumCulled = false;
  scene.add(cloud);

  // Base trail fade per slot; scaled each frame by how far the orb actually moved
  const fade = Array.from({ length: T }, (_, k) => (k === 0 ? 1 : Math.pow(1 - k / (T - 1), 1.8) * 0.5));

  // History ring per orb, sampled at a fixed rate so trails look the same at any fps
  const history = Array.from({ length: MAX }, () => Array.from({ length: T }, () => new THREE.Vector3()));
  let head = 0;
  let sampleAcc = 0;
  const SAMPLE = 1 / 60;

  // ---- Dust ----
  const DUST = 700;
  const dPos = new Float32Array(DUST * 3);
  for (let i = 0; i < DUST; i++) {
    const r = 6 + Math.random() * 30, a = Math.random() * TAU, y = (Math.random() - 0.5) * 30;
    dPos.set([Math.cos(a) * r, y, Math.sin(a) * r], i * 3);
  }
  const dGeo = new THREE.BufferGeometry();
  dGeo.setAttribute("position", new THREE.BufferAttribute(dPos, 3));
  const dust = new THREE.Points(dGeo, new THREE.PointsMaterial({
    color: 0x6f9cff, size: 0.06, transparent: true, opacity: 0.55,
    blending: THREE.AdditiveBlending, depthWrite: false,
  }));
  scene.add(dust);

  // ---- Guide outlines: a faint line tracing the whole shape, crossfaded on morph ----
  const MAX_SEG = 4200;
  const GUIDE_OPACITY = 0.2;
  function makeGuide() {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(new Float32Array(MAX_SEG * 6), 3).setUsage(THREE.DynamicDrawUsage));
    g.setDrawRange(0, 0);
    const line = new THREE.LineSegments(g, new THREE.LineBasicMaterial({
      transparent: true, opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false, depthTest: false,
    }));
    line.frustumCulled = false;
    scene.add(line);
    return line;
  }
  const guideCur = makeGuide(), guidePrev = makeGuide();
  const gp = new THREE.Vector3(), gq = new THREE.Vector3();
  function buildGuide(line, f, opacity, reveal = 1) {
    line.visible = opacity > 0.001;
    if (!line.visible) return;
    f._guides ??= f.guides();
    const arr = line.geometry.attributes.position.array;
    let w = 0;
    for (const cv of f._guides) {
      const div = cv.closed ? cv.samples : cv.samples - 1;
      toWorld(f, t, cv.at(0, t, gp));
      const upto = Math.ceil(div * reveal);
      for (let k = 1; k <= upto && w < arr.length; k++) {
        toWorld(f, t, cv.at(k / div, t, gq));
        arr[w++] = gp.x; arr[w++] = gp.y; arr[w++] = gp.z;
        arr[w++] = gq.x; arr[w++] = gq.y; arr[w++] = gq.z;
        gp.copy(gq);
      }
    }
    line.geometry.setDrawRange(0, w / 3);
    line.geometry.attributes.position.needsUpdate = true;
    line.material.color.setHSL(f.hue, 0.8, 0.62);
    line.material.opacity = opacity;
  }

  // ---- Post ----
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(1, 1), cfg.bloom, 0, 0.3);
  // Keep only the fine bloom levels: the coarse ones upscale tiny bright dots into squares
  bloom.compositeMaterial.uniforms.bloomFactors.value = [1.0, 0.6, 0.22, 0.0, 0.0];
  composer.addPass(bloom);
  composer.addPass(new OutputPass());

  let dpr = Math.min(devicePixelRatio || 1, cfg.maxPixelRatio);
  function resize() {
    const w = Math.max(1, canvas.clientWidth), h = Math.max(1, canvas.clientHeight);
    renderer.setPixelRatio(dpr);
    renderer.setSize(w, h, false);
    composer.setPixelRatio(dpr);
    composer.setSize(w, h);
    camera.aspect = w / h;
    camera.fov = w / h < 1 ? 42 + (1 - w / h) * 34 : 42;
    camera.updateProjectionMatrix();
    bgUniforms.uAspect.value = w / h;
    orbUniforms.uScale.value = (h * dpr) / 900;
    if (!running) frame(0);
  }
  const ro = new ResizeObserver(resize);
  ro.observe(canvas);

  // ---- Pointer parallax ----
  const ndc = new THREE.Vector2(), parallax = new THREE.Vector2();
  const onMove = (e) => {
    const r = canvas.getBoundingClientRect();
    ndc.set(((e.clientX - r.left) / r.width) * 2 - 1, -((e.clientY - r.top) / r.height) * 2 + 1);
  };
  window.addEventListener("pointermove", onMove);

  // ---- Outline toggle (click or tap the scene) ----
  let linesOn = cfg.lines, linesLevel = linesOn ? 1 : 0, reveal = 1, flash = 0;
  function setLines(on) {
    if (on === linesOn) return;
    linesOn = on;
    if (on) { reveal = 0; flash = 1; }
  }
  let downAt = null;
  const onDown = (e) => { downAt = { x: e.clientX, y: e.clientY }; };
  const onUp = (e) => {
    // A tap, not a drag
    if (downAt && Math.hypot(e.clientX - downAt.x, e.clientY - downAt.y) < 10) setLines(!linesOn);
    downAt = null;
  };
  canvas.addEventListener("pointerdown", onDown);
  canvas.addEventListener("pointerup", onUp);

  // ---- Formation state ----
  const wrap = (i) => ((i % FORMATIONS.length) + FORMATIONS.length) % FORMATIONS.length;
  const palette = (f) => Array.from({ length: f.n }, (_, i) =>
    new THREE.Color().setHSL((f.hue + (i / Math.max(1, f.n - 1) - 0.5) * f.spread + 1) % 1, 0.85, 0.62));
  const sizeFor = (f) => cfg.orbSize * Math.max(0.55, Math.sqrt(7 / f.n));

  let cur = wrap(cfg.start);
  let prev = cur;
  let morph = 1;
  let palCur = palette(FORMATIONS[cur]);
  let palPrev = palCur;

  function go(index) {
    const next = wrap(index);
    if (next === cur && morph >= 1) return;
    prev = cur;
    palPrev = palCur;
    cur = next;
    palCur = palette(FORMATIONS[cur]);
    morph = 0;
    cfg.onChange(cur, FORMATIONS[cur]);
  }

  // ---- Loop ----
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const a = new THREE.Vector3(), b = new THREE.Vector3(), c = new THREE.Color();
  const heads = Array.from({ length: MAX }, () => new THREE.Vector3());
  const vis = new Float32Array(MAX);
  let t = 0, last = performance.now(), raf = 0, running = false, visible = true, onscreen = true;
  let primed = false;

  // Orbs beyond a formation's count ride on top of a visible orb, invisible, so
  // when the count changes they split off from (or merge into) a neighbor
  function place() {
    const e = easeInOutCubic(Math.min(1, morph));
    const fc = FORMATIONS[cur], fp = FORMATIONS[prev];
    for (let i = 0; i < MAX; i++) {
      toWorld(fc, t, fc.at(i % fc.n, fc.n, t, a));
      let v = i < fc.n ? 1 : 0;
      if (e < 1) {
        toWorld(fp, t, fp.at(i % fp.n, fp.n, t, b));
        // Arc outward mid-morph so the swap reads as flight, not a slide
        a.lerpVectors(b, a, e).multiplyScalar(1 + Math.sin(e * Math.PI) * 0.3);
        v = lerp(i < fp.n ? 1 : 0, v, e);
      }
      heads[i].copy(a);
      vis[i] = v;
    }
  }

  function frame(dt, draw = true) {
    t += dt;
    if (morph < 1) morph += dt / cfg.morphSeconds;

    stepLorenz(dt);
    place();

    // Fill the whole trail on the first frame so it does not streak in from the origin
    if (!primed) {
      for (let i = 0; i < MAX; i++) for (const v of history[i]) v.copy(heads[i]);
      primed = true;
    }
    sampleAcc += dt;
    while (sampleAcc >= SAMPLE) {
      sampleAcc -= SAMPLE;
      head = (head + 1) % T;
      for (let i = 0; i < MAX; i++) history[i][head].copy(heads[i]);
    }

    const e = easeInOutCubic(Math.min(1, morph));
    // Outline toggle: draws on with a bright glow when switched on, fades when off
    linesLevel += ((linesOn ? 1 : 0) - linesLevel) * Math.min(1, dt * (linesOn ? 6 : 3));
    if (linesOn) reveal = Math.min(1, reveal + dt / 0.9);
    flash *= Math.exp(-dt * 2.2);
    const glow = linesLevel * (GUIDE_OPACITY + flash * 0.6);
    buildGuide(guideCur, FORMATIONS[cur], glow * e, Math.min(reveal, e));
    buildGuide(guidePrev, FORMATIONS[prev], e < 1 ? glow * (1 - e) : 0);
    const orbSize = lerp(sizeFor(FORMATIONS[prev]), sizeFor(FORMATIONS[cur]), e);
    for (let i = 0; i < MAX; i++) {
      c.copy(palPrev[i % palPrev.length]).lerp(palCur[i % palCur.length], e);
      const pulse = 1 + 0.12 * Math.sin(t * 2.1 + i * 1.9);
      let prevV = heads[i];
      for (let k = 0; k < T; k++) {
        const slot = i * T + k;
        const v = k === 0 ? heads[i] : history[i][(head - k + T) % T];
        // Samples bunched on top of each other would stack into a blown-out blob
        const spread = k === 0 ? 1 : fade[k] * Math.min(1, v.distanceTo(prevV) / 0.09);
        alpha[slot] = spread * vis[i];
        prevV = v;
        pos[slot * 3] = v.x; pos[slot * 3 + 1] = v.y; pos[slot * 3 + 2] = v.z;
        col[slot * 3] = c.r; col[slot * 3 + 1] = c.g; col[slot * 3 + 2] = c.b;
        size[slot] = k === 0 ? orbSize * pulse : orbSize * 0.4 * (1 - k / T) + 0.1;
      }
    }
    aPos.needsUpdate = aCol.needsUpdate = aSize.needsUpdate = aAlpha.needsUpdate = true;

    // Camera: a gentle sway (never a full orbit, so flat shapes never go edge-on)
    parallax.lerp(ndc, Math.min(1, dt * 2 || 1));
    const ang = Math.sin(t * 0.07) * 0.3 + parallax.x * 0.35;
    const r = 15;
    camera.position.set(Math.sin(ang) * r, 1.5 + parallax.y * 2.2 + Math.sin(t * 0.13) * 0.8, Math.cos(ang) * r);
    camera.lookAt(0, -0.7, 0);
    dust.rotation.y = t * 0.01;

    bgUniforms.uTime.value = t;
    if (draw) composer.render();
  }

  function loop(now) {
    raf = requestAnimationFrame(loop);
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    frame(dt);
  }

  function setRunning() {
    const should = !reduced && visible && onscreen;
    if (should && !running) { running = true; last = performance.now(); raf = requestAnimationFrame(loop); }
    else if (!should && running) { running = false; cancelAnimationFrame(raf); }
  }
  const io = new IntersectionObserver(([en]) => { onscreen = en.isIntersecting; setRunning(); });
  io.observe(canvas);
  const onVis = () => { visible = document.visibilityState === "visible"; setRunning(); };
  document.addEventListener("visibilitychange", onVis);

  // Optional jump ahead (used for testing and screenshots)
  if (cfg.startTime) { for (let s = 0; s < cfg.startTime; s += 1 / 30) frame(1 / 30, false); }
  resize();
  setRunning();
  canvas.dataset.orbs = "ready";
  cfg.onChange(cur, FORMATIONS[cur]);

  return {
    supported: true,
    go,
    next: () => go(cur + 1),
    toggleLines: () => setLines(!linesOn),
    setLines,
    prev: () => go(cur - 1),
    get index() { return cur; },
    destroy() {
      running = false;
      cancelAnimationFrame(raf);
      ro.disconnect(); io.disconnect();
      document.removeEventListener("visibilitychange", onVis);
      window.removeEventListener("pointermove", onMove);
      canvas.removeEventListener("pointerdown", onDown);
      canvas.removeEventListener("pointerup", onUp);
      scene.traverse((o) => { o.geometry?.dispose(); o.material?.dispose(); });
      renderer.dispose();
    },
  };
}
