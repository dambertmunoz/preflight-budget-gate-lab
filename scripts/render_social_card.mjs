import { promises as fs } from "node:fs";
import path from "node:path";

let sharp;
try {
  sharp = (await import("sharp")).default;
} catch {
  sharp = (await import("/Users/dambert.munoz/Documents/Gridam/wasicode/node_modules/sharp/lib/index.js")).default;
}

const OUT = path.resolve("assets");
const SIZE = 1080;

const esc = (value) =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");

function cardChrome({ x, y, w, h, r = 34, opacity = 0.72 }) {
  return `
    <rect x="${x}" y="${y + 20}" width="${w}" height="${h}" rx="${r}" fill="#020617" opacity="0.34" filter="url(#blur24)"/>
    <rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="rgba(5,10,31,${opacity})" stroke="rgba(255,255,255,0.16)" stroke-width="1.4"/>
    <path d="M ${x + r} ${y + 1} H ${x + w - r}" stroke="rgba(255,255,255,0.34)" stroke-width="1.6"/>
  `;
}

function renderSvg() {
  return `<svg width="${SIZE}" height="${SIZE}" viewBox="0 0 ${SIZE} ${SIZE}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#07111f"/>
      <stop offset="0.42" stop-color="#172554"/>
      <stop offset="0.72" stop-color="#3b1d68"/>
      <stop offset="1" stop-color="#0f172a"/>
    </linearGradient>
    <radialGradient id="cyanGlow" cx="22%" cy="16%" r="70%">
      <stop offset="0" stop-color="#68e1fd" stop-opacity="0.48"/>
      <stop offset="0.56" stop-color="#68e1fd" stop-opacity="0.08"/>
      <stop offset="1" stop-color="#68e1fd" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="violetGlow" cx="80%" cy="38%" r="65%">
      <stop offset="0" stop-color="#a78bfa" stop-opacity="0.48"/>
      <stop offset="0.56" stop-color="#a78bfa" stop-opacity="0.1"/>
      <stop offset="1" stop-color="#a78bfa" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="amberGlow" cx="86%" cy="84%" r="56%">
      <stop offset="0" stop-color="#ffb86c" stop-opacity="0.38"/>
      <stop offset="0.58" stop-color="#ffb86c" stop-opacity="0.08"/>
      <stop offset="1" stop-color="#ffb86c" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="brandGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#68e1fd"/>
      <stop offset="0.55" stop-color="#a78bfa"/>
      <stop offset="1" stop-color="#ffb86c"/>
    </linearGradient>
    <linearGradient id="mintGrad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#8fffcd"/>
      <stop offset="1" stop-color="#68e1fd"/>
    </linearGradient>
    <filter id="blur24" x="-35%" y="-35%" width="170%" height="170%">
      <feGaussianBlur stdDeviation="24"/>
    </filter>
    <filter id="softShadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="24" stdDeviation="24" flood-color="#000820" flood-opacity="0.35"/>
    </filter>
    <filter id="glow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="8" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <style>
      .display { font-family: "Arial", "Helvetica", sans-serif; font-weight: 800; letter-spacing: -2px; }
      .label { font-family: "Arial", "Helvetica", sans-serif; font-weight: 700; letter-spacing: 0; }
      .body { font-family: "Arial", "Helvetica", sans-serif; font-weight: 500; letter-spacing: 0; }
      .mono { font-family: "Menlo", "SFMono-Regular", "Consolas", monospace; font-weight: 700; }
    </style>
  </defs>

  <rect width="${SIZE}" height="${SIZE}" fill="url(#bg)"/>
  <rect width="${SIZE}" height="${SIZE}" fill="url(#cyanGlow)"/>
  <rect width="${SIZE}" height="${SIZE}" fill="url(#violetGlow)"/>
  <rect width="${SIZE}" height="${SIZE}" fill="url(#amberGlow)"/>

  <path d="M 632 98 C 850 132 992 286 1002 506 C 1018 786 816 930 592 856 C 458 812 458 650 486 464 C 514 278 492 146 632 98 Z" fill="rgba(255,255,255,0.07)" stroke="rgba(255,255,255,0.09)"/>
  <path d="M 688 166 C 812 184 904 296 898 426 C 888 586 734 632 626 558 C 518 484 548 328 602 240 C 626 202 652 172 688 166 Z" fill="rgba(255,255,255,0.045)"/>

  <g opacity="0.24">
    ${Array.from({ length: 80 }, (_, i) => {
      const x = (i * 137) % 1040 + 20;
      const y = (i * 223) % 1040 + 20;
      const r = i % 7 === 0 ? 1.6 : 0.9;
      return `<circle cx="${x}" cy="${y}" r="${r}" fill="#ffffff" opacity="${i % 5 === 0 ? 0.5 : 0.25}"/>`;
    }).join("")}
  </g>

  <g>
    <rect x="72" y="64" width="222" height="50" rx="25" fill="rgba(5,10,31,0.58)" stroke="rgba(255,255,255,0.18)"/>
    <circle cx="96" cy="89" r="10" fill="#68e1fd"/>
    <text x="124" y="97" class="label" font-size="22" fill="#ffffff">Dambert Lab</text>

    <text x="72" y="176" class="label" font-size="28" fill="#68e1fd">Agentic AI Architecture</text>
    <text x="72" y="288" class="display" font-size="74" fill="#ffffff">Your agent</text>
    <text x="72" y="368" class="display" font-size="74" fill="#ffffff">spends before</text>
    <text x="72" y="448" class="display" font-size="74" fill="#ffffff">it thinks</text>

    <text x="74" y="534" class="label" font-size="27" fill="#ffffff">Preflight admission control</text>
    <text x="74" y="575" class="body" font-size="27" fill="#dbeafe">before tool side effects.</text>

    <g transform="translate(72 864)">
      ${["Intent", "Policy", "Reserve", "Audit"].map((label, i) => {
        const colors = ["#68e1fd", "#a78bfa", "#8fffcd", "#ffb86c"];
        return `<rect x="${i * 105}" y="0" width="88" height="42" rx="21" fill="rgba(5,10,31,0.56)" stroke="${colors[i]}" stroke-opacity="0.58"/>
        <text x="${i * 105 + 44}" y="27" text-anchor="middle" class="label" font-size="16" fill="#ffffff">${label}</text>`;
      }).join("")}
    </g>

    <rect x="72" y="952" width="252" height="58" rx="29" fill="#ffffff"/>
    <text x="198" y="988" text-anchor="middle" class="label" font-size="23" fill="#0f172a">View repo</text>
    <text x="804" y="984" text-anchor="middle" class="body" font-size="20" fill="rgba(255,255,255,0.78)">dambertmunoz.com</text>
    <text x="804" y="1014" text-anchor="middle" class="body" font-size="16" fill="rgba(255,255,255,0.56)">linkedin.com/in/dambert-m-4b772397</text>
  </g>

  <g filter="url(#softShadow)">
    ${cardChrome({ x: 614, y: 156, w: 358, h: 210, r: 34, opacity: 0.54 })}
    <rect x="648" y="190" width="134" height="20" rx="10" fill="#68e1fd" opacity="0.95"/>
    <rect x="648" y="246" width="22" height="72" rx="11" fill="#a78bfa" opacity="0.72"/>
    <rect x="690" y="218" width="22" height="100" rx="11" fill="#68e1fd" opacity="0.76"/>
    <rect x="732" y="258" width="22" height="60" rx="11" fill="#a78bfa" opacity="0.68"/>
    <rect x="774" y="202" width="22" height="116" rx="11" fill="#8fffcd" opacity="0.7"/>
    <path d="M 826 300 C 858 260 880 282 910 226" fill="none" stroke="#68e1fd" stroke-width="6" stroke-linecap="round" opacity="0.78"/>

    ${cardChrome({ x: 548, y: 442, w: 470, h: 332, r: 40, opacity: 0.78 })}
    <text x="592" y="504" class="label" font-size="18" fill="#68e1fd">ADMISSION CONTROL</text>
    <text x="592" y="556" class="display" font-size="34" fill="#ffffff" letter-spacing="-0.4">No side effect before</text>
    <text x="592" y="598" class="display" font-size="34" fill="#ffffff" letter-spacing="-0.4">policy + reservation</text>

    <g transform="translate(592 650)">
      <rect x="0" y="0" width="88" height="50" rx="18" fill="rgba(5,10,31,0.72)" stroke="#68e1fd" stroke-opacity="0.85"/>
      <circle cx="19" cy="25" r="7" fill="#68e1fd"/>
      <text x="51" y="31" text-anchor="middle" class="label" font-size="14" fill="#ffffff">Intent</text>
      <path d="M 88 25 H 126" stroke="#a78bfa" stroke-width="4" opacity="0.65"/>

      <rect x="126" y="0" width="88" height="50" rx="18" fill="rgba(5,10,31,0.72)" stroke="#a78bfa" stroke-opacity="0.85"/>
      <circle cx="145" cy="25" r="7" fill="#a78bfa"/>
      <text x="177" y="31" text-anchor="middle" class="label" font-size="14" fill="#ffffff">Policy</text>
      <path d="M 214 25 H 252" stroke="#8fffcd" stroke-width="4" opacity="0.65"/>

      <rect x="252" y="0" width="92" height="50" rx="18" fill="rgba(5,10,31,0.72)" stroke="#8fffcd" stroke-opacity="0.85"/>
      <circle cx="271" cy="25" r="7" fill="#8fffcd"/>
      <text x="306" y="31" text-anchor="middle" class="label" font-size="14" fill="#ffffff">Reserve</text>
      <path d="M 344 25 H 382" stroke="#68e1fd" stroke-width="4" opacity="0.65"/>

      <rect x="382" y="-10" width="58" height="70" rx="20" fill="rgba(5,10,31,0.82)" stroke="#68e1fd" stroke-opacity="0.96"/>
      <path d="M 397 24 L 412 39 L 431 15" fill="none" stroke="#68e1fd" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
    </g>

    <rect x="594" y="724" width="166" height="44" rx="22" fill="#a78bfa" opacity="0.92"/>
    <text x="677" y="753" text-anchor="middle" class="label" font-size="17" fill="#ffffff">manual_review</text>
    <rect x="780" y="724" width="158" height="44" rx="22" fill="#ffb86c" opacity="0.94"/>
    <text x="859" y="753" text-anchor="middle" class="label" font-size="17" fill="#ffffff">no tool call</text>

    ${cardChrome({ x: 646, y: 808, w: 318, h: 86, r: 26, opacity: 0.58 })}
    <text x="680" y="844" class="mono" font-size="19" fill="#dbeafe">audit_event</text>
    <rect x="840" y="828" width="92" height="30" rx="15" fill="url(#mintGrad)"/>
    <rect x="680" y="864" width="96" height="14" rx="7" fill="#68e1fd" opacity="0.9"/>
    <rect x="794" y="864" width="134" height="14" rx="7" fill="#a78bfa" opacity="0.9"/>
  </g>
</svg>`;
}

await fs.mkdir(OUT, { recursive: true });
const svg = renderSvg();
const svgPath = path.join(OUT, "preflight-budget-gate-social-card.svg");
const pngPath = path.join(OUT, "preflight-budget-gate-social-card.png");
await fs.writeFile(svgPath, svg, "utf8");
await sharp(Buffer.from(svg)).png({ quality: 96, compressionLevel: 9 }).toFile(pngPath);
console.log(pngPath);
