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

# --- batch kata kerja --------------------------------------------------------
pairs = {p["id"]: p for p in base_v["pairs"]}
ventries = base_v["entries"]
vplan = {}
file_pairs = []
for e in ventries:
    if e["pairId"] not in file_pairs:
        file_pairs.append(e["pairId"])
for k in range(3):
    vplan[f"V{k + 1:02d}"] = file_pairs[k * 130:(k + 1) * 130] if k < 2 else file_pairs[260:]
json.dump(vplan, open(B / "vplan.json", "w"), indent=0)


def side_forms(side):
    return set(cell_forms(side)) if side else set()


# perbaikan per baris kata kerja (kunci vNNN) dari semua file fix V
for fpath in sorted(B.glob("V*.fix.json")):
    for key, fx in json.load(open(fpath)).items():
        if key.startswith("v"):
            for e in ventries:
                if e["id"] == key:
                    e.update(fx)
_vid = {e["id"]: e for e in ventries}
for e in base_w:
    ref = e.get("verbRef")
    if ref and ref.get("entry"):
        ref["pair"] = _vid[ref["entry"]]["pairId"]
referenced = {e["pairId"] for e in ventries} | {e["verbRef"]["pair"] for e in base_w if e.get("verbRef")}
dropped = [pid for pid in pairs if pid not in referenced]
for pid in dropped:
    pairs.pop(pid)
vplan = {k: [pid for pid in v if pid in pairs] for k, v in vplan.items()}

for bname, pids in vplan.items():
    tsv = read_tsv(B / f"{bname}.tsv")
    fix = json.load(open(B / f"{bname}.fix.json")) if (B / f"{bname}.fix.json").exists() else {}
    if not tsv and not fix:
        continue
    rep = {"pairs": len(pids), "rows": sum(1 for e in ventries if e["pairId"] in set(pids)),
           "written": 0, "examples": 0, "fixes": 0, "problems": []}
    for pid, fx in fix.items():
        if pid.startswith("v") or pid not in pairs:
            continue
        for path, val in fx.items():
            pr = pairs[pid]
            if path in ("pairSource", "pairNote", "type", "aspectNote"):
                pr[path] = val
            elif path.endswith(".aspect") and val == "ok":
                resolved.add((pid, path))
            else:
                v = val if isinstance(val, list) else ([val, "g"] if val not in ("-", None) else None)
                set_path(pr, path, v)
                rest = ".".join(path.split(".")[1:])
                resolved.add((f"{pid}.{path.split('.')[0]}", rest))
                resolved.add((f"{pid}.{path.split('.')[0]}", rest.replace("fut.", "pres.")))
                resolved.add((pid, path))
            rep["fixes"] += 1
    for pid in pids:
        pr = pairs[pid]
        row = tsv.get(pid)
        if not row:
            rep["problems"].append(f"{pid}: baris hilang")
            continue
        row = row + [""] * (7 - len(row))
        tr_ipf, tr_pf, ex1, ex1id, ex2, ex2id, contrast = row[:7]
        pr["translation"] = {"ipf": tr_ipf or None, "pf": tr_pf or None, "s": "g"}
        pr["examples"] = {}
        for side, ru, idn in (("ipf", ex1, ex1id), ("pf", ex2, ex2id)):
            if ru:
                pr["examples"][side] = {"ru": accent_sentence(ru), "id": idn, "s": "g"}
                rep["examples"] += 1
                lem = pr[f"{side}Lemma"] if pr["type"] != "biaspectual" else (pr["ipfLemma"] or pr["pfLemma"])
                forms = side_forms(pr.get(side)) | {norm(lem)}
                if pr["type"] == "biaspectual":
                    forms |= side_forms(pr.get("ipf")) | side_forms(pr.get("pf"))
                hit = False
                for t in tokens(ru):
                    for part in t.split("-"):
                        nt = norm(part)
                        if nt in forms or any(norm(p.normal_form) == norm(lem) for p in M.parse(nt)):
                            hit = True
                        if not M.word_is_known(nt):
                            rep["problems"].append(f"{pid}: kata tidak dikenal '{part}'")
                if not hit:
                    rep["problems"].append(f"{pid} {side} {lem}: kata kerja tidak ditemukan di contoh")
        if contrast:
            pr["examples"]["contrast"] = contrast
        need = [s for s in ("ipf", "pf") if pr.get(f"{s}Lemma")]
        if pr["type"] == "pair" and not (ex1 and ex2):
            rep["problems"].append(f"{pid}: pasangan butuh 2 contoh")
        if pr["type"] != "pair" and not (ex1 or ex2):
            rep["problems"].append(f"{pid}: butuh 1 contoh")
        rep["written"] += 1
    report["batches"][bname] = rep

# terjemahan tiap baris kata kerja + salin ke entri kata yang terhubung
for e in ventries:
    pr = pairs[e["pairId"]]
    tr = pr.get("translation")
    if tr:
        side = "pf" if e["aspect"] == "pf" else "ipf"
        e["translation"] = {"text": tr.get(side) or tr.get("ipf") or tr.get("pf"), "s": "g"}
ve_by_id = {e["id"]: e for e in ventries}
for e in base_w:
    ref = e.get("verbRef")
    if ref and ref.get("entry") and ve_by_id[ref["entry"]].get("translation"):
        ve = ve_by_id[ref["entry"]]
        e["translation"] = ve["translation"]
        pr = pairs[ve["pairId"]]
        side = "pf" if ve["aspect"] == "pf" else "ipf"
        ex = (pr.get("examples") or {}).get(side) or (pr.get("examples") or {}).get("ipf")
        if ex:
            e["example"] = ex

# --- review: tandai yang sudah dibetulkan ------------------------------------
final_review = []
review = [r for r in review if r["ref"].split(".")[0] not in set(dropped)]
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
json.dump({"meta": {"rows": len(ventries), "pairs": len(pairs)}, "pairs": list(pairs.values()), "entries": ventries},
          open(DATA / "verbs.json", "w"), ensure_ascii=False, separators=(",", ":"))
json.dump(final_review, open(DATA / "review.json", "w"), ensure_ascii=False, indent=0)
json.dump(report, open(W / "merge_report.json", "w"), ensure_ascii=False, indent=1)
for b, r in report["batches"].items():
    print(b, {k: v for k, v in r.items() if k != "problems"}, "masalah:", len(r["problems"]))
    for p in r["problems"][:40]:
        print("   ", p)
