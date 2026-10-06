// Top menu behavior shared by both pages.
// Launch Disc and Storage show the pillars page; Memory Files opens the orbs page. The site lands on
// Storage (its elf shelf); #launch-disc opens Launch Disc. onSelect hears every change of tab on the page.
// Selecting Launch Disc sparks the pillars (onLaunch), right away if we are already
// there, or on arrival after navigating over from the orbs page.
// Labels follow the visitor's language (override with ?lang=xx).
// The PS2 mark (assets/logo.png) rides under the selected label and flies between them.

const KEY = "ps2-menu";
const ORDER = ["launch", "storage", "memory"];

// [Launch Disc, Storage, Memory Files]
const LABELS = {
  en: ["Launch Disc", "Storage", "Memory Files"],
  es: ["Iniciar disco", "Almacenamiento", "Archivos de memoria"],
  fr: ["Lancer le disque", "Stockage", "Fichiers mémoire"],
  de: ["Disc starten", "Speicher", "Speicherdateien"],
  it: ["Avvia disco", "Archiviazione", "File di memoria"],
  pt: ["Iniciar disco", "Armazenamento", "Arquivos de memória"],
  nl: ["Disc starten", "Opslag", "Geheugenbestanden"],
  sv: ["Starta skiva", "Lagring", "Minnesfiler"],
  da: ["Start disk", "Lagring", "Hukommelsesfiler"],
  no: ["Start plate", "Lagring", "Minnefiler"],
  fi: ["Käynnistä levy", "Tallennustila", "Muistitiedostot"],
  pl: ["Uruchom płytę", "Pamięć", "Pliki pamięci"],
  tr: ["Diski başlat", "Depolama", "Bellek dosyaları"],
  ru: ["Запуск диска", "Хранилище", "Файлы памяти"],
  ja: ["ディスク起動", "ストレージ", "メモリーファイル"],
  ko: ["디스크 실행", "저장소", "메모리 파일"],
  zh: ["启动光盘", "存储", "记忆文件"],
  "zh-tw": ["啟動光碟", "儲存空間", "記憶檔案"],
};
const ALIASES = { nb: "no", nn: "no" };

// Characters the site font can draw (Basic Latin + Latin-1)
const IN_FONT = /^[ -~ -ÿ]*$/;

// Label float: each word drifts on its own phase (seconds into a 6.4 s cycle)
const FLOAT_PERIOD = 6.4, FLOAT_AMP = 4, PHASES = [0, -2.1, -4.3];

function pickLanguage() {
  const forced = new URLSearchParams(location.search).get("lang");
  const wanted = forced ? [forced] : navigator.languages?.length ? navigator.languages : [navigator.language || "en"];
  for (const tag of wanted) {
    const low = tag.toLowerCase();
    const base = ALIASES[low.split("-")[0]] || low.split("-")[0];
    if (base === "zh") return /-(tw|hk|mo|hant)/.test(low) ? "zh-tw" : "zh";
    if (LABELS[base]) return base;
  }
  return "en";
}

const clamp01 = (x) => Math.min(1, Math.max(0, x));
const lerp = (a, b, t) => a + (b - a) * t;
const easeInOutCubic = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);

export function initMenu({ onLaunch, onSelect } = {}) {
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const onPillars = !location.pathname.endsWith("orbs.html");
  const nav = document.querySelector(".options");
  const items = ORDER.map((name) => nav.querySelector(`[data-item="${name}"]`));
  const labels = items.map((el) => el.querySelector(".label"));

  // Localize, and hand whole labels the font cannot draw to the fallback font
  const lang = pickLanguage();
  document.documentElement.lang = lang;
  labels.forEach((label, k) => {
    const text = LABELS[lang][k];
    label.textContent = text;
    label.classList.toggle("fb", !IN_FONT.test(text.toLocaleUpperCase(lang)));
  });

  const currentFromPage = () => ORDER.indexOf(!onPillars ? "memory" : location.hash === "#launch-disc" ? "launch" : "storage");
  function mark(idx) {
    items.forEach((el, k) => (k === idx ? el.setAttribute("aria-current", "page") : el.removeAttribute("aria-current")));
  }

  // ---- Selector mark ----
  const makeMark = (cls) => {
    const img = document.createElement("img");
    img.src = "assets/logo.png";
    img.alt = "";
    img.className = cls;
    img.setAttribute("aria-hidden", "true");
    nav.append(img);
    return img;
  };
  const ghosts = [makeMark("selector ghost"), makeMark("selector ghost"), makeMark("selector ghost")];
  const selector = makeMark("selector");
  let hasMark = true;
  selector.addEventListener("error", () => { hasMark = false; selector.remove(); ghosts.forEach((g) => g.remove()); });

  let cur = currentFromPage();
  let flight = null;              // { t0, dur, from: {x, y}, to, hops, dir }
  let landAt = -1;                // time of the last landing (for the squash spring)
  let last = null;                // last rendered { x, y }
  const trailHistory = [];        // recent transforms, for the afterimages

  // Where the mark sits under label idx (nav-relative px), following its float
  function anchor(idx) {
    const n = nav.getBoundingClientRect(), r = labels[idx].getBoundingClientRect();
    const em = parseFloat(getComputedStyle(nav).fontSize);
    return { x: r.left + r.width / 2 - n.left, y: r.bottom - n.top + em * 0.2 };
  }

  function flyTo(idx) {
    if (idx === cur && !flight) return 0;
    const from = last || anchor(cur);
    const hops = Math.max(1, Math.abs(idx - cur));
    const dur = reduced ? 0 : 520 + 230 * hops;
    flight = dur ? { t0: performance.now(), dur, from: { ...from }, to: idx, hops, dir: Math.sign(idx - cur) || 1 } : null;
    cur = idx;
    mark(idx);
    return dur;
  }

  function frame() {
    requestAnimationFrame(frame);
    // One clock for everything: flights are started with performance.now() too
    const now = performance.now();
    const t = now / 1000;

    // Floats first, so the anchors below read the floated positions
    labels.forEach((label, k) => {
      const f = reduced ? 0 : -FLOAT_AMP * (0.5 - 0.5 * Math.cos((2 * Math.PI * (t + PHASES[k])) / FLOAT_PERIOD));
      label.style.transform = `translateY(${f.toFixed(2)}px)`;
    });
    if (!hasMark) return;

    const em = parseFloat(getComputedStyle(nav).fontSize);
    const w = selector.offsetWidth;
    let x, y, sx = 1, sy = 1, lean = 0, flip = 0, trail = 0;

    if (flight) {
      const p = clamp01((now - flight.t0) / flight.dur);
      const e = easeInOutCubic(p);
      const to = anchor(flight.to);
      const arc = Math.sin(Math.PI * e);
      // Swoop down and across; end to end dives deeper and coin-flips
      x = lerp(flight.from.x, to.x, e);
      y = lerp(flight.from.y, to.y, e) + arc * em * (0.55 + 0.45 * flight.hops);
      const s = Math.sin(Math.PI * p);
      sx = 1 + 0.32 * s;
      sy = 1 - 0.16 * s;
      lean = flight.dir * 9 * Math.sin(2 * Math.PI * p) * (1 - p);
      flip = flight.hops >= 2 ? 360 * e * flight.dir : 0;
      trail = s;
      if (p >= 1) {
        flight = null;
        landAt = now;
        labels[cur].animate(
          [{ filter: "brightness(2.2)" }, { filter: "brightness(1)" }],
          { duration: 520, easing: "cubic-bezier(.2,.7,.3,1)" },
        );
      }
    } else {
      ({ x, y } = anchor(cur));
    }

    // Landing squash: a damped spring
    if (landAt >= 0) {
      const tt = (now - landAt) / 1000;
      const a = 0.24 * Math.exp(-7 * tt) * Math.cos(19 * tt);
      sx *= 1 + a;
      sy *= 1 - a;
      if (tt > 0.9) landAt = -1;
    }

    last = { x, y };
    const tf = `translate(${(x - w / 2).toFixed(2)}px, ${y.toFixed(2)}px) perspective(${(em * 30).toFixed(0)}px) ` +
      `rotate(${lean.toFixed(2)}deg) rotateY(${flip.toFixed(1)}deg) scale(${sx.toFixed(3)}, ${sy.toFixed(3)})`;
    selector.style.transform = tf;

    // Afterimages trail a few frames behind while flying
    trailHistory.unshift(tf);
    trailHistory.length = 10;
    ghosts.forEach((g, k) => {
      const back = trailHistory[(k + 1) * 3];
      g.style.transform = back || tf;
      g.style.opacity = (trail * [0.42, 0.24, 0.12][k]).toFixed(3);
    });
  }

  // ---- Clicks ----
  items.forEach((el, idx) => {
    el.addEventListener("click", (e) => {
      const name = ORDER[idx];
      const samePage = onPillars && name !== "memory";
      e.preventDefault();
      if (samePage) {
        history.replaceState(null, "", name === "storage" ? "#storage" : "#launch-disc");
        flyTo(idx);
        onSelect?.(name);
        if (name === "launch") onLaunch?.();
      } else {
        // Crossing pages: let the mark land first, then tell the next page how we arrived
        try { sessionStorage.setItem(KEY, name); } catch {}
        const wait = hasMark ? flyTo(idx) : 0;
        setTimeout(() => { location.href = el.href; }, wait ? wait + 90 : 0);
      }
    });
  });

  mark(cur);
  // Arriving from the other page: the mark drops into place
  let arrived = null;
  try { arrived = sessionStorage.getItem(KEY); sessionStorage.removeItem(KEY); } catch {}
  if (arrived && !reduced) landAt = performance.now();
  requestAnimationFrame(frame);

  return { arrived, lang, current: ORDER[cur] };
}
