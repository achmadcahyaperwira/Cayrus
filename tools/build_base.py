"""Tahap A: gabungkan daftar kata dari file dengan bentuk OpenRussian + pymorphy3.

Pemakaian: python3 tools/build_base.py <folder-openrussian>
Hasil: work/base_words.json, work/base_verbs.json, work/review_base.json, work/accent_lookup.json
"""
import csv, json, re, sys, collections
from pathlib import Path
import pymorphy3

ROOT = Path(__file__).resolve().parent.parent
ORD = Path(sys.argv[1])
SRC = ROOT / "work" / "source"
OUT = ROOT / "work"
M = pymorphy3.MorphAnalyzer()
ACUTE = "́"
VOWELS = "аеёиоуыэюяАЕЁИОУЫЭЮЯ"
CASES = ["nom", "gen", "dat", "acc", "ins", "pre"]
PM_CASE = {"nom": "nomn", "gen": "gent", "dat": "datv", "acc": "accs", "ins": "ablt", "pre": "loct"}
ORD_CASE = {"nom": "nom", "gen": "gen", "dat": "dat", "acc": "acc", "ins": "inst", "pre": "prep"}
review = []


def norm(s):
    return s.replace(ACUTE, "").replace("'", "").replace("ё", "е").replace("Ё", "Е").strip().lower()


def nvow(s):
    return sum(1 for c in s if c in VOWELS)


def acc_ord(s):
    """'челове'к' -> 'челове́к'; tanda dibuang untuk kata satu suku dan kata dengan ё."""
    s = s.strip().strip("*/").strip()
    if not s:
        return ""
    out = s.replace("'", ACUTE)
    plain = out.replace(ACUTE, "")
    if nvow(plain) <= 1 or "ё" in plain.lower():
        return plain
    return out


def split_vars(cell):
    return [v for v in (acc_ord(x) for x in re.split(r"[,;/]", cell or "")) if v]


def load(name):
    d = collections.defaultdict(list)
    with open(ORD / f"{name}.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter="\t"):
            d[norm(r["bare"])].append(r)
    return d


T = {n: load(n) for n in ("nouns", "adjectives", "verbs", "others")}

# --- kamus aksen global: bentuk tanpa aksen -> bentuk beraksen -------------
LOOK = collections.defaultdict(set)
for tname, tab in T.items():
    for rows in tab.values():
        for r in rows:
            for k, v in r.items():
                if k in ("bare", "accented") or re.match(r"(sg|pl)_|decl_|short_|past_|presfut_|imperative_", k or ""):
                    for x in split_vars(v or ""):
                        if re.fullmatch(r"[а-яёА-ЯЁ́\-]+", x):
                            LOOK[norm(x)].add(x.lower())


def accent(word):
    """Beri aksen bila hanya ada satu kemungkinan; None bila ambigu/tidak dikenal."""
    w = word.replace(ACUTE, "")
    if nvow(w) <= 1 or "ё" in w.lower():
        return w
    c = {x for x in LOOK.get(norm(w), set()) if ACUTE in x or nvow(x) <= 1 or "ё" in x}
    if len(c) == 1:
        a = c.pop()
        return a[0].upper() + a[1:] if w[:1].isupper() else a
    return None


def pm_parse(lemma, pos_set):
    for p in M.parse(lemma):
        if p.tag.POS in pos_set and norm(p.normal_form) == norm(lemma):
            return p
    return None


def pm_forms(p, need, exclude=()):
    """Semua bentuk dalam leksem yang tagnya memuat semua 'need'."""
    if p is None:
        return []
    out = []
    for f in p.lexeme:
        if all(t in f.tag for t in need) and not any(t in f.tag for t in exclude):
            if f.word not in out:
                out.append(f.word)
    return out


def decide(ref, field, ord_cell, pm_list, allow_empty=False):
    """Kembalikan [bentuk, status] atau None, sesuai aturan status PRD bagian 8."""
    ov = split_vars(ord_cell)
    pm = {norm(x) for x in pm_list}
    if ov:
        good = [v for v in ov if norm(v) in pm]
        if good and len(good) == len(ov):
            return [", ".join(good), "v"]
        if good:
            review.append({"ref": ref, "field": field, "value": ", ".join(good),
                           "alt": ", ".join(x for x in ov if x not in good),
                           "reason": "varian OpenRussian tidak dikenal pymorphy3; varian ini dibuang", "kind": "info"})
            return [", ".join(good), "v"]
        review.append({"ref": ref, "field": field, "value": ", ".join(ov), "alt": ", ".join(pm_list),
                       "reason": "OpenRussian dan pymorphy3 berbeda", "kind": "uncertain"})
        return [", ".join(ov), "u"]
    if pm_list:
        if allow_empty:
            return None
        forms = [accent(x) or x for x in pm_list]
        review.append({"ref": ref, "field": field, "value": ", ".join(forms), "alt": "",
                       "reason": "OpenRussian kosong; bentuk dari pymorphy3 saja", "kind": "uncertain"})
        return [", ".join(forms), "u"]
    return None


def one_source(ref, field, pm_list, why):
    if not pm_list:
        return None
    forms = []
    unacc = False
    for x in pm_list:
        a = accent(x)
        unacc |= a is None
        forms.append(a or x)
    st = "g"
    if unacc:
        st = "u"
        review.append({"ref": ref, "field": field, "value": ", ".join(forms), "alt": "",
                       "reason": why + "; aksen tidak bisa dipastikan", "kind": "uncertain"})
    return [", ".join(forms), st]


# --- bentuk per kelas kata -------------------------------------------------
def noun_decl(ref, lemma, row, p):
    num = "both"
    if row is not None:
        if row["sg_only"] == "1":
            num = "sg_only"
        elif row["pl_only"] == "1":
            num = "pl_only"
    elif p is not None and "Pltm" in p.tag:
        num = "pl_only"
    d = {"type": "noun", "number": num, "sg": {}, "pl": {}}
    for n, pmn in (("sg", "sing"), ("pl", "plur")):
        skip = (num == "sg_only" and n == "pl") or (num == "pl_only" and n == "sg")
        for c in CASES:
            pmf = pm_forms(p, {pmn, PM_CASE[c]})
            if skip:
                d[n][c] = None
                continue
            cell = row[f"{n}_{ORD_CASE[c]}"] if row is not None else ""
            d[n][c] = decide(ref, f"decl.{n}.{c}", cell, pmf)
    return d


def adj_decl(ref, row, p):
    d = {"type": "adj"}
    for g, pmg in (("m", "masc"), ("n", "neut"), ("f", "femn"), ("pl", "plur")):
        d[g] = {}
        for c in CASES:
            need = {pmg, PM_CASE[c]}
            cell = row[f"decl_{g}_{ORD_CASE[c]}"] if row is not None else ""
            if c == "acc" and g in ("m", "pl"):
                an = pm_forms(p, need | {"anim"}) or pm_forms(p, need)
                ina = pm_forms(p, need | {"inan"}) or pm_forms(p, need)
                ov = split_vars(cell)
                nom = {norm(x) for x in split_vars(row[f"decl_{g}_nom"])} if row is not None else set()
                o_an = ", ".join(x for x in ov if norm(x) not in nom) if ov else ""
                o_in = ", ".join(x for x in ov if norm(x) in nom) if ov else ""
                if ov and not o_an:
                    o_an = o_in
                d[g][c] = {"anim": decide(ref, f"decl.{g}.acc.anim", o_an, an),
                           "inan": decide(ref, f"decl.{g}.acc.inan", o_in, ina)}
            else:
                d[g][c] = decide(ref, f"decl.{g}.{c}", cell, pm_forms(p, need, exclude={"ADJS"}))
    short = {}
    any_short = False
    for g, pmg in (("m", "masc"), ("n", "neut"), ("f", "femn"), ("pl", "plur")):
        pmf = pm_forms(p, {"ADJS", pmg})
        cell = row[f"short_{g}"] if row is not None else ""
        if split_vars(cell) or pmf:
            any_short = True
        short[g] = decide(ref, f"short.{g}", cell, pmf, allow_empty=True) if split_vars(cell) else None
    d["short"] = short if any(short.values()) else None
    return d


def pron_decl(ref, lemma, p):
    d = {"type": "pron", "forms": {}, "afterPrep": {}}
    for c in CASES:
        f = pm_forms(p, {PM_CASE[c]}, exclude={"Af-p"})
        if lemma in ("он", "она", "оно", "они"):
            gn = {"он": {"masc"}, "оно": {"neut"}, "она": {"femn"}, "они": {"plur"}}[lemma]
            f = pm_forms(p, {PM_CASE[c]} | gn, exclude={"Af-p"})
            ap = pm_forms(p, {PM_CASE[c], "Af-p"} | gn)
            if ap:
                d["afterPrep"][c] = one_source(ref, f"decl.afterPrep.{c}", ap, "kata ganti: satu sumber (pymorphy3)")
        d["forms"][c] = one_source(ref, f"decl.forms.{c}", f, "kata ganti: satu sumber (pymorphy3)")
    if not d["afterPrep"]:
        d["afterPrep"] = None
    return d


def num_decl(ref, lemma, p):
    gendered = lemma in ("два", "оба", "полтора")
    d = {"type": "num"}
    if gendered:
        d["cols"] = {}
        for g, need in (("mn", {"masc"}), ("f", {"femn"})):
            col = {}
            for c in CASES:
                f = pm_forms(p, {PM_CASE[c]} | need) or pm_forms(p, {PM_CASE[c]})
                col[c] = one_source(ref, f"decl.{g}.{c}", f, "bilangan: satu sumber (pymorphy3)")
            d["cols"][g] = col
    else:
        d["forms"] = {c: one_source(ref, f"decl.forms.{c}", pm_forms(p, {PM_CASE[c]}),
                                    "bilangan: satu sumber (pymorphy3)") for c in CASES}
    return d


def verb_forms(ref, inf, row, p):
    asp = None
    if row is not None:
        asp = {"imperfective": "ipf", "perfective": "pf"}.get(row["aspect"])
    if asp is None and p is not None:
        asp = "pf" if "perf" in p.tag else "ipf"
    tense = "futr" if asp == "pf" else "pres"
    out = {"inf": [acc_ord(row["accented"]) if row is not None else (accent(inf) or inf),
                   "v" if row is not None and p is not None else "u"]}
    pers = {"1sg": {"1per", "sing"}, "2sg": {"2per", "sing"}, "3sg": {"3per", "sing"},
            "1pl": {"1per", "plur"}, "2pl": {"2per", "plur"}, "3pl": {"3per", "plur"}}
    ocol = {"1sg": "presfut_sg1", "2sg": "presfut_sg2", "3sg": "presfut_sg3",
            "1pl": "presfut_pl1", "2pl": "presfut_pl2", "3pl": "presfut_pl3"}
    key = "fut" if asp == "pf" else "pres"
    out[key] = {k: decide(ref, f"{key}.{k}", row[ocol[k]] if row is not None else "",
                          pm_forms(p, need | {tense, "indc"})) for k, need in pers.items()}
    out["past"] = {g: decide(ref, f"past.{g}", row[f"past_{g}"] if row is not None else "",
                             pm_forms(p, need | {"past", "indc"}))
                   for g, need in (("m", {"masc", "sing"}), ("f", {"femn", "sing"}),
                                   ("n", {"neut", "sing"}), ("pl", {"plur"}))}
    out["imp"] = {n: decide(ref, f"imp.{n}", row[f"imperative_{n}"] if row is not None else "",
                            pm_forms(p, {"impr", "excl", pn}))
                  for n, pn in (("sg", "sing"), ("pl", "plur"))}
    return asp, out


# --- sumber: file kata ----------------------------------------------------
words = json.load(open(SRC / "words_parsed.json"))
raw = open(SRC / "words_raw.txt").read()
svc1 = re.search(r"служебные слова:(.*?)смысловые", raw, re.S).group(1)
svc2 = re.search(r"2-я ТЫСЯЧА.*?служебные слова:(.*?)\n", raw, re.S).group(1)
service = [w.strip() for w in re.split(r"[,\n]", svc1) if w.strip()] + [w.strip() for w in svc2.split(",") if w.strip()]

ODD_SPELLING = {"придтись": "ejaan tidak baku; bentuk baku прийтись",
                "честной": "kemungkinan maksudnya честный",
                "столовый": "kemungkinan maksudnya столовая (ruang makan)",
                "лед": "ejaan tanpa ё: лёд", "твердый": "ejaan tanpa ё: твёрдый",
                "серьезно": "ejaan tanpa ё: серьёзно", "насчет": "ejaan tanpa ё: насчёт",
                "пошлый": "arti 'vulgar'; periksa apakah maksudnya прошлый (sudah ada #269)",
                "кой": "kata arkais (кой = какой)"}
FORCE_POS = {("знать", 569): "noun", ("правда", None): "noun", ("мало", None): "adv", ("что", None): "pron", ("хотеться", None): "verb"}

entries = {}
order = []
for w in sorted(words, key=lambda x: x["rank"]):
    lem = w["word"]
    key = norm(lem)
    if key == "знать" and w["rank"] == 569:
        key = "знать#2"
    if key in entries:
        entries[key]["rank"].append(w["rank"])
        entries[key]["flags"].append("ganda_digabung")
        continue
    e = {"lemma": lem, "rank": [w["rank"]], "service": False, "flags": []}
    if " " in w["raw"]:
        e["flags"].append("disambung_dari_potongan_baris")
        review.append({"ref": key, "field": "lemma", "value": lem, "alt": w["raw"],
                       "reason": "kata terpotong tanda hubung di PDF, disambung otomatis", "kind": "check"})
    entries[key] = e
    order.append(key)
for s in service:
    key = norm(s)
    if key in entries:
        entries[key]["service"] = True
        continue
    entries[key] = {"lemma": s, "rank": [], "service": True, "flags": []}
    order.append(key)

# --- sumber: file kata kerja ----------------------------------------------
verbs = json.load(open(SRC / "verbs_parsed.json"))
TYPO = {"понесит": "понести"}
SPECIAL = {"приехать": ("приезжать", "приехать", "file_corrected", "file menulis ехать/поехать"),
           "проходить": ("проходить", "пройти", "file_corrected", "file menulis происходить/произойти"),
           "придтись": ("приходиться", "прийтись", "file_corrected", "ejaan tidak baku dari прийтись"),
           "готовиться": ("готовиться", "приготовиться", "uncertain", "file menulis готовить/приготовить")}


def ord_row(table, lemma):
    r = T[table].get(norm(lemma))
    return r[0] if r else None


META_COLS = {"bare", "accented", "translations_en", "translations_de", "partner", "aspect", "gender", "animate",
             "indeclinable", "sg_only", "pl_only", "comparative", "superlative"}


def best_row(table, lemma, p):
    """Untuk homograf: pilih baris OpenRussian yang bentuknya paling cocok dengan leksem pymorphy3."""
    rows = T[table].get(norm(lemma)) or []
    if not rows:
        return None
    if p is None or len(rows) == 1:
        return rows[0]
    lex = {norm(f.word) for f in p.lexeme}
    def score(r):
        return sum(1 for k, v in r.items() if k not in META_COLS for x in split_vars(v or "") if norm(x) in lex)
    return max(rows, key=score)


def ord_aspect(v):
    r = ord_row("verbs", v)
    return r["aspect"] if r else ""


pairs, pair_index, ventries = [], {}, []


def get_pair(ipf, pf, ptype, source, note):
    k = (norm(ipf or ""), norm(pf or ""), ptype)
    if k in pair_index:
        return pair_index[k]
    pid = f"p{len(pairs) + 1:03d}"
    pair_index[k] = pid
    pairs.append({"id": pid, "type": ptype, "ipfLemma": ipf, "pfLemma": pf,
                  "pairSource": source, "pairNote": note})
    return pid


for v in verbs:
    lem = v["verb"]
    ps = re.sub(r"/\s+", "/", v["pair"]).strip()
    ref = f"v{v['rank']:03d}"
    note = ""
    if lem in SPECIAL:
        ipf, pf, src, note = SPECIAL[lem]
        pid = get_pair(ipf, pf, "pair", src, note)
        review.append({"ref": ref, "field": "pair", "value": f"{ipf}/{pf}", "alt": ps,
                       "reason": note, "kind": "uncertain" if src == "uncertain" else "check"})
        aspect = "ipf" if norm(lem) == norm(ipf) else "pf"
        if lem == "придтись":
            aspect = "pf"
    elif "/" in ps:
        a, b = [TYPO.get(x.strip(), x.strip()) for x in ps.split("/")[:2]]
        src = "file"
        if TYPO.keys() & set(x.strip() for x in ps.split("/")):
            src, note = "file_corrected", "salah ketik di file diperbaiki"
        if ord_aspect(a) == "perfective" and ord_aspect(b) == "imperfective":
            a, b = b, a
            src, note = "file_corrected", "urutan НСВ/СВ di file terbalik"
        partners = set()
        for x in (a, b):
            r = ord_row("verbs", x)
            if r and r["partner"].strip() not in ("", "-"):
                partners |= {norm(y) for y in re.split(r"[;,]", r["partner"]) if y.strip()}
        r_a, r_b = ord_row("verbs", a), ord_row("verbs", b)
        pa = {norm(y) for y in re.split(r"[;,]", r_a["partner"])} if r_a and r_a["partner"].strip() not in ("", "-") else set()
        pb = {norm(y) for y in re.split(r"[;,]", r_b["partner"])} if r_b and r_b["partner"].strip() not in ("", "-") else set()
        if (pa and norm(b) not in pa) and (pb and norm(a) not in pb) or (pa and not pb and norm(b) not in pa) or (pb and not pa and norm(a) not in pb):
            src = "uncertain"
            note = (note + "; " if note else "") + "OpenRussian mencatat pasangan lain: " + ", ".join(sorted((pa | pb) - {norm(a), norm(b)}))
            review.append({"ref": ref, "field": "pair", "value": f"{a}/{b}", "alt": ", ".join(sorted(pa | pb)),
                           "reason": "pasangan aspek di file berbeda dengan OpenRussian", "kind": "uncertain"})
        elif src == "file_corrected":
            review.append({"ref": ref, "field": "pair", "value": f"{a}/{b}", "alt": ps, "reason": note, "kind": "check"})
        pid = get_pair(a, b, "pair", src, note)
        aspect = "ipf" if norm(lem) == norm(a) else "pf"
    else:
        low = ps.lower()
        if "imperf. and perfective" in low:
            ptype = "biaspectual"
        elif low.startswith("perfective"):
            ptype = "pf_only"
        else:
            ptype = "ipf_only"
        if not ps:
            note = "kolom pasangan kosong di file"
            review.append({"ref": ref, "field": "pair", "value": ptype, "alt": "",
                           "reason": "kolom pasangan aspek kosong di file; aspek dari OpenRussian", "kind": "check"})
        pid = get_pair(lem if ptype != "pf_only" else None, lem if ptype == "pf_only" else None, ptype, "file", note)
        pairs[int(pid[1:]) - 1]["fileNote"] = ps
        aspect = {"pf_only": "pf", "ipf_only": "ipf", "biaspectual": "both"}[ptype]
    ventries.append({"id": ref, "rank": v["rank"], "lemma": lem, "aspect": aspect, "pairId": pid,
                     "file": {"en": v["en"], "pair": ps}})

verb_lemmas = {norm(v["lemma"]): v for v in ventries}

# --- kata: kelas kata dan bentuk -------------------------------------------
POSMAP = {"NOUN": "noun", "INFN": "verb", "VERB": "verb", "ADJF": "adj", "ADJS": "adj", "PRTF": "adj",
          "NPRO": "pron", "NUMR": "num", "ADVB": "adv", "PREP": "prep", "CONJ": "conj",
          "PRCL": "part", "INTJ": "intj", "PRED": "pred", "COMP": "adv"}
out_words = []
pos_count = collections.Counter()
for i, key in enumerate(order):
    e = entries[key]
    lem = e["lemma"]
    rank0 = e["rank"][0] if e["rank"] else None
    wid = f"w{rank0:04d}" if rank0 else f"ws{len([k for k in order[:i] if not entries[k]['rank']]) + 1:03d}"
    forced = FORCE_POS.get((norm(lem), rank0)) or FORCE_POS.get((norm(lem), None))
    pos = forced
    if pos is None:
        for p in M.parse(lem):
            if norm(p.normal_form) == norm(lem):
                pos = POSMAP.get(p.tag.POS)
                break
    if norm(lem) in verb_lemmas and key != "знать#2":
        pos = "verb"
    if pos is None:
        pos = "noun" if norm(lem) in T["nouns"] else "adj" if norm(lem) in T["adjectives"] else "other"
    if e["service"] and pos not in ("pron", "verb"):
        pos = pos if pos in ("prep", "conj", "part", "intj", "pred", "adv") else "part"
    nrow = ord_row("nouns", lem)
    arow = ord_row("adjectives", lem)
    if pos == "noun" and nrow is None and arow is not None:
        pos = "adj"
    rec = {"id": wid, "rank": e["rank"], "lemma": lem, "pos": pos, "service": e["service"],
           "flags": e["flags"], "gender": None, "animate": None, "indeclinable": False,
           "decl": None, "verbRef": None}
    if norm(lem) in ODD_SPELLING:
        rec["flags"].append("ejaan_janggal")
        review.append({"ref": wid, "field": "lemma", "value": lem, "alt": "",
                       "reason": ODD_SPELLING[norm(lem)], "kind": "uncertain"})
    anyrow = nrow if pos == "noun" else arow if pos == "adj" else ord_row("verbs", lem) if pos == "verb" else None
    anyrow = anyrow or nrow or arow or ord_row("others", lem) or ord_row("verbs", lem)
    if anyrow is not None:
        rec["accented"] = [acc_ord(anyrow["accented"]), "v"]
        rec["ref_en"] = (anyrow.get("translations_en") or "")[:120]
    else:
        a = accent(lem)
        rec["accented"] = [a or lem, "v" if a else "u"]
        rec["ref_en"] = ""
        if not a:
            review.append({"ref": wid, "field": "accented", "value": lem, "alt": "",
                           "reason": "aksen tidak ditemukan di OpenRussian", "kind": "uncertain"})
    if lem[:1].isupper() and rec["accented"][0][:1].islower():
        rec["accented"][0] = rec["accented"][0][:1].upper() + rec["accented"][0][1:]
    if pos == "noun":
        cands = [q for q in M.parse(lem) if q.tag.POS == "NOUN" and norm(q.normal_form) == norm(lem)]
        gmap = {"m": "masc", "f": "femn", "n": "neut"}
        want = gmap.get(nrow["gender"]) if nrow else None
        p = next((q for q in cands if want and want in q.tag), cands[0] if cands else None)
        nrow = best_row("nouns", lem, p) if nrow is not None else None
        rec["gender"] = {"m": "m", "f": "f", "n": "n", "pl": "pl"}.get(nrow["gender"]) if nrow else (
            "m" if p and "masc" in p.tag else "f" if p and "femn" in p.tag else "n" if p and "neut" in p.tag else None)
        rec["animate"] = (nrow["animate"] == "1") if nrow else (bool(p and "anim" in p.tag) if p else None)
        if (nrow and nrow["indeclinable"] == "1") or (p and "Fixd" in p.tag):
            rec["indeclinable"] = True
        else:
            rec["decl"] = noun_decl(wid, lem, nrow, p)
    elif pos == "adj":
        p = pm_parse(lem, {"ADJF"})
        arow = best_row("adjectives", lem, p) if arow is not None else None
        rec["decl"] = adj_decl(wid, arow, p)
    elif pos == "pron":
        p = pm_parse(lem, {"NPRO"})
        rec["decl"] = pron_decl(wid, norm(lem), p) if p else None
        rec["indeclinable"] = rec["decl"] is None
    elif pos == "num":
        p = pm_parse(lem, {"NUMR"})
        rec["decl"] = num_decl(wid, norm(lem), p) if p else None
        rec["indeclinable"] = rec["decl"] is None
    elif pos == "verb":
        if norm(lem) in verb_lemmas:
            ve = verb_lemmas[norm(lem)]
            rec["verbRef"] = {"entry": ve["id"], "pair": ve["pairId"]}
        else:
            asp = ord_aspect(lem)
            ptype = "pf_only" if asp == "perfective" else "ipf_only"
            pid = get_pair(lem if ptype == "ipf_only" else None, lem if ptype == "pf_only" else None,
                           ptype, "not_in_file", "pasangan aspek tidak tercantum di file")
            rec["verbRef"] = {"entry": None, "pair": pid}
    else:
        rec["indeclinable"] = True
    d = rec["decl"]
    if d and d.get("type") == "noun":
        if all(v is None for v in d["pl"].values()) and d["number"] == "both":
            d["number"] = "sg_only"
        elif all(v is None for v in d["sg"].values()) and d["number"] == "both":
            d["number"] = "pl_only"
    a = rec["accented"][0]
    if ACUTE not in a and nvow(a) > 1 and "ё" not in a.lower():
        cand = None
        if d and d.get("type") == "noun":
            cand = (d["sg"].get("nom") or d["pl"].get("nom") or [None])[0]
        elif d and d.get("type") == "adj":
            cand = (d["m"].get("nom") or [None])[0]
        cand = (cand or "").split(",")[0].strip() or accent(lem)
        if cand and ACUTE in cand and norm(cand) == norm(lem):
            rec["accented"] = [cand[:1].upper() + cand[1:] if lem[:1].isupper() else cand, rec["accented"][1]]
        elif rec["accented"][1] == "v" and nvow(a) > 1:
            rec["accented"][1] = "u"
            review.append({"ref": wid, "field": "accented", "value": a, "alt": "",
                           "reason": "lema tanpa tanda aksen di OpenRussian", "kind": "uncertain"})
    pos_count[pos] += 1
    out_words.append(rec)

# --- bentuk kata kerja untuk tiap pasangan ---------------------------------
for pr in pairs:
    for side in ("ipf", "pf"):
        lem = pr[f"{side}Lemma"]
        if not lem:
            pr[side] = None
            continue
        want = "perf" if side == "pf" else "impf"
        cands = [q for q in M.parse(lem) if q.tag.POS == "INFN" and norm(q.normal_form) == norm(lem)]
        p = next((q for q in cands if want in q.tag), cands[0] if cands else None)
        row = best_row("verbs", lem, p)
        asp, forms = verb_forms(f"{pr['id']}.{side}", lem, row, p)
        if pr["type"] == "biaspectual":
            forms.pop("pres", None)
            forms["fut"] = None
            _, f2 = verb_forms(f"{pr['id']}.{side}", lem, row, p)
            forms["presfut"] = f2.get("pres") or f2.get("fut")
            forms.pop("fut")
        elif side == "pf" and "pres" in forms:
            forms["fut"] = forms.pop("pres")
            review.append({"ref": pr["id"], "field": "pf.aspect", "value": lem, "alt": "",
                           "reason": "kamus menandai kata kerja ini НСВ, file menempatkannya sebagai СВ", "kind": "uncertain"})
        elif side == "ipf" and "fut" in forms:
            forms["pres"] = forms.pop("fut")
            review.append({"ref": pr["id"], "field": "ipf.aspect", "value": lem, "alt": "",
                           "reason": "kamus menandai kata kerja ini СВ, file menempatkannya sebagai НСВ", "kind": "uncertain"})
        pr[side] = forms

json.dump({"meta": {"count": len(out_words), "pos": dict(pos_count)}, "entries": out_words},
          open(OUT / "base_words.json", "w"), ensure_ascii=False, indent=1)
json.dump({"meta": {"rows": len(ventries), "pairs": len(pairs)}, "pairs": pairs, "entries": ventries},
          open(OUT / "base_verbs.json", "w"), ensure_ascii=False, indent=1)
json.dump(review, open(OUT / "review_base.json", "w"), ensure_ascii=False, indent=1)
json.dump({k: sorted(v) for k, v in LOOK.items()}, open(OUT / "accent_lookup.json", "w"), ensure_ascii=False)
print("kata:", len(out_words), dict(pos_count))
print("kata kerja: baris", len(ventries), "pasangan", len(pairs), collections.Counter(p["type"] for p in pairs),
      collections.Counter(p["pairSource"] for p in pairs))
print("review:", len(review), collections.Counter(r["kind"] for r in review))
