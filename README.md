# RIPPS2

A PS2-inspired front end, starting life as a web theme. This first beta is the browser version: glowing data-tower pillars and flying light orbs behind a floating three-way menu. The same look is headed for a custom OPL theme bundled into a single `RIPPS2.elf` for real hardware.

**Live demo:** https://akilluminati47.github.io/RIPPS2/

> Status: **beta 0.0.0.1** (web version). The ELF build is in progress.

## The menu

| Option | Opens |
| --- | --- |
| **Launch Disc** | The pillars, with a double blast fired into the centre of the field |
| **Storage** | The pillars |
| **Memory Files** | The orbs |

The PS2 mark rides under the selected option and flies between them: a swoop to a neighbour, a deeper dive with a coin flip when going end to end. Labels follow the visitor's system language (18 languages, override with `?lang=fr` and similar). Anything the menu font cannot draw falls back to a clean sans as a whole word.

## Pillars

- Glass data towers with glowing edges, seams, flickering cells and energy pulses, on a reflective floor
- Towers rise out of the ground on load, then breathe and ripple
- Light beams, drifting motes, bloom, grain and a subtle lens finish
- Moving the pointer (or swiping) sends ripples; clicking sets off a big area blast
- Adapts resolution on slow devices, pauses off screen, respects reduced motion

## Orbs

- Twelve formations: Browser Orbit, Borromean Rings, Torus Orbit, Icosahedron, Double Helix, Strange Attractor (a live Lorenz system), Trefoil Knot, Möbius Strip, Klein Bottle, Golden Spiral, Lissajous and Seven-Point Star
- Each formation uses as many orbs as it needs to read clearly, splitting and merging between formations
- Faint outlines trace every shape; tap or click the scene (or press `L`, or controller A) to toggle them
- Arrow bubbles lean toward the pointer, ripple on press and fill a progress ring while swiping
- Switch with the arrows, the dots, a swipe, the arrow keys, or a controller's d-pad or bumpers

## Run it locally

ES modules need a web server (opening the file directly will not work):

```bash
python -m http.server 8000
```

Then open http://localhost:8000. Everything is bundled, so it works offline. Add `?t=12` to skip the pillars intro, or `orbs.html?f=3` to open a specific formation.

## Credits

- [three.js](https://threejs.org) r160, MIT (see `vendor/LICENSE`)
- [Albert Sans](https://github.com/usted/Albert-Sans), SIL Open Font License (see `vendor/fonts/OFL.txt`)
- Planet N Compact by [Iconian Fonts](https://www.iconian.com) (`assets/master.ttf`)

Unofficial fan project. PlayStation, PS2 and the PS2 logo are trademarks of Sony Interactive Entertainment. This project is not affiliated with or endorsed by Sony.
