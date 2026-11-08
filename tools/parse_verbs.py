import pdfplumber, re, json, sys
from collections import defaultdict

PDF = "/mnt/user-data/uploads/dokumen_tips_500-russian-verbs-569390d7d9743.pdf"
OUT = sys.argv[1]
rows = []
with pdfplumber.open(PDF) as pdf:
    for pno, page in enumerate(pdf.pages):
        words = page.extract_words(keep_blank_chars=False, use_text_flow=False)
        # rank tokens like "12." at the far left
        ranks = [w for w in words if re.fullmatch(r"\d{1,3}\.", w["text"]) and w["x0"] < 110]
        if not ranks:
            continue
        # column starts: first word right of the rank on the same line -> verb col
        cols = {"verb": [], "en": [], "pair": []}
        for r in ranks:
            same = sorted([w for w in words if abs(w["top"] - r["top"]) < 2 and w["x0"] > r["x1"]], key=lambda w: w["x0"])
            if same:
                cols["verb"].append(same[0]["x0"])
        verb_x = min(cols["verb"])
        # translation col / pair col: header on page 1, else infer from gaps
        allx = sorted(set(round(w["x0"]) for w in words if w["x0"] > verb_x + 40))
        # cluster left edges of words that start a cell: use words whose left neighbour gap > 12
        lines = defaultdict(list)
        for w in words:
            lines[round(w["top"])].append(w)
        starts = []
        for y, ws in lines.items():
            ws = sorted(ws, key=lambda w: w["x0"])
            prev = None
            for w in ws:
                if w["x0"] > verb_x + 40 and (prev is None or w["x0"] - prev["x1"] > 12):
                    starts.append(round(w["x0"]))
                prev = w
        hist = defaultdict(int)
        for s in starts:
            hist[s // 6 * 6] += 1
        peaks = sorted(hist.items(), key=lambda kv: -kv[1])[:2]
        en_x, pair_x = sorted(p[0] for p in peaks)
        ry = sorted([(r["top"], int(r["text"][:-1])) for r in ranks])
        cells = {n: {"verb": [], "en": [], "pair": []} for _, n in ry}
        for w in words:
            if w in ranks or w["top"] < ry[0][0] - 20:
                continue
            if re.fullmatch(r"\d{1,3}\.", w["text"]):
                continue
            # nearest rank row
            n = min(ry, key=lambda t: abs(t[0] - w["top"]))[1]
            x = w["x0"]
            col = "verb" if x < en_x - 3 else ("en" if x < pair_x - 3 else "pair")
            cells[n][col].append((round(w["top"]), w["x0"], w["text"]))
        for _, n in ry:
            rec = {"rank": n, "page": pno + 1}
            for c in ("verb", "en", "pair"):
                ws = sorted(cells[n][c], key=lambda t: (t[0], t[1]))
                rec[c] = " ".join(t[2] for t in ws)
            rows.append(rec)
rows.sort(key=lambda r: r["rank"])
json.dump(rows, open(OUT, "w"), ensure_ascii=False, indent=1)
print(len(rows), "rows")
