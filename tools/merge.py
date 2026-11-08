"""Gabungkan data dasar + batch (terjemahan, contoh, perbaikan) menjadi data aplikasi.

Pemakaian: python3 tools/merge.py
Masukan : work/base_words.json, work/base_verbs.json, work/review_base.json,
          work/batches/Wnn.tsv, Wnn.fix.json, Vnn.tsv, Vnn.fix.json
Hasil   : data/words.json, data/verbs.json, data/review.json, work/merge_report.json
"""
import csv, json, re, sys, collections
from pathlib import Path
import pymorphy3

ROOT = Path(__file__).resolve().parent.parent
W = ROOT / "work"
B = W / "batches"
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)
M = pymorphy3.MorphAnalyzer()
ACUTE = "́"
VOW = "аеёиоуыэюяАЕЁИОУЫЭЮЯ"
LOOK = json.load(open(W / "accent_lookup.json"))
CASES = ["nom", "gen", "dat", "acc", "ins", "pre"]


def norm(s):
    return s.replace(ACUTE, "").replace("'", "").replace("ё", "е").replace("Ё", "Е").strip().lower()


def nvow(s):
    return sum(1 for c in s if c in VOW)


def accent_token(t):
    if ACUTE in t or nvow(t) <= 1 or "ё" in t.lower():
        return t
    c = LOOK.get(norm(t), [])
    c = [x for x in c if ACUTE in x or "ё" in x]
    if len({x.replace("ё", "е") for x in c}) == 1 and len(c) >= 1:
        a = c[0]
        if t.isupper() and len(t) > 1:
            return t
        return a[:1].upper() + a[1:] if t[:1].isupper() else a
    return t


TOKEN = re.compile(r"[А-Яа-яЁё́]+(?:-[А-Яа-яЁё́]+)*")


def accent_sentence(s):
    return TOKEN.sub(lambda m: "-".join(accent_token(p) for p in m.group(0).split("-")), s)


def tokens(s):
    return [p for m in TOKEN.finditer(s) for p in [m.group(0)]]


def cell_forms(d):
    out = []
    if d is None:
        return out
    if isinstance(d, list) and len(d) == 2 and isinstance(d[1], str):
        return [norm(x) for x in d[0].split(",")]
    if isinstance(d, dict):
        for v in d.values():
            out += cell_forms(v)
    return out


def set_path(obj, path, value):
    keys = path.split(".")
    for k in keys[:-1]:
        if obj.get(k) is None:
            obj[k] = {}
        obj = obj[k]
    obj[keys[-1]] = value


def k_is_form(x):
    return x not in ("noun", "adj", "num", "pron", "both", "sg_only", "pl_only")


def apply_fix(rec, path, val, resolved):
    """val: string (status g) atau [bentuk, status]. 'decl.m': 'a|b|c|d/e|f|g' = 6 kasus."""
    if isinstance(val, str) and "|" in val and path.startswith("decl."):
        parts = val.split("|")
        assert len(parts) == 6, (rec["id"], path, val)
        for c, f in zip(CASES, parts):
            if c == "acc" and "/" in f:
                an, ina = f.split("/")
                apply_fix(rec, f"{path}.acc.anim", an, resolved)
                apply_fix(rec, f"{path}.acc.inan", ina, resolved)
            else:
                apply_fix(rec, f"{path}.{c}", f, resolved)
        return
    if path == "decl" and isinstance(val, dict):
        def conv(x):
            if isinstance(x, dict):
                return {k: conv(v) for k, v in x.items()}
            return [x, "g"] if isinstance(x, str) and k_is_form(x) else x
        rec["decl"] = conv(val)
        resolved.add((rec["id"], "decl:*"))
        return
    if path in ("gender", "pos", "number_note", "animate", "indeclinable"):
        rec[path] = val
        return
    if path == "accented":
        rec["accented"] = [val, "g"]
        resolved.add((rec["id"], "accented"))
        return
    if path == "decl.number":
        rec["decl"]["number"] = val
        return
    v = val if isinstance(val, list) else ([val, "g"] if val not in ("-", "—", None) else None)
    set_path(rec, path, v)
    key = path[5:] if path.startswith("decl.short.") else path
    resolved.add((rec["id"], key))
    resolved.add((rec["id"], key.replace("decl.cols.", "decl.")))


def read_tsv(path):
    rows = {}
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        rows[parts[0].strip()] = [p.strip() for p in parts[1:]]
    return rows


base_w = json.load(open(W / "base_words.json"))["entries"]
base_v = json.load(open(W / "base_verbs.json"))
review = json.load(open(W / "review_base.json"))
plan = json.load(open(B / "plan.json"))
wid = {e["id"]: e for e in base_w}
report = {"batches": {}, "problems": []}
resolved = set()

# --- batch kata -------------------------------------------------------------
for bname, ids in plan.items():
    tsv = read_tsv(B / f"{bname}.tsv")
    fix = json.load(open(B / f"{bname}.fix.json")) if (B / f"{bname}.fix.json").exists() else {}
    if not tsv and not fix:
        continue
    rep = {"entries": len(ids), "written": 0, "linked_verbs": 0, "examples": 0, "fixes": 0, "problems": []}
    for i in ids:
        e = wid[i]
        if e.get("verbRef") and e["verbRef"]["entry"]:
            rep["linked_verbs"] += 1
            if i in tsv:
                rep["problems"].append(f"{i}: kata kerja terhubung tidak perlu baris W")
            continue
        row = tsv.get(i)
        if not row or len(row) < 3:
            rep["problems"].append(f"{i} {e['lemma']}: baris hilang/tidak lengkap")
            continue
        tr, ex_ru, ex_id = row[0], row[1], row[2]
        e["translation"] = {"text": tr, "s": "g"}
        e["example"] = {"ru": accent_sentence(ex_ru), "id": ex_id, "s": "g"}
        if len(row) > 3 and row[3]:
            e.setdefault("notes", []).append(row[3])
        rep["written"] += 1
        rep["examples"] += 1
    for i, fx in fix.items():
        for path, val in fx.items():
            apply_fix(wid[i], path, val, resolved)
            rep["fixes"] += 1
    # cek contoh: semua token dikenal, dan kata entri muncul di kalimat
    for i in ids:
        e = wid[i]
        ex = e.get("example")
        if not ex:
            continue
        toks = tokens(ex["ru"])
        forms = set(cell_forms(e.get("decl"))) | {norm(e["lemma"])}
        hit = False
        for t in toks:
            for part in t.split("-"):
                nt = norm(part)
                if nt in forms or any(norm(p.normal_form) == norm(e["lemma"]) for p in M.parse(nt)):
                    hit = True
                if not M.word_is_known(nt):
                    rep["problems"].append(f"{i}: kata tidak dikenal '{part}' di contoh")
        if not hit:
            rep["problems"].append(f"{i} {e['lemma']}: kata entri tidak ditemukan di contoh")
    report["batches"][bname] = rep

# --- review: tandai yang sudah dibetulkan ------------------------------------
final_review = []
for r in review:
    key = (r["ref"], r["field"])
    if key in resolved or ((r["ref"], "decl:*") in resolved and (r["field"].startswith("decl.") or r["field"].startswith("short."))):
        r = dict(r, kind="resolved_g", reason=r["reason"] + " → dibetulkan manual, status g")
        # nilai baru diambil dari entri
    final_review.append(r)

# --- keluaran ---------------------------------------------------------------
KEEP = ["id", "rank", "lemma", "accented", "pos", "service", "gender", "animate", "indeclinable",
        "decl", "verbRef", "translation", "example", "notes", "flags"]
words_out = [{k: e.get(k) for k in KEEP if e.get(k) not in (None, [], False) or k in ("decl", "indeclinable")}
             for e in sorted(base_w, key=lambda e: (e["rank"][0] if e["rank"] else 10000, e["id"]))]
json.dump({"meta": {"count": len(words_out)}, "entries": words_out},
          open(DATA / "words.json", "w"), ensure_ascii=False, separators=(",", ":"))
json.dump(final_review, open(DATA / "review.json", "w"), ensure_ascii=False, indent=0)
json.dump(report, open(W / "merge_report.json", "w"), ensure_ascii=False, indent=1)
for b, r in report["batches"].items():
    print(b, {k: v for k, v in r.items() if k != "problems"}, "masalah:", len(r["problems"]))
    for p in r["problems"][:40]:
        print("   ", p)
