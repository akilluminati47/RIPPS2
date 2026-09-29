// Living arrow buttons: exact SVG geometry (ring, 12 ticks, a true 90 degree chevron,
// an orbiting dot), spring physics toward the pointer, ripples on press, and a
// progress arc that fills while swiping.
//
// Usage:
//   const arrows = createArrows({ prev: btnEl, next: btnEl });
//   arrows.press(1);       // play the press animation on next (-1 for prev)
//   arrows.pull(-1, 0.6);  // swipe progress 0..1 toward prev, 0 to release

const NS = "http://www.w3.org/2000/svg";
const R = 19;           // ring radius in SVG units (viewBox is 48 wide)
const TICK_R = 22.5;    // tick ring radius
const TICKS = 12;

// One button, drawn pointing +x; prev is the exact mirror image
function build(btn, dir) {
  btn.innerHTML = "";
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("viewBox", "-24 -24 48 48");
  svg.setAttribute("aria-hidden", "true");
  const g = document.createElementNS(NS, "g");
  if (dir < 0) g.setAttribute("transform", "scale(-1 1)");
  svg.append(g);

  const el = (tag, attrs) => {
    const e = document.createElementNS(NS, tag);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    g.append(e);
    return e;
  };
  const ring = el("circle", { class: "ring", r: R });
  // pathLength normalises the circumference, so 12 dashes land exactly 30 degrees apart
  const ticks = el("circle", { class: "ticks", r: TICK_R, pathLength: TICKS * 10, "stroke-dasharray": "0.9 9.1" });
  const progress = el("circle", { class: "progress", r: R, pathLength: 100, "stroke-dasharray": "0 100", transform: "rotate(-90)" });
  const orbit = el("g", {});
  const dot = document.createElementNS(NS, "circle");
  dot.setAttribute("class", "dot");
  dot.setAttribute("cx", 0);
  dot.setAttribute("cy", -R);
  dot.setAttribute("r", 1.7);
  orbit.append(dot);
  const chev = el("path", { class: "chev", d: "M -3.5 -7 L 3.5 0 L -3.5 7" });
  const ripples = [el("circle", { class: "ripple", r: R }), el("circle", { class: "ripple", r: R })];
  btn.append(svg);

  return {
    btn, dir, ring, ticks, progress, orbit, chev, ripples,
    x: 0, y: 0, vx: 0, vy: 0,   // magnetic offset (px)
    s: 1, vs: 0,                // scale
    ang: -90, omega: 40, kick: 0, // orbit dot angle and speed (degrees)
    nudge: 0, vn: 0,            // chevron push (SVG units)
    pull: 0,                    // swipe progress 0..1
  };
}

export function createArrows({ prev, next }) {
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const items = [build(prev, -1), build(next, 1)];
  const byDir = (d) => (d < 0 ? items[0] : items[1]);

  const pointer = { x: -1e4, y: -1e4 };
  const onMove = (e) => { pointer.x = e.clientX; pointer.y = e.clientY; };
  // A finger lifting should not leave a phantom hover behind
  const onUp = (e) => { if (e.pointerType !== "mouse") { pointer.x = -1e4; pointer.y = -1e4; } };
  addEventListener("pointermove", onMove, { passive: true });
  addEventListener("pointerdown", onMove, { passive: true });
  addEventListener("pointerup", onUp, { passive: true });
  addEventListener("pointercancel", onUp, { passive: true });

  function press(d) {
    const it = byDir(d);
    it.kick += 720;      // one fast extra lap for the orbit dot
    it.vs -= 0.09;       // squash, then spring back
    it.vn += 2.2;        // chevron punches forward
    it.ripples.forEach((r, k) => r.animate(
      [{ transform: "scale(1)", opacity: 0.75 }, { transform: "scale(1.75)", opacity: 0 }],
      { duration: 700, delay: k * 110, easing: "cubic-bezier(.16,.7,.3,1)" },
    ));
  }

  function pull(d, amount) {
    for (const it of items) it.pull = it.dir === d ? Math.max(0, Math.min(1, amount)) : 0;
  }

  let last = performance.now();
  let raf = 0;
  function tick(now) {
    raf = requestAnimationFrame(tick);
    const dt = Math.min(0.05, (now - last) / 1000);
    last = now;

    for (const it of items) {
      // Center of the button's resting spot (undo the current offset)
      const r = it.btn.getBoundingClientRect();
      const cx = r.left + r.width / 2 - it.x, cy = r.top + r.height / 2 - it.y;
      const dx = pointer.x - cx, dy = pointer.y - cy;
      const near = reduced ? 0 : Math.max(0, 1 - Math.hypot(dx, dy) / 120);
      const ease = near * near * (3 - 2 * near);   // smoothstep

      // Magnetic lean toward the pointer, plus a lean along the swipe
      const lim = 7;
      const tx = Math.max(-lim, Math.min(lim, dx * 0.2 * ease)) + it.dir * it.pull * 6;
      const ty = Math.max(-lim, Math.min(lim, dy * 0.2 * ease));

      // Critically-ish damped springs, frame rate independent
      const k = 1 - Math.exp(-dt * 26), damp = Math.exp(-dt * 9);
      it.vx = (it.vx + (tx - it.x) * k) * damp; it.x += it.vx;
      it.vy = (it.vy + (ty - it.y) * k) * damp; it.y += it.vy;
      const ts = 1 + 0.1 * ease + 0.12 * it.pull;
      it.vs = (it.vs + (ts - it.s) * k) * damp; it.s += it.vs;
      it.vn = (it.vn + (ease * 1.2 + it.pull * 3 - it.nudge) * k) * damp; it.nudge += it.vn;

      // Orbit dot: idles, quickens near the pointer and while swiping, whips on press
      const target = reduced ? 0 : 40 + 260 * ease + 420 * it.pull;
      it.omega += (target - it.omega) * Math.min(1, dt * 4);
      it.kick *= Math.exp(-dt * 3.2);
      it.ang = (it.ang + (it.omega + it.kick * 3.2) * dt) % 360;

      it.btn.style.transform = `translate(${it.x.toFixed(2)}px, ${it.y.toFixed(2)}px) scale(${it.s.toFixed(4)})`;
      it.orbit.setAttribute("transform", `rotate(${(it.ang + 90).toFixed(2)})`);
      it.ticks.setAttribute("transform", `rotate(${(-it.ang * 0.2).toFixed(2)})`);
      it.chev.setAttribute("transform", `translate(${it.nudge.toFixed(3)} 0)`);
      it.progress.setAttribute("stroke-dasharray", `${(it.pull * 100).toFixed(2)} 100`);
      it.btn.classList.toggle("hot", ease > 0.35 || it.pull > 0.05);
      it.btn.style.setProperty("--glow-k", (ease * 0.8 + it.pull).toFixed(3));
    }
  }
  raf = requestAnimationFrame(tick);

  return {
    press,
    pull,
    destroy() {
      cancelAnimationFrame(raf);
      removeEventListener("pointermove", onMove);
      removeEventListener("pointerdown", onMove);
      removeEventListener("pointerup", onUp);
      removeEventListener("pointercancel", onUp);
    },
  };
}
