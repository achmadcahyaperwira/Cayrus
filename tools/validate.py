"""M6: validasi data CayRus + daftar review yang mudah dibaca.

Pemakaian: python3 tools/validate.py
Hasil   : work/validate_report.json, REVIEW.md
"""
import json, re, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"
W = json.load(open(D / "words.json"))["entries"]
V = json.load(open(D / "verbs.json"))
G = json.load(open(D / "grammar.json"))
Q = json.load(open(D / "questions.json"))["questions"]
R = json.load(open(D / "review.json"))
src_words = json.load(open(ROOT / "work/source/words_parsed.json"))
src_verbs = json.load(open(ROOT / "work/source/verbs_parsed.json"))
raw = open(ROOT / "work/source/words_raw.txt").read()
CASES = ["nom", "gen", "dat", "acc", "ins", "pre"]
checks = []


def norm(s):
    return s.replace("́", "").replace("ё", "е").lower().strip()


def check(name, cond, detail=""):
    checks.append({"check": name, "pass": bool(cond), "detail": detail})
    print(("LULUS " if cond else "GAGAL ") + name + (f" — {detail}" if detail else ""))


def cells(x, path=""):
    if x is None:
        return []
    if isinstance(x, list) and len(x) == 2 and isinstance(x[1], str):
        return [(path, x)]
    if isinstance(x, dict):
        return [c for k, v in x.items() for c in cells(v, f"{path}.{k}" if path else k)]
    return []


# 1. jumlah dan cakupan file sumber
svc = re.search(r"служебные слова:(.*?)смысловые", raw, re.S).group(1)
svc2 = re.search(r"2-я ТЫСЯЧА.*?служебные слова:(.*?)\n", raw, re.S).group(1)
service = [w.strip() for w in re.split(r"[,\n]", svc) if w.strip()] + [w.strip() for w in svc2.split(",") if w.strip()]
app_lemmas = {norm(e["lemma"]) for e in W}
src_lemmas = {norm(x["word"]) for x in src_words} | {norm(s) for s in service}
missing = sorted(src_lemmas - app_lemmas)
check("entri kata = 1.841", len(W) == 1841, len(W))
check("setiap kata di file kata ada di aplikasi (1.736 bernomor + 111 kata tugas)", not missing, f"{len(src_lemmas)} lema sumber, hilang: {missing[:10]}")
ranks_src = {x["rank"] for x in src_words}
ranks_app = {r for e in W for r in e.get("rank", [])}
check("setiap peringkat di file kata ada di aplikasi", ranks_src <= ranks_app, f"{len(ranks_src)} peringkat")
check("baris kata kerja = 500, peringkat 1–500 lengkap", len(V["entries"]) == 500 and {e["rank"] for e in V["entries"]} == set(range(1, 501)))
vl = {norm(e["lemma"]) for e in V["entries"]}
check("setiap kata kerja di file kata kerja ada di aplikasi", vl == {norm(x["verb"]) for x in src_verbs})

# 2. kelengkapan entri kata
no_tr = [e["id"] for e in W if not (e.get("translation") or {}).get("text")]
no_ex = [e["id"] for e in W if not (e.get("example") or {}).get("ru") or not e["example"].get("id")]
no_acc = [e["id"] for e in W if not e.get("accented")]
check("setiap entri kata punya terjemahan Indonesia", not no_tr, no_tr[:5])
check("setiap entri kata punya 1 contoh + terjemahan", not no_ex, no_ex[:5])
check("setiap entri punya kata beraksen", not no_acc)
bad_noun, no_gender = [], []
for e in W:
    if e["pos"] == "noun" and not e.get("indeclinable"):
        d = e["decl"]
        if d is None:
            bad_noun.append(e["id"]); continue
        for num in ("sg", "pl"):
            if (num == "pl" and d["number"] == "sg_only") or (num == "sg" and d["number"] == "pl_only"):
                continue
            if any(d[num].get(c) is None for c in CASES):
                bad_noun.append(f"{e['id']}.{num}")
        if not e.get("gender") and norm(e["lemma"]) != "сша":
            no_gender.append(e["id"])
check("setiap kata benda yang dideklinasi punya 6 kasus (tunggal & jamak, kecuali hanya-tunggal/jamak)", not bad_noun, bad_noun[:10])
check("setiap kata benda punya gender", not no_gender, no_gender)
indecl_bad = [e["id"] for e in W if e.get("indeclinable") and e.get("decl")]
check("kata yang tidak dideklinasi tidak punya tabel", not indecl_bad, indecl_bad[:5])
nodecl = [e["id"] for e in W if e["pos"] in ("adj", "pron", "num") and not e.get("indeclinable") and not e.get("decl")]
check("kata sifat/kata ganti/bilangan yang dideklinasi punya tabel", not nodecl, nodecl[:5])

# 3. kata kerja
pairs = {p["id"]: p for p in V["pairs"]}
bad_v = []
for p in V["pairs"]:
    if p["type"] == "pair":
        i, f = p.get("ipf"), p.get("pf")
        if not i or not f:
            bad_v.append(p["id"]); continue
        if len(i.get("pres") or {}) != 6 or len(i.get("past") or {}) != 4 or len(i.get("imp") or {}) != 2:
            bad_v.append(f"{p['id']}.ipf")
        if len(f.get("fut") or {}) != 6 or len(f.get("past") or {}) != 4 or len(f.get("imp") or {}) != 2:
            bad_v.append(f"{p['id']}.pf")
        ex = p.get("examples") or {}
        if not (ex.get("ipf") and ex.get("pf") and ex.get("contrast")):
            bad_v.append(f"{p['id']}.contoh")
    else:
        side = p.get("ipf") or p.get("pf")
        if not side or not side.get("inf"):
            bad_v.append(p["id"])
check("setiap pasangan НСВ/СВ lengkap (kini 6, lampau 4, masa depan 6, imperatif 2) + 2 contoh + kalimat pembeda", not bad_v, bad_v[:10])
types = collections.Counter(p["type"] for p in V["pairs"])
check("kata kerja satu aspek/biaspektual ditandai", types["ipf_only"] + types["pf_only"] + types["biaspectual"] > 0, dict(types))
no_vtr = [e["id"] for e in V["entries"] if not (e.get("translation") or {}).get("text")]
check("setiap baris kata kerja punya terjemahan", not no_vtr, no_vtr[:5])
pair_src = collections.Counter(p["pairSource"] for p in V["pairs"])

# 4. status
wcells = [c for e in W for c in cells(e.get("decl"))]
vcells = [c for p in V["pairs"] for s in ("ipf", "pf") for c in cells(p.get(s))]
allst = collections.Counter(c[1][1] for c in wcells + vcells)
check("status hanya v/g/u", set(allst) <= {"v", "g", "u"}, dict(allst))
u_refs = {e["id"] for e in W if any(c[1][1] == "u" for c in cells(e.get("decl")))} | \
         {p["id"] for p in V["pairs"] if any(c[1][1] == "u" for s in ("ipf", "pf") for c in cells(p.get(s)))}
r_refs = {r["ref"].split(".")[0] for r in R if r["kind"] == "uncertain"}
check("setiap entri dengan bentuk [uncertain] tercatat di daftar review", u_refs <= r_refs, sorted(u_refs - r_refs)[:10])

# 5. grammar dan soal
wid = {e["id"]: e for e in W}
check("modul grammar: 6 kasus, masing-masing ≥ 3 contoh", len(G["cases"]) == 6 and all(len(c["examples"]) >= 3 for c in G["cases"]))
bad_ex = [ex["ru"] for c in G["cases"] for ex in c["examples"]
          if (wid[ex["ref"]["entry"]]["decl"][ex["ref"]["num"]][ex["ref"]["case"]] or [None, "x"])[1] != "v"]
check("contoh grammar memakai bentuk terverifikasi", not bad_ex, bad_ex)
per_case = collections.Counter(q["case"] for q in Q)
check("≥ 15 soal per kasus", all(per_case[c] >= 15 for c in CASES), dict(per_case))
check("3 format soal ada di setiap kasus", all({q["type"] for q in Q if q["case"] == c} == {"mcq", "fill", "pick_case"} for c in CASES))
bad_q = []
for q in Q:
    t = q["target"]; f = wid[t["entry"]]["decl"]["sg"][t["case"]]
    if not f or f[1] != "v":
        bad_q.append(q["id"])
    elif q["type"] != "pick_case" and norm(q["answer"]) not in {norm(x) for x in f[0].split(",")}:
        bad_q.append(q["id"] + " jawaban")
check("soal hanya memakai bentuk berstatus terverifikasi", not bad_q, bad_q[:10])

summary = {
    "entri_kata": len(W), "baris_kata_kerja": len(V["entries"]), "pasangan": len(V["pairs"]), "tipe_pasangan": dict(types),
    "sumber_pasangan": dict(pair_src), "kelas_kata": dict(collections.Counter(e["pos"] for e in W)),
    "bentuk_kata": dict(collections.Counter(c[1][1] for c in wcells)), "bentuk_kata_kerja": dict(collections.Counter(c[1][1] for c in vcells)),
    "review": dict(collections.Counter(r["kind"] for r in R)), "soal": len(Q), "soal_per_kasus": dict(per_case),
    "contoh_kata_kerja": sum(1 for p in V["pairs"] for k in ("ipf", "pf") if (p.get("examples") or {}).get(k)),
}
passed = sum(c["pass"] for c in checks)
json.dump({"passed": passed, "total": len(checks), "checks": checks, "summary": summary},
          open(ROOT / "work/validate_report.json", "w"), ensure_ascii=False, indent=1)
print(f"\n{passed}/{len(checks)} pemeriksaan lulus")
print(json.dumps(summary, ensure_ascii=False))

# 6. REVIEW.md
lemma_of = {e["id"]: e["lemma"] for e in W} | {p["id"]: f"{p.get('ipfLemma') or ''}/{p.get('pfLemma') or ''}".strip("/") for p in V["pairs"]} \
    | {e["id"]: e["lemma"] for e in V["entries"]}
def row(r):
    ref = r["ref"].split(".")[0]
    return f"| {r['ref']} | {lemma_of.get(ref, '')} | {r['field']} | {r['value']} | {r.get('alt', '')} | {r['reason']} |"
unc = [r for r in R if r["kind"] == "uncertain"]
chk = [r for r in R if r["kind"] == "check"]
fix = [r for r in R if r["kind"] == "resolved_g"]
by_entry = collections.Counter(r["ref"].split(".")[0] for r in fix)
lines = [
    "# Daftar review CayRus", "",
    f"Dibuat otomatis oleh `tools/validate.py`. Status: {len(unc)} butir [uncertain], {len(chk)} butir perlu dicek, "
    f"{len(fix)} sel yang dibetulkan manual (status generated). Data lengkap ada di `data/review.json`.", "",
    "Cara membaca: `ref` = id entri (w… kata, v… baris kata kerja, p… pasangan), `kolom` = bagian tabel, `nilai` = yang tampil di aplikasi, `alternatif` = bentuk dari sumber lain.", "",
    "## A. Bentuk [uncertain] (tampil dengan tanda ? kuning)", "",
    "| ref | kata | kolom | nilai | alternatif | alasan |", "| --- | --- | --- | --- | --- | --- |", *[row(r) for r in unc], "",
    "## B. Perlu dicek (kata yang disambung dari potongan baris PDF, pasangan aspek yang dibetulkan)", "",
    "| ref | kata | kolom | nilai | alternatif | alasan |", "| --- | --- | --- | --- | --- | --- |", *[row(r) for r in chk], "",
    "## C. Dibetulkan manual (status generated, tanda G abu-abu)", "",
    "Bentuk dari kamus bertentangan atau kosong, lalu saya isi dengan bentuk baku. Ringkasan per entri:", "",
    "| ref | kata | jumlah sel |", "| --- | --- | --- |", *[f"| {k} | {lemma_of.get(k, '')} | {n} |" for k, n in sorted(by_entry.items())], "",
]
(ROOT / "REVIEW.md").write_text("\n".join(lines), encoding="utf-8")
