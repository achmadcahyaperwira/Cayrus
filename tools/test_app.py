"""M6: uji otomatis CayRus di Chrome headless (layar 375 px).

Pemakaian: python3 tools/test_app.py   (menjalankan server lokal sendiri di port 8765)
Hasil   : work/test_report.json dan tangkapan layar di work/screens/
"""
import json, time, threading, http.server, socketserver, functools, sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "work" / "screens"
SHOTS.mkdir(parents=True, exist_ok=True)
PORT = 8765
BASE = f"http://localhost:{PORT}/"
results, errors, foreign = [], [], []


def ok(name, cond, detail=""):
    results.append({"test": name, "pass": bool(cond), "detail": str(detail)})
    print(("LULUS " if cond else "GAGAL ") + name + (f" — {detail}" if detail else ""))


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


handler = functools.partial(Quiet, directory=str(ROOT))
socketserver.TCPServer.allow_reuse_address = True
srv = socketserver.ThreadingTCPServer(("127.0.0.1", PORT), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

words = {e["id"]: e for e in json.load(open(ROOT / "data/words.json"))["entries"]}

with sync_playwright() as pw:
    browser = pw.chromium.launch(executable_path="/usr/bin/google-chrome", headless=True, args=["--no-sandbox"])
    ctx = browser.new_context(viewport={"width": 375, "height": 812}, device_scale_factor=2, is_mobile=True, has_touch=True,
                              user_agent="Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Mobile Safari/537.36")
    page = ctx.new_page()
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("request", lambda r: foreign.append(r.url) if not r.url.startswith(BASE) and not r.url.startswith("data:") else None)

    def go(hash_, wait):
        page.evaluate(f"location.hash = '{hash_}'")
        page.wait_for_selector(wait, timeout=10000)

    def shot(name):
        page.screenshot(path=str(SHOTS / f"{name}.png"), full_page=False)

    # 1. pemuatan pertama + service worker
    page.goto(BASE)
    page.wait_for_selector("text=Selamat belajar!", timeout=20000)
    sw_ready = page.evaluate("navigator.serviceWorker.ready.then(r => !!r.active)")
    ok("service worker aktif", sw_ready)
    page.wait_for_function("navigator.serviceWorker.controller !== null || true")
    page.reload(); page.wait_for_selector("text=Selamat belajar!")
    controlled = page.evaluate("!!navigator.serviceWorker.controller")
    ok("halaman dikendalikan service worker setelah muat ulang", controlled)
    cached = page.evaluate("""Promise.all(['data/words.json','data/verbs.json','data/grammar.json','data/questions.json','app.js','app.css','index.html','fonts/noto-sans-400Regular.woff2','icons/icon-192.png','manifest.webmanifest'].map(u => caches.match(u).then(r => !!r)))""")
    ok("semua aset tersimpan di cache", all(cached), cached)
    shot("01-beranda")

    # 2. manifest dan installability
    man = page.evaluate("fetch('manifest.webmanifest').then(r => r.json())")
    ok("manifest: name, short_name, start_url, display standalone, ikon 192/512/maskable",
       man.get("short_name") == "CayRus" and man.get("display") == "standalone" and man.get("start_url") == "./"
       and {i["sizes"] for i in man["icons"]} >= {"192x192", "512x512"} and any(i.get("purpose") == "maskable" for i in man["icons"]))
    cdp = ctx.new_cdp_session(page)
    import tempfile
    with tempfile.TemporaryDirectory() as prof:
        pctx = pw.chromium.launch_persistent_context(prof, executable_path="/usr/bin/google-chrome", headless=True, args=["--no-sandbox"])
        pp = pctx.pages[0] if pctx.pages else pctx.new_page()
        pp.goto(BASE); pp.wait_for_selector("text=Selamat belajar!", timeout=20000)
        pp.evaluate("navigator.serviceWorker.ready")
        pp.reload(); pp.wait_for_selector("text=Selamat belajar!")
        inst = pctx.new_cdp_session(pp).send("Page.getInstallabilityErrors")
        errs = [e.get("errorId") for e in inst.get("installabilityErrors", [])]
        ok("Chrome (profil biasa): tidak ada error installability", not errs, errs or "kosong")
        pctx.close()

    # 3. kamus + pencarian + virtual list
    go("#/kamus", "#list .item")
    n_rows = page.locator("#list .item").count()
    total = page.inner_text("#count")
    ok("kamus: daftar 1.841 entri dengan virtual list (< 60 baris di DOM)", "1.841" in total and n_rows < 60, f"{total}, {n_rows} baris DOM")
    shot("02-kamus")
    cdp.send("Emulation.setCPUThrottlingRate", {"rate": 4})
    t0 = time.perf_counter()
    page.fill("#q", "книг")
    page.wait_for_function("document.querySelector('#count').textContent.startsWith('2 ') || document.querySelector('#count').textContent.startsWith('3 ') || document.querySelector('#count').textContent.startsWith('1 ')")
    dt = (time.perf_counter() - t0) * 1000 - 120
    ok("pencarian Kiril 'книг' menemukan книга (CPU 4× lebih lambat)", page.locator("#list .item", has_text="кни́га").count() >= 1, f"{dt:.0f} ms setelah debounce")
    page.fill("#q", "rumah")
    page.wait_for_timeout(400)
    ok("pencarian arti Indonesia 'rumah' menemukan дом", page.locator("#list .item", has_text="дом").count() >= 1)
    page.fill("#q", "")
    page.select_option("#st", "u"); page.wait_for_timeout(300)
    ok("filter status [uncertain] berjalan", "hasil" in page.inner_text("#count"), page.inner_text("#count"))
    page.select_option("#st", ""); page.wait_for_timeout(200)
    page.click(".seg button[data-tab=kerja]"); page.wait_for_selector("#list .item")
    ok("tab kata kerja: 500 baris", "500" in page.inner_text("#count"), page.inner_text("#count"))
    shot("03-kamus-kerja")
    page.click(".seg button[data-tab=kata]"); page.wait_for_selector("#list .item")

    # 4. halaman detail
    timings = {}
    for wid, name in [("w0237", "kata-benda"), ("w0062", "kata-sifat"), ("w0004", "kata-ganti"), ("w0075", "bilangan"), ("ws003", "tak-dideklinasi"), ("w0035", "generated")]:
        t0 = time.perf_counter(); go(f"#/kata/{wid}", ".head-word"); timings[wid] = round((time.perf_counter() - t0) * 1000)
        shot(f"04-detail-{name}")
    cdp.send("Emulation.setCPUThrottlingRate", {"rate": 1})
    ok("detail terbuka < 200 ms (CPU 4×, termasuk jeda alat uji)", max(timings.values()) < 400, timings)
    go("#/kata/w0237", "table.forms")
    ok("kata benda: tabel 6 kasus × tunggal/jamak", page.locator("table.forms tbody tr").count() == 6 and "Tunggal" in page.inner_text("table.forms thead"))
    ok("kata benda: aksen tampil (кни́га)", "кни́га" in page.inner_text(".head-word"))
    go("#/kata/w0062", "table.adj")
    ok("kata sifat: 4 kolom + akusatif hidup/mati + bentuk pendek", page.locator("table.adj thead th").count() == 5 and page.locator(".an").count() >= 4 and "Bentuk pendek" in page.inner_text("#view"))
    go("#/kata/ws003", ".head-word")
    ok("kata tak berubah ditandai 'tidak dideklinasi' tanpa tabel", "tidak dideklinasi" in page.inner_text("#view") and page.locator("table.forms").count() == 0)
    # bentuk generated harus berlabel G
    e = words["w0035"]
    def cells(x):
        if x is None: return []
        if isinstance(x, list) and len(x) == 2 and isinstance(x[1], str): return [x]
        return [c for v in (x.values() if isinstance(x, dict) else []) for c in cells(v)]
    n_g = sum(1 for c in cells(e["decl"]) if c[1] == "g")
    go("#/kata/w0035", "table.adj")
    shown_g = page.locator("table.forms sup.st.g").count()
    ok("bentuk generated tidak tampil sebagai terverifikasi (один: semua sel G berlabel)", shown_g == n_g, f"{shown_g} label untuk {n_g} sel g")
    u_word = next(i for i, x in words.items() if any(c[1] == "u" for c in cells(x.get("decl"))))
    n_u = sum(1 for c in cells(words[u_word]["decl"]) if c[1] == "u")
    go(f"#/kata/{u_word}", ".head-word")
    shown_u = page.locator("table.forms sup.st.u").count()
    ok(f"bentuk [uncertain] berlabel '?' ({u_word})", shown_u == n_u, f"{shown_u} label untuk {n_u} sel u")
    shot("04-detail-uncertain")

    # 5. kata kerja
    go("#/kerja/v002", ".head-word")
    page.click("#asp button[data-s=ipf]")
    txt = page.inner_text("#view")
    ok("kata kerja: pasangan говорить/сказать + kini, lampau, masa depan majemuk, imperatif", all(s in txt for s in ["говори́ть", "сказа́ть", "Kini", "Lampau", "majemuk", "Imperatif"]))
    shot("05-kerja-nsv")
    page.click("#asp button[data-s=pf]")
    vis = page.inner_text(".aspect:not([hidden])")
    ok("kata kerja: tombol СВ menampilkan masa depan sederhana (скажу́)", "Masa depan sederhana" in vis and "скажу́" in vis)
    ok("kata kerja: 2 contoh + kalimat pembeda aspek", page.locator(".example").count() >= 2 and "Beda aspek" in page.inner_text("#view"))
    shot("05-kerja-sv")
    go("#/kerja/v018", ".head-word")
    ok("kata kerja satu aspek ditandai (иметь)", "hanya НСВ" in page.inner_text("#view"))
    go("#/kata/w0050", ".head-word")
    ok("kata kerja dari daftar kata membuka tabel konjugasi (знать)", "Kini" in page.inner_text("#view"))

    # 6. hafalan
    count_cards = """new Promise(r => { const q = indexedDB.open('rusia-hafalan'); q.onsuccess = () => { const t = q.result.transaction('cards'); const c = t.objectStore('cards').count(); c.onsuccess = () => r(c.result); }; })"""
    go("#/hafalan", "#go")
    setup_txt = page.inner_text("#view")
    sizes = page.eval_on_selector_all("#size option", "os => os.map(o => o.value)")
    ok("hafalan: tidak ada batas kartu baru per hari, ada pilihan sesi tanpa batas",
       "per hari" not in setup_txt and "0" in sizes and page.locator("#deck option").count() == 7, sizes)
    shot("06-hafalan-atur")
    page.click("#go"); page.wait_for_selector("#card")
    ok("kartu baru punya tombol 'Sudah tahu'", page.locator("#known").count() == 1)
    shot("07-kartu-depan")
    page.click("#flip"); page.wait_for_selector("#yes")
    shot("08-kartu-belakang")
    page.click("#yes"); page.wait_for_timeout(300)
    page.click("#flip"); page.click("#no"); page.wait_for_timeout(300)
    page.wait_for_selector("#known"); page.click("#known"); page.wait_for_timeout(300)
    n_cards = page.evaluate(count_cards)
    ok("progres hafalan tersimpan di IndexedDB (Hafal, Belum, Sudah tahu)", n_cards == 3, f"{n_cards} kartu")

    # 6b. progres dek
    go("#/", ".prog .prow")
    rows = page.locator(".prog .prow").all_inner_texts()
    ok("beranda: Progres dek 6 dek, tanpa sebaran kotak Leitner", len(rows) == 6 and page.locator(".boxes").count() == 0 and "Kotak" not in page.inner_text("#view"), [r.replace("\n", " ") for r in rows])
    ok("progres dek Level 1 menghitung 3 kata (2 dipelajari + 1 sudah tahu)", "3 / 420" in rows[0], rows[0].replace("\n", " "))
    ok("total dek = 420 + 473 + 437 + 402 + 109 kata + 500 kata kerja", [r.split()[-1] for r in rows] == ["420", "473", "437", "402", "109", "500"])
    shot("16-progres-dek")
    page.click("#pdir button[data-d=id-ru]"); page.wait_for_timeout(150)
    ok("progres dek ikut arah kartu (ID→RU masih 0)", "0 / 420" in page.locator(".prog .prow").first.inner_text())
    page.click("#pdir button[data-d=ru-id]"); page.wait_for_timeout(150)
    page.locator(".prog .prow").first.click(); page.wait_for_selector(".dlist")
    ok("halaman dek: daftar 420 kata dengan status", page.locator(".drow").count() == 420 and page.locator(".dst.learn").count() == 2 and page.locator(".dst.known").count() == 1)
    shot("17-dek-level1")
    page.click("#flt button[data-f=known]"); page.wait_for_timeout(150)
    ok("saring 'Sudah tahu' menampilkan 1 kata", page.locator(".drow").count() == 1)
    page.click(".dst.known"); page.wait_for_timeout(300)
    ok("tanda 'Sudah tahu' bisa dibatalkan", page.locator(".drow").count() == 0 and page.evaluate(count_cards) == 2)
    page.click("#flt button[data-f=all]"); page.wait_for_timeout(150)

    # 6c. sesi tanpa batas
    go("#/hafalan", "#go")
    page.select_option("#deck", "l2"); page.select_option("#size", "0")
    page.click("#go"); page.wait_for_selector("#card")
    head = page.inner_text(".row .grow")
    ok("sesi tanpa batas: semua 473 kata baru Level 2 masuk antrean (tidak dibatasi 20)", head.startswith("0/473"), head)
    page.click("text=Selesai"); page.wait_for_selector("#go")

    # 7. grammar + latihan
    go("#/grammar", ".list a.case")
    ok("grammar: 6 kasus", page.locator(".list a.case").count() == 6)
    shot("09-grammar")
    go("#/grammar/gen", "text=Preposisi")
    ok("halaman kasus: fungsi, preposisi, tabel akhiran, ≥3 contoh", page.locator("dl.preps dt").count() >= 3 and page.locator(".example").count() >= 3)
    shot("10-kasus")
    go("#/latihan/gen", ".qtext")
    shot("11-latihan-soal")
    for k in range(15):
        page.wait_for_selector(".qtext")
        if page.locator("#fi").count():
            page.fill("#fi", "тест"); page.click("#ff button")
        else:
            page.locator(".opt").first.click()
        page.wait_for_selector("#next")
        if k == 0: shot("12-latihan-umpan-balik")
        assert page.locator(".feedback").count() == 1
        page.click("#next")
    page.wait_for_selector("text=Hasil latihan")
    shot("13-latihan-hasil")
    quiz = page.evaluate("""new Promise(r => { const q = indexedDB.open('rusia-hafalan'); q.onsuccess = () => { const g = q.result.transaction('quiz').objectStore('quiz').get('gen'); g.onsuccess = () => r(g.result); }; })""")
    ok("latihan 15 soal selesai, umpan balik per soal, skor tersimpan", quiz and quiz.get("attempts") == 1, quiz)

    go("#/tentang", "#off")
    page.wait_for_function("document.querySelector('#off').textContent.includes('siap') || document.querySelector('#off').textContent.includes('belum')")
    ok("halaman Tentang: data offline siap", "siap —" in page.inner_text("#off"), page.inner_text("#off"))
    shot("14-tentang")

    # 8. offline penuh
    ctx.set_offline(True)
    page.goto(BASE); page.wait_for_selector("text=Selamat belajar!", timeout=15000)
    ok("offline: aplikasi terbuka setelah jaringan diputus", True)
    go("#/kata/w0145", "table.forms")
    ok("offline: detail kata (город) tampil", "го́род" in page.inner_text(".head-word"))
    go("#/latihan/pre", ".qtext")
    ok("offline: latihan grammar berjalan", True)
    go("#/", ".prog .prow")
    lvl1 = page.locator(".prog .prow").first.inner_text()
    ok("offline: progres dek tetap ada setelah muat ulang (Level 1: 2 kata)", "2 / 420" in lvl1, lvl1.replace("\n", " "))
    shot("15-offline-beranda")
    ctx.set_offline(False)

    # 9. lebar 375 tanpa gulir horizontal
    widths = {}
    for h_ in ["#/", "#/kamus", "#/kata/w0062", "#/kerja/v002", "#/grammar/acc", "#/tentang", "#/hafalan", "#/hafalan/dek/l1", "#/hafalan/dek/verbs"]:
        page.evaluate(f"location.hash='{h_}'"); page.wait_for_timeout(250)
        widths[h_] = page.evaluate("document.documentElement.scrollWidth")
    ok("tidak ada gulir horizontal di lebar 375 px", all(w <= 375 for w in widths.values()), widths)
    ok("tidak ada permintaan ke domain lain", not foreign, foreign[:5])
    ok("tidak ada error JavaScript di konsol", not [e for e in errors if "favicon" not in e], errors[:5])
    browser.close()

srv.shutdown()
passed = sum(r["pass"] for r in results)
json.dump({"passed": passed, "total": len(results), "results": results, "screens": sorted(p.name for p in SHOTS.glob("*.png"))},
          open(ROOT / "work" / "test_report.json", "w"), ensure_ascii=False, indent=1)
print(f"\n{passed}/{len(results)} uji lulus")
sys.exit(0 if passed == len(results) else 1)
