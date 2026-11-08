// CayRus — aplikasi hafalan kosakata Rusia–Indonesia (PWA, tanpa backend).
const APP_VERSION = "1.1.0";
const view = document.getElementById("view");
const S = { words: [], verbs: null, grammar: null, questions: [], w: {}, v: {}, p: {}, cards: new Map(), dict: null, cleanup: null };

// ---------- utilitas ----------
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const norm = (s) => String(s || "").normalize("NFD").replace(/́/g, "").normalize("NFC").toLowerCase().replace(/ё/g, "е").trim();
const today = () => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`; };
const addDays = (iso, n) => { const [y, m, d] = iso.split("-").map(Number); const t = new Date(y, m - 1, d + n); return `${t.getFullYear()}-${String(t.getMonth() + 1).padStart(2, "0")}-${String(t.getDate()).padStart(2, "0")}`; };
const shuffle = (a) => { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };
const first = (form) => String(form || "").split(",")[0].trim();

const POS = { noun: "kata benda", verb: "kata kerja", adj: "kata sifat", adv: "adverbia", prep: "preposisi", conj: "konjungsi",
  part: "partikel", pron: "kata ganti", num: "bilangan", intj: "interjeksi", pred: "predikatif", other: "lainnya" };
const GENDER = { m: "maskulin (м)", f: "feminin (ж)", n: "netral (ср)", pl: "hanya jamak" };
const CASES = [
  ["nom", "Имени́тельный", "кто? что?"], ["gen", "Роди́тельный", "кого́? чего́?"], ["dat", "Да́тельный", "кому́? чему́?"],
  ["acc", "Вини́тельный", "кого́? что?"], ["ins", "Твори́тельный", "кем? чем?"], ["pre", "Предло́жный", "о ком? о чём?"],
];
const CASE_ID = { nom: "Nominatif", gen: "Genitif", dat: "Datif", acc: "Akusatif", ins: "Instrumental", pre: "Preposisional" };
const PERSONS = [["1sg", "я"], ["2sg", "ты"], ["3sg", "он/она́/оно́"], ["1pl", "мы"], ["2pl", "вы"], ["3pl", "они́"]];
const PAST = [["m", "он (м)"], ["f", "она́ (ж)"], ["n", "оно́ (ср)"], ["pl", "они́ (мн)"]];
const IMP = [["sg", "ты"], ["pl", "вы"]];
const BUDU = ["бу́ду", "бу́дешь", "бу́дет", "бу́дем", "бу́дете", "бу́дут"];
const INTERVAL = { 1: 0, 2: 1, 3: 3, 4: 7, 5: 16 };

// ---------- penyimpanan (IndexedDB, cadangan localStorage) ----------
const DB = (() => {
  let dbp = null, fallback = false;
  const open = () => dbp || (dbp = new Promise((res, rej) => {
    try {
      const r = indexedDB.open("rusia-hafalan", 1);
      r.onupgradeneeded = () => { for (const s of ["cards", "quiz", "settings", "daily"]) if (!r.result.objectStoreNames.contains(s)) r.result.createObjectStore(s); };
      r.onsuccess = () => res(r.result);
      r.onerror = () => rej(r.error);
    } catch (e) { rej(e); }
  }).catch(() => { fallback = true; return null; }));
  const lsKey = (st, k) => `cayrus:${st}:${k}`;
  return {
    async get(st, k) {
      const d = await open();
      if (!d) { try { return JSON.parse(localStorage.getItem(lsKey(st, k))); } catch { return null; } }
      return new Promise((res) => { const q = d.transaction(st).objectStore(st).get(k); q.onsuccess = () => res(q.result ?? null); q.onerror = () => res(null); });
    },
    async set(st, k, v) {
      const d = await open();
      if (!d) { try { localStorage.setItem(lsKey(st, k), JSON.stringify(v)); } catch {} return; }
      return new Promise((res) => { const t = d.transaction(st, "readwrite"); t.objectStore(st).put(v, k); t.oncomplete = () => res(); t.onerror = () => res(); });
    },
    async del(st, k) {
      const d = await open();
      if (!d) { try { localStorage.removeItem(lsKey(st, k)); } catch {} return; }
      return new Promise((res) => { const t = d.transaction(st, "readwrite"); t.objectStore(st).delete(k); t.oncomplete = () => res(); t.onerror = () => res(); });
    },
    async all(st) {
      const d = await open();
      const out = {};
      if (!d) {
        try { for (let i = 0; i < localStorage.length; i++) { const k = localStorage.key(i); if (k.startsWith(`cayrus:${st}:`)) out[k.slice(st.length + 8)] = JSON.parse(localStorage.getItem(k)); } } catch {}
        return out;
      }
      return new Promise((res) => {
        const t = d.transaction(st); const q = t.objectStore(st).openCursor();
        q.onsuccess = () => { const c = q.result; if (c) { out[c.key] = c.value; c.continue(); } };
        t.oncomplete = () => res(out); t.onerror = () => res(out);
      });
    },
    get usingFallback() { return fallback; },
  };
})();

// ---------- data ----------
async function loadData() {
  const get = (f) => fetch(f).then((r) => { if (!r.ok) throw new Error(f); return r.json(); });
  const [w, v, g, q] = await Promise.all([get("data/words.json"), get("data/verbs.json"), get("data/grammar.json"), get("data/questions.json")]);
  S.words = w.entries; S.verbs = v; S.grammar = g; S.questions = q.questions;
  for (const e of S.words) S.w[e.id] = e;
  for (const p of v.pairs) S.p[p.id] = p;
  for (const e of v.entries) S.v[e.id] = e;
  for (const e of S.words) prepWord(e);
  for (const e of v.entries) prepVerb(e);
  const cards = await DB.all("cards");
  for (const [k, c] of Object.entries(cards)) S.cards.set(k, c);
}

function cellsOf(x, out = []) {
  if (!x) return out;
  if (Array.isArray(x) && x.length === 2 && typeof x[1] === "string") { out.push(x); return out; }
  if (typeof x === "object") for (const val of Object.values(x)) cellsOf(val, out);
  return out;
}
function pairCells(p) { return [...cellsOf(p.ipf), ...cellsOf(p.pf)]; }
function prepWord(e) {
  const cells = e.decl ? cellsOf(e.decl) : [];
  if (e.verbRef && S.p[e.verbRef.pair]) cells.push(...pairCells(S.p[e.verbRef.pair]));
  e._u = cells.some((c) => c[1] === "u") || e.accented[1] === "u";
  e._g = cells.some((c) => c[1] === "g");
  e._key = norm(e.lemma);
  e._tr = norm(e.translation?.text);
  e._rank = e.rank && e.rank.length ? e.rank[0] : 99999;
}
function verbSide(e) { const p = S.p[e.pairId]; return e.aspect === "pf" ? p.pf : p.ipf || p.pf; }
function prepVerb(e) {
  const p = S.p[e.pairId];
  const side = verbSide(e);
  e._acc = side?.inf?.[0] || e.lemma;
  const cells = pairCells(p);
  e._u = cells.some((c) => c[1] === "u") || p.pairSource === "uncertain";
  e._g = cells.some((c) => c[1] === "g");
  e._key = norm(e.lemma);
  e._tr = norm(e.translation?.text);
}

// ---------- tampilan sel & legenda ----------
function cell(c) {
  if (!c) return '<span class="na">—</span>';
  const tag = c[1] === "g" ? '<sup class="st g" title="generated: dibuat, bukan dari kamus">G</sup>'
    : c[1] === "u" ? '<sup class="st u" title="uncertain: belum pasti">?</sup>' : "";
  const parts = String(c[0]).split(/,\s*/).map((x) => `<span class="nw">${esc(x)}</span>`).join(", ");
  return `<span lang="ru">${parts}</span>${tag}`;
}
const td = (c) => `<td${c && c[1] === "u" ? ' class="is-u"' : ""}>${cell(c)}</td>`;
const LEGEND = '<p class="legend">Tanpa tanda = terverifikasi (kamus OpenRussian + pymorphy3). <sup class="st g">G</sup> = dibuat (generated). <sup class="st u">?</sup> = belum pasti, masuk daftar review.</p>';
const statusTag = (s) => s === "g" ? ' <sup class="st g" title="generated">G</sup>' : s === "u" ? ' <sup class="st u" title="uncertain">?</sup>' : "";

function formsSet(e) {
  const set = new Set([norm(e.lemma)]);
  const add = (x) => cellsOf(x).forEach((c) => c[0].split(",").forEach((f) => set.add(norm(f))));
  if (e.decl) add(e.decl);
  if (e.verbRef && S.p[e.verbRef.pair]) { add(S.p[e.verbRef.pair].ipf); add(S.p[e.verbRef.pair].pf); }
  return set;
}
function highlight(ru, set) {
  return esc(ru).replace(/[А-Яа-яЁё́]+/g, (t) => set.has(norm(t)) ? `<mark>${t}</mark>` : t);
}

// ---------- router ----------
const routes = [
  [/^\/$/, home], [/^\/kamus$/, dictView], [/^\/kata\/([\w]+)$/, wordView], [/^\/kerja\/(v\d+)$/, verbView],
  [/^\/hafalan$/, studySetup], [/^\/hafalan\/sesi$/, studySession], [/^\/hafalan\/dek\/(\w+)$/, deckView], [/^\/grammar$/, grammarList],
  [/^\/grammar\/(\w+)$/, grammarCase], [/^\/latihan\/(\w+)$/, quizView], [/^\/tentang$/, about],
];
function route() {
  if (S.cleanup) { S.cleanup(); S.cleanup = null; }
  const path = (location.hash.slice(1) || "/").split("?")[0];
  const tab = path.startsWith("/kamus") || path.startsWith("/kata") || path.startsWith("/kerja") ? "kamus"
    : path.startsWith("/hafalan") ? "hafalan" : path.startsWith("/grammar") || path.startsWith("/latihan") ? "grammar" : path === "/" ? "home" : "";
  document.querySelectorAll(".tabs a").forEach((a) => a.classList.toggle("on", a.dataset.tab === tab));
  for (const [re, fn] of routes) {
    const m = path.match(re);
    if (m) { fn(...m.slice(1)); return; }
  }
  view.innerHTML = '<h1>Halaman tidak ditemukan</h1><p><a href="#/">Kembali ke beranda</a></p>';
}
function show(html, keepScroll) { view.innerHTML = html; if (!keepScroll) window.scrollTo(0, 0); }

// ---------- beranda ----------
async function home() {
  const t = today();
  let due = 0;
  for (const c of S.cards.values()) if (!c.known && c.due <= t) due++;
  const quiz = await DB.all("quiz");
  const set = (await DB.get("settings", "app")) || {};
  S.progDir ||= set.dir || "ru-id";
  show(`
    <h1>Selamat belajar!</h1>
    <div class="card">
      <div class="row"><div class="grow"><b style="font-size:28px">${due}</b><div class="muted small">kartu jatuh tempo hari ini · kartu baru tanpa batas</div></div></div>
      <p><a class="btn primary block" href="#/hafalan">Mulai hafalan</a></p>
    </div>
    <div id="progwrap"></div>
    <h2>Latihan grammar</h2>
    <div class="list">${CASES.map(([id, name]) => { const r = quiz[id]; return `<a class="case" href="#/grammar/${id}"><span lang="ru"><b>${name}</b></span><span class="score">${r ? `terbaik ${r.best}/15` : "belum dicoba"}</span></a>`; }).join("")}</div>
    <h2>Isi data</h2>
    <div class="grid2">
      <div class="stat"><b>${S.words.length.toLocaleString("id")}</b><span class="muted small">entri kata</span></div>
      <div class="stat"><b>${S.verbs.entries.length}</b><span class="muted small">kata kerja (${S.verbs.pairs.length} pasangan)</span></div>
    </div>
    <p class="small"><a href="#/tentang">Tentang data, label status, dan lisensi</a></p>`);
  mountProgress(document.getElementById("progwrap"), true);
}

// ---------- kamus ----------
function dictState() {
  if (!S.dict) S.dict = { tab: "kata", q: "", pos: "", st: "", sort: "rank", scroll: 0 };
  return S.dict;
}
function dictView() {
  const st = dictState();
  const posOpts = Object.entries(POS).filter(([k]) => S.words.some((e) => e.pos === k)).map(([k, v]) => `<option value="${k}" ${st.pos === k ? "selected" : ""}>${v}</option>`).join("");
  show(`
    <div class="search">
      <div class="row"><div class="seg" role="tablist">
        <button data-tab="kata" class="${st.tab === "kata" ? "on" : ""}">Kata (${S.words.length.toLocaleString("id")})</button>
        <button data-tab="kerja" class="${st.tab === "kerja" ? "on" : ""}">Kata kerja (${S.verbs.entries.length})</button>
      </div></div>
      <input type="search" id="q" placeholder="Cari kata Rusia (Kiril) atau arti Indonesia" value="${esc(st.q)}" autocomplete="off" aria-label="Cari kata">
      <div class="filters">
        <select id="pos" aria-label="Kelas kata" ${st.tab === "kerja" ? "disabled" : ""}><option value="">Semua kelas</option>${posOpts}</select>
        <select id="st" aria-label="Status data"><option value="">Semua status</option><option value="u" ${st.st === "u" ? "selected" : ""}>Ada [uncertain]</option><option value="g" ${st.st === "g" ? "selected" : ""}>Ada generated</option><option value="v" ${st.st === "v" ? "selected" : ""}>Semua terverifikasi</option></select>
        <select id="sort" aria-label="Urutan"><option value="rank">Frekuensi</option><option value="alpha" ${st.sort === "alpha" ? "selected" : ""}>Alfabet</option></select>
      </div>
      <div class="count" id="count"></div>
    </div>
    <div class="vl" id="list"></div>`, true);
  const list = document.getElementById("list");
  const items = () => filterItems(st);
  let data = items();
  const ROW = 64;
  const draw = () => {
    const top = list.getBoundingClientRect().top + window.scrollY;
    const y = window.scrollY - top;
    const start = Math.max(0, Math.floor(y / ROW) - 8);
    const end = Math.min(data.length, Math.ceil((y + window.innerHeight) / ROW) + 8);
    let html = "";
    for (let i = start; i < end; i++) html += rowHTML(data[i], i * ROW);
    list.innerHTML = html;
  };
  const refresh = () => {
    data = items();
    list.style.height = `${data.length * ROW}px`;
    document.getElementById("count").textContent = `${data.length.toLocaleString("id")} hasil`;
    draw();
  };
  let raf = 0;
  const onScroll = () => { if (!raf) raf = requestAnimationFrame(() => { raf = 0; draw(); }); st.scroll = window.scrollY; };
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  S.cleanup = () => { window.removeEventListener("scroll", onScroll); window.removeEventListener("resize", onScroll); };
  let timer = 0;
  view.querySelector("#q").addEventListener("input", (ev) => { clearTimeout(timer); timer = setTimeout(() => { st.q = ev.target.value; st.scroll = 0; window.scrollTo(0, 0); refresh(); }, 120); });
  for (const id of ["pos", "st", "sort"]) view.querySelector(`#${id}`).addEventListener("change", (ev) => { st[id] = ev.target.value; window.scrollTo(0, 0); refresh(); });
  view.querySelectorAll(".seg button").forEach((b) => b.addEventListener("click", () => { st.tab = b.dataset.tab; st.scroll = 0; dictView(); }));
  refresh();
  if (st.scroll) { window.scrollTo(0, st.scroll); draw(); } else window.scrollTo(0, 0);
}
function filterItems(st) {
  const q = norm(st.q);
  const isCyr = /[а-я]/.test(q);
  let arr = st.tab === "kata" ? S.words : S.verbs.entries;
  if (st.tab === "kata" && st.pos) arr = arr.filter((e) => e.pos === st.pos);
  if (st.st === "u") arr = arr.filter((e) => e._u);
  else if (st.st === "g") arr = arr.filter((e) => e._g);
  else if (st.st === "v") arr = arr.filter((e) => !e._u && !e._g);
  if (q) {
    if (isCyr) arr = arr.filter((e) => e._key.startsWith(q));
    else { const re = new RegExp(`(^|[^a-z])${q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}`); arr = arr.filter((e) => re.test(e._tr)); }
  }
  const rank = (e) => e._rank ?? e.rank;
  arr = arr.slice().sort(st.sort === "alpha" ? (a, b) => a._key.localeCompare(b._key, "ru") : (a, b) => rank(a) - rank(b) || a._key.localeCompare(b._key, "ru"));
  if (q && isCyr) arr.sort((a, b) => (a._key === q ? -1 : 0) - (b._key === q ? -1 : 0));
  return arr;
}
function rowHTML(e, y) {
  const isVerb = e.id.startsWith("v");
  const word = isVerb ? e._acc : e.accented[0];
  const label = isVerb ? (e.aspect === "pf" ? "СВ" : e.aspect === "both" ? "НСВ/СВ" : "НСВ") : POS[e.pos] || e.pos;
  const rank = isVerb ? `#${e.rank}` : e.rank && e.rank.length ? `#${e.rank[0]}` : "kata tugas";
  return `<a class="item" style="top:${y}px" href="#/${isVerb ? "kerja" : "kata"}/${e.id}">
    <div class="l"><div class="w" lang="ru">${esc(word)}${e._u ? '<span class="dot" title="ada bentuk [uncertain]"></span>' : ""}</div><div class="t">${esc(label)} · ${esc(e.translation?.text || "")}</div></div>
    <div class="r">${esc(rank)}</div></a>`;
}

// ---------- detail kata ----------
function wordView(id) {
  const e = S.w[id];
  if (!e) { show('<h1>Kata tidak ditemukan</h1><p><a href="#/kamus">Kembali ke kamus</a></p>'); return; }
  if (e.verbRef) { pairPage(S.p[e.verbRef.pair], e.verbRef.entry ? S.v[e.verbRef.entry] : null, e); return; }
  const chips = [`<span class="chip info">${esc(POS[e.pos] || e.pos)}</span>`];
  if (e.gender) chips.push(`<span class="chip">${GENDER[e.gender] || e.gender}</span>`);
  if (e.pos === "noun" && e.animate != null) chips.push(`<span class="chip">${e.animate ? "bernyawa" : "tak bernyawa"}</span>`);
  chips.push(`<span class="chip">${e.rank?.length ? "peringkat #" + e.rank.join(", #") : "kata tugas"}</span>`);
  if (e.indeclinable) chips.push('<span class="chip warn">tidak dideklinasi</span>');
  let table = "";
  const d = e.decl;
  if (!e.indeclinable && d) {
    if (d.type === "noun") table = nounTable(d);
    else if (d.type === "adj") table = adjTable(d);
    else if (d.type === "pron") table = pronTable(d);
    else if (d.type === "num") table = numTable(d);
  } else table = '<p class="note">Kata ini <b>tidak dideklinasi</b>: bentuknya tidak berubah menurut kasus.</p>';
  const set = formsSet(e);
  show(`
    <a class="back" href="#/kamus">‹ Kamus</a>
    <div class="head-word" lang="ru">${esc(e.accented[0])}${statusTag(e.accented[1])}</div>
    <div class="tr">${esc(e.translation?.text || "")}${statusTag("g")}</div>
    <div class="meta">${chips.join("")}</div>
    ${(e.notes || []).map((n) => `<p class="note">${esc(n)}</p>`).join("")}
    ${e._u ? '<p class="note warn">Sebagian bentuk kata ini berstatus [uncertain] dan masuk daftar review.</p>' : ""}
    <h2>Bentuk kata</h2>${table}${!e.indeclinable && d ? LEGEND : ""}
    ${e.example ? `<h2>Contoh</h2><div class="example"><div class="ru" lang="ru">${highlight(e.example.ru, set)}</div><div class="id">${esc(e.example.id)}</div><div class="legend">Contoh dan terjemahan dibuat (generated).</div></div>` : ""}`);
}
const CASE_ABBR = { nom: "Им.", gen: "Род.", dat: "Дат.", acc: "Вин.", ins: "Тв.", pre: "Пр." };
function caseHead(c, compact) { return `<th lang="ru" title="${c[1]}">${CASE_ABBR[c[0]]}${compact ? "" : `<small>${c[2]}</small>`}</th>`; }
function nounTable(d) {
  const sgOnly = d.number === "sg_only", plOnly = d.number === "pl_only";
  return `<table class="forms"><thead><tr><th>Kasus</th><th>Tunggal</th><th>Jamak</th></tr></thead><tbody>
    ${CASES.map((c) => `<tr>${caseHead(c)}${td(d.sg?.[c[0]])}${td(d.pl?.[c[0]])}</tr>`).join("")}</tbody></table>
    ${sgOnly ? '<p class="small muted">Kata ini hanya dipakai dalam bentuk tunggal.</p>' : plOnly ? '<p class="small muted">Kata ini hanya dipakai dalam bentuk jamak.</p>' : ""}`;
}
function accCell(x) {
  if (x && !Array.isArray(x) && typeof x === "object") {
    const u = (x.anim && x.anim[1] === "u") || (x.inan && x.inan[1] === "u");
    if (!x.anim && !x.inan) return td(null);
    return `<td${u ? ' class="is-u"' : ""}>${cell(x.anim)}<span class="an">hidup</span>${cell(x.inan)}<span class="an">mati</span></td>`;
  }
  return td(x);
}
function adjTable(d) {
  const gs = [["m", "м"], ["n", "ср"], ["f", "ж"], ["pl", "мн"]];
  const full = CASES.some((c) => gs.some(([g]) => { const x = d[g]?.[c[0]]; return x && (Array.isArray(x) || x.anim || x.inan); }));
  let html = "";
  if (full) html += `<div class="wide"><table class="forms adj"><thead><tr><th></th>${gs.map(([, l]) => `<th lang="ru">${l}</th>`).join("")}</tr></thead><tbody>
    ${CASES.map((c) => `<tr>${caseHead(c, true)}${gs.map(([g]) => c[0] === "acc" ? accCell(d[g]?.acc) : td(d[g]?.[c[0]])).join("")}</tr>`).join("")}</tbody></table></div>
    <p class="small muted">Akusatif м dan мн: "hidup" untuk kata benda bernyawa (= Родительный), "mati" untuk tak bernyawa (= Именительный).</p>`;
  else html += '<p class="note">Kata ini hanya punya bentuk pendek (tidak punya bentuk penuh).</p>';
  const sh = d.short;
  const hasShort = sh && Object.values(sh).some(Boolean);
  html += hasShort ? `<h3>Bentuk pendek</h3><table class="forms"><tbody>${[["m", "м"], ["f", "ж"], ["n", "ср"], ["pl", "мн"]].map(([g, l]) => `<tr><th lang="ru">${l}</th>${td(sh[g])}</tr>`).join("")}</tbody></table>`
    : '<p class="small muted">Tidak punya bentuk pendek.</p>';
  return html;
}
function pronTable(d) {
  const ap = d.afterPrep && Object.values(d.afterPrep).some(Boolean);
  return `<table class="forms"><thead><tr><th>Kasus</th><th>Bentuk</th>${ap ? "<th>Setelah preposisi</th>" : ""}</tr></thead><tbody>
    ${CASES.map((c) => `<tr>${caseHead(c)}${td(d.forms?.[c[0]])}${ap ? td(d.afterPrep?.[c[0]]) : ""}</tr>`).join("")}</tbody></table>`;
}
function numTable(d) {
  if (d.cols) return `<table class="forms"><thead><tr><th>Kasus</th><th lang="ru">м / ср</th><th lang="ru">ж</th></tr></thead><tbody>
    ${CASES.map((c) => `<tr>${caseHead(c)}${td(d.cols.mn?.[c[0]])}${td(d.cols.f?.[c[0]])}</tr>`).join("")}</tbody></table>`;
  return `<table class="forms"><thead><tr><th>Kasus</th><th>Bentuk</th></tr></thead><tbody>${CASES.map((c) => `<tr>${caseHead(c)}${td(d.forms?.[c[0]])}</tr>`).join("")}</tbody></table>`;
}

// ---------- detail kata kerja ----------
function verbView(vid) {
  const e = S.v[vid];
  if (!e) { show('<h1>Kata kerja tidak ditemukan</h1><p><a href="#/kamus">Kembali ke kamus</a></p>'); return; }
  pairPage(S.p[e.pairId], e, null);
}
const TYPE_LABEL = { pair: "pasangan НСВ/СВ", ipf_only: "hanya НСВ (tidak punya pasangan aspek)", pf_only: "hanya СВ (tidak punya pasangan aspek)", biaspectual: "biaspektual (satu bentuk untuk НСВ dan СВ)" };
function pairPage(p, ve, we) {
  const focus = ve ? (ve.aspect === "pf" ? "pf" : "ipf") : (p.ipf ? "ipf" : "pf");
  const rows = S.verbs.entries.filter((x) => x.pairId === p.id);
  const inf = (s) => p[s]?.inf;
  const headParts = [];
  if (p.ipf) headParts.push(`<span lang="ru">${esc(inf("ipf")[0])}</span>${statusTag(inf("ipf")[1])} <span class="chip">${p.type === "biaspectual" ? "НСВ = СВ" : "НСВ"}</span>`);
  if (p.pf) headParts.push(`<span lang="ru">${esc(inf("pf")[0])}</span>${statusTag(inf("pf")[1])} <span class="chip">СВ</span>`);
  const tr = p.translation || {};
  const notes = [];
  if (p.pairSource === "uncertain") notes.push(`<p class="note warn"><b>Pasangan aspek [uncertain].</b> ${esc(p.pairNote || "")}</p>`);
  else if (p.pairNote) notes.push(`<p class="note">${esc(p.pairNote)}</p>`);
  if (p.aspectNote) notes.push(`<p class="note">${esc(p.aspectNote)}</p>`);
  if (p.pairSource === "file_corrected") notes.push('<p class="small muted">Pasangan ini dibetulkan dari tulisan di file (salah ketik/urutan); lihat daftar review.</p>');
  const sides = p.type === "pair" ? ["ipf", "pf"] : [p.ipf ? "ipf" : "pf"];
  const set = new Set(); [p.ipf, p.pf].forEach((s) => cellsOf(s).forEach((c) => c[0].split(",").forEach((f) => set.add(norm(f)))));
  const exs = p.examples || {};
  const exHTML = (s, lbl) => exs[s] ? `<div class="example"><div class="lbl">${lbl}</div><div class="ru" lang="ru">${highlight(exs[s].ru, set)}</div><div class="id">${esc(exs[s].id)}</div></div>` : "";
  const wordEx = we && we.example && !ve ? `<div class="example"><div class="ru" lang="ru">${highlight(we.example.ru, set)}</div><div class="id">${esc(we.example.id)}</div></div>` : "";
  show(`
    <a class="back" href="#/kamus">‹ Kamus</a>
    <div class="head-word">${headParts.join('<span class="muted"> / </span>')}</div>
    <div class="tr">${p.type === "pair" ? `<b>НСВ:</b> ${esc(tr.ipf || "")}<br><b>СВ:</b> ${esc(tr.pf || "")}` : esc(tr.ipf || tr.pf || we?.translation?.text || "")}${statusTag("g")}</div>
    <div class="meta"><span class="chip info">kata kerja</span><span class="chip">${TYPE_LABEL[p.type] || p.type}</span>
      ${rows.length ? `<span class="chip">di file: ${rows.map((r) => `#${r.rank} ${esc(r.lemma)}`).join(", ")}</span>` : '<span class="chip">pasangan tidak tercantum di file kata kerja</span>'}
      ${we && we.rank?.length ? `<span class="chip">daftar kata #${we.rank.join(", #")}</span>` : ""}</div>
    ${notes.join("")}
    ${sides.length === 2 ? `<p><span class="seg" id="asp"><button data-s="ipf" class="${focus === "ipf" ? "on" : ""}">НСВ</button><button data-s="pf" class="${focus === "pf" ? "on" : ""}">СВ</button></span></p>` : ""}
    ${sides.map((s) => `<div class="aspect" data-s="${s}" ${sides.length === 2 && s !== focus ? "hidden" : ""}>${conjHTML(p, s)}</div>`).join("")}
    ${LEGEND}
    <h2>Contoh</h2>
    ${exHTML("ipf", p.type === "biaspectual" ? "Makna НСВ" : "НСВ")}${exHTML("pf", p.type === "biaspectual" ? "Makna СВ" : "СВ")}${wordEx}
    ${exs.contrast ? `<p class="note"><b>Beda aspek:</b> ${esc(exs.contrast)}</p>` : ""}
    <p class="legend">Contoh dan terjemahan dibuat (generated).</p>`);
  const seg = document.getElementById("asp");
  if (seg) seg.addEventListener("click", (ev) => {
    const b = ev.target.closest("button"); if (!b) return;
    seg.querySelectorAll("button").forEach((x) => x.classList.toggle("on", x === b));
    view.querySelectorAll(".aspect").forEach((x) => { x.hidden = x.dataset.s !== b.dataset.s; });
  });
}
function conjHTML(p, s) {
  const f = p[s];
  if (!f) return "";
  const block = (title, rows, src) => `<h3>${title}</h3><table class="forms"><tbody>${rows.map(([k, l]) => `<tr><th lang="ru">${l}</th>${td(src?.[k])}</tr>`).join("")}</tbody></table>`;
  let html = `<p class="small muted">Infinitif: <span lang="ru">${esc(f.inf[0])}</span>${statusTag(f.inf[1])}</p>`;
  if (p.type === "biaspectual") {
    html += block("Kini (НСВ) / masa depan (СВ)", PERSONS, f.presfut);
  } else if (s === "ipf") {
    html += block("Kini (настоя́щее)", PERSONS, f.pres);
  }
  html += block("Lampau (проше́дшее)", PAST, f.past);
  if (p.type !== "biaspectual") {
    if (s === "ipf") {
      const fut = f.fut || Object.fromEntries(PERSONS.map(([k], i) => [k, [`${BUDU[i]} ${f.inf[0]}`, f.inf[1]]]));
      html += block(f.fut ? "Masa depan (бу́дущее)" : "Masa depan majemuk (бу́ду + infinitif)", PERSONS, fut);
    } else html += block("Masa depan sederhana (бу́дущее)", PERSONS, f.fut);
  }
  html += block("Imperatif (повели́тельное)", IMP, f.imp);
  return html;
}

// ---------- hafalan (pengulangan berjarak) ----------
// Dek mengikuti peringkat di file kata; kata tanpa peringkat = kata tugas; dek terakhir = 500 baris file kata kerja.
const DECKS = [
  ["l1", "Level 1 · #1–500"], ["l2", "Level 2 · #501–1000"], ["l3", "Level 3 · #1001–1500"], ["l4", "Level 4 · #1501–2000"],
  ["tugas", "Kata Tugas"], ["verbs", "500 Kata Kerja"],
];
const DECK_NAME = Object.fromEntries([["all", "Semua kata (Level 1–4 + Kata Tugas)"], ...DECKS]);
const DECK_SHORT = { ...DECK_NAME, all: "Semua kata" };
const LEVEL = { l1: [1, 500], l2: [501, 1000], l3: [1001, 1500], l4: [1501, 2000] };
const deckCache = {};
function deckIds(deck) {
  if (deckCache[deck]) return deckCache[deck];
  let ids;
  if (deck === "verbs") ids = S.verbs.entries.slice().sort((a, b) => a.rank - b.rank).map((e) => e.id);
  else {
    let arr = S.words.slice().sort((a, b) => a._rank - b._rank || a._key.localeCompare(b._key, "ru"));
    if (LEVEL[deck]) arr = arr.filter((e) => e._rank >= LEVEL[deck][0] && e._rank <= LEVEL[deck][1]);
    else if (deck === "tugas") arr = arr.filter((e) => !e.rank?.length);
    ids = arr.map((e) => e.id);
  }
  return (deckCache[deck] = ids);
}
// Status per kartu (per arah): new = belum dipelajari, learn = dipelajari, hafal = kotak 5, known = ditandai "Sudah tahu".
const KNOWN_DUE = "9999-12-31";
function cardStatus(id, dir) {
  const c = S.cards.get(`${id}:${dir}`);
  if (!c) return "new";
  if (c.known) return "known";
  return c.box >= 5 ? "hafal" : "learn";
}
function deckStats(ids, dir) {
  const s = { hafal: 0, learn: 0, known: 0, new: 0, total: ids.length };
  for (const id of ids) s[cardStatus(id, dir)]++;
  return s;
}
function progBar(s) {
  const pc = (n) => (s.total ? (n / s.total) * 100 : 0).toFixed(2);
  return `<div class="pbar" role="img" aria-label="${s.hafal} hafal, ${s.learn} dipelajari, ${s.known} sudah tahu, dari ${s.total} kata">${["hafal", "learn", "known"].map((k) => s[k] ? `<i class="${k}" style="width:${pc(s[k])}%"></i>` : "").join("")}</div>`;
}
const legendHTML = (s) => `<div class="plegend"><span><i class="hafal"></i>Hafal${s ? ` ${s.hafal}` : ""}</span><span><i class="learn"></i>Dipelajari${s ? ` ${s.learn}` : ""}</span><span><i class="known"></i>Sudah tahu${s ? ` ${s.known}` : ""}</span></div>`;
const dirSeg = (dir) => `<span class="seg sm" id="pdir" role="group" aria-label="Arah kartu"><button data-d="ru-id" class="${dir === "ru-id" ? "on" : ""}">RU→ID</button><button data-d="id-ru" class="${dir === "id-ru" ? "on" : ""}">ID→RU</button></span>`;
function progressHTML(dir, toggle) {
  return `<div class="card prog">
    <div class="row phead"><span class="eyebrow grow">Progres dek</span>${toggle ? dirSeg(dir) : `<span class="muted small">${dir === "ru-id" ? "RU → ID" : "ID → RU"}</span>`}</div>
    ${DECKS.map(([k, name]) => { const s = deckStats(deckIds(k), dir);
      return `<a class="prow" href="#/hafalan/dek/${k}"><span class="row"><span class="grow">${esc(name)}</span><span class="num">${s.total - s.new} / ${s.total}</span></span>${progBar(s)}</a>`; }).join("")}
    ${legendHTML()}
  </div>`;
}
function mountProgress(el, toggle) {
  if (!el) return;
  el.innerHTML = progressHTML(S.progDir, toggle);
  el.querySelectorAll("#pdir button").forEach((b) => b.addEventListener("click", () => { S.progDir = b.dataset.d; mountProgress(el, toggle); }));
}
async function studySetup() {
  const set = (await DB.get("settings", "app")) || {};
  const deck = DECK_NAME[set.deck] ? set.deck : "all", size = set.sessionSize ?? 20;
  let dir = set.dir || "ru-id";
  S.progDir = dir;
  const t = today();
  const deckInfo = (k, d) => {
    let due = 0, fresh = 0;
    for (const id of deckIds(k)) { const c = S.cards.get(`${id}:${d}`); if (!c) fresh++; else if (!c.known && c.due <= t) due++; }
    return `${due} kartu perlu diulang hari ini · ${fresh.toLocaleString("id")} kata baru`;
  };
  show(`
    <h1>Hafalan</h1>
    <p class="muted">Flashcard dua arah dengan pengulangan berjarak. Kartu yang ditandai <b>Hafal</b> muncul lagi setelah 1, 3, 7, lalu 16 hari. Kartu baru tidak dibatasi.</p>
    <label class="field"><span>Dek</span><select id="deck">${Object.entries(DECK_SHORT).map(([k, name]) => `<option value="${k}" ${k === deck ? "selected" : ""}>${esc(name)}</option>`).join("")}</select></label>
    <p class="small muted" id="deckinfo"></p>
    <label class="field"><span>Arah</span><span class="seg" id="dir"><button data-d="ru-id" class="${dir === "ru-id" ? "on" : ""}">RU → ID</button><button data-d="id-ru" class="${dir === "id-ru" ? "on" : ""}">ID → RU</button></span></label>
    <label class="field"><span>Jumlah kartu per sesi</span><select id="size">${[10, 20, 50, 100, 0].map((n) => `<option value="${n}" ${n === size ? "selected" : ""}>${n || "Tanpa batas (sampai Anda tekan Selesai)"}</option>`).join("")}</select></label>
    <p><button class="btn primary block" id="go">Mulai sesi</button></p>
    <div id="progwrap"></div>
    <p class="small muted"><b>Hafal</b> = ditandai Hafal 4 kali berturut-turut, dengan jeda 1, 3, dan 7 hari. <b>Dipelajari</b> = sudah muncul di sesi, belum hafal. <b>Sudah tahu</b> = Anda tandai sudah tahu, kartunya tidak muncul lagi. Ketuk nama dek untuk melihat kata-katanya.</p>`);
  const sel = view.querySelector("#deck"), info = view.querySelector("#deckinfo");
  const prog = document.getElementById("progwrap");
  const refresh = () => { info.textContent = deckInfo(sel.value, dir); mountProgress(prog, false); };
  refresh();
  sel.addEventListener("change", refresh);
  view.querySelector("#dir").addEventListener("click", (ev) => {
    const b = ev.target.closest("button"); if (!b) return;
    dir = S.progDir = b.dataset.d;
    view.querySelectorAll("#dir button").forEach((x) => x.classList.toggle("on", x === b));
    refresh();
  });
  view.querySelector("#go").addEventListener("click", async () => {
    const s = { deck: sel.value, dir, sessionSize: +view.querySelector("#size").value };
    delete set.newPerDay;
    await DB.set("settings", "app", Object.assign(set, s));
    location.hash = "#/hafalan/sesi";
  });
}
function brief(id) {
  if (id.startsWith("v")) { const e = S.v[id]; return { word: e._acc, tr: e.translation?.text, href: `#/kerja/${id}`, rank: `#${e.rank}` }; }
  const e = S.w[id];
  return { word: e.accented[0], tr: e.translation?.text, href: `#/kata/${id}`, rank: e.rank?.length ? `#${e.rank[0]}` : "" };
}
const FILTERS = [["all", "Semua"], ["hafal", "Hafal"], ["learn", "Dipelajari"], ["known", "Sudah tahu"], ["new", "Belum"]];
async function deckView(k) {
  if (!LEVEL[k] && k !== "tugas" && k !== "verbs") { show('<h1>Dek tidak ditemukan</h1><p><a href="#/hafalan">Kembali ke hafalan</a></p>'); return; }
  const set = (await DB.get("settings", "app")) || {};
  S.progDir ||= set.dir || "ru-id";
  if (S.deckFilterFor !== k) { S.deckFilter = "all"; S.deckFilterFor = k; }
  const ids = deckIds(k);
  const draw = (keepScroll) => {
    const dir = S.progDir, f = S.deckFilter;
    const s = deckStats(ids, dir);
    const rows = ids.filter((id) => f === "all" || cardStatus(id, dir) === f);
    const rowHTML = (id) => {
      const b = brief(id), st = cardStatus(id, dir);
      const tag = st === "hafal" ? '<span class="dst hafal">Hafal</span>' : st === "learn" ? '<span class="dst learn">Dipelajari</span>'
        : st === "known" ? `<button class="dst known" data-reset="${id}" aria-label="Batalkan tanda Sudah tahu untuk ${esc(b.word)}">Sudah tahu ✕</button>` : "";
      return `<div class="drow"><a href="${b.href}"><span class="w" lang="ru">${esc(b.word)}</span><span class="t">${b.rank ? `${b.rank} · ` : ""}${esc(b.tr || "")}</span></a>${tag}</div>`;
    };
    show(`
      <a class="back" href="#/hafalan">‹ Hafalan</a>
      <h1>${esc(DECK_NAME[k])}</h1>
      <div class="card prog">
        <div class="row phead"><span class="grow"><b class="big-num">${s.total - s.new}</b> <span class="muted">/ ${s.total} kata</span></span>${dirSeg(dir)}</div>
        ${progBar(s)}${legendHTML(s)}
        <p style="margin-bottom:0"><button class="btn primary block" id="go">Hafalkan dek ini</button></p>
      </div>
      <div class="fchips" id="flt" role="group" aria-label="Saring status">${FILTERS.map(([v, l]) => `<button class="fchip ${f === v ? "on" : ""}" data-f="${v}">${l} <span>${v === "all" ? s.total : s[v]}</span></button>`).join("")}</div>
      ${s.known ? '<p class="small muted">Ketuk "Sudah tahu ✕" untuk mengembalikan kata itu ke daftar belajar.</p>' : ""}
      ${rows.length ? `<div class="dlist">${rows.map(rowHTML).join("")}</div>` : '<p class="muted">Tidak ada kata dengan status ini.</p>'}`, keepScroll);
    view.querySelectorAll("#pdir button").forEach((b) => b.addEventListener("click", () => { S.progDir = b.dataset.d; draw(true); }));
    view.querySelectorAll("#flt button").forEach((b) => b.addEventListener("click", () => { S.deckFilter = b.dataset.f; draw(true); }));
    view.querySelector(".dlist")?.addEventListener("click", async (ev) => {
      const btn = ev.target.closest("[data-reset]"); if (!btn) return;
      const key = `${btn.dataset.reset}:${S.progDir}`;
      S.cards.delete(key); await DB.del("cards", key);
      draw(true);
    });
    view.querySelector("#go").addEventListener("click", async () => {
      await DB.set("settings", "app", Object.assign(set, { deck: k, dir: S.progDir }));
      location.hash = "#/hafalan/sesi";
    });
  };
  draw(false);
}
function cardInfo(id) {
  if (id.startsWith("v")) {
    const e = S.v[id], p = S.p[e.pairId], side = verbSide(e);
    const pair = [p.ipf?.inf?.[0], p.pf?.inf?.[0]].filter(Boolean).join(" / ");
    const one = side?.pres?.["1sg"] || side?.fut?.["1sg"] || side?.presfut?.["1sg"];
    return { word: e._acc, label: `kata kerja ${e.aspect === "pf" ? "СВ" : e.aspect === "both" ? "НСВ/СВ" : "НСВ"}`, tr: e.translation?.text, keys: [pair && `pasangan: ${pair}`, one && `я ${first(one[0])}`].filter(Boolean), href: `#/kerja/${id}` };
  }
  const e = S.w[id];
  const keys = [];
  const d = e.decl;
  if (e.verbRef) { const p = S.p[e.verbRef.pair]; const pair = [p.ipf?.inf?.[0], p.pf?.inf?.[0]].filter(Boolean).join(" / "); if (pair) keys.push(`pasangan: ${pair}`); }
  else if (d?.type === "noun") { if (d.sg?.gen) keys.push(`Р tunggal: ${first(d.sg.gen[0])}`); if (d.pl?.nom) keys.push(`И jamak: ${first(d.pl.nom[0])}`); }
  else if (d?.type === "adj") { if (d.f?.nom) keys.push(`ж: ${first(d.f.nom[0])}`); if (d.n?.nom) keys.push(`ср: ${first(d.n.nom[0])}`); if (d.pl?.nom) keys.push(`мн: ${first(d.pl.nom[0])}`); }
  else if (d?.type === "pron" && d.forms?.gen) keys.push(`Р: ${first(d.forms.gen[0])}`);
  else if (e.indeclinable) keys.push("tidak dideklinasi");
  const g = e.gender ? ` · ${GENDER[e.gender]}` : "";
  return { word: e.accented[0], label: `${POS[e.pos] || e.pos}${g}`, tr: e.translation?.text, keys, href: `#/kata/${id}` };
}
async function studySession() {
  const set = (await DB.get("settings", "app")) || {};
  const t = today();
  const deck = DECK_NAME[set.deck] ? set.deck : "all";
  const ids = deckIds(deck);
  const dir = set.dir || "ru-id";
  const due = ids.filter((id) => { const c = S.cards.get(`${id}:${dir}`); return c && !c.known && c.due <= t; })
    .sort((a, b) => S.cards.get(`${a}:${dir}`).due.localeCompare(S.cards.get(`${b}:${dir}`).due));
  const size = set.sessionSize === 0 ? Infinity : set.sessionSize || 20; // 0 = tanpa batas
  const fresh = ids.filter((id) => !S.cards.has(`${id}:${dir}`)).slice(0, Math.max(0, size - due.length));
  const queue = [...due.slice(0, size), ...fresh];
  const fails = {};
  let done = 0, ok = 0, bad = 0, kn = 0, flipped = false;
  if (!queue.length) {
    show(`<h1>Tidak ada kartu</h1><p>Semua kata di dek <b>${esc(DECK_NAME[deck])}</b> sudah dipelajari, dan tidak ada kartu yang jatuh tempo hari ini. Pilih dek lain atau kembali besok.</p><p><a class="btn" href="#/hafalan">Ganti pengaturan</a></p>`);
    return;
  }
  const total = queue.length;
  const render = () => {
    if (!queue.length) {
      show(`<h1>Sesi selesai</h1><div class="grid3"><div class="stat"><b>${ok}</b><span class="muted small">Hafal</span></div><div class="stat"><b>${bad}</b><span class="muted small">Belum</span></div><div class="stat"><b>${kn}</b><span class="muted small">Sudah tahu</span></div></div>
        <p><a class="btn primary block" href="#/hafalan/sesi">Sesi berikutnya</a></p><p><a class="btn block" href="#/hafalan">Lihat progres dek</a></p>`);
      return;
    }
    const id = queue[0]; const info = cardInfo(id); const isNew = !S.cards.has(`${id}:${dir}`);
    const front = dir === "ru-id" ? `<div class="big" lang="ru">${esc(info.word)}</div><div class="sub">${esc(info.label)}</div>`
      : `<div class="mid">${esc(info.tr)}</div><div class="sub">${esc(info.label)}</div>`;
    const back = dir === "ru-id" ? `<div class="mid">${esc(info.tr)}</div>` : `<div class="big" lang="ru">${esc(info.word)}</div>`;
    const knownBtn = isNew ? '<p><button class="btn block" id="known">Sudah tahu, jangan tampilkan lagi</button></p>' : "";
    show(`
      <div class="row"><span class="muted small grow">${done}/${total} · ${isNew ? "kartu baru" : "ulangan"}</span><a class="small" href="#/hafalan">Selesai</a></div>
      <div class="progress"><i style="width:${Math.round((done / total) * 100)}%"></i></div>
      <div class="flash" id="card" role="button" tabindex="0" aria-label="Balik kartu">${front}
        ${flipped ? `<hr>${back}${info.keys.length ? `<div class="sub" lang="ru">${info.keys.map(esc).join(" · ")}</div>` : ""}<div class="sub"><a href="${info.href}">Lihat detail</a></div>` : '<div class="sub">Ketuk untuk melihat jawaban</div>'}
      </div>
      ${flipped ? '<div class="grid2"><button class="btn bad" id="no">Belum</button><button class="btn ok" id="yes">Hafal</button></div>' : '<button class="btn primary block" id="flip">Tampilkan jawaban</button>'}
      ${knownBtn}`);
    const flip = () => { if (!flipped) { flipped = true; render(); } };
    view.querySelector("#card").addEventListener("click", (ev) => { if (!ev.target.closest("a")) flip(); });
    view.querySelector("#card").addEventListener("keydown", (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); flip(); } });
    view.querySelector("#flip")?.addEventListener("click", flip);
    view.querySelector("#yes")?.addEventListener("click", () => answer(id, "yes"));
    view.querySelector("#no")?.addEventListener("click", () => answer(id, "no"));
    view.querySelector("#known")?.addEventListener("click", () => answer(id, "known"));
  };
  const answer = async (id, kind) => {
    const key = `${id}:${dir}`;
    const prev = S.cards.get(key);
    const c = prev ? { ...prev } : { box: 1, due: t, reps: 0, lapses: 0 };
    c.updatedAt = Date.now();
    queue.shift();
    if (kind === "known") { c.known = true; c.due = KNOWN_DUE; c.last = "tahu"; kn++; done++; }
    else if (kind === "yes") { c.reps++; c.box = Math.min((c.box || 1) + 1, 5); c.due = addDays(t, INTERVAL[c.box]); c.last = "hafal"; ok++; done++; }
    else { c.reps++; c.box = 1; c.due = t; c.lapses++; c.last = "belum"; bad++; fails[id] = (fails[id] || 0) + 1; if (fails[id] < 3) queue.push(id); else done++; }
    S.cards.set(key, c);
    await DB.set("cards", key, c);
    flipped = false; render();
  };
  render();
}

// ---------- grammar ----------
async function grammarList() {
  const quiz = await DB.all("quiz");
  show(`<h1>Grammar: 6 падеж</h1><p class="muted">${esc(S.grammar.intro)}</p>
    <div class="list">${S.grammar.cases.map((c) => { const r = quiz[c.id]; const n = S.questions.filter((q) => q.case === c.id).length;
      return `<a class="case" href="#/grammar/${c.id}"><div><b lang="ru">${esc(c.name)}</b> <span class="muted small">${esc(c.nameId)}</span><div class="q" lang="ru">${esc(c.question)}</div></div><div class="score">${r ? `terbaik ${r.best}/15<br>${r.attempts}× latihan` : `${n} soal`}</div></a>`; }).join("")}</div>`);
}
function grammarCase(id) {
  const c = S.grammar.cases.find((x) => x.id === id);
  if (!c) { show('<h1>Kasus tidak ditemukan</h1>'); return; }
  const e = c.endings;
  const endRow = (k, l) => `<tr><th>${l}</th><td lang="ru">${esc(e.sg[k])}</td><td lang="ru">${esc(e.pl[k])}</td></tr>`;
  show(`
    <a class="back" href="#/grammar">‹ Grammar</a>
    <h1 lang="ru">${esc(c.name)} <span class="muted" style="font-size:16px">${esc(c.nameId)}</span></h1>
    <p><span class="chip info" lang="ru">${esc(c.question)}</span></p>
    <p>${esc(c.summary)}</p>
    <h2>Fungsi</h2><ul class="clean">${c.functions.map((f) => `<li>${esc(f)}</li>`).join("")}</ul>
    <h2>Preposisi</h2><dl class="preps">${c.prepositions.map((p) => `<dt lang="ru">${esc(p.prep)}</dt><dd>${esc(p.meaning)} — <span lang="ru">${esc(p.example)}</span></dd>`).join("")}</dl>
    <h2>Akhiran kata benda</h2>
    <div class="wide"><table class="forms"><thead><tr><th>Gender</th><th>Tunggal</th><th>Jamak</th></tr></thead><tbody>
      ${endRow("m", "maskulin")}${endRow("f", "feminin")}${endRow("n", "netral")}</tbody></table></div>
    <h3>Akhiran kata sifat</h3>
    <table class="forms"><tbody>${[["m", "м"], ["n", "ср"], ["f", "ж"], ["pl", "мн"]].map(([k, l]) => `<tr><th lang="ru">${l}</th><td lang="ru">${esc(e.adj[k])}</td></tr>`).join("")}</tbody></table>
    <h2>Contoh</h2>${c.examples.map((x) => `<div class="example"><div class="ru" lang="ru">${highlight(x.ru, new Set([norm(x.form)]))}</div><div class="id">${esc(x.id)}</div></div>`).join("")}
    <p><a class="btn primary block" href="#/latihan/${c.id}">Latihan (15 soal)</a></p>`);
}
async function quizView(id) {
  const c = S.grammar.cases.find((x) => x.id === id);
  if (!c) { show('<h1>Kasus tidak ditemukan</h1>'); return; }
  const qs = shuffle(S.questions.filter((q) => q.case === id)).slice(0, 15);
  let i = 0, score = 0, answered = false; const wrong = [];
  const caseName = Object.fromEntries(CASES.map(([k, n]) => [k, n]));
  const render = () => {
    if (i >= qs.length) return finish();
    const q = qs[i];
    const ru = q.type === "pick_case" ? esc(q.prompt.ru).replace(/\[(.+?)\]/, "<mark>$1</mark>") : esc(q.prompt.ru).replace("___", '<span class="gap">&nbsp;</span>');
    const instr = q.type === "mcq" ? "Pilih bentuk yang benar." : q.type === "fill" ? "Ketik bentuk yang benar (tanda aksen dan ё boleh diabaikan)." : "Kata yang disorot ada dalam kasus apa?";
    let body = "";
    if (q.type === "mcq") body = `<div class="opts">${q.options.map((o) => `<button class="opt" data-v="${esc(o)}" lang="ru">${esc(o)}</button>`).join("")}</div>`;
    else if (q.type === "fill") body = `<form id="ff" class="row" style="margin:12px 0"><input type="text" id="fi" class="grow" lang="ru" autocomplete="off" autocapitalize="off" spellcheck="false" aria-label="Jawaban"><button class="btn primary">Periksa</button></form>`;
    else body = `<div class="opts two">${CASES.map(([k, n]) => `<button class="opt" data-v="${k}"><span lang="ru">${n}</span><small>${CASE_ID[k]}</small></button>`).join("")}</div>`;
    show(`
      <a class="back" href="#/grammar/${id}">‹ ${esc(c.name)}</a>
      <div class="row"><span class="muted small grow">Soal ${i + 1}/${qs.length} · skor ${score}</span></div>
      <div class="progress"><i style="width:${Math.round((i / qs.length) * 100)}%"></i></div>
      <p class="muted small">${instr}</p>
      <div class="qtext" lang="ru">${ru}</div>
      <p class="muted">${esc(q.prompt.id)}</p>
      ${body}<div id="fb"></div>`);
    answered = false;
    view.querySelectorAll(".opt").forEach((b) => b.addEventListener("click", () => check(q, b.dataset.v, b)));
    const ff = view.querySelector("#ff");
    if (ff) { const inp = view.querySelector("#fi"); inp.focus(); ff.addEventListener("submit", (ev) => { ev.preventDefault(); if (inp.value.trim()) check(q, inp.value, null); }); }
  };
  const check = (q, val, btn) => {
    if (answered) return; answered = true;
    let right;
    if (q.type === "fill") right = (q.accept || [q.answer]).some((a) => norm(a) === norm(val).replace(/\s+/g, " "));
    else right = norm(val) === norm(q.answer);
    if (right) score++; else wrong.push(q);
    view.querySelectorAll(".opt").forEach((b) => { b.disabled = true; if (norm(b.dataset.v) === norm(q.answer)) b.classList.add("right"); });
    if (btn && !right) btn.classList.add("wrong");
    const ansText = q.type === "pick_case" ? `${caseName[q.answer]} (${CASE_ID[q.answer]})` : q.answer;
    const gapAns = q.type === "pick_case" ? null : q.answer;
    if (gapAns) { const g = view.querySelector(".gap"); if (g) g.textContent = gapAns; }
    view.querySelector("#fb").innerHTML = `<div class="feedback ${right ? "right" : "wrong"}"><b>${right ? "Benar!" : "Belum tepat."}</b>
      ${right ? "" : `Jawaban: <span lang="ru"><b>${esc(ansText)}</b></span><br>`}${esc(q.explanation)}</div>
      <button class="btn primary block" id="next">${i + 1 < qs.length ? "Soal berikutnya" : "Lihat hasil"}</button>`;
    const fi = view.querySelector("#fi"); if (fi) fi.disabled = true;
    const nx = view.querySelector("#next"); nx.focus(); nx.addEventListener("click", () => { i++; render(); });
  };
  const finish = async () => {
    const prev = (await DB.get("quiz", id)) || { best: 0, attempts: 0, history: [] };
    const rec = { best: Math.max(prev.best || 0, score), last: score, attempts: (prev.attempts || 0) + 1, history: [...(prev.history || []), { date: today(), score }].slice(-20) };
    await DB.set("quiz", id, rec);
    show(`<a class="back" href="#/grammar/${id}">‹ ${esc(c.name)}</a><h1>Hasil latihan</h1>
      <div class="grid2"><div class="stat"><b>${score}/${qs.length}</b><span class="muted small">skor sesi ini</span></div><div class="stat"><b>${rec.best}/15</b><span class="muted small">skor terbaik (${rec.attempts}× latihan)</span></div></div>
      ${wrong.length ? `<h2>Yang perlu diulang</h2>${wrong.map((q) => `<div class="example"><div class="ru" lang="ru">${esc(q.prompt.ru.replace("___", q.type === "pick_case" ? "___" : q.answer).replace(/\[(.+?)\]/, "$1"))}</div><div class="id">${q.type === "pick_case" ? `Kasus: ${esc(caseName[q.answer])} — ` : ""}${esc(q.explanation)}</div></div>`).join("")}` : "<p>Semua jawaban benar. Hebat!</p>"}
      <p><a class="btn primary block" href="#/latihan/${id}">Ulangi latihan</a></p><p><a class="btn block" href="#/grammar">Pilih kasus lain</a></p>`);
  };
  render();
}

// ---------- tentang ----------
async function about() {
  let offline = "memeriksa…";
  show(aboutHTML(offline));
  try {
    const ok = "caches" in window && (await caches.match("data/words.json")) && (await caches.match("app.js"));
    offline = ok ? "siap — aplikasi bisa dipakai tanpa internet" : "belum siap — buka aplikasi sekali saat online";
  } catch { offline = "tidak dapat diperiksa di browser ini"; }
  const persisted = navigator.storage?.persisted ? await navigator.storage.persisted() : false;
  const el = document.getElementById("off");
  if (el) el.textContent = `Data offline: ${offline}. Penyimpanan ${persisted ? "persisten" : "biasa"}${DB.usingFallback ? " (localStorage)" : " (IndexedDB)"}.`;
}
function aboutHTML(offline) {
  const nW = S.words.length, nV = S.verbs.entries.length, nP = S.verbs.pairs.length;
  return `
    <h1>Tentang CayRus</h1>
    <p id="off" class="note">Data offline: ${esc(offline)}</p>
    <p>CayRus berisi <b>${nW.toLocaleString("id")}</b> entri kata dan <b>${nV}</b> kata kerja (${nP} pasangan aspek) dari dua file daftar kata yang Anda lampirkan, plus modul 6 падеж dengan ${S.questions.length} soal.</p>
    <h2>Arti label status</h2>
    <ul class="clean">
      <li>Tanpa tanda: <b>terverifikasi</b>. Bentuk dan aksen dari kamus OpenRussian, dan bentuknya cocok dengan analisis morfologi pymorphy3.</li>
      <li><sup class="st g">G</sup> <b>generated</b>: dibuat atau dibetulkan secara manual, tanpa sumber pembanding. Semua terjemahan Indonesia dan contoh kalimat berstatus ini.</li>
      <li><sup class="st u">?</sup> <b>uncertain</b>: sumber bertentangan atau belum pasti. Masuk daftar review.</li>
    </ul>
    <p>Soal latihan grammar hanya memakai bentuk yang terverifikasi.</p>
    <h2>Sumber dan lisensi</h2>
    <ul class="clean">
      <li>Daftar kata dan kata kerja: file "1000 & 2000 самых встречаемых слов" dan "500 Russian Verbs".</li>
      <li>Bentuk kata dan aksen: data <a href="https://github.com/Badestrand/russian-dictionary" rel="noopener">OpenRussian</a> (openrussian.org), lisensi <a href="https://creativecommons.org/licenses/by-sa/4.0/" rel="noopener">CC BY-SA 4.0</a>. Data turunan di aplikasi ini ikut berlisensi CC BY-SA 4.0.</li>
      <li>Pemeriksaan bentuk: pymorphy3 dengan kamus OpenCorpora (hanya dipakai saat membuat data, tidak ikut di aplikasi).</li>
      <li>Huruf: Noto Sans, lisensi <a href="fonts/OFL.txt">SIL Open Font License 1.1</a>.</li>
    </ul>
    <h2>Privasi</h2>
    <p>Tanpa akun, iklan, atau pelacakan. Progres hafalan dan skor disimpan hanya di perangkat ini. Menghapus data situs/browser akan menghapus progres.</p>
    <p class="muted small">Versi ${APP_VERSION}</p>`;
}

// ---------- mulai ----------
async function start() {
  try {
    await loadData();
  } catch (err) {
    view.innerHTML = `<h1>Data gagal dimuat</h1><p>Periksa koneksi lalu muat ulang. Setelah pemuatan pertama berhasil, aplikasi bisa dipakai offline.</p><p class="muted small">${esc(err.message)}</p>`;
    return;
  }
  window.addEventListener("hashchange", route);
  route();
  try { if (navigator.storage?.persist) navigator.storage.persist(); } catch {}
}
if ("serviceWorker" in navigator) {
  // Saat versi baru terpasang (bukan pemasangan pertama), muat ulang sekali agar versi baru langsung dipakai.
  const hadController = !!navigator.serviceWorker.controller;
  let reloading = false;
  navigator.serviceWorker.addEventListener("controllerchange", () => { if (hadController && !reloading) { reloading = true; location.reload(); } });
  window.addEventListener("load", () => navigator.serviceWorker.register("sw.js").catch(() => {}));
}
start();
